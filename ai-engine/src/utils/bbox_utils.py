from utils.geometry_utils import calculate_distance

SCOOTER_CLASS_ID = 0
PERSON_CLASS_ID = 1
def detect_scooters(results):
    """Детекция самокатов на изображении"""
    scooters = []

    if len(results) <= 0:
        return scooters

    scooters = [{
        'bbox': n.bbox,
        'confidence': n.confidence,
        'class_id': n.class_id,
        'class_name': n.class_name
    }
    for n in results if n.class_id == SCOOTER_CLASS_ID]

    return scooters

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

def is_intersect(box1, box2):
    """
    Проверяет, пересекаются ли два прямоугольника.
    """
    # Проверяем перекрытие по X
    x_overlap = not (box1[2] < box2[0] or box2[2] < box1[0])

    # Проверяем перекрытие по Y
    y_overlap = not (box1[3] < box2[1] or box2[3] < box1[1])

    return x_overlap and y_overlap

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

def get_bbox_height(bbox):
    return bbox[3] - bbox[1]

def get_bbox_width(bbox):
    return bbox[2] - bbox[0]