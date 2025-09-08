from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle
import numpy as np

class SquatCounter(RepCounter):
    def __init__(self):
        super().__init__("Squat")
        self.stage = None
        self.knee_up_threshold = 160
        self.knee_down_threshold = 90
        self.hip_back_threshold = 70

    def update(self, landmarks, debug=False):
        left_knee = calculate_angle(landmarks['LEFT_HIP'], landmarks['LEFT_KNEE'], landmarks['LEFT_ANKLE'])
        right_knee = calculate_angle(landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'], landmarks['RIGHT_ANKLE'])
        left_hip = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_HIP'], landmarks['LEFT_KNEE'])
        right_hip = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'])

        avg_knee = (left_knee + right_knee) / 2
        avg_hip = (left_hip + right_hip) / 2

        is_back_straight = avg_hip > self.hip_back_threshold
        form_ok = is_back_straight

        if avg_knee > self.knee_up_threshold:
            self.stage = "up"
        elif avg_knee < self.knee_down_threshold and self.stage == "up":
            self.stage = "down"
            feedback = ""
            if not is_back_straight:
                feedback = "Keep your back straighter."
                form_ok = False
            self.add_rep(form_ok, feedback)

        if debug:
            info = f"Knees: L={left_knee:.1f}, R={right_knee:.1f}; Hips: L={left_hip:.1f}, R={right_hip:.1f}; Stage={self.stage}"
            print(info)
