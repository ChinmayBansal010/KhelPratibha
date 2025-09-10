# File: sports_analyzer/app/services/scoring/track/hurdles_score.py
from typing import Dict, Any

def calculate_hurdles_score(metrics: Dict[str, Any], height: float) -> float:
    """Calculates a placeholder score for a hurdles performance."""
    # Placeholder: score based on rhythm and symmetry
    rhythm = metrics.get("rhythm_consistency", 0)
    symmetry = metrics.get("leg_symmetry_score", 0)
    return round(((rhythm * 0.6) + (symmetry * 0.4)) * 100, 1)

def generate_hurdles_feedback(metrics: Dict[str, Any]) -> str:
    """Generates placeholder feedback for a hurdles performance."""
    if metrics.get("rhythm_consistency", 0) < 0.8:
        return "Focus on maintaining a consistent stride pattern between hurdles."
    return "Good rhythm over the hurdles. Work on maintaining speed during clearance."
