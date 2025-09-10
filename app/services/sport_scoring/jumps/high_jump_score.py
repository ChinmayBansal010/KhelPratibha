# File: sports_analyzer/app/services/scoring/jumps/high_jump_score.py
from typing import Dict, Any

def calculate_high_jump_score(metrics: Dict[str, Any], height: float) -> float:
    """Calculates the talent score for a high jump performance."""
    jump_height = metrics.get("jump_height_m", 0)
    score = min(jump_height / (height * 1.2), 1.0) * 100
    return round(score, 1)

def generate_high_jump_feedback(metrics: Dict[str, Any]) -> str:
    """Generates feedback for a high jump performance."""
    if metrics.get("jump_height_m", 0) < 1.5:
        return "Build explosive leg power through plyometrics and squats to boost jump height."
    return "Strong performance! Next, refine your approach run and takeoff mechanics."
