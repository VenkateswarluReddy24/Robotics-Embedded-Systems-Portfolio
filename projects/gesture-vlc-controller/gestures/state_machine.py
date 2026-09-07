"""Gesture state machine for edge-triggered and long-hold VLC controls."""
from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from gestures.classifier import Gesture
@dataclass(frozen=True)
class ActionEvent:
    action: str
    source_gesture: Gesture
    confidence: float
    hold_seconds: float = 0.0
class GestureStateMachine:
    STATIC_ACTIONS = {Gesture.ONE_FINGER: "play", Gesture.TWO_FINGER: "pause", Gesture.THREE_FINGER: "stop"}
    LONG_HOLD_ACTIONS = {
        Gesture.ONE_FINGER: ("volume_up", 4.0, True),
        Gesture.TWO_FINGER: ("volume_down", 4.0, True),
        Gesture.OPEN_PALM: ("long_forward", 5.0, False),
        Gesture.FOUR_FINGER: ("long_backward", 5.0, False),
    }
    def __init__(self, cooldowns=None, *, hold_repeat_interval=1.0, long_hold_enabled=True):
        self.cooldowns = dict(cooldowns or {})
        self.hold_repeat_interval = max(0.1, float(hold_repeat_interval))
        self.long_hold_enabled = bool(long_hold_enabled)
        self.state = Gesture.NONE
        self.last_action_time = {}
        self._active_gesture = Gesture.NONE
        self._hold_started_at = None
        self._long_hold_started = False
        self._last_long_hold_event = -1e9
    def update(self, gesture, confidence, palm_center=None, now=None, gesture_entered=False):
        timestamp = monotonic() if now is None else float(now)
        if gesture is not self._active_gesture:
            self._active_gesture = gesture
            self._hold_started_at = timestamp if gesture is not Gesture.NONE else None
            self._long_hold_started = False
            self._last_long_hold_event = -1e9
        if gesture is Gesture.NONE:
            self.reset(); return None
        hold_seconds = 0.0 if self._hold_started_at is None else max(0.0, timestamp - self._hold_started_at)
        if gesture_entered and gesture in self.STATIC_ACTIONS:
            action = self.STATIC_ACTIONS[gesture]
            if self._allowed(action, timestamp):
                event = ActionEvent(action, gesture, float(confidence), 0.0)
                self._record(event, timestamp); self.state = gesture; return event
        if self.long_hold_enabled:
            spec = self.LONG_HOLD_ACTIONS.get(gesture)
            if spec is not None:
                action, threshold, repeat = spec
                if hold_seconds >= threshold:
                    first_fire = not self._long_hold_started
                    can_repeat = repeat and timestamp - self._last_long_hold_event >= self.hold_repeat_interval
                    if (first_fire or can_repeat) and self._allowed(action, timestamp):
                        event = ActionEvent(action, gesture, float(confidence), hold_seconds)
                        self._record(event, timestamp); self._long_hold_started = True
                        self._last_long_hold_event = timestamp; self.state = gesture; return event
        self.state = gesture
        return None
    def _allowed(self, action, now):
        return now - self.last_action_time.get(action, -1e9) >= self.cooldowns.get(action, 0.0)
    def _record(self, event, now): self.last_action_time[event.action] = now
    def reset(self):
        self.state = Gesture.NONE; self._active_gesture = Gesture.NONE; self._hold_started_at = None
        self._long_hold_started = False; self._last_long_hold_event = -1e9
