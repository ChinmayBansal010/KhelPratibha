# File: sports_analyzer/app/services/scoring/track/sprint_score.py
from typing import Dict, Any

def calculate_sprint_score(metrics: Dict[str, Any], height: float) -> float:
    """Calculates the talent score for a sprint performance."""
    # Reference benchmarks for elite performance
    BENCHMARKS = {
        "speed": 12.0, "stride_length": 2.7, "cadence": 5.0, "knee_drive": 75.0,
        "ankle_drive": 40.0, "acceleration": 7.0, "endurance_drop": 10.0,
        "vertical_oscillation": 0.12, "asymmetry": 0.02, "stride_variability": 0.05,
        "contact_time": 0.12,
    }

    # Normalized scores (0-1)
    speed_score = min(metrics.get("max_speed_mps", 0) / BENCHMARKS["speed"], 1.0)
    stride_score = min(metrics.get("avg_stride_length_m", 0) / BENCHMARKS["stride_length"], 1.0)
    cadence_score = min(metrics.get("cadence_hz", 0) / BENCHMARKS["cadence"], 1.0)
    knee_score = min(metrics.get("max_knee_drive_deg", 0) / BENCHMARKS["knee_drive"], 1.0)
    ankle_score = min(metrics.get("max_ankle_drive_deg", 0) / BENCHMARKS["ankle_drive"], 1.0)
    accel_score = min(metrics.get("max_acceleration_mps2", 0) / BENCHMARKS["acceleration"], 1.0)
    endurance_score = 1.0 - min(metrics.get("speed_endurance_drop_pct", 0) / BENCHMARKS["endurance_drop"], 1.0)
    vertical_score = 1.0 - min(metrics.get("vertical_oscillation_m", 0) / BENCHMARKS["vertical_oscillation"], 1.0)
    asymmetry_score = 1.0 - min(metrics.get("asymmetry_m", 0) / BENCHMARKS["asymmetry"], 1.0)
    stride_var_score = 1.0 - min(metrics.get("stride_variability_m", 0) / BENCHMARKS["stride_variability"], 1.0)
    contact_score = 1.0 - min(metrics.get("estimated_contact_time_s", 0) / BENCHMARKS["contact_time"], 1.0)
    avg_ankle_drive_score = min(metrics.get("avg_ankle_drive_m", 0) / BENCHMARKS["ankle_drive"], 1.0)

    # Weighted scoring
    weights = {
        "speed": 0.20, "stride": 0.15, "cadence": 0.10, "knee": 0.10, "ankle": 0.10,
        "avg_ankle_drive": 0.05, "accel": 0.10, "endurance": 0.05, "vertical": 0.05,
        "asymmetry": 0.05, "stride_var": 0.03, "contact": 0.02
    }

    final_score = (
        speed_score * weights["speed"] + stride_score * weights["stride"] +
        cadence_score * weights["cadence"] + knee_score * weights["knee"] +
        ankle_score * weights["ankle"] + avg_ankle_drive_score * weights["avg_ankle_drive"] +
        accel_score * weights["accel"] + endurance_score * weights["endurance"] +
        vertical_score * weights["vertical"] + asymmetry_score * weights["asymmetry"] +
        stride_var_score * weights["stride_var"] + contact_score * weights["contact"]
    )
    return round(final_score * 100, 1)

def generate_sprint_feedback(metrics: Dict[str, Any]) -> str:
    """Generates feedback for a sprint performance."""
    msgs = []
    if metrics.get("max_speed_mps", 0) < 8.0:
        msgs.append("Improve explosive power and sprint acceleration.")
    if metrics.get("avg_stride_length_m", 0) < 1.8:
        msgs.append("Work on hip extension and bounding drills to lengthen your stride.")
    if metrics.get("cadence_hz", 0) < 3.5:
        msgs.append("Train for quicker ground contact with fast-leg drills.")
    if metrics.get("max_knee_drive_deg", 0) < 50:
        msgs.append("Emphasize knee drive with A-skips and sprint-specific plyometrics.")
    if metrics.get("max_acceleration_mps2", 0) < 3.5:
        msgs.append("Include resisted sprints and explosive starts to improve acceleration.")
    if metrics.get("speed_endurance_drop_pct", 0) > 15:
        msgs.append("Work on sprint endurance with interval training to maintain top speed.")
    if metrics.get("vertical_oscillation_m", 0) > 0.1:
        msgs.append("Focus on minimizing vertical bounce to conserve energy.")
    if metrics.get("asymmetry_m", 0) > 0.03:
        msgs.append("Address left-right imbalance to prevent injury and improve efficiency.")
    if metrics.get("stride_variability_m", 0) > 0.05:
        msgs.append("Increase stride consistency through technique drills.")
    if metrics.get("estimated_contact_time_s", 0) > 0.13:
        msgs.append("Reduce ground contact time with plyometrics and reactive drills.")
    
    return " ".join(msgs) if msgs else "Excellent sprint mechanics! Keep refining speed and technique."
