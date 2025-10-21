from dataclasses import dataclass
from typing import Set


@dataclass
class SegmentCategory:
    name: str
    description: str
    classes: Set[str]
    color: tuple[int, int, int] = None


class SegmentConfig:
    """Конфигурация категорий сегментации"""

    CATEGORIES = {
        'crosswalk': SegmentCategory(
            name="crosswalk",
            description="Пешеходный переход",
            classes={'crosswalk', 'lane marking - crosswalk'},
            color=(0, 0, 255)
        ),
        'acceptable': SegmentCategory(
            name="acceptable",
            description="Приемлемо для нахождения самоката",
            classes={'sidewalk', 'bike lane', 'pedestrian area',
                     'parking', 'curb', 'curb cut'},
            color=(0, 255, 0)
        ),
        'unacceptable': SegmentCategory(
            name="unacceptable",
            description="Неприемлемо для нахождения самоката",
            classes={'terrain', 'rail track', 'grass', 'vegetation', 'water'},
            color=(255, 0, 0)
        ),
        'road': SegmentCategory(
            name="road",
            description="Проезжая часть",
            classes={'road', 'service lane'},
            color=(255, 165, 0)
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
