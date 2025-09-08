from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle, calculate_3d_distance
import numpy as np

class BicepCurlCounter(RepCounter):
    def __init__(self):
        super().__init__("BicepCurl")
        self.stage = None
        self.initial_elbow_angles = None

    def update(self, landmarks, debug=False):
        left_elbow_angle = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_ELBOW'], landmarks['LEFT_WRIST'])
        right_elbow_angle = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_ELBOW'], landmarks['RIGHT_WRIST'])
        left_shoulder_angle = calculate_angle(landmarks['LEFT_HIP'], landmarks['LEFT_SHOULDER'], landmarks['LEFT_ELBOW'])
        right_shoulder_angle = calculate_angle(landmarks['RIGHT_HIP'], landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_ELBOW'])

        # Optional: initialize reference elbow angles for adaptive thresholds
        if self.initial_elbow_angles is None:
            self.initial_elbow_angles = {'left': left_elbow_angle, 'right': right_elbow_angle}

        elbow_threshold_up = 40
        elbow_threshold_down = 160
        shoulder_flare_limit = 45

        avg_elbow = (left_elbow_angle + right_elbow_angle) / 2
        avg_shoulder = (left_shoulder_angle + right_shoulder_angle) / 2

        is_down = avg_elbow > elbow_threshold_down
        is_up = avg_elbow < elbow_threshold_up
        is_shoulder_stable = avg_shoulder < shoulder_flare_limit

        if is_down:
            self.stage = "down"

        if is_up and self.stage == "down":
            self.stage = "up"
            feedback = ""
            form_ok = True
            if not is_shoulder_stable:
                feedback += "Keep your upper arms still. "
                form_ok = False
            if left_elbow_angle > elbow_threshold_up + 10 or right_elbow_angle > elbow_threshold_up + 10:
                feedback += "Curl fully to hit the top position. "
                form_ok = False
            self.add_rep(form_ok, feedback.strip())

        if debug:
            info = f"Elbows: L={left_elbow_angle:.1f}, R={right_elbow_angle:.1f}; Shoulders: L={left_shoulder_angle:.1f}, R={right_shoulder_angle:.1f}; Stage={self.stage}"
            print(info)
