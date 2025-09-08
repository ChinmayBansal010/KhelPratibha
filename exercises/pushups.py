from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle
import numpy as np

class PushupCounter(RepCounter):
    def __init__(self):
        super().__init__("Pushup")
        self.stage = None
        self.elbow_up_threshold = 160
        self.elbow_down_threshold = 90
        self.hip_angle_threshold = 150

    def update(self, landmarks, debug=False):
        left_elbow = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_ELBOW'], landmarks['LEFT_WRIST'])
        right_elbow = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_ELBOW'], landmarks['RIGHT_WRIST'])
        left_hip = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_HIP'], landmarks['LEFT_KNEE'])
        right_hip = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'])

        avg_elbow = (left_elbow + right_elbow) / 2
        avg_hip = (left_hip + right_hip) / 2

        is_body_straight = avg_hip > self.hip_angle_threshold
        form_ok = is_body_straight

        if avg_elbow > self.elbow_up_threshold:
            self.stage = "up"
        elif avg_elbow < self.elbow_down_threshold and self.stage == "up":
            self.stage = "down"
            feedback = ""
            if not is_body_straight:
                feedback = "Keep your body straight."
                form_ok = False
            self.add_rep(form_ok, feedback)

        if debug:
            info = f"Elbows: L={left_elbow:.1f}, R={right_elbow:.1f}; Hips: L={left_hip:.1f}, R={right_hip:.1f}; Stage={self.stage}"
            print(info)
