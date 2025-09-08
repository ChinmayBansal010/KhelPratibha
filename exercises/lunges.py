from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle, calculate_3d_distance
import numpy as np

class LungeCounter(RepCounter):
    def __init__(self):
        super().__init__("Lunge")
        self.stage = None

    def update(self, landmarks, debug=False):
        left_knee_angle = calculate_angle(landmarks['LEFT_HIP'], landmarks['LEFT_KNEE'], landmarks['LEFT_ANKLE'])
        right_knee_angle = calculate_angle(landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'], landmarks['RIGHT_ANKLE'])
        left_hip_angle = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_HIP'], landmarks['LEFT_KNEE'])
        right_hip_angle = calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'])
        torso_angle = calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['MID_HIP'], landmarks['RIGHT_HIP'])
        
        torso_width = calculate_3d_distance(landmarks['LEFT_SHOULDER'], landmarks['RIGHT_SHOULDER'])
        ankle_dist = calculate_3d_distance(landmarks['LEFT_ANKLE'], landmarks['RIGHT_ANKLE'])

        # Adaptive thresholds based on body
        knee_stand_thresh = 160
        knee_lunge_thresh = 100
        hip_stand_thresh = 160
        hip_lunge_thresh = 110
        ankle_width_thresh = torso_width * 0.8

        is_standing = (left_knee_angle > knee_stand_thresh and right_knee_angle > knee_stand_thresh and
                       left_hip_angle > hip_stand_thresh and right_hip_angle > hip_stand_thresh)
        is_lunge_down = ((left_knee_angle < knee_lunge_thresh or right_knee_angle < knee_lunge_thresh) and
                         (left_hip_angle < hip_lunge_thresh or right_hip_angle < hip_lunge_thresh) and
                         ankle_dist > ankle_width_thresh)

        # Stage transitions
        if is_lunge_down:
            self.stage = "down"

        if is_standing and self.stage == "down":
            self.stage = "up"
            # Form scoring
            form_ok = (left_knee_angle < 110 and right_knee_angle < 110 and
                       left_hip_angle < 120 and right_hip_angle < 120 and
                       torso_angle > 160)
            feedback = ""
            if not form_ok:
                if left_knee_angle > 110 or right_knee_angle > 110:
                    feedback += "Bend your knees more. "
                if left_hip_angle > 120 or right_hip_angle > 120:
                    feedback += "Keep your hips lower. "
                if torso_angle < 160:
                    feedback += "Keep your torso upright. "
            self.add_rep(form_ok, feedback.strip())

        if debug:
            angles_info = f"Knees: L={left_knee_angle:.1f}, R={right_knee_angle:.1f}; Hips: L={left_hip_angle:.1f}, R={right_hip_angle:.1f}; Torso={torso_angle:.1f}"
            stage_info = f"Stage: {self.stage}, Standing: {is_standing}, Lunge Down: {is_lunge_down}"
            print(f"{angles_info} | {stage_info}")
