import pandas as pd
from ultralytics import YOLO

from pose_classification.pose_analyzer import extract_features
from pose_classification.pose_classifier import PoseClassifier
from pose_classification.simple_ensemble import SimpleEnsemble
from utils.bbox_utils import find_nearest_scooter


def _make_classifiers(ensemble_classifiers):
    classifiers = []
    for clf in ensemble_classifiers:
        classifiers.append(PoseClassifier(clf))

    return classifiers


class PosePredictor:
    def __init__(self, scooters, pose_model_path='../app/models/pose_classification/yolo11m-pose.pt',
                 use_ensemble=False, ensemble_classifiers=None, ensemble_weights=None):
        if use_ensemble:
            self.classifiers = _make_classifiers(ensemble_classifiers)
            for classifier in self.classifiers:
                if not classifier.load_model():
                    raise Exception(f"Не удалось загрузить модель для ансамбля!")

            self.ensemble = SimpleEnsemble(
                classifiers=self.classifiers,
                weights=ensemble_weights
            )
            self.label_encoder = self.classifiers[0].label_encoder
            self.is_ensemble = True

            self.all_feature_columns = set()
            for clf in self.classifiers:
                self.all_feature_columns.update(clf.feature_columns)
            self.all_feature_columns = list(self.all_feature_columns)

        else:
            self.classifier = PoseClassifier(ensemble_classifiers[0])
            if not self.classifier.load_model():
                raise Exception("Сначала обучите классификатор!")
            self.label_encoder = self.classifier.label_encoder
            self.all_feature_columns = self.classifier.feature_columns
            self.is_ensemble = False

        self.pose_model = YOLO(pose_model_path)
        self.scooters = scooters

    def extract_features_from_image(self, image):
        """Извлечение признаков из изображения"""
        results = self.pose_model(image, conf=0.5, verbose=False)

        if results[0].keypoints.shape[0] == 0:
            return None, None, None

        all_features = []
        bboxes = []
        nearest_scooters =  []

        for i, (keypoints, box) in enumerate(zip(results[0].keypoints.data, results[0].boxes)):
            bbox = box.xyxy[0].cpu().numpy()
            bboxes.append(bbox)
            kp_array = keypoints.cpu().numpy()

            nearest_scooter = find_nearest_scooter(bbox, self.scooters)
            nearest_scooters.append(nearest_scooter)
            scooter_bbox = nearest_scooter['bbox'] if nearest_scooter else None

            features, visible_points = extract_features(kp_array, bbox, scooter_bbox)

            all_features.append(features)

        return all_features, bboxes, nearest_scooters

    def predict_image(self, image):
        """Предсказание позы на изображении"""
        features_list, bboxes, nearest_scooters = self.extract_features_from_image(image)

        if not features_list:
            return None

        predictions = []

        for i, features in enumerate(features_list):
            feature_vector = self._prepare_feature_vector(features, self.is_ensemble)

            if feature_vector is not None:
                if self.is_ensemble:
                    pred_idx, probabilities = self.ensemble.predict(feature_vector)
                    prediction = pred_idx[0]
                    probability = probabilities[0]
                else:
                    prediction = self.classifier.model.predict(feature_vector)[0]
                    probability = self.classifier.model.predict_proba(feature_vector)[0]

                class_name = self.label_encoder.inverse_transform([prediction])[0]
                confidence = probability[prediction]

                predictions.append({
                    'person_id': i + 1,
                    'class': class_name,
                    'confidence': confidence,
                    'all_probabilities': dict(zip(self.label_encoder.classes_, probability)),
                    'bbox': bboxes[i],
                    'nearest_scooter': nearest_scooters[i],
                    'violations': []
                })

                print(f"Человек {i + 1}: {class_name} (уверенность: {confidence:.3f})")
                print(probability)

        return predictions

    def _prepare_feature_vector(self, features, is_ensemble: bool):
        """Подготовка вектора признаков для модели"""
        try:

            feature_df = pd.DataFrame([features])

            exclude_cols = ['image_path']
            feature_df = feature_df.drop(columns=[col for col in exclude_cols if col in feature_df.columns],
                                         errors='ignore')

            for col in self.all_feature_columns:
                if col not in feature_df.columns:
                    feature_df[col] = 0.0

            if is_ensemble:
                return feature_df[self.all_feature_columns]

            return feature_df[self.classifier.feature_columns]

        except Exception as e:
            print(f"Ошибка при подготовке признаков: {e}")
            return None