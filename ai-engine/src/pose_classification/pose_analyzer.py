import numpy as np

from utils.bbox_utils import is_point_visible, normalize_by_bbox, get_bbox_center
from utils.geometry_utils import calculate_angle, calculate_distance, calculate_slope


def _calculate_human_height(keypoints):
    """Вычисление роста человека по ключевым точкам"""
    shoulder_points = []
    ankle_points = []

    # Левое и правое плечо
    if is_point_visible(keypoints[5][:3]):
        shoulder_points.append(keypoints[5][1])
    if is_point_visible(keypoints[6][:3]):
        shoulder_points.append(keypoints[6][1])

    # Левая и правая лодыжка
    if is_point_visible(keypoints[15][:3]):
        ankle_points.append(keypoints[15][1])
    if is_point_visible(keypoints[16][:3]):
        ankle_points.append(keypoints[16][1])

    if shoulder_points and ankle_points:
        avg_shoulder_y = np.max(shoulder_points)
        avg_ankle_y = np.min(ankle_points)
        return abs(avg_ankle_y - avg_shoulder_y)

    hips_points = []
    # Левое и правое бедро
    if is_point_visible(keypoints[11][:3]):
        hips_points.append(keypoints[11][1])
    if is_point_visible(keypoints[12][:3]):
        hips_points.append(keypoints[12][1])

    if shoulder_points and hips_points:
        avg_shoulder_y = np.mean(shoulder_points)
        avg_hip_y = np.mean(hips_points)
        return abs(avg_shoulder_y - avg_hip_y)

    if ankle_points and hips_points:
        avg_hip_y = np.mean(hips_points)
        avg_ankle_y = np.mean(ankle_points)
        return abs(avg_ankle_y - avg_hip_y)

    return np.nan

def _extract_essential_angles(kp_array):
    """Извлечение основных углов"""
    features = {}
    essential_angles = [
        (5, 7, 9), (6, 8, 10), (11, 13, 15), (12, 14, 16)  # сгиб руки, сгиб ноги
    ]

    for i, j, k in essential_angles:
        point_i = kp_array[i][:3]
        point_j = kp_array[j][:3]
        point_k = kp_array[k][:3]

        if all(is_point_visible(p) for p in [point_i, point_j, point_k]):
            angle = calculate_angle(point_i, point_j, point_k)
            features[f'angle_{i}_{j}_{k}'] = angle
        else:
            features[f'angle_{i}_{j}_{k}'] = np.nan

    return features


def _extract_essential_distances(kp_array, human_height):
    """Извлечение основных расстояний"""
    features = {}
    essential_distances = [(5, 6), (11, 12)]  # ширина плеч, ширина бедер

    for i, j in essential_distances:
        point_i = kp_array[i][:3]
        point_j = kp_array[j][:3]

        if is_point_visible(point_i) and is_point_visible(point_j):
            dist = calculate_distance(point_i, point_j)
            norm_dist = dist / human_height if human_height > 0 else np.nan
            features[f'dist_{i}_{j}'] = norm_dist
        else:
            features[f'dist_{i}_{j}'] = np.nan

    return features


def _count_visible_points(kp_array):
    """Подсчет видимых ключевых точек"""
    visible_points = 0
    for i in range(17):
        if is_point_visible(kp_array[i][:3]):
            visible_points += 1
    return visible_points


def _extract_keypoint_coordinates(kp_array, bbox):
    """Извлечение координат ключевых точек"""
    features = {}
    keypoint_indices = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    for i in range(17):
        if i in keypoint_indices:
            x, y = kp_array[i][:2]
            features[f'kp_{i}_x'] = normalize_by_bbox(x, bbox, is_x=True)
            features[f'kp_{i}_y'] = normalize_by_bbox(y, bbox, is_x=False)

    return features


def _extract_bbox_features(bbox):
    """Извлечение признаков ограничивающего прямоугольника"""
    features = {}
    bbox_width = bbox[2] - bbox[0]
    bbox_height = bbox[3] - bbox[1]
    features['aspect_ratio'] = bbox_width / bbox_height if bbox_height > 0 else np.nan
    return features


