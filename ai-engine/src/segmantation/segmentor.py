from typing import Any, Optional

import cv2
import numpy as np
import torch
from PIL import Image
from numpy import ndarray, dtype
from transformers import pipeline

from segmantation.segmentation_categories import SegmentConfig, SegmentCategory


class ObjectSegmenter:

    def __init__(self, model_name: str, config_class=SegmentConfig):
        self.model_name = model_name
        self.model = self._load_model()
        self.config = config_class
        self.target_classes = config_class.get_all_classes()

    def _load_model(self):
        try:
            segmenter = pipeline(
                "image-segmentation",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1,
                use_fast=True
            )
            return segmenter
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели сегментации {self.model_name}: {e}")

    def _load_image(self, image: ndarray[Any, dtype]) -> Image.Image:
        """Загружает и валидирует изображение"""

        try:
            return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        except Exception as e:
            raise ValueError(f"Ошибка загрузки изображения {image}: {e}")

    def segment(self, image):
        """
        Сегментирует изображение.

        Returns:
            Результаты сегментации по целевым классам и начальное изображение
        """

        image = self._load_image(image)
        results = self.model(image)

        categorized = {category_name: [] for category_name in self.config.CATEGORIES.keys()}
        categorized['unknown'] = []

        for result in results:
            result_class = result['label'].lower()
            category_name = self.config.find_category_for_class(result_class)

            if category_name:
                categorized[category_name].append(result)
            else:
                categorized['unknown'].append(result)

        return results

    def categorize_escooter_surface(self, image, scooters, result=None):
        image = self._load_image(image)
        results = result if result is not None else self.model(image)

        for i in range(0, len(scooters)):
            surf = self.get_dominant_type_in_bbox(segmentation_results=results,
                                           bbox=scooters[i]['bbox'])
            scooters[i]['surface'] = surf if surf is not None else 'unknown'

        return scooters, results

    def get_category_info(self, category_name: str) -> SegmentCategory:
        """Возвращает информацию о категории"""
        return self.config.CATEGORIES.get(category_name)

    def get_dominant_type_in_bbox(self, segmentation_results, bbox) -> Optional[str]:
        """
        Определяет преобладающий тип дорожной инфраструктуры в bounding box.

        Args:
            segmentation_results: Результаты сегментации
            bbox: Bounding box в формате (x1, y1, x2, y2)
            target_types: Целевые типы для анализа (по умолчанию ['road', 'sidewalk'])

        Returns:
            Преобладающий тип или None, если целевые типы не найдены
        """

        x1, y1, x2, y2 = [int(i) for i in bbox]
        bbox_height = y2 - y1

        present_types = {target_type: 0 for target_type in self.config.CATEGORIES}

        lower_half_y1 = y1 + bbox_height // 2

        for result in segmentation_results:
            label_lower = result['label'].lower()
            for target_type, category in self.config.CATEGORIES.items():
                if label_lower in category.classes:
                    mask = np.array(result['mask'])
                    lower_bbox_mask = mask[lower_half_y1:y2, x1:x2]
                    pixel_count = np.sum(lower_bbox_mask > 0)
                    present_types[target_type] += pixel_count
                    break

        dominant_lower_type = max(present_types.items(), key=lambda x: x[1])[0]
        return dominant_lower_type