# Portfolio positioning

## One-line pitch

A real-time webcam-only VLC controller that converts noisy hand landmarks into stable, explainable user intent through temporal filtering and a deterministic state machine.

## Resume bullets

- Engineered a real-time webcam gesture-control pipeline using OpenCV and MediaPipe Hand Landmarker, converting 21-point hand landmarks into normalized finger-geometry features and deterministic gesture states.
- Implemented temporal stabilization, edge-triggered playback actions, long-hold interactions, action cooldowns, and explicit hand-loss recovery to reduce accidental commands in a noisy camera environment.
- Integrated VLC through its local HTTP/Lua interface, including VLC-native volume and long-jump actions, with authentication handling, reconnect logic, and clean runtime shutdown.

## Interview story

**Problem:** Single-frame gesture predictions are noisy and direct command triggering can cause false positives and repeated actions.

**Approach:** Separate perception from decision making, require temporal confirmation, use an explicit state machine for action transitions, and add cooldowns/hold thresholds around user intent.

**Result:** A webcam-only VLC controller that remains explainable, testable, and modular.

## 30-second demo sequence

1. Start the controller.
2. One finger -> Play.
3. Two fingers -> Pause.
4. Three fingers -> Stop.
5. One finger held -> Volume Up.
6. Two fingers held -> Volume Down.
7. Open palm held -> VLC Long Forward.
8. Four fingers held -> VLC Long Backward.
9. Press `Ctrl+C` in the terminal -> clean shutdown.
