from utils.bbox_utils import is_point_visible


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