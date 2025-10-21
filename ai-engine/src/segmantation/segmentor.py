import torch
from PIL import Image
from transformers import pipeline

from segmantation.segmentation_categories import SegmentConfig, SegmentCategory


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