import numpy as np
from typing import Dict, List, Any
from ...utils import smooth_series_ema, calculate_angle

def calculate_sprint_metrics(landmarks: List[Any], fps: float, height: float) -> Dict[str, Any]:
    if not landmarks or fps <= 0 or height <= 0:
        return {}

    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    pose0 = landmarks[0].landmark
    pixel_height = abs(pose0[30].y - pose0[0].y) if len(pose0) > 30 else 0
    pixel_to_meter = height / pixel_height if pixel_height > 0 else 0.0

    hip_x = smooth_series_ema([(f.landmark[LEFT_HIP].x + f.landmark[RIGHT_HIP].x)/2 for f in landmarks])
    hip_y = smooth_series_ema([(f.landmark[LEFT_HIP].y + f.landmark[RIGHT_HIP].y)/2 for f in landmarks])
    knee_y_l = smooth_series_ema([f.landmark[LEFT_KNEE].y for f in landmarks])
    knee_y_r = smooth_series_ema([f.landmark[RIGHT_KNEE].y for f in landmarks])
    ankle_y_l = smooth_series_ema([f.landmark[LEFT_ANKLE].y for f in landmarks])
    ankle_y_r = smooth_series_ema([f.landmark[RIGHT_ANKLE].y for f in landmarks])

    max_knee_angle, max_ankle_angle, stride_count_knee, stride_count_ankle = 0.0, 0.0, 0, 0
    toe_offs_knee, toe_offs_ankle = [], []
    speeds, vertical_disp, ankle_drive = [], [], []

    window_size = max(2, int(fps*0.05))
    for i in range(window_size, len(landmarks)):
        curr, prev = landmarks[i].landmark, landmarks[i-window_size].landmark
        hip_curr_x = (curr[LEFT_HIP].x + curr[RIGHT_HIP].x)/2
        hip_prev_x = (prev[LEFT_HIP].x + prev[RIGHT_HIP].x)/2
        hip_curr_y = (curr[LEFT_HIP].y + curr[RIGHT_HIP].y)/2
        hip_prev_y = (prev[LEFT_HIP].y + prev[RIGHT_HIP].y)/2
        dx_m, dy_m = (hip_curr_x-hip_prev_x)*pixel_to_meter, (hip_curr_y-hip_prev_y)*pixel_to_meter
        dt = window_size/fps
        speed = np.hypot(dx_m, dy_m)/dt if dt>0 else 0.0
        speeds.append(speed)
        vertical_disp.append(dy_m)

        angles_knee, angles_ankle = [], []
        for hip_idx, knee_idx, ankle_idx in [(LEFT_HIP, LEFT_KNEE, LEFT_ANKLE), (RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE)]:
            hip_p = [curr[hip_idx].x, curr[hip_idx].y]
            knee_p = [curr[knee_idx].x, curr[knee_idx].y]
            ankle_p = [curr[ankle_idx].x, curr[ankle_idx].y]
            angles_knee.append(calculate_angle(hip_p, knee_p, ankle_p))
            angles_ankle.append(calculate_angle(knee_p, ankle_p, hip_p))
            ankle_drive.append((curr[ankle_idx].y - prev[ankle_idx].y)*pixel_to_meter)
        max_knee_angle = max(max_knee_angle, max(angles_knee))
        max_ankle_angle = max(max_ankle_angle, max(angles_ankle))

    for i in range(1, len(knee_y_l)-1):
        if (knee_y_l[i]<knee_y_l[i-1] and knee_y_l[i]<knee_y_l[i+1]) or \
           (knee_y_r[i]<knee_y_r[i-1] and knee_y_r[i]<knee_y_r[i+1]):
            stride_count_knee += 1
            toe_offs_knee.append(i)

    for i in range(1, len(ankle_y_l)-1):
        if (ankle_y_l[i]>ankle_y_l[i-1] and ankle_y_l[i]>ankle_y_l[i+1]) or \
           (ankle_y_r[i]>ankle_y_r[i-1] and ankle_y_r[i]>ankle_y_r[i+1]):
            stride_count_ankle += 1
            toe_offs_ankle.append(i)

    duration = len(landmarks)/fps
    cadence_knee = stride_count_knee/duration if duration>0 else 0.0
    cadence_ankle = stride_count_ankle/duration if duration>0 else 0.0

    stride_len_knee, stride_len_ankle = 0.0, 0.0
    if len(toe_offs_knee)>1:
        dist_m = abs(hip_x[toe_offs_knee[-1]] - hip_x[toe_offs_knee[0]])*pixel_to_meter
        stride_len_knee = dist_m/max(1, len(toe_offs_knee)-1)
    if len(toe_offs_ankle)>1:
        dist_m = abs(hip_x[toe_offs_ankle[-1]] - hip_x[toe_offs_ankle[0]])*pixel_to_meter
        stride_len_ankle = dist_m/max(1, len(toe_offs_ankle)-1)

    acceleration = 0.0
    if len(speeds) > 1:
        accels = [(speeds[i]-speeds[i-1])/(window_size/fps) for i in range(1,len(speeds))]
        acceleration = np.percentile(accels,95)

    endurance_drop = 0.0
    if len(speeds)>10:
        peak_speed = np.percentile(speeds,95)
        end_speed = np.mean(speeds[int(0.8*len(speeds)):])
        endurance_drop = (peak_speed-end_speed)/peak_speed*100 if peak_speed>0 else 0.0

    vertical_oscillation = np.std(vertical_disp)*pixel_to_meter if vertical_disp else 0.0
    asymmetry_knee = np.abs(np.mean(knee_y_l)-np.mean(knee_y_r))*pixel_to_meter
    asymmetry_ankle = np.abs(np.mean(ankle_y_l)-np.mean(ankle_y_r))*pixel_to_meter
    stride_variability_knee = np.std(np.diff([hip_x[t] for t in toe_offs_knee]))*pixel_to_meter if len(toe_offs_knee)>1 else 0.0
    stride_variability_ankle = np.std(np.diff([hip_x[t] for t in toe_offs_ankle]))*pixel_to_meter if len(toe_offs_ankle)>1 else 0.0
    avg_ankle_drive = np.mean(np.abs(ankle_drive)) if ankle_drive else 0.0
    contact_time_est_knee = duration/stride_count_knee if stride_count_knee>0 else 0.0
    contact_time_est_ankle = duration/stride_count_ankle if stride_count_ankle>0 else 0.0

    return {
        "max_speed_mps": round(np.percentile(speeds,95) if speeds else 0.0,2),
        "cadence_knee_hz": round(cadence_knee,2),
        "cadence_ankle_hz": round(cadence_ankle,2),
        "avg_stride_length_knee_m": round(stride_len_knee,2),
        "avg_stride_length_ankle_m": round(stride_len_ankle,2),
        "stride_count_knee": stride_count_knee,
        "stride_count_ankle": stride_count_ankle,
        "max_knee_drive_deg": round(max_knee_angle,2),
        "max_ankle_drive_deg": round(max_ankle_angle,2),
        "max_acceleration_mps2": round(acceleration,2),
        "speed_endurance_drop_pct": round(endurance_drop,1),
        "vertical_oscillation_m": round(vertical_oscillation,3),
        "asymmetry_knee_m": round(asymmetry_knee,3),
        "asymmetry_ankle_m": round(asymmetry_ankle,3),
        "stride_variability_knee_m": round(stride_variability_knee,3),
        "stride_variability_ankle_m": round(stride_variability_ankle,3),
        "avg_ankle_drive_m": round(avg_ankle_drive,3),
        "contact_time_est_knee_s": round(contact_time_est_knee,3),
        "contact_time_est_ankle_s": round(contact_time_est_ankle,3),
        "fps": fps,
        "duration_s": round(duration,2),
        "pixel_to_meter": pixel_to_meter
    }
