# File: sports_analyzer/app/services/analysis/track/sprint.py
import numpy as np
from typing import Dict, List, Any

def _calculate_angle(a, b, c) -> float:
    """Calculate angle ABC (degrees), handles zero-length vectors."""
    a, b, c = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64), np.array(c, dtype=np.float64)
    ab, cb = a - b, c - b
    norm_ab, norm_cb = np.linalg.norm(ab), np.linalg.norm(cb)
    if norm_ab < 1e-6 or norm_cb < 1e-6:
        return 0.0
    angle = np.arctan2(np.linalg.det([ab, cb]), np.dot(ab, cb))
    return min(np.degrees(abs(angle)), 180.0)

def _smooth_series_ema(values: List[float], alpha: float = 0.2) -> List[float]:
    if not values: return []
    smoothed = [values[0]]
    for v in values[1:]:
        smoothed.append(alpha*v + (1-alpha)*smoothed[-1])
    return smoothed

def calculate_sprint_metrics(landmarks: List[Any], fps: float, height: float) -> Dict[str, Any]:
    if not landmarks or fps <= 0 or height <= 0: return {}

    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    pose0 = landmarks[0].landmark
    pixel_height = abs(pose0[30].y - pose0[0].y) if len(pose0) > 30 else 0
    pixel_to_meter = height / pixel_height if pixel_height > 0 else 0.0

    # Smoothed joint trajectories (all hips, knees, ankles)
    hip_x = _smooth_series_ema([(f.landmark[LEFT_HIP].x + f.landmark[RIGHT_HIP].x)/2 for f in landmarks])
    hip_y = _smooth_series_ema([(f.landmark[LEFT_HIP].y + f.landmark[RIGHT_HIP].y)/2 for f in landmarks])
    knee_y_l = _smooth_series_ema([f.landmark[LEFT_KNEE].y for f in landmarks])
    knee_y_r = _smooth_series_ema([f.landmark[RIGHT_KNEE].y for f in landmarks])
    ankle_y_l = _smooth_series_ema([f.landmark[LEFT_ANKLE].y for f in landmarks])
    ankle_y_r = _smooth_series_ema([f.landmark[RIGHT_ANKLE].y for f in landmarks])

    max_knee_angle, max_ankle_angle, stride_count, toe_offs = 0.0, 0.0, 0, []
    speeds, vertical_disp, ankle_drive = [], [], []

    window_size = max(2, int(fps*0.05))
    for i in range(window_size, len(landmarks)):
        curr, prev = landmarks[i].landmark, landmarks[i-window_size].landmark
        # Horizontal & vertical hip movement
        hip_curr_x = (curr[LEFT_HIP].x + curr[RIGHT_HIP].x)/2
        hip_prev_x = (prev[LEFT_HIP].x + prev[RIGHT_HIP].x)/2
        hip_curr_y = (curr[LEFT_HIP].y + curr[RIGHT_HIP].y)/2
        hip_prev_y = (prev[LEFT_HIP].y + prev[RIGHT_HIP].y)/2
        dx_m, dy_m = (hip_curr_x - hip_prev_x)*pixel_to_meter, (hip_curr_y - hip_prev_y)*pixel_to_meter
        dt = window_size / fps
        speed = np.sqrt(dx_m**2 + dy_m**2)/dt if dt > 0 else 0.0
        speeds.append(speed)
        vertical_disp.append(dy_m)

        # Knee & ankle angles for both legs
        angles_knee, angles_ankle = [], []
        for hip_idx, knee_idx, ankle_idx in [(LEFT_HIP, LEFT_KNEE, LEFT_ANKLE), (RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE)]:
            hip_p = [curr[hip_idx].x, curr[hip_idx].y]
            knee_p = [curr[knee_idx].x, curr[knee_idx].y]
            ankle_p = [curr[ankle_idx].x, curr[ankle_idx].y]
            angles_knee.append(_calculate_angle(hip_p, knee_p, ankle_p))
            angles_ankle.append(_calculate_angle(knee_p, ankle_p, hip_p))  # ankle drive angle
            # Ankle drive displacement
            ankle_drive.append((curr[ankle_idx].y - prev[ankle_idx].y)*pixel_to_meter)
        max_knee_angle = max(max_knee_angle, max(angles_knee))
        max_ankle_angle = max(max_ankle_angle, max(angles_ankle))

    # Toe-off detection (knee minima)
    for i in range(1, len(knee_y_l)-1):
        if (knee_y_l[i]<knee_y_l[i-1] and knee_y_l[i]<knee_y_l[i+1]) or \
           (knee_y_r[i]<knee_y_r[i-1] and knee_y_r[i]<knee_y_r[i+1]):
            stride_count += 1
            toe_offs.append(i)

    duration = len(landmarks)/fps
    cadence = stride_count/duration if duration>0 else 0.0

    # Avg stride length
    stride_len = 0.0
    if len(toe_offs)>1:
        dist_m = abs(hip_x[toe_offs[-1]] - hip_x[toe_offs[0]])*pixel_to_meter
        stride_len = dist_m/max(1, len(toe_offs)-1)

    # Acceleration
    acceleration = 0.0
    if len(speeds) > 1:
        accels = [(speeds[i]-speeds[i-1])/dt for i in range(1,len(speeds))]
        acceleration = np.percentile(accels,95)

    # Speed endurance (peak vs final 20%)
    endurance_drop = 0.0
    if len(speeds)>10:
        peak_speed = np.percentile(speeds,95)
        end_speed = np.mean(speeds[int(0.8*len(speeds)):])
        endurance_drop = (peak_speed-end_speed)/peak_speed*100 if peak_speed>0 else 0.0

    # Advanced metrics
    vertical_oscillation = np.std(vertical_disp)*pixel_to_meter if vertical_disp else 0.0
    asymmetry = np.abs(np.mean(knee_y_l)-np.mean(knee_y_r))*pixel_to_meter
    stride_variability = np.std(np.diff([hip_x[t] for t in toe_offs]))*pixel_to_meter if len(toe_offs)>1 else 0.0
    avg_ankle_drive = np.mean(np.abs(ankle_drive)) if ankle_drive else 0.0
    contact_time_est = duration/stride_count if stride_count>0 else 0.0

    return {
        "max_speed_mps": round(np.percentile(speeds,95) if speeds else 0.0,2),
        "avg_stride_length_m": round(stride_len,2),
        "cadence_hz": round(cadence,2),
        "max_knee_drive_deg": round(max_knee_angle,2),
        "max_ankle_drive_deg": round(max_ankle_angle,2),
        "stride_count": stride_count,
        "max_acceleration_mps2": round(acceleration,2),
        "speed_endurance_drop_pct": round(endurance_drop,1),
        "vertical_oscillation_m": round(vertical_oscillation,3),
        "asymmetry_m": round(asymmetry,3),
        "stride_variability_m": round(stride_variability,3),
        "avg_ankle_drive_m": round(avg_ankle_drive,3),
        "estimated_contact_time_s": round(contact_time_est,3),
        "fps": fps,
        "duration_s": round(duration,2),
        "pixel_to_meter": pixel_to_meter
    }
