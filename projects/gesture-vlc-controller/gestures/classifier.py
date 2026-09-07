"""Calibrated, explainable static hand-gesture classifier."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence
class Gesture(str, Enum):
    NONE="NONE"; ONE_FINGER="ONE_FINGER"; TWO_FINGER="TWO_FINGER"; THREE_FINGER="THREE_FINGER"; FOUR_FINGER="FOUR_FINGER"; OPEN_PALM="OPEN_PALM"
@dataclass(frozen=True)
class FingerReadings:
    index: float; middle: float; ring: float; pinky: float; thumb: float
@dataclass(frozen=True)
class ClassificationResult:
    gesture: Gesture; confidence: float; readings: FingerReadings
    @property
    def finger_scores(self): return {"index":self.readings.index,"middle":self.readings.middle,"ring":self.readings.ring,"pinky":self.readings.pinky}
    @property
    def thumb_score(self): return self.readings.thumb
class GestureClassifier:
    def __init__(self, extended_threshold=0.72, folded_threshold=0.65, thumb_extended_threshold=0.72, thumb_folded_threshold=0.45, **_: Any):
        if not 0.0 <= folded_threshold < extended_threshold <= 1.0: raise ValueError("Require 0 <= folded_threshold < extended_threshold <= 1")
        self.extended_threshold=float(extended_threshold); self.folded_threshold=float(folded_threshold)
        self.thumb_extended_threshold=float(thumb_extended_threshold); self.thumb_folded_threshold=float(thumb_folded_threshold)
        self.four_open_thumb_boundary=0.62
    def _readings(self, landmarks):
        from vision.features import finger_scores, thumb_extension_score
        return FingerReadings(float(finger_scores(landmarks,"index").extension), float(finger_scores(landmarks,"middle").extension), float(finger_scores(landmarks,"ring").extension), float(finger_scores(landmarks,"pinky").extension), float(thumb_extension_score(landmarks)))
    def _extended_confidence(self, score):
        if score<=self.folded_threshold: return 0.0
        if score>=self.extended_threshold: return 1.0
        return (score-self.folded_threshold)/(self.extended_threshold-self.folded_threshold)
    def _folded_confidence(self, score):
        if score<=self.folded_threshold: return 1.0
        if score>=self.extended_threshold: return 0.0
        return (self.extended_threshold-score)/(self.extended_threshold-self.folded_threshold)
    def _pattern_confidence(self,r,pattern):
        values=(r.index,r.middle,r.ring,r.pinky); scores=[]
        for value,state in zip(values,pattern): scores.append(self._extended_confidence(value) if state=="E" else self._folded_confidence(value))
        return sum(scores)/4.0
    def is_one_finger(self,r): return r.index>=self.extended_threshold and r.middle<=self.folded_threshold and r.ring<=self.folded_threshold and r.pinky<=self.folded_threshold
    def is_two_finger(self,r): return r.index>=self.extended_threshold and r.middle>=self.extended_threshold and r.ring<=self.folded_threshold and r.pinky<=self.folded_threshold
    def is_three_finger(self,r): return r.index>=self.extended_threshold and r.middle>=self.extended_threshold and r.ring>=self.extended_threshold and r.pinky<=self.folded_threshold
    def is_four_finger(self,r): return r.index>=self.extended_threshold and r.middle>=self.extended_threshold and r.ring>=self.extended_threshold and r.pinky>=self.extended_threshold and r.thumb<self.four_open_thumb_boundary
    def is_open_palm(self,r): return r.index>=self.extended_threshold and r.middle>=self.extended_threshold and r.ring>=self.extended_threshold and r.pinky>=self.extended_threshold and r.thumb>=self.four_open_thumb_boundary
    def classify(self,landmarks):
        r=self._readings(landmarks)
        candidates=[(Gesture.ONE_FINGER,self._pattern_confidence(r,("E","F","F","F"))), (Gesture.TWO_FINGER,self._pattern_confidence(r,("E","E","F","F"))), (Gesture.THREE_FINGER,self._pattern_confidence(r,("E","E","E","F"))), (Gesture.FOUR_FINGER,self._pattern_confidence(r,("E","E","E","E"))), (Gesture.OPEN_PALM,self._pattern_confidence(r,("E","E","E","E")))]
        adjusted=[]
        for gesture,confidence in candidates:
            if gesture is Gesture.FOUR_FINGER:
                if r.thumb>=self.four_open_thumb_boundary: confidence=0.0
                else: confidence=0.80*confidence+0.20*max(0.0,min((self.four_open_thumb_boundary-r.thumb)/self.four_open_thumb_boundary,1.0))
            elif gesture is Gesture.OPEN_PALM:
                if r.thumb<self.four_open_thumb_boundary: confidence=0.0
                else: confidence=0.80*confidence+0.20*max(0.0,min((r.thumb-self.four_open_thumb_boundary)/(1.0-self.four_open_thumb_boundary),1.0))
            adjusted.append((gesture,confidence))
        gesture,confidence=max(adjusted,key=lambda x:x[1])
        checks={Gesture.ONE_FINGER:self.is_one_finger,Gesture.TWO_FINGER:self.is_two_finger,Gesture.THREE_FINGER:self.is_three_finger,Gesture.FOUR_FINGER:self.is_four_finger,Gesture.OPEN_PALM:self.is_open_palm}
        if not checks[gesture](r) or confidence<0.75: gesture,confidence=Gesture.NONE,0.0
        return ClassificationResult(gesture,float(max(0.0,min(confidence,1.0))),r)
