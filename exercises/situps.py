from utils.rep_counter import RepCounter
from utils.pose_utils import calculate_angle

class SitupCounter(RepCounter):
    def __init__(self):
        super().__init__("Situp")

    def update(self, landmarks):
        avg_hip = (calculate_angle(landmarks['LEFT_SHOULDER'], landmarks['LEFT_HIP'], landmarks['LEFT_KNEE']) +
                   calculate_angle(landmarks['RIGHT_SHOULDER'], landmarks['RIGHT_HIP'], landmarks['RIGHT_KNEE'])) / 2

        if avg_hip > 140: self.stage = "down"
        if avg_hip < 90 and self.stage == 'down':
            self.stage = "up"
            self.add_rep(True, "")