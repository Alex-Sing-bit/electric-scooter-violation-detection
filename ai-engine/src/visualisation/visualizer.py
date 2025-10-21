import cv2
import numpy as np
from matplotlib import pyplot as plt

from segmantation.segmentation_categories import SegmentConfig


class ResultVisualizer:
    def __init__(self, config = SegmentConfig):
        self.config = config

    def visualize_segmentation(self, image, segmentation_results, alpha=0.6):
        """Визуализация результатов сегментации с легендой"""

        seg_image = np.array(image.copy())
        overlay = np.zeros_like(seg_image)

        segmentation_results['unknown'] = []

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