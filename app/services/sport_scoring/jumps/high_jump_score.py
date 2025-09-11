from typing import Dict, Any
from ...utils import normalize_metric 

BENCHMARKS = {
    "jump_height_m": (1.2, 2.4),
    "take_off_velocity_mps": (3.0, 5.0),
    "take_off_angle_deg": (70, 80),
    "approach_speed_mps": (6.0, 9.0),
    "symmetry_knee": (0.9, 1.0),
    "symmetry_ankle": (0.9, 1.0),
    "symmetry_shoulder": (0.9, 1.0),
    "torso_lean_from_vertical_deg": (0, 25),
    "power_index": (10, 25),
}


def calculate_high_jump_score(metrics: Dict[str, Any], height: float) -> float:
    if not metrics or height <= 0: return 0.0
    weights = {
        "jump_height_m": 0.35,
        "take_off_velocity_mps": 0.2,
        "take_off_angle_deg": 0.1,
        "approach_speed_mps": 0.1,
        "symmetry_knee": 0.05,
        "symmetry_ankle": 0.05,
        "symmetry_shoulder": 0.05,
        "torso_lean_from_vertical_deg": 0.05,
        "power_index": 0.05,
    }
    score = 0.0
    score += weights["jump_height_m"] * normalize_metric(metrics.get("jump_height_m", 0), BENCHMARKS["jump_height_m"], 'higher') * 100
    score += weights["take_off_velocity_mps"] * normalize_metric(metrics.get("take_off_velocity_mps", 0), BENCHMARKS["take_off_velocity_mps"], 'higher') * 100
    score += weights["take_off_angle_deg"] * normalize_metric(metrics.get("take_off_angle_deg", 0), BENCHMARKS["take_off_angle_deg"], 'middle') * 100
    score += weights["approach_speed_mps"] * normalize_metric(metrics.get("approach_speed_mps", 0), BENCHMARKS["approach_speed_mps"], 'higher') * 100
    score += weights["symmetry_knee"] * normalize_metric(metrics.get("symmetry_knee", 0), BENCHMARKS["symmetry_knee"], 'higher') * 100
    score += weights["symmetry_ankle"] * normalize_metric(metrics.get("symmetry_ankle", 0), BENCHMARKS["symmetry_ankle"], 'higher') * 100
    score += weights["symmetry_shoulder"] * normalize_metric(metrics.get("symmetry_shoulder", 0), BENCHMARKS["symmetry_shoulder"], 'higher') * 100
    score += weights["torso_lean_from_vertical_deg"] * normalize_metric(metrics.get("torso_lean_from_vertical_deg", 0), BENCHMARKS["torso_lean_from_vertical_deg"], 'lower') * 100
    score += weights["power_index"] * normalize_metric(metrics.get("power_index", 0), BENCHMARKS["power_index"], 'higher') * 100
    return round(score, 1)

def generate_high_jump_feedback(metrics: Dict[str, Any]) -> str:
    if not metrics: return "No valid data. Ensure landmarks and height are correct."
    feedback = []
    if normalize_metric(metrics.get("jump_height_m", 0), BENCHMARKS["jump_height_m"], 'higher') < 0.5:
        feedback.append("Increase explosive leg power with plyometrics and squats.")
    if normalize_metric(metrics.get("take_off_velocity_mps", 0), BENCHMARKS["take_off_velocity_mps"], 'higher') < 0.5:
        feedback.append("Work on faster ground reaction and sprint training.")
    if normalize_metric(metrics.get("take_off_angle_deg", 0), BENCHMARKS["take_off_angle_deg"], 'middle') < 0.5:
        feedback.append("Adjust takeoff angle to optimal range.")
    if normalize_metric(metrics.get("approach_speed_mps", 0), BENCHMARKS["approach_speed_mps"], 'higher') < 0.5:
        feedback.append("Refine your approach run for better speed.")
    if normalize_metric(metrics.get("symmetry_knee", 0), BENCHMARKS["symmetry_knee"], 'higher') < 0.5:
        feedback.append("Focus on bilateral strength to reduce knee imbalance.")
    if normalize_metric(metrics.get("symmetry_shoulder", 0), BENCHMARKS["symmetry_shoulder"], 'higher') < 0.5:
        feedback.append("Improve upper body balance and posture control.")
    if normalize_metric(metrics.get("torso_lean_from_vertical_deg", 0), BENCHMARKS["torso_lean_from_vertical_deg"], 'lower') < 0.5:
        feedback.append("Keep torso more upright at takeoff to maximize lift.")
    if normalize_metric(metrics.get("power_index", 0), BENCHMARKS["power_index"], 'higher') < 0.5:
        feedback.append("Develop explosive strength with Olympic lifts and bounding.")
    if not feedback: return "Excellent performance! Keep refining timing and consistency."
    return " | ".join(feedback)
