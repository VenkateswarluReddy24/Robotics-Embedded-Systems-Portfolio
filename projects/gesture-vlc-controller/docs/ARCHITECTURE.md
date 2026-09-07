# Architecture Notes

The system is deliberately split into layers so perception noise does not directly become an application command.

```text
PERCEPTION
  Webcam -> OpenCV -> MediaPipe landmarks

FEATURE ENGINEERING
  Landmarks -> normalized finger-extension features

DECISION
  Features -> calibrated, explainable gesture classifier

TEMPORAL REASONING
  Frame predictions -> stable confirmed gesture

BEHAVIOR
  Confirmed gesture -> edge-trigger / long-hold state machine

ACTUATION
  Action -> authenticated VLC HTTP/Lua request
```

The key engineering boundary is **intent vs actuation**. The vision subsystem determines user intent; the VLC controller is responsible for translating that intent into VLC-specific commands.

This makes the perception stack reusable while keeping the playback backend isolated and testable.
