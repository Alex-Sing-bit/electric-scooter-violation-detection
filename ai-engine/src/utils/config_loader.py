import os
import yaml


def load_config(config_path: str) -> dict:
    """Загружает конфигурацию из YAML файла"""
    if not os.path.exists(config_path):
        base_config = {
            'models': {
                'detection': {
                        'model_path': 'models/detection/best.pt',
                        'confidence_threshold': 0.44,
                        'iou_threshold': 0.8,
                },
                'pose_estimation': {
                    'model_path': 'models/pose_classification/yolo11m-pose.pt'
                },
                'pose_classification': {
                    'ensemble_paths': ['models/pose_classification/pose_classifier.joblib', 'models/pose_classification/pose_classifier_B.joblib'],
                    'ensemble_weights': [1, 1]
                    },
                'segmentation': {
                    'segmentation_model': 'facebook/mask2former-swin-large-mapillary-vistas-semantic'
                },
            },
        }

        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(base_config, f, default_flow_style=False)
        print(f"Создан базовый конфиг: {config_path}")
        return base_config
    else:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)