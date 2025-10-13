import os
import yaml


def load_config(config_path: str) -> dict:
    """Загружает конфигурацию из YAML файла"""
    if not os.path.exists(config_path):
        base_config = {
            'paths': {
                'detection_model': 'models/detection/best.pt',
            },
            'models': {
                'detection': {
                    'confidence_threshold': 0.6,
                    'iou_threshold': 0.7
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