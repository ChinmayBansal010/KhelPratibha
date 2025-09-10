# File: sports_analyzer/app/services/scoring.py
from typing import Dict, Any, Callable

# Import exercise-specific functions
from .sport_scoring.track.sprint_score import calculate_sprint_score, generate_sprint_feedback
from .sport_scoring.track.hurdles_score import calculate_hurdles_score, generate_hurdles_feedback
from .sport_scoring.jumps.high_jump_score import calculate_high_jump_score, generate_high_jump_feedback
from .sport_scoring.throws.shot_put_score import calculate_shot_put_score, generate_shot_put_feedback

# --- Function Routers ---
# Maps a sport key to its dedicated scoring function
_SCORE_FUNCTIONS: Dict[str, Callable] = {
    "sprint": calculate_sprint_score,
    "hurdles": calculate_hurdles_score,
    "high_jump": calculate_high_jump_score,
    "shot_put": calculate_shot_put_score,
    # Add other sports here as they are implemented
}

# Maps a sport key to its dedicated feedback function
_FEEDBACK_FUNCTIONS: Dict[str, Callable] = {
    "sprint": generate_sprint_feedback,
    "hurdles": generate_hurdles_feedback,
    "high_jump": generate_high_jump_feedback,
    "shot_put": generate_shot_put_feedback,
    # Add other sports here as they are implemented
}

def calculate_talent_score(sport: str, metrics: Dict[str, Any], height: float) -> float:
    """
    Dispatcher that finds and calls the correct scoring function for the given sport.
    """
    score_func = _SCORE_FUNCTIONS.get(sport)
    if score_func:
        return score_func(metrics, height)
    
    return 50.0  # Default score for sports without a specific scoring function

def generate_feedback(sport: str, metrics: Dict[str, Any]) -> str:
    """
    Dispatcher that finds and calls the correct feedback function for the given sport.
    """
    feedback_func = _FEEDBACK_FUNCTIONS.get(sport)
    if feedback_func:
        return feedback_func(metrics)

    return "Great effort! Keep practicing your technique for steady improvement."

