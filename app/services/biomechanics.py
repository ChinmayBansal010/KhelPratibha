# File: sports_analyzer/app/services/biomechanics.py
import cv2
import mediapipe as mp
from typing import List, Tuple, Dict, Any
from .analysis.track import sprint, hurdles
from .analysis import jumps, throws

mp_pose = mp.solutions.pose

_CALCULATION_FUNCTIONS = {
    "sprint": sprint.calculate_sprint_metrics,
    "hurdles": hurdles.calculate_hurdles_metrics,
    # "high_jump": jumps.calculate_high_jump_metrics,
    # "long_jump": jumps.calculate_long_jump_metrics,
    # "shot_put": throws.calculate_shot_put_metrics,
    # "javelin": throws.calculate_javelin_throw_metrics,
    # "discus": throws.calculate_discus_throw_metrics,
}

def process_video(video_path: str) -> Tuple[List[Any], float]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    all_landmarks = []
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            
            if results.pose_landmarks:
                all_landmarks.append(results.pose_landmarks)
                
    cap.release()
    return all_landmarks, fps

def calculate_all_metrics(sport: str, landmarks: List[Any], fps: float, height: float) -> Dict[str, Any]:
    func = _CALCULATION_FUNCTIONS.get(sport)
    return func(landmarks, fps, height) if func else {}

