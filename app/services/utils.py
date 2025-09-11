from typing import List
import numpy as np
def smooth_series_ema(values: List[float], alpha: float = 0.25) -> List[float]:
    if not values: 
        return []
    smoothed = np.zeros(len(values))
    smoothed[0] = values[0]
    for i in range(1, len(values)):
        smoothed[i] = alpha * values[i] + (1 - alpha) * smoothed[i - 1]
    return smoothed.tolist()

def calculate_angle(a, b, c) -> float:
    """Calculate angle ABC (degrees), handles zero-length vectors."""
    a, b, c = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64), np.array(c, dtype=np.float64)
    ab, cb = a - b, c - b
    norm_ab, norm_cb = np.linalg.norm(ab), np.linalg.norm(cb)
    if norm_ab < 1e-6 or norm_cb < 1e-6:
        return 0.0
    angle = np.arctan2(np.linalg.det([ab, cb]), np.dot(ab, cb))
    return min(np.degrees(abs(angle)), 180.0)

def normalize_metric(value: float, benchmark: tuple, norm_type: str = 'higher') -> float:
    min_val, max_val = benchmark
    if max_val - min_val == 0: return 0.0
    if norm_type == 'higher':
        score = (value - min_val) / (max_val - min_val)
    elif norm_type == 'lower':
        score = 1.0 - ((value - min_val) / (max_val - min_val))
    elif norm_type == 'middle':
        mid_point = (min_val + max_val) / 2
        deviation = abs(value - mid_point)
        score = max(0.0, 1.0 - deviation / (mid_point - min_val))
    else:
        score = 0.0
    return max(0.0, min(1.0, score))
