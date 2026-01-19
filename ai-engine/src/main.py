import os
import time
from typing import Any

import cv2
from numpy import ndarray, dtype

from detection.object_detector import ObjectDetector
from segmantation.segmentor import ObjectSegmenter
from utils.config_loader import load_config
from visualisation.visualizer import ResultVisualizer


def get_primary_detection_statistics(detections_list):
    """Собирает статистику по обнаруженным объектам"""
    people_count = sum(1 for detection in detections_list if detection.class_name == 'person')
    scooter_count = sum(1 for detection in detections_list if detection.class_name == 'electricscooter')

    return people_count, scooter_count

def process_image(image: ndarray[Any, dtype], config: dict):
    """Выполняет общий анализ изображения на нарушения"""

    detector = ObjectDetector(
        model_path=config['paths']['detection_model'],
        confidence_threshold=config['models']['detection']['confidence_threshold'],
        iou_threshold=config['models']['detection']['iou_threshold']
    )

    result = detector.detect(image)
    detections_list = result["detections"]

    people_count, scooter_count = get_primary_detection_statistics(detections_list)
    print(f"Найдено объектов: {people_count} людей, {scooter_count} самокатов")

    segmenter = ObjectSegmenter()
    segmented_results, image = segmenter.segment(image)
    image.show()
    print(f"Результат сегментации\n{segmented_results}")

    visualizer = ResultVisualizer()
    visualizer.visualize_segmentation(image, segmented_results)

    # TODO: 5. АНАЛИЗ ПОЗ

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