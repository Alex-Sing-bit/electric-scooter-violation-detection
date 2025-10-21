from dataclasses import dataclass
from enum import Enum
from typing import List, Set

import torch
from PIL import Image
from transformers import pipeline


@dataclass
class SegmentCategory:
    name: str
    description: str
    classes: Set[str]
    color: str = None  # для визуализации


class SegmentConfig:
    """Конфигурация категорий сегментации"""

    CATEGORIES = {
        'crosswalk': SegmentCategory(
            name="crosswalk",
            description="Пешеходный переход",
            classes={'crosswalk'},
            color="#0022FF"
        ),
        'acceptable': SegmentCategory(
            name="acceptable",
            description="Приемлемо для нахождения самоката",
            classes={'sidewalk', 'bike lane', 'pedestrian area',
                     'parking', 'curb', 'curb cut'},
            color="#00FF00"
        ),
        'unacceptable': SegmentCategory(
            name="unacceptable",
            description="Неприемлемо для нахождения самоката",
            classes={'terrain', 'rail track', 'grass', 'vegetation', 'water'},
            color="#FF0000"
        ),
        'road': SegmentCategory(
            name="road",
            description="Проезжая часть",
            classes={'road', 'service lane'},
            color="#FFA500"
        )
    }

    @classmethod
    def get_all_classes(cls) -> Set[str]:
        return {
            cls for category in cls.CATEGORIES.values()
            for cls in category.classes
        }

    @classmethod
    def find_category_for_class(cls, class_name: str) -> str:
        """Находит категорию для конкретного класса"""
        for category_name, category in cls.CATEGORIES.items():
            if class_name.lower() in category.classes:
                return category_name
        return None

class ObjectSegmenter:
    MODEL_NAME = 'facebook/mask2former-swin-large-mapillary-vistas-semantic'

    def __init__(self, config_class=SegmentConfig):
        self.model = self._load_model()
        self.config = config_class
        self.target_classes = config_class.get_all_classes()

    def _load_model(self):
        model_name = 'facebook/mask2former-swin-large-mapillary-vistas-semantic'
        try:
            segmenter = pipeline(
                "image-segmentation",
                model=self.MODEL_NAME,
                device=0 if torch.cuda.is_available() else -1
            )
            return segmenter
        except Exception as e:
            raise Exception(f"Ошибка загрузки модели сегментации {model_name}: {e}")

    def segment(self, image_path: str):
        """
        Сегментирует изображение.

        Returns:
            Результаты сегментации по целевым классам
        """

        image = Image.open(image_path).convert('RGB')
        results = self.model(image)

        categorized = {category_name: [] for category_name in self.config.CATEGORIES.keys()}
        categorized['unknown'] = []  # для классов не попавших в категории

        for result in results:
            result_class = result['label'].lower()
            category_name = self.config.find_category_for_class(result_class)

            if category_name:
                categorized[category_name].append(result)
            else:
                categorized['unknown'].append(result)

        return categorized

    def get_category_info(self, category_name: str) -> SegmentCategory:
        """Возвращает информацию о категории"""
        return self.config.CATEGORIES.get(category_name)