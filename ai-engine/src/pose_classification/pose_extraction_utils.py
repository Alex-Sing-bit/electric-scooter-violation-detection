from ultralytics import YOLO

from pose_classification.geometry_utils import calculate_distance

SCOOTER_CLASS_ID = 0

def get_bbox_center(bbox):
    """Получение центра bounding box"""
    return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]


def is_point_visible(point, confidence_threshold=0.5):
    """Проверка видимости точки с учетом confidence"""
    if point is None:
        return False

    if len(point) > 2:
        confidence = point[2]
        # Проверка confidence если есть
        if confidence < confidence_threshold:
            return False

    # Базовая проверка координат
    if point[0] < 2 or point[1] < 2:
        return False

    return True

def normalize_by_bbox(value, bbox, is_x=True):
    """Нормализация значения относительно bounding box"""
    if is_x:
        return (value - bbox[0]) / (bbox[2] - bbox[0]) if (bbox[2] - bbox[0]) > 0 else 0
    else:
        return (value - bbox[1]) / (bbox[3] - bbox[1]) if (bbox[3] - bbox[1]) > 0 else 0


def is_intersect(box1, box2):
    """
    Проверяет, пересекаются ли два прямоугольника.
    """
    # Проверяем перекрытие по X
    x_overlap = not (box1[2] < box2[0] or box2[2] < box1[0])

    # Проверяем перекрытие по Y
    y_overlap = not (box1[3] < box2[1] or box2[3] < box1[1])

    return x_overlap and y_overlap

def find_nearest_scooter(person_bbox, scooters):
    """Нахождение ближайшего самоката к человеку"""
    if not scooters:
        return None

    person_center = get_bbox_center(person_bbox)
    min_distance = float('inf')
    nearest_scooter = None

    for scooter in scooters:
        scooter_center = get_bbox_center(scooter['bbox'])
        distance = calculate_distance(person_center, scooter_center)

        if distance < min_distance:
            min_distance = distance
            nearest_scooter = scooter

    # Проверяем, достаточно ли близко самокат к человеку
    if is_intersect(nearest_scooter['bbox'], person_bbox):
        return nearest_scooter
    else:
        return None

def calculate_point_relative_to_scooter(point, scooter_bbox):
    """расчет относительного положения точки к самокату"""
    if point is None or scooter_bbox is None:
        return 0, 0

    scooter_x1, scooter_y1, scooter_x2, scooter_y2 = scooter_bbox
    point_x, point_y = point

    scooter_width = scooter_x2 - scooter_x1
    scooter_height = scooter_y2 - scooter_y1

    if scooter_width <= 0 or scooter_height <= 0:
        return 0, 0

    # Относительные координаты внутри bounding box самоката
    # X: 0 = левый край самоката, 1 = правый край самоката
    rel_x = (point_x - scooter_x1) / scooter_width
    # Y: 0 = верхний край самоката, 1 = нижний край самоката
    rel_y = (point_y - scooter_y1) / scooter_height

    return rel_x, rel_y

def filter_person(bbox, visible_points, keypoints):
        """Фильтрация людей по качеству детекции"""
        # Слишком маленький bbox
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if bbox_area < 1000:  # минимальная площадь в пикселях
            return False

        # Слишком мало видимых ключевых точек
        if visible_points < 4:
            return False

        # Проверяем, что есть достаточно ключевых точек для определения половины человека
        upper_body_points = [5, 6, 11, 12, 15, 16]  # плечи, бедра, лодыжки
        visible_upper = sum(1 for i in upper_body_points if is_point_visible(keypoints[i][:3]))

        if visible_upper < 3:
            return False

        return True