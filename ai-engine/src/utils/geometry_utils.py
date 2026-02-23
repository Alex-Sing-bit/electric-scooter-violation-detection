import math

import numpy as np


def calculate_angle(a, b, c):
    """Вычисление угла между тремя точками"""
    try:
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1, 1)
        angle = np.degrees(np.arccos(cosine_angle))
        return angle
    except:
        return 0.0


def calculate_slope(point1, point2):
    """Вычисляет наклон линии между двумя точками в градусах"""
    if point1 is None or point2 is None:
        return None

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    if dx == 0:
        return 90.0

    slope_rad = math.atan2(dy, dx)
    slope_deg = math.degrees(slope_rad)
    return slope_deg

def calculate_distance(point1, point2):
    """Вычисление расстояния между двумя точками"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
