from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle, calculate_3d_distance
import numpy as np

class JumpingJackCounter(RepCounter):
    def __init__(self):
        super().__init__("JumpingJack")
        self.stage = None

    def update(self, landmarks, debug=False):
        left_arm_angle = calculate_angle(landmarks['LEFT_HIP'], landmarks['LEFT_SHOULDER'], landmarks['LEFT_ELBOW'])
        right_arm_angle = calculate_angle(landmarks['RIGHT_HIP'], landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_ELBOW'])
        avg_arm_angle = (left_arm_angle + right_arm_angle) / 2

        ankle_distance = calculate_3d_distance(landmarks['LEFT_ANKLE'], landmarks['RIGHT_ANKLE'])
        shoulder_width = calculate_3d_distance(landmarks['LEFT_SHOULDER'], landmarks['RIGHT_SHOULDER'])

        is_up = avg_arm_angle > 140 and ankle_distance > shoulder_width * 1.5
        is_down = avg_arm_angle < 45 and ankle_distance < shoulder_width

        if is_down:
            self.stage = "down"
        elif is_up and self.stage == 'down':
            self.stage = "up"
            form_ok = avg_arm_angle > 150 and ankle_distance > shoulder_width * 1.5
            feedback = "" if form_ok else "Raise your arms and legs fully."
            self.add_rep(form_ok, feedback)

        if debug:
            info = f"Arm Angle: {avg_arm_angle:.1f}, Ankle Dist: {ankle_distance:.1f}, Stage: {self.stage}"
            print(info)
