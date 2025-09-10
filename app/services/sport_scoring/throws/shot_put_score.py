# File: sports_analyzer/app/services/scoring/throws/shot_put_score.py
from typing import Dict, Any

def calculate_shot_put_score(metrics: Dict[str, Any], height: float) -> float:
    """Calculates the talent score for a shot put performance."""
    angle = metrics.get("release_angle_deg", 0)
    angle_score = max(0, 1.0 - abs(angle - 45) / 45)
    
    # Placeholder for distance
    distance_score = min(metrics.get("distance_m", 0) / 20.0, 1.0)
    
    final_score = (0.6 * distance_score + 0.4 * angle_score) * 100
    return round(final_score, 1)

def generate_shot_put_feedback(metrics: Dict[str, Any]) -> str:
    """Generates feedback for a shot put performance."""
    angle = metrics.get("release_angle_deg", 0)
    if angle < 35:
        return "Aim for a higher release angle (close to 45°) to maximize distance."
    elif angle > 55:
        return "Lower your release angle slightly for more horizontal distance."
    return "Great technique! Keep refining your footwork and rotational speed."
