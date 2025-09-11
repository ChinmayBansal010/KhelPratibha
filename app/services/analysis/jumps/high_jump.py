from typing import Dict, List, Any
import numpy as np
from ...utils import smooth_series_ema, calculate_angle

def calculate_high_jump_metrics(landmarks: List[Any], fps: float, height: float) -> Dict[str, Any]:
    if not landmarks or fps <= 0 or height <= 0:
        return {}

    L_HIP, R_HIP = 23, 24
    L_KNEE, R_KNEE = 25, 26
    L_ANKLE, R_ANKLE = 27, 28
    L_SHOULDER, R_SHOULDER = 11, 12
    NOSE = 0

    pose0 = landmarks[0].landmark
    if len(pose0) > R_ANKLE:
        pixel_height = abs(pose0[NOSE].y - pose0[L_ANKLE].y)
    elif len(pose0) > L_SHOULDER:
        pixel_height = abs(pose0[L_SHOULDER].y - pose0[L_ANKLE].y)
    else:
        pixel_height = 0
    pixel_to_meter = height / pixel_height if pixel_height > 0 else 0.0

    def _col(idx, coord):
        return [getattr(f.landmark[idx], coord) for f in landmarks]

    hip_x = np.array(smooth_series_ema([ (x+y)/2 for x,y in zip(_col(L_HIP,'x'), _col(R_HIP,'x')) ]))
    hip_y = np.array(smooth_series_ema([ (x+y)/2 for x,y in zip(_col(L_HIP,'y'), _col(R_HIP,'y')) ]))

    knee_l_y = np.array(smooth_series_ema(_col(L_KNEE, 'y')))
    knee_r_y = np.array(smooth_series_ema(_col(R_KNEE, 'y')))

    ankle_l_y = np.array(smooth_series_ema(_col(L_ANKLE, 'y')))
    ankle_r_y = np.array(smooth_series_ema(_col(R_ANKLE, 'y')))

    sh_l_x = np.array(smooth_series_ema(_col(L_SHOULDER, 'x')))
    sh_l_y = np.array(smooth_series_ema(_col(L_SHOULDER, 'y')))
    sh_r_x = np.array(smooth_series_ema(_col(R_SHOULDER, 'x')))
    sh_r_y = np.array(smooth_series_ema(_col(R_SHOULDER, 'y')))

    hip_mid_x = hip_x
    hip_mid_y = hip_y
    sh_mid_x = (sh_l_x + sh_r_x) / 2 if sh_l_x.size and sh_r_x.size else np.zeros_like(hip_x)
    sh_mid_y = (sh_l_y + sh_r_y) / 2 if sh_l_y.size and sh_r_y.size else np.zeros_like(hip_y)

    if ankle_l_y.size == 0 or ankle_r_y.size == 0:
        return {}

    take_off_foot_y = ankle_l_y if np.nanmean(ankle_l_y) > np.nanmean(ankle_r_y) else ankle_r_y
    if take_off_foot_y.size == 0:
        return {}

    take_off_frame = int(np.argmin(take_off_foot_y))
    if take_off_frame >= len(hip_y) - 1:
        return {}

    peak_rel = int(np.argmin(hip_y[take_off_frame:])) if take_off_frame < len(hip_y) else 0
    peak_frame = take_off_frame + peak_rel
    landing_rel = int(np.argmax(hip_y[peak_frame:])) if peak_frame < len(hip_y) - 1 else 0
    landing_frame = min(len(hip_y) - 1, peak_frame + landing_rel)

    hip_y_to, hip_y_pk = hip_mid_y[take_off_frame], hip_mid_y[peak_frame]
    jump_height_m = (hip_y_to - hip_y_pk) * pixel_to_meter

    window = max(1, int(fps * 0.05))
    idx_pre = max(0, take_off_frame - window)
    idx_post = min(len(hip_y) - 1, take_off_frame + window)
    dy = (hip_mid_y[idx_post] - hip_mid_y[idx_pre]) * pixel_to_meter
    dt = (idx_post - idx_pre) / fps if (idx_post - idx_pre) > 0 else 1.0
    take_off_velocity_mps = -dy / dt

    p_idx_post = min(len(hip_x) - 1, take_off_frame + int(fps * 0.1))
    dx = hip_mid_x[p_idx_post] - hip_mid_x[take_off_frame]
    dy2 = hip_mid_y[p_idx_post] - hip_mid_y[take_off_frame]
    take_off_angle_deg = float(np.degrees(np.arctan2(-dy2, dx))) if dx != 0 or dy2 != 0 else 0.0

    pre_takeoff_idx = max(0, take_off_frame - int(fps * 0.2))
    dx_approach = abs(hip_mid_x[take_off_frame] - hip_mid_x[pre_takeoff_idx]) * pixel_to_meter
    dt_approach = (take_off_frame - pre_takeoff_idx) / fps if (take_off_frame - pre_takeoff_idx) > 0 else 1.0
    approach_speed_mps = dx_approach / dt_approach

    flight_time_s = (landing_frame - take_off_frame) / fps

    vert_vel_mps = (hip_y_to - hip_y_pk) * pixel_to_meter / (flight_time_s / 2) if flight_time_s > 0 else 0.0
    vertical_acceleration = take_off_velocity_mps / dt if dt > 0 else 0.0
    power_index = take_off_velocity_mps * approach_speed_mps

    symmetry_knee = 1 - abs(np.nanmean(knee_l_y) - np.nanmean(knee_r_y)) / (abs(np.nanmean(knee_l_y)) + abs(np.nanmean(knee_r_y)) + 1e-6)
    symmetry_ankle = 1 - abs(np.nanmean(ankle_l_y) - np.nanmean(ankle_r_y)) / (abs(np.nanmean(ankle_l_y)) + abs(np.nanmean(ankle_r_y)) + 1e-6)
    symmetry_shoulder = 1 - abs(np.nanmean(sh_l_y) - np.nanmean(sh_r_y)) / (abs(np.nanmean(sh_l_y)) + abs(np.nanmean(sh_r_y)) + 1e-6)
    shoulder_symmetry_m = abs(np.nanmean(sh_l_y) - np.nanmean(sh_r_y)) * pixel_to_meter

    shoulder_tilt_deg = float(np.degrees(np.arctan2(sh_r_y[take_off_frame] - sh_l_y[take_off_frame],
                                                      sh_r_x[take_off_frame] - sh_l_x[take_off_frame]))) if sh_l_x.size and sh_r_x.size else 0.0

    torso_vec_x = sh_mid_x[take_off_frame] - hip_mid_x[take_off_frame]
    torso_vec_y = sh_mid_y[take_off_frame] - hip_mid_y[take_off_frame]
    torso_angle_deg = float(np.degrees(np.arctan2(torso_vec_y, torso_vec_x))) if torso_vec_x != 0 or torso_vec_y != 0 else 0.0
    torso_lean_from_vertical = abs(90.0 - abs(torso_angle_deg))

    frame = landmarks[take_off_frame]
    left_hip_angle = calculate_angle(
        (frame.landmark[L_SHOULDER].x, frame.landmark[L_SHOULDER].y),
        (frame.landmark[L_HIP].x, frame.landmark[L_HIP].y),
        (frame.landmark[L_KNEE].x, frame.landmark[L_KNEE].y)
    ) if len(frame.landmark) > L_KNEE else 0.0
    right_hip_angle = calculate_angle(
        (frame.landmark[R_SHOULDER].x, frame.landmark[R_SHOULDER].y),
        (frame.landmark[R_HIP].x, frame.landmark[R_HIP].y),
        (frame.landmark[R_KNEE].x, frame.landmark[R_KNEE].y)
    ) if len(frame.landmark) > R_KNEE else 0.0
    hip_angle_deg = (left_hip_angle + right_hip_angle) / 2.0

    left_knee_angle = calculate_angle(
        (frame.landmark[L_HIP].x, frame.landmark[L_HIP].y),
        (frame.landmark[L_KNEE].x, frame.landmark[L_KNEE].y),
        (frame.landmark[L_ANKLE].x, frame.landmark[L_ANKLE].y)
    ) if len(frame.landmark) > L_ANKLE else 0.0
    right_knee_angle = calculate_angle(
        (frame.landmark[R_HIP].x, frame.landmark[R_HIP].y),
        (frame.landmark[R_KNEE].x, frame.landmark[R_KNEE].y),
        (frame.landmark[R_ANKLE].x, frame.landmark[R_ANKLE].y)
    ) if len(frame.landmark) > R_ANKLE else 0.0
    knee_angle_deg = (left_knee_angle + right_knee_angle) / 2.0

    horizontal_displacement_m = (hip_mid_x[landing_frame] - hip_mid_x[take_off_frame]) * pixel_to_meter

    return {
        "jump_height_m": round(float(jump_height_m), 2),
        "take_off_velocity_mps": round(float(take_off_velocity_mps), 2),
        "take_off_angle_deg": round(float(take_off_angle_deg), 1),
        "approach_speed_mps": round(float(approach_speed_mps), 2),
        "flight_time_s": round(float(flight_time_s), 3),
        "vertical_velocity_mps": round(float(vert_vel_mps), 2),
        "vertical_acceleration": round(float(vertical_acceleration), 2),
        "power_index": round(float(power_index), 2),
        "symmetry_knee": round(float(symmetry_knee), 3),
        "symmetry_ankle": round(float(symmetry_ankle), 3),
        "symmetry_shoulder": round(float(symmetry_shoulder), 3),
        "shoulder_symmetry_m": round(float(shoulder_symmetry_m), 3),
        "shoulder_tilt_deg": round(float(shoulder_tilt_deg), 1),
        "torso_angle_deg": round(float(torso_angle_deg), 1),
        "torso_lean_from_vertical_deg": round(float(torso_lean_from_vertical), 1),
        "hip_angle_deg": round(float(hip_angle_deg), 1),
        "knee_angle_deg": round(float(knee_angle_deg), 1),
        "horizontal_displacement_m": round(float(horizontal_displacement_m), 2),
        "take_off_frame": take_off_frame,
        "peak_frame": peak_frame,
        "landing_frame": landing_frame,
        "fps": fps,
        "duration_s": round(len(landmarks) / fps, 2),
        "pixel_to_meter": round(float(pixel_to_meter), 6),
    }