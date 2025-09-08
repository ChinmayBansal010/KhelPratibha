from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle
import numpy as np

class PullupCounter(RepCounter):
    def __init__(self):
        super().__init__("Pullup")
        self.stage = None
        self.elbow_down_threshold = 160

    def update(self, landmarks, debug=False):
        left_elbow_angle = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_ELBOW'], landmarks['LEFT_WRIST'])
        right_elbow_angle = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_ELBOW'], landmarks['RIGHT_WRIST'])
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

        avg_shoulder_y = (landmarks['LEFT_SHOULDER'][1] + landmarks['RIGHT_SHOULDER'][1]) / 2
        avg_elbow_y = (landmarks['LEFT_ELBOW'][1] + landmarks['RIGHT_ELBOW'][1]) / 2

        is_down = avg_elbow_angle > self.elbow_down_threshold
        is_up = avg_shoulder_y < avg_elbow_y

        if is_down:
            self.stage = "down"
        elif is_up and self.stage == "down":
            self.stage = "up"
            form_ok = True  # Optionally, you could check if legs/torso are stable
            feedback = ""   # Can add form feedback if desired
            self.add_rep(form_ok, feedback)

        if debug:
            info = f"Elbow Angle: {avg_elbow_angle:.1f}, Shoulder Y: {avg_shoulder_y:.1f}, Elbow Y: {avg_elbow_y:.1f}, Stage: {self.stage}"
            print(info)
