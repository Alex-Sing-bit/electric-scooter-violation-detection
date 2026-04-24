import cv2
import numpy as np
from matplotlib import pyplot as plt

from segmantation.segmentation_categories import SegmentConfig
from utils.bbox_utils import join_bboxes


def visualize_violation(image, prediction):
    if image is None or prediction is None:
        return image

    if  prediction['violations'] is None or len(prediction['violations']) == 0:
        return image

    x1, y1, x2, y2 = map(int, join_bboxes(prediction['bbox'], prediction['nearest_scooter']['bbox']))
    color = (0, 0, 255)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 5)
    cv2.putText(image, " ".join(set(prediction['violations'])), (x1 + 5, y1 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    return image


def visualize_warning(image, warning):
    if image is None or warning is None:
        return image

    if warning['warning'] is None or len(warning['warning']) == 0:
        return image

    x1, y1, x2, y2 = map(int, warning['bbox'])
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 165, 255), 2)

    return image


def print_violations(image, violations):
    border_size = 50
    h, w = image.shape[:2]

    bordered_image = cv2.copyMakeBorder(
        image,
        0, border_size,
        0, 0,
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )

    violations_text = " ".join(set(violations))
    text_position = (20, h + border_size - 20)
    cv2.putText(
        bordered_image,
        violations_text,
        text_position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    return bordered_image


class ResultVisualizer:
    def __init__(self, config = SegmentConfig):
        self.config = config

    def visualize_segmentation(self, image, segmentation_results, alpha=0.6):
        """Визуализация результатов сегментации с легендой"""

        seg_image = np.array(image.copy())
        overlay = np.zeros_like(seg_image)

        legend_info = []
        for category in segmentation_results:
            for segmentation in segmentation_results[category]:
                mask = np.array(segmentation['mask'])

                color = self.config.CATEGORIES[category].color
                overlay[mask > 0] = color
                legend_info.append((color, segmentation['label']))

        result_image = cv2.addWeighted(seg_image, 1 - alpha, overlay, alpha, 0)

        plt.figure(figsize=(15, 8))

        plt.subplot(1, 2, 1)
        plt.imshow(result_image)
        plt.axis('off')

        plt.subplot(1, 2, 2)
        legend_height = max(200, len(legend_info) * 35 + 20)
        legend_img = np.ones((legend_height, 400, 3), dtype=np.uint8) * 255

        for i, (color, label) in enumerate(legend_info):
            y_pos = 30 + i * 35
            cv2.rectangle(legend_img, (20, y_pos - 15), (50, y_pos + 5), color, -1)
            cv2.putText(legend_img, label, (60, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        plt.imshow(legend_img)
        plt.title("Легенда классов")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

        return result_image

    def visualize_predictions(self, image, predictions, save_path=None):
        """Визуализация предсказаний на изображении"""
        if image is None:
            return None

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if predictions is None:
            plt.figure(figsize=(12, 8))
            plt.imshow(image_rgb)
            plt.axis('off')
            plt.show()

            return image_rgb

        class_colors = {
            'riding': (0, 255, 0),
            'pushing': (255, 165, 0),
            'climbing': (255, 255, 0),
            'on_foot': (255, 0, 0),
            'other': (128, 0, 128)
        }

        for pred in predictions:
            bbox = pred['bbox'] if 'bbox' in pred else None
            class_name = pred['class']
            confidence = pred['confidence']
            person_id = pred['person_id']

            color = class_colors.get(class_name, (255, 255, 0))

            if bbox is not None:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(image_rgb, (x1, y1), (x2, y2), color, 2)

                '''text = f"ID {person_id}: {class_name} ({confidence:.2f})"
                cv2.putText(image_rgb, text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)'''
            else:
                text = f"ID {person_id}: {class_name} ({confidence:.2f})"
                cv2.putText(image_rgb, text, (10, 30 + 30 * person_id),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        legend_y = 30
        for class_name, color in class_colors.items():
            cv2.putText(image_rgb, f"{class_name}", (image.shape[1] - 150, legend_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            legend_y += 25

        '''plt.figure(figsize=(12, 8))
        plt.imshow(image_rgb)
        plt.axis('off')
        plt.show()'''

        return image_rgb

