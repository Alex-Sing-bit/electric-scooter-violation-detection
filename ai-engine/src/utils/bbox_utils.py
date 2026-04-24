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

    max_intersect = 0
    nearest_scooter = None

    for scooter in scooters:
       lower_on = (person_bbox[3] - scooter['bbox'][3]) / get_bbox_height(person_bbox)

       if lower_on > -0.4:
            _, intersect_percent = is_intersect(person_bbox, scooter['bbox'])
            if intersect_percent > max_intersect:
                max_intersect = intersect_percent
                nearest_scooter = scooter

    if max_intersect > 30:
        return nearest_scooter
    else:
        return None

def is_intersect(box1, box2):
    """
    Проверяет, пересекаются ли два прямоугольника и возвращает процент пересечения.

    Возвращает:
        (bool, float): (пересекаются_ли, процент_пересечения_от_большего_прямоугольника)
    """
    x_overlap = not (box1[2] < box2[0] or box2[2] < box1[0])
    y_overlap = not (box1[3] < box2[1] or box2[3] < box1[1])

    if not (x_overlap and y_overlap):
        return False, 0.0

    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    intersection_area = (x_left - x_right) * (y_top - y_bottom)
    if area1 < area2:
        overlap_percentage = (intersection_area / area1) * 100
    else:
        overlap_percentage = (intersection_area / area2) * 100

    return True, round(overlap_percentage, 1)

def is_lower(lower_box, upper_box):
    centre_lower = lower_box[3]
    centre_upper= upper_box[3]

    lower_on = centre_upper - centre_lower
    return lower_on > 0, lower_on

def get_bbox_center(bbox):
    """Получение центра bounding box"""
    return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]

def is_point_visible(point, confidence_threshold=0.5):
    """Проверка видимости точки с учетом confidence"""
    if point is None:
        return False

    if len(point) > 2:
        confidence = point[2]
        if confidence < confidence_threshold:
            return False

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

def join_bboxes(bbox1, bbox2):
    x1 = min(bbox1[0], bbox2[0])
    y1 = min(bbox1[1], bbox2[1])
    x2 = max(bbox1[2], bbox2[2])
    y2 = max(bbox1[3], bbox2[3])
    return [x1, y1, x2, y2]