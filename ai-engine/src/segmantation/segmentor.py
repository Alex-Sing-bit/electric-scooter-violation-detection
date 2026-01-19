from pathlib import Path
from typing import Any

import cv2
import torch
from PIL import Image
from numpy import ndarray, dtype
from transformers import pipeline

from segmantation.segmentation_categories import SegmentConfig, SegmentCategory


class ObjectSegmenter:
    MODEL_NAME = 'facebook/mask2former-swin-large-mapillary-vistas-semantic'

    def __init__(self, config_class=SegmentConfig):
        self.model = self._load_model()
        self.config = config_class
        self.target_classes = config_class.get_all_classes()

    def _load_model(self):
        try:
            segmenter = pipeline(
                "image-segmentation",
                model=self.MODEL_NAME,
                device=0 if torch.cuda.is_available() else -1,
                use_fast=True
            )
            return segmenter
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели сегментации {self.MODEL_NAME}: {e}")

    def _load_image(self, image: ndarray[Any, dtype]) -> Image.Image:
        """Загружает и валидирует изображение"""

        try:
            return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        except Exception as e:
            raise ValueError(f"Ошибка загрузки изображения {image}: {e}")

    def segment(self,  image: ndarray[Any, dtype]):
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

        return categorized, image

    def get_category_info(self, category_name: str) -> SegmentCategory:
        """Возвращает информацию о категории"""
        return self.config.CATEGORIES.get(category_name)