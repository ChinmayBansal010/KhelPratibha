import cv2
import numpy as np
import mediapipe as mp
from collections import Counter, deque
from .pose_utils import calculate_angle, calculate_3d_distance


mp_pose = mp.solutions.pose

class ExerciseClassifier:
    def __init__(self, max_frames=150, smoothing_window=5, debug=False):
        self.max_frames = max_frames
        self.smoothing_window = smoothing_window
        self.debug = debug
        self.pose_history = deque(maxlen=smoothing_window)

        self.thresholds = {
            'orientation_ratio': 1.2,
            'stand_knee_angle': 165, 'stand_hip_angle': 165, 'stand_back_angle': 160,
            'squat_knee_angle': 100, 'squat_hip_angle': 110, 'squat_back_angle': 150,
            'pullup_elbow_angle': 100,
            'pushup_straight_hip_angle': 150, 'pushup_back_angle': 150,
            'pushup_up_elbow_angle': 160, 'pushup_down_elbow_angle': 100,
            'situp_down_hip_angle': 160, 'situp_down_knee_angle': 160, 'situp_back_angle': 150,
            'situp_up_hip_angle': 100,
            'lunge_knee_angle': 100,
            'bicep_curl_up_elbow': 40, 'bicep_curl_down_elbow': 160,
            'jj_up_ankle_dist_ratio': 1.5,
            'pullup_wrist_dist_ratio': 1.5
        }

    def _orientation(self, landmarks):
        shoulder_mid = (np.array(landmarks['LEFT_SHOULDER']) + np.array(landmarks['RIGHT_SHOULDER'])) / 2
        ankle_mid = (np.array(landmarks['LEFT_ANKLE']) + np.array(landmarks['RIGHT_ANKLE'])) / 2
        y_span = abs(shoulder_mid[1] - ankle_mid[1])
        x_span = abs(shoulder_mid[0] - ankle_mid[0])
        return 'horizontal' if x_span > y_span * self.thresholds['orientation_ratio'] else 'vertical'

    def _normalize_distance(self, dist, torso_width):
        return dist / torso_width

    def _average_angle(self, landmarks, triples):
        return np.mean([calculate_angle(landmarks[a], landmarks[b], landmarks[c]) for a,b,c in triples])

    def _smooth_pose(self, pose):
        self.pose_history.append(pose)
        return Counter(self.pose_history).most_common(1)[0][0]

    def _get_pose_from_landmarks(self, landmarks):
        torso_width = calculate_3d_distance(landmarks['LEFT_SHOULDER'], landmarks['RIGHT_SHOULDER'])
        avg_knee = self._average_angle(landmarks, [('LEFT_HIP','LEFT_KNEE','LEFT_ANKLE'), ('RIGHT_HIP','RIGHT_KNEE','RIGHT_ANKLE')])
        avg_hip = self._average_angle(landmarks, [('LEFT_SHOULDER','LEFT_HIP','LEFT_KNEE'), ('RIGHT_SHOULDER','RIGHT_HIP','RIGHT_KNEE')])
        avg_elbow = self._average_angle(landmarks, [('LEFT_SHOULDER','LEFT_ELBOW','LEFT_WRIST'), ('RIGHT_SHOULDER','RIGHT_ELBOW','RIGHT_WRIST')])
        avg_back = self._average_angle(landmarks, [('LEFT_SHOULDER','LEFT_HIP','LEFT_KNEE'), ('RIGHT_SHOULDER','RIGHT_HIP','RIGHT_KNEE')])
        shoulder_mid = (np.array(landmarks['LEFT_SHOULDER']) + np.array(landmarks['RIGHT_SHOULDER'])) / 2
        ankle_mid = (np.array(landmarks['LEFT_ANKLE']) + np.array(landmarks['RIGHT_ANKLE'])) / 2
        wrist_dist = calculate_3d_distance(landmarks['LEFT_WRIST'], landmarks['RIGHT_WRIST'])
        ankle_dist = calculate_3d_distance(landmarks['LEFT_ANKLE'], landmarks['RIGHT_ANKLE'])
        hands_up = (landmarks['LEFT_WRIST'][1] < shoulder_mid[1]) and (landmarks['RIGHT_WRIST'][1] < shoulder_mid[1])
        orientation = self._orientation(landmarks)

        pose_rules = [
            ('standing', orientation=='vertical' and avg_knee>self.thresholds['stand_knee_angle'] and avg_hip>self.thresholds['stand_hip_angle'] and avg_back>self.thresholds['stand_back_angle']),
            ('squatting', orientation=='vertical' and avg_knee<self.thresholds['squat_knee_angle'] and avg_hip<self.thresholds['squat_hip_angle'] and avg_back<self.thresholds['squat_back_angle']),
            ('pullup_up', orientation=='vertical' and hands_up and avg_elbow<self.thresholds['pullup_elbow_angle'] and self._normalize_distance(wrist_dist, torso_width)<self.thresholds['pullup_wrist_dist_ratio']),
            ('jumping_jacks_up', orientation=='vertical' and hands_up and self._normalize_distance(ankle_dist, torso_width)>self.thresholds['jj_up_ankle_dist_ratio']),
            ('pushup_up', orientation=='horizontal' and avg_hip>self.thresholds['pushup_straight_hip_angle'] and avg_back>self.thresholds['pushup_back_angle'] and avg_elbow>self.thresholds['pushup_up_elbow_angle']),
            ('pushup_down', orientation=='horizontal' and avg_hip>self.thresholds['pushup_straight_hip_angle'] and avg_back>self.thresholds['pushup_back_angle'] and avg_elbow<self.thresholds['pushup_down_elbow_angle']),
            ('situp_down', orientation=='horizontal' and avg_hip>self.thresholds['situp_down_hip_angle'] and avg_knee>self.thresholds['situp_down_knee_angle'] and avg_back>self.thresholds['situp_back_angle']),
            ('situp_up', orientation=='horizontal' and avg_hip<self.thresholds['situp_up_hip_angle']),
            ('lunge_pose', orientation=='vertical' and landmarks['LEFT_KNEE'][1]>landmarks['RIGHT_KNEE'][1] and avg_knee<self.thresholds['lunge_knee_angle']),
            ('bicep_curl_up', orientation=='vertical' and avg_elbow<self.thresholds['bicep_curl_up_elbow']),
            ('bicep_curl_down', orientation=='vertical' and avg_elbow>self.thresholds['bicep_curl_down_elbow']),
        ]
        for name, cond in pose_rules:
            if cond:
                return name
        return 'transitioning'

    def classify(self, filepath):
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened(): return "unknown"
        pose_sequence = []
        frame_count = 0
        with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
            while cap.isOpened() and frame_count<self.max_frames:
                ret, frame = cap.read()
                if not ret: break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    h,w,_ = frame.shape
                    landmarks = {name:(lm[mark.value].x*w, lm[mark.value].y*h, lm[mark.value].z) for name,mark in mp_pose.PoseLandmark.__members__.items()}
                    current_pose = self._get_pose_from_landmarks(landmarks)
                    smoothed_pose = self._smooth_pose(current_pose)
                    if smoothed_pose != 'transitioning' and (not pose_sequence or pose_sequence[-1]!=smoothed_pose):
                        pose_sequence.append(smoothed_pose)
                    if self.debug:
                        for name, coord in landmarks.items():
                            cv2.circle(frame, (int(coord[0]), int(coord[1])), 4, (0,255,0), -1)
                        cv2.putText(frame, smoothed_pose, (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                        cv2.imshow("Debug Pose", frame)
                        if cv2.waitKey(1)&0xFF==27: break
                frame_count+=1
        cap.release()
        if self.debug:
            cv2.destroyAllWindows()
        if not pose_sequence: return "unknown"
        detected_poses = set(pose_sequence)
        rules = [
            ('squats', {'standing','squatting'}),
            ('pushups', {'pushup_up','pushup_down'}),
            ('situps', {'situp_up','situp_down'}),
            ('pullups', {'pullup_up'}),
            ('jumpingjacks', {'standing','jumping_jacks_up'}),
            ('lunges', {'standing','lunge_pose'}),
            ('bicepcurls', {'bicep_curl_up','bicep_curl_down'}),
        ]
        for ex, req in rules:
            if req.issubset(detected_poses):
                confidence = sum([pose_sequence.count(p)/len(pose_sequence) for p in req])/len(req)
                return f"{ex} ({confidence*100:.0f}%)"
        most_common = Counter(pose_sequence).most_common(1)[0][0]
        fallback_map = {
            'squatting':'squats','standing':'squats',
            'pushup_up':'pushups','pushup_down':'pushups',
            'situp_up':'situps','situp_down':'situps',
            'lunge_pose':'lunges',
            'bicep_curl_up':'bicepcurls','bicep_curl_down':'bicepcurls',
        }
        return fallback_map.get(most_common,"unknown")
