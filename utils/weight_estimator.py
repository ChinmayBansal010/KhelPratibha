import cv2
import numpy as np
import mediapipe as mp
from .pose_utils import calculate_3d_distance

mp_pose = mp.solutions.pose

class WeightEstimator:
    """
    Estimates the weight category of a lift by analyzing the peak velocity
    of the user's wrists during the exercise.
    """
    def estimate_weight_category(self, filepath):
        """
        Analyzes a video to determine the plausible weight category of the lift.
        
        Returns:
            str: One of 'bodyweight', 'light', 'medium', 'heavy'.
        """
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            return "unknown"

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30  # Default to 30 FPS if unavailable

        prev_wrist_pos = None
        peak_velocity = 0.0

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)

                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    
                    # Use the average position of both wrists
                    left_wrist = np.array([lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y])
                    right_wrist = np.array([lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y])
                    current_wrist_pos = (left_wrist + right_wrist) / 2.0

                    if prev_wrist_pos is not None:
                        # Calculate distance moved in normalized screen coordinates
                        distance = np.linalg.norm(current_wrist_pos - prev_wrist_pos)
                        # Velocity = Distance / Time (time between frames is 1/fps)
                        velocity = distance * fps
                        
                        if velocity > peak_velocity:
                            peak_velocity = velocity
                    
                    prev_wrist_pos = current_wrist_pos
        
        cap.release()
        
        # --- Velocity-based Weight Categorization ---
        # These thresholds are a starting point and would be fine-tuned with testing.
        # A higher peak velocity implies a lighter weight.
        print(f"Detected Peak Lift Velocity: {peak_velocity:.2f}")

        if peak_velocity > 10.0:
            return 'bodyweight'
        elif peak_velocity > 6.0:
            return 'light'
        elif peak_velocity > 3.0:
            return 'medium'
        else:
            return 'heavy'
