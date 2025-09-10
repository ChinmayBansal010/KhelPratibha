# File: sports_analyzer/app/services/analysis/track/hurdles.py
import numpy as np
from typing import Dict, List, Any

def calculate_hurdles_metrics(landmarks: List[Any], fps: float, height: float) -> Dict[str, Any]:
    """
    Hurdles analysis:
    - Avg clearance height (m)
    - Rhythm consistency (stride timing variability)
    - Lead vs trail leg symmetry (deg diff)
    """
    if not landmarks or fps <= 0 or height <= 0:
        return {}

    LEFT_KNEE, RIGHT_KNEE = 25, 26

    # Knee trajectories (used to detect hurdle clearance)
    left_knee_y = [f.landmark[LEFT_KNEE].y for f in landmarks]
    right_knee_y = [f.landmark[RIGHT_KNEE].y for f in landmarks]

    # Simulate clearance height = avg of min knee height (normalized by body height)
    clearance_norm = (np.min(left_knee_y) + np.min(right_knee_y)) / 2
    avg_clearance_height = (1 - clearance_norm) * height  # invert since y is usually normalized

    # Rhythm = variability in stride intervals
    stride_intervals = []
    for i in range(2, len(left_knee_y)):
        if left_knee_y[i - 1] < left_knee_y[i] and left_knee_y[i - 1] < left_knee_y[i - 2]:
            stride_intervals.append(i / fps)
    
    rhythm_consistency = 0.0
    if len(stride_intervals) > 2:
        diffs = np.diff(stride_intervals)
        # Check for division by zero
        if np.mean(diffs) > 0:
            rhythm_consistency = 1.0 - (np.std(diffs) / np.mean(diffs))

    # Symmetry = difference in max knee flexion L vs R
    lead_leg_angle = np.min(left_knee_y)
    trail_leg_angle = np.min(right_knee_y)
    symmetry = 1.0 - abs(lead_leg_angle - trail_leg_angle)

    return {
        "avg_clearance_height_m": round(avg_clearance_height, 2),
        "rhythm_consistency": round(max(0.0, min(rhythm_consistency, 1.0)), 2),
        "leg_symmetry_score": round(max(0.0, symmetry), 2)
    }
