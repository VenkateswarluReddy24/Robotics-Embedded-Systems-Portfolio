"""VLC HTTP controller using VLC's internal hotkey actions."""
from __future__ import annotations
import base64
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import requests
from requests.exceptions import RequestException
LOGGER = logging.getLogger(__name__)
@dataclass(frozen=True)
class VLCStatus:
    connected: bool
    state: str = "unknown"
    volume: int = 0
    time_seconds: float = 0.0
    length_seconds: float = 0.0
class VLCController:
    STATUS_PATH = "/requests/status.json"
    HOTKEY_ACTIONS = {"volume_up": "vol-up", "volume_down": "vol-down", "long_forward": "jump+long", "long_backward": "jump-long"}
    def __init__(self, host="127.0.0.1", port=4000, password="CHANGE_ME", timeout=1.5, reconnect_interval=2.0, executable=r"C:\Program Files\VideoLAN\VLC\vlc.exe", auto_start=True, startup_timeout=8.0):
        self.host, self.port, self.password = host, int(port), password
        self.timeout, self.reconnect_interval = float(timeout), float(reconnect_interval)
        self.executable = Path(executable) if executable else None
        self.auto_start, self.startup_timeout = bool(auto_start), float(startup_timeout)
        self.base_url = f"http://{self.host}:{self.port}"; self.status_url = f"{self.base_url}{self.STATUS_PATH}"
        self._session = requests.Session(); token = base64.b64encode(f":{self.password}".encode()).decode()
        self._session.headers.update({"Authorization": f"Basic {token}", "User-Agent": "Gesture-VLC-Controller/1.0"})
        self._connected = False; self._last_connection_attempt = 0.0; self._process = None; self._last_status = VLCStatus(False); self._last_error = None
    @property
    def connected(self): return self._connected
    @property
    def last_error(self): return self._last_error
    def connect(self, force=False):
        now=time.monotonic()
        if not force and now-self._last_connection_attempt < self.reconnect_interval: return self._connected
        self._last_connection_attempt=now
        if self._probe(): return True
        if self.auto_start and self.executable and self.executable.exists():
            if self._process is None or self._process.poll() is not None: self._start_vlc()
            deadline=time.monotonic()+self.startup_timeout
            while time.monotonic()<deadline:
                if self._probe(): return True
                time.sleep(0.15)
        self._connected=False; return False
    def _probe(self):
        try:
            r=self._session.get(self.status_url, timeout=self.timeout)
            if r.status_code==401: self._last_error="VLC authentication failed"; self._connected=False; return False
            r.raise_for_status(); self._last_status=self._parse_status(r.json()); self._connected=True; self._last_error=None; return True
        except (RequestException, ValueError) as exc: self._last_error=str(exc); self._connected=False; return False
    def _start_vlc(self):
        command=[str(self.executable),"--extraintf=http","--http-host=127.0.0.1",f"--http-port={self.port}",f"--http-password={self.password}"]
        try: self._process=subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        except OSError as exc: self._process=None; self._last_error=str(exc)
    def _command(self, command, **params):
        params=dict(params); params["command"]=command
        try:
            r=self._session.get(self.status_url, params=params, timeout=self.timeout)
            if r.status_code==401: self._connected=False; self._last_error="VLC authentication failed"; return False
            r.raise_for_status()
            try: self._last_status=self._parse_status(r.json())
            except ValueError: pass
            self._connected=True; self._last_error=None; return True
        except RequestException as exc: self._connected=False; self._last_error=str(exc); return False
    def _hotkey(self, action_name): return self._command("key", val=self.HOTKEY_ACTIONS[action_name])
    def play(self): return self._command("pl_play")
    def pause(self): return self._command("pl_pause")
    def stop(self): return self._command("pl_stop")
    def volume_up(self): return self._hotkey("volume_up")
    def volume_down(self): return self._hotkey("volume_down")
    def long_forward(self): return self._hotkey("long_forward")
    def long_backward(self): return self._hotkey("long_backward")
    def seek_forward(self, seconds=10): return self.long_forward()
    def seek_backward(self, seconds=10): return self.long_backward()
    def get_status(self): return self._last_status
    @staticmethod
    def _parse_status(data: dict[str, Any]):
        try: volume=int(data.get("volume",0))
        except (TypeError,ValueError): volume=0
        try: current=float(data.get("time",0.0))
        except (TypeError,ValueError): current=0.0
        try: length=float(data.get("length",0.0))
        except (TypeError,ValueError): length=0.0
        return VLCStatus(True, str(data.get("state","unknown")), volume, current, length)
    def close(self): self._session.close(); self._connected=False
