from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Any, List

from numpy import dtype, ndarray
from ultralytics import YOLO

@lru_cache(maxsize=1)
def _load_model(model_path: str):
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        raise Exception(f"Ошибка загрузки модели {model_path}: {e}")


@dataclass
class Detection:
    """
    Результат детекции одного объекта.

    Attributes:
        bbox: Координаты ограничивающей рамки [x1, y1, x2, y2]
        confidence: Уверенность детекции (0.0 - 1.0)
        class_name: Название класса на английском языке
        class_id: Числовой идентификатор класса
    """
    bbox: List[float]
    confidence: float
    class_name: str
    class_id: int


class ObjectDetector:

    def __init__(self, model_path: str, confidence_threshold: float = 0.5, iou_threshold: float = 0.5):
        self.model = _load_model(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

    def detect(self, image: ndarray[Any, dtype]) -> Dict[str, Any]:
        """
        Детектирует объекты на изображении.

        Returns:
            Словарь с результатами:
            {
                "detections": List[Detection],  # Список найденных объектов
                "image": np.array | None        # Изображение с нарисованными bbox (если доступно)
            }
        """
        results = self.model(image, conf=self.confidence_threshold, iou=self.iou_threshold)

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    detection = Detection(
                        bbox=box.xyxy[0].tolist(),
                        confidence=box.conf.item(),
                        class_name=result.names[int(box.cls)],
                        class_id=int(box.cls)
                    )
                    detections.append(detection)

        return {
            "detections": detections,
            "image": result.plot() if hasattr(result, 'plot') else None
        }

    def track(self, image: ndarray[Any, dtype]) -> Dict[str, Any]:
        results = self.model.track(image, conf=self.confidence_threshold, iou=self.iou_threshold,
                                   persist=True, show=False, verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    detection = Detection(
                        bbox=box.xyxy[0].tolist(),
                        confidence=box.conf.item(),
                        class_name=result.names[int(box.cls)],
                        class_id=int(box.cls)
                    )
                    detections.append(detection)

        return {
            "detections": detections,
            "image": result.plot() if hasattr(result, 'plot') else None
        }