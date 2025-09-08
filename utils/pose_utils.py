import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a[:2])
    b = np.array(b[:2])
    c = np.array(c[:2])
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def calculate_3d_distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)

def calculate_xyz_distances(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.abs(p1 - p2)