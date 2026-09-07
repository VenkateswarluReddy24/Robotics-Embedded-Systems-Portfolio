# Gesture VLC Controller

> Real-time, webcam-only human-computer interaction for VLC Media Player using MediaPipe Hand Landmarker, explainable hand-geometry classification, temporal stabilization, a deterministic gesture state machine, and VLC's local HTTP/Lua interface.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white) ![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red) ![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Landmarker-orange) ![VLC](https://img.shields.io/badge/VLC-HTTP%2FLua-black) ![Tests](https://img.shields.io/badge/Tests-13%20passed-success)

## What it does

Controls VLC using only a normal webcam. No OS-level keyboard simulation, mouse automation, browser automation, or external gesture hardware is required.

| Gesture | Interaction | Action |
|---|---:|---|
| One finger | Immediate | Play |
| Two fingers | Immediate | Pause |
| Three fingers | Immediate | Stop |
| One finger | Hold 4 s | Volume up, repeated while held |
| Two fingers | Hold 4 s | Volume down, repeated while held |
| Open palm | Hold 5 s | VLC long forward jump |
| Four fingers | Hold 5 s | VLC long backward jump |

## Architecture

```text
Webcam
  -> OpenCV
  -> MediaPipe Hand Landmarker
  -> 21 landmarks
  -> normalized finger geometry
  -> explainable classifier
  -> temporal stabilizer
  -> gesture state machine
  -> authenticated VLC HTTP/Lua controller
  -> VLC Media Player
```

## Engineering highlights

- **Explainable perception:** final gesture decisions are deterministic and based on normalized landmark geometry.
- **Real-camera calibration:** one/two/three/four-finger and open-palm thresholds were calibrated from measured webcam observations.
- **Four vs open-palm disambiguation:** the thumb separates the two four-primary-finger poses using a calibrated boundary.
- **Temporal stabilization:** commands are not fired from a single noisy frame.
- **Edge-triggered actions:** play/pause/stop do not spam VLC while a gesture remains held.
- **Long-hold interaction:** a second interaction dimension is added without requiring many additional poses.
- **VLC-native controls:** volume and long-jump behavior are delegated to VLC's internal actions rather than duplicated in Python.
- **Failure handling:** VLC authentication/reconnect failures, hand loss, webcam cleanup, and terminal `Ctrl+C` are handled explicitly.
- **Testing:** unit tests cover geometry, calibrated patterns, temporal confirmation, state-machine timing, and VLC command mapping.

## Repository structure

```text
main.py                    # real-time orchestration
config.py / config.json    # typed + runtime configuration
vision/                    # camera, landmarks, geometric features
gestures/                  # classifier, temporal layer, state machine
controllers/               # VLC HTTP/Lua integration
ui/                        # runtime dashboard
utils/                     # logging
scripts/                   # model/test helpers
tests/                     # automated tests
docs/                      # architecture and portfolio notes
```

## Run

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\download_model.py
python main.py
```

Configure the VLC HTTP password locally. The published configuration contains only `CHANGE_ME`; never commit a real credential.

## Test

```powershell
python -m pytest -q
```

The final local validation completed with **13 tests passing**.

## Portfolio positioning

This project demonstrates real-time computer vision, landmark-based feature engineering, temporal signal stabilization, deterministic state machines, protocol integration, runtime fault handling, modular Python design, and automated testing.

For a concise interview story and resume-ready bullets, see [`docs/PORTFOLIO.md`](docs/PORTFOLIO.md).
