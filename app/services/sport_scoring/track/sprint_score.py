from typing import Dict, Any
from ...utils import normalize_metric 

BENCHMARKS = {
    "speed": (8.0, 12.0),
    "stride_length": (1.5, 2.7),
    "cadence": (3.0, 5.0),
    "knee_drive": (50.0, 75.0),
    "ankle_drive": (25.0, 40.0),
    "acceleration": (3.5, 7.0),
    "endurance_drop": (0, 10),
    "vertical_oscillation": (0, 0.12),
    "asymmetry": (0, 0.02),
    "stride_variability": (0, 0.05),
    "contact_time": (0, 0.12),
}

def calculate_sprint_score(metrics: Dict[str, Any], height: float) -> float:
    scores = {
        "speed": normalize_metric(metrics.get("max_speed_mps", 0), BENCHMARKS["speed"], 'higher'),
        "stride_knee": normalize_metric(metrics.get("avg_stride_length_knee_m", 0), BENCHMARKS["stride_length"], 'higher'),
        "stride_ankle": normalize_metric(metrics.get("avg_stride_length_ankle_m", 0), BENCHMARKS["stride_length"], 'higher'),
        "cadence_knee": normalize_metric(metrics.get("cadence_knee_hz", 0), BENCHMARKS["cadence"], 'higher'),
        "cadence_ankle": normalize_metric(metrics.get("cadence_ankle_hz", 0), BENCHMARKS["cadence"], 'higher'),
        "knee_drive": normalize_metric(metrics.get("max_knee_drive_deg", 0), BENCHMARKS["knee_drive"], 'higher'),
        "ankle_drive": normalize_metric(metrics.get("max_ankle_drive_deg", 0), BENCHMARKS["ankle_drive"], 'higher'),
        "avg_ankle_drive": normalize_metric(metrics.get("avg_ankle_drive_m", 0), BENCHMARKS["ankle_drive"], 'higher'),
        "acceleration": normalize_metric(metrics.get("max_acceleration_mps2", 0), BENCHMARKS["acceleration"], 'higher'),
        "endurance": normalize_metric(metrics.get("speed_endurance_drop_pct", 0), BENCHMARKS["endurance_drop"], 'lower'),
        "vertical": normalize_metric(metrics.get("vertical_oscillation_m", 0), BENCHMARKS["vertical_oscillation"], 'lower'),
        "asymmetry_knee": normalize_metric(metrics.get("asymmetry_knee_m", 0), BENCHMARKS["asymmetry"], 'lower'),
        "asymmetry_ankle": normalize_metric(metrics.get("asymmetry_ankle_m", 0), BENCHMARKS["asymmetry"], 'lower'),
        "stride_var_knee": normalize_metric(metrics.get("stride_variability_knee_m", 0), BENCHMARKS["stride_variability"], 'lower'),
        "stride_var_ankle": normalize_metric(metrics.get("stride_variability_ankle_m", 0), BENCHMARKS["stride_variability"], 'lower'),
        "contact_knee": normalize_metric(metrics.get("contact_time_est_knee_s", 0), BENCHMARKS["contact_time"], 'lower'),
        "contact_ankle": normalize_metric(metrics.get("contact_time_est_ankle_s", 0), BENCHMARKS["contact_time"], 'lower'),
    }

    weights = {
        "speed": 0.20,
        "stride_knee": 0.07, "stride_ankle": 0.07,
        "cadence_knee": 0.05, "cadence_ankle": 0.05,
        "knee_drive": 0.08, "ankle_drive": 0.08, "avg_ankle_drive": 0.05,
        "acceleration": 0.10, "endurance": 0.05,
        "vertical": 0.04,
        "asymmetry_knee": 0.03, "asymmetry_ankle": 0.03,
        "stride_var_knee": 0.02, "stride_var_ankle": 0.02,
        "contact_knee": 0.03, "contact_ankle": 0.03,
    }

    final_score = sum(scores[k] * weights[k] for k in scores if k in weights)
    return round(final_score * 100, 1)

def generate_sprint_feedback(metrics: Dict[str, Any]) -> str:
    msgs = []
    if metrics.get("max_speed_mps", 0) < BENCHMARKS["speed"][0]:
        msgs.append("Improve explosive power and sprint acceleration.")
    if metrics.get("avg_stride_length_knee_m", 0) < BENCHMARKS["stride_length"][0]:
        msgs.append("Work on hip extension and bounding drills to lengthen your stride.")
    if metrics.get("cadence_knee_hz", 0) < BENCHMARKS["cadence"][0]:
        msgs.append("Train for quicker ground contact with fast-leg drills.")
    if metrics.get("max_knee_drive_deg", 0) < BENCHMARKS["knee_drive"][0]:
        msgs.append("Emphasize knee drive with A-skips and sprint-specific plyometrics.")
    if metrics.get("max_acceleration_mps2", 0) < BENCHMARKS["acceleration"][0]:
        msgs.append("Include resisted sprints and explosive starts to improve acceleration.")
    if metrics.get("speed_endurance_drop_pct", 0) > BENCHMARKS["endurance_drop"][1]:
        msgs.append("Work on sprint endurance with interval training to maintain top speed.")
    if metrics.get("vertical_oscillation_m", 0) > BENCHMARKS["vertical_oscillation"][1]:
        msgs.append("Focus on minimizing vertical bounce to conserve energy.")
    if metrics.get("asymmetry_knee_m", 0) > BENCHMARKS["asymmetry"][1]:
        msgs.append("Address left-right imbalance to prevent injury and improve efficiency.")
    if metrics.get("stride_variability_knee_m", 0) > BENCHMARKS["stride_variability"][1]:
        msgs.append("Increase stride consistency through technique drills.")
    if metrics.get("contact_time_est_knee_s", 0) > BENCHMARKS["contact_time"][1]:
        msgs.append("Reduce ground contact time with plyometrics and reactive drills.")
    if not msgs:
        return "Excellent sprint mechanics! Keep refining speed and technique."
    return " | ".join(msgs)