def _analyze_points_relative_to_scooter(points, scooter_bbox):
    """Анализ относительных положений точек к самокату"""
    features = {}

    point_names = ['left_wrist', 'right_wrist', 'left_ankle', 'right_ankle']

    if scooter_bbox is not None and scooter_bbox[2] > 0:
        for point_name in point_names:
            if points[point_name] is not None:
                rel_x, rel_y = _calculate_point_relative_to_scooter(points[point_name], scooter_bbox)
                features[f'{point_name}_to_scooter_x'] = rel_x
                features[f'{point_name}_to_scooter_y'] = rel_y
            else:
                features[f'{point_name}_to_scooter_x'] = np.nan
                features[f'{point_name}_to_scooter_y'] = np.nan
    else:
        for point_name in point_names:
            features[f'{point_name}_to_scooter_x'] = np.nan
            features[f'{point_name}_to_scooter_y'] = np.nan

    return features

def _calculate_point_relative_to_scooter(point, scooter_bbox):
    """расчет относительного положения точки к самокату"""
    if point is None or scooter_bbox is None:
        return 0, 0

    scooter_x1, scooter_y1, scooter_x2, scooter_y2 = scooter_bbox
    point_x, point_y = point

    scooter_width = scooter_x2 - scooter_x1
    scooter_height = scooter_y2 - scooter_y1

    if scooter_width <= 0 or scooter_height <= 0:
        return 0, 0

    rel_x = (point_x - scooter_x1) / scooter_width
    rel_y = (point_y - scooter_y1) / scooter_height

    return rel_x, rel_y


def _analyze_joint_distances(points, human_height):
    """Анализ расстояний между суставами"""
    features = {}

    if all(points[p] is not None for p in points):
        ankle_distance = abs(points['left_ankle'][0] - points['right_ankle'][0])
        knees_distance = abs(points['left_knee'][0] - points['right_knee'][0])
        hip_distance = abs(points['left_hip'][0] - points['right_hip'][0])
        elbow_distance = abs(points['left_elbow'][0] - points['right_elbow'][0])
        wrist_width = abs(points['left_wrist'][0] - points['right_wrist'][0])
        shoulder_width = abs(points['left_shoulder'][0] - points['right_shoulder'][0])

        features['ankle_distance_ratio'] = ankle_distance / hip_distance if hip_distance > 0 else np.nan
        features['hip_width'] = hip_distance / human_height if human_height > 0 else np.nan
        features['knees_width'] = knees_distance / human_height if human_height > 0 else np.nan
        features['ankle_width'] = ankle_distance / human_height if human_height > 0 else np.nan
        features['elbow_width'] = elbow_distance / human_height if human_height > 0 else np.nan
        features['wrist_width'] = wrist_width / human_height if human_height > 0 else np.nan
        features['shoulder_width'] = shoulder_width / human_height if human_height > 0 else np.nan

        features['hands_shoulder_width_ratio'] = (
            features['ankle_width'] / features['shoulder_width']
            if features['shoulder_width'] > 10e-3 else 0
        )
    else:
        features.update({
            'ankle_distance_ratio': np.nan,
            'hip_width': np.nan,
            'knees_width': np.nan,
            'ankle_width': np.nan,
            'elbow_width': np.nan,
            'wrist_width': np.nan,
            'shoulder_width': np.nan,
            'hands_shoulder_width_ratio': np.nan
        })

    return features


def _analyze_ankle_position(points, scooter_bbox):
    """Анализ положения лодыжек относительно самоката"""
    features = {}

    if scooter_bbox is not None and scooter_bbox[2] > 0:
        scooter_height = scooter_bbox[3] - scooter_bbox[1]
        for side in ['left', 'right']:
            ankle_key = f'{side}_ankle'
            if points[ankle_key] is not None:
                ankle_height_from_bottom = scooter_bbox[3] - points[ankle_key][1]
                features[f'ankle_height_ratio_{side}'] = (
                    ankle_height_from_bottom / scooter_height if scooter_height > 0 else np.nan
                )
            else:
                features[f'ankle_height_ratio_{side}'] = np.nan
    else:
        for side in ['left', 'right']:
            features[f'ankle_height_ratio_{side}'] = np.nan

    return features


