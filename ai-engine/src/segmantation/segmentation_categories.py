from dataclasses import dataclass
from typing import Set


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
