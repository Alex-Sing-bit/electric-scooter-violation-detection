import os
import time
from typing import Any

import cv2
from numpy import ndarray, dtype

from detection.object_detector import ObjectDetector
from pose_classification.pose_predictor import PosePredictor
from segmantation.segmentor import ObjectSegmenter
from utils.config_loader import load_config
from visualisation.visualizer import ResultVisualizer


def get_primary_detection_statistics(detections_list):
    """Собирает статистику по обнаруженным объектам"""
    people_count = sum(1 for detection in detections_list if detection.class_name == 'person')
    scooter_count = sum(1 for detection in detections_list if detection.class_name == 'electricscooter')

    return people_count, scooter_count

SCOOTER_CLASS_ID = 0
def detect_scooters(results):
    """Детекция самокатов на изображении"""
    scooters = []

    if len(results) <= 0:
        return scooters

    for n in results:
        class_id = n.class_id

        if class_id == SCOOTER_CLASS_ID:
            bbox = n.bbox
            confidence = n.confidence
            class_name = n.class_name

            scooters.append({
                'bbox': bbox,
                'confidence': confidence,
                'class_id': class_id,
                'class_name': class_name
            })

    return scooters

def process_image(image: ndarray[Any, dtype], config: dict):
    """Выполняет общий анализ изображения на нарушения"""

    detector = ObjectDetector(
        model_path=config['models']['detection']['model_path'],
        confidence_threshold=config['models']['detection']['confidence_threshold'],
        iou_threshold=config['models']['detection']['iou_threshold']
    )

    result = detector.detect(image)
    detections_list = result["detections"]
    scooters = detect_scooters(detections_list)

    people_count, scooter_count = get_primary_detection_statistics(detections_list)
    print(f"Найдено объектов: {people_count} людей, {scooter_count} самокатов")

    segmenter = ObjectSegmenter(config['models']['segmentation']['segmentation_model'])
    segmented_results, image = segmenter.segment(image)
    print(f"Результат сегментации\n{segmented_results}")

    visualizer = ResultVisualizer()
    visualizer.visualize_segmentation(image, segmented_results)

    predictor = PosePredictor(
        scooters=scooters,
        use_ensemble=True,
        ensemble_classifiers=config['models']['pose_classification']['ensemble_paths'],
        ensemble_weights=config['models']['pose_classification']['ensemble_weights'],
        pose_model_path=config['models']['pose_estimation']['model_path']
    )
    predictions = predictor.predict_image(image)
    visualizer.visualize_predictions(image, predictions)

    # TODO: 6. КЛАССИФИКАЦИЯ НАЕЗДНИК/ПЕШЕХОД

    # TODO: 7. OCR ДЛЯ НОМЕРОВ

    # TODO: 8. ПРОВЕРКА НАРУШЕНИЙ
    violations = [{
        'type': 'detection_only',
        'message': 'Анализ нарушений скоро будет!'
    }]

    # TODO: 9. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ
    output_image = None

    return output_image, violations


def run_image_analysis(input_image_path, output_image_path, config_path='config/main.yaml'):
    """
    Основная функция для запуска детекции на изображении
    """
    if not os.path.exists(input_image_path):
        print(f"Ошибка: файл {input_image_path} не найден!")
        return False

    input_image = cv2.imread(input_image_path)

    print("Начало анализа")

    try:
        config = load_config(config_path)
        output_image, violations = process_image(input_image, config)

        cv2.imwrite(output_image_path, output_image)
        #TODO: Сделать вывод для нарушений

        return True

    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        return False


def main():
    """Пример использования системы"""
    input_image = "image.jpg"
    output_image = "output.jpg"
    config_file = "config/main.yaml"

    success = run_image_analysis(input_image, output_image, config_file)

    if success:
        print("Анализ завершен успешно")
        print(f"Результат сохранен в: {output_image}")
    else:
        print("Анализ завершен с ошибками")


if __name__ == "__main__":
    main()