def _analyze_body_verticality(points, human_height):
    """Анализ вертикальности тела"""
    features = {}

    if all(points[p] is not None for p in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
        shoulder_center_x = (points['left_shoulder'][0] + points['right_shoulder'][0]) / 2
        hip_center_x = (points['left_hip'][0] + points['right_hip'][0]) / 2
        horizontal_diff = abs(shoulder_center_x - hip_center_x)

        features['body_tilt_degrees'] = calculate_slope(
            (shoulder_center_x, points['left_shoulder'][1]),
            (hip_center_x, points['left_hip'][1])
        ) or 0
        features['shoulder_hip_alignment'] = horizontal_diff / human_height
    else:
        features.update({'body_tilt_degrees': np.nan, 'shoulder_hip_alignment': np.nan})

    return features


def _extract_keypoints(kp_array):
    """Извлечение ключевых точек"""
    point_indices = {
        'left_shoulder': 5, 'right_shoulder': 6,
        'left_elbow': 7, 'right_elbow': 8,
        'left_wrist': 9, 'right_wrist': 10,
        'left_hip': 11, 'right_hip': 12,
        'left_knee': 13, 'right_knee': 14,
        'left_ankle': 15, 'right_ankle': 16
    }

    points = {}
    for name, idx in point_indices.items():
        points[name] = kp_array[idx][:2] if is_point_visible(kp_array[idx][:2]) else None

    return points


def _extract_scooter_parameters(bbox, scooter_bbox, human_height = 1.0):
    """Извлечение параметров связанных с самокатом"""
    features = {}

    if scooter_bbox is not None:
        scooter_center = get_bbox_center(scooter_bbox)
        scooter_width = scooter_bbox[2] - scooter_bbox[0]
        scooter_height = scooter_bbox[3] - scooter_bbox[1]

        bbox_width = bbox[2] - bbox[0]
        bbox_height = bbox[3] - bbox[1]

        # Нормализуем относительно размеров человека
        features.update({
            'scooter_center_x': (scooter_center[0] - scooter_bbox[0]) / bbox_width if bbox_width > 0 else np.nan,
            'scooter_center_y': (scooter_center[1] - scooter_bbox[1]) / bbox_height if bbox_height > 0 else np.nan,
            'scooter_width': scooter_width / human_height if human_height > 0 else np.nan,
            'scooter_height': scooter_height / human_height if human_height > 0 else np.nan
        })

        # Расстояние между центрами человека и самоката
        person_center = get_bbox_center(bbox)
        features['scooter_person_center_distance'] = calculate_distance(
            person_center, scooter_center
        ) / human_height
    else:
        features.update({
            'scooter_center_x': np.nan, 'scooter_center_y': np.nan,
            'scooter_width': np.nan, 'scooter_height': np.nan,
            'scooter_person_center_distance': np.nan
        })

    return features


def _extract_basic_parameters(kp_array):
    """Извлечение базовых параметров"""
    features = {}
    human_height = _calculate_human_height(kp_array)
    features['human_height'] = human_height
    return features


def extract_optimized_features(bbox, kp_array, scooter_bbox=None):
    """Извлечение оптимизированных признаков"""
    features = {}
    # Извлечение базовых параметров
    features.update(_extract_basic_parameters(kp_array))

    # Извлечение параметров связанных с самокатом
    features.update(_extract_scooter_parameters(bbox, scooter_bbox, features.get('human_height', 1.0)))

    # Извлечение ключевых точек
    points = _extract_keypoints(kp_array)

    # Анализ вертикальности тела
    features.update(_analyze_body_verticality(points, features.get('human_height', 1.0)))

    # Анализ положения лодыжек относительно самоката
    features.update(_analyze_ankle_position(points, scooter_bbox))

    # Анализ расстояний между суставами
    features.update(_analyze_joint_distances(points, features.get('human_height', 1.0)))

    # Анализ относительных положений точек к самокату
    features.update(_analyze_points_relative_to_scooter(points, scooter_bbox))

    return features


def extract_features(keypoints, bbox, scooter_bbox=None):
    """Объединенное извлечение признаков"""
    features = {}

    # Базовые параметры bbox
    features.update(_extract_bbox_features(bbox))

    # Координаты ключевых точек
    features.update(_extract_keypoint_coordinates(keypoints, bbox))

    # Количество видимых точек
    visible_points = _count_visible_points(keypoints)
    features['num_visible_points'] = visible_points

    # Оптимизированные расстояния
    features.update(_extract_essential_distances(keypoints, features.get('human_height', bbox[3] - bbox[1])))

    # Ключевые углы
    features.update(_extract_essential_angles(keypoints))

    # Добавляем оптимизированные признаки
    optimized_features = extract_optimized_features(bbox, keypoints, scooter_bbox)
    features.update(optimized_features)

    return features, visible_points

#TODO: 0 Ноль используется как отсутствие параметра. Исправить!
#TODO: Если нет роста - альтернативные пути поиска