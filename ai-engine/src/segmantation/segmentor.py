from dataclasses import dataclass
from typing import List

import torch
from PIL import Image
from transformers import pipeline


def _load_model(model_name: str):
    try:
        segmenter = pipeline(
            "image-segmentation",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1
        )
        return segmenter
    except Exception as e:
        raise Exception(f"Ошибка загрузки модели сегментации {model_name}: {e}")

class ObjectSegmenter:

    def __init__(self, model_name: str, target_classes: List[str] = ("Road", "Sidewalk", "Crosswalk")):
        self.model = _load_model(model_name)
        self.target_classes = target_classes

    def segment(self, image_path: str):
        """
        Сегментирует изображение.

        Returns:
            Результаты сегментации по целевым классам
        """

        image = Image.open(image_path).convert('RGB')
        results = self.model(image)

        filtered_results = []
        for result in results:
            if any(target_class.lower() in result['label'].lower() for target_class in self.target_classes):
                filtered_results.append(result)


        return filtered_results

