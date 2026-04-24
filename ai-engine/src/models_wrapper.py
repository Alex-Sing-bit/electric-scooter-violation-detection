from utils.config_loader import load_config
from detection.object_detector import ObjectDetector
from pose_classification.pose_predictor import PosePredictor
from segmantation.segmentor import ObjectSegmenter
from violations.analyzer import ViolationsAnalyser

class ModelsEngine:
    def __init__(self, config_path="src/config/main.yaml"):
        self.config = load_config(config_path)
        self.detector = ObjectDetector(
            model_path=self.config['models']['detection']['model_path'],
            confidence_threshold=self.config['models']['detection']['confidence_threshold'],
            iou_threshold=self.config['models']['detection']['iou_threshold']
        )
        self.segmenter = ObjectSegmenter(self.config['models']['segmentation']['segmentation_model'])
        self.analyzer = ViolationsAnalyser()
        self.predictor = PosePredictor(
            scooters=[],
            use_ensemble=True,
            ensemble_classifiers=self.config['models']['pose_classification']['ensemble_paths'],
            ensemble_weights=self.config['models']['pose_classification']['ensemble_weights'],
            pose_model_path=self.config['models']['pose_estimation']['model_path']
        )