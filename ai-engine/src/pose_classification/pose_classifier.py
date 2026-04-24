import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


class PoseClassifier:
    def __init__(self, model_path='pose_classifier.joblib'):
        self.model_path = model_path
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_columns = None

    def load_and_prepare_data(self, csv_path):
        """Загрузка и подготовка данных"""
        df = pd.read_csv(csv_path)
        print(f"Загружено {len(df)} записей")
        print(f"Распределение классов:\n{df['label'].value_counts()}")

        y = self.label_encoder.fit_transform(df['label'].values)
        print(
            f"Закодированные классы: {dict(zip(self.label_encoder.classes_, self.label_encoder.transform(self.label_encoder.classes_)))}")

        exclude_cols = ['image_path', 'label']
        self.feature_columns = [
            col for col in df.columns
            if col not in exclude_cols
        ]

        X = df[self.feature_columns]

        X = self._clean_data(X)

        return X, y

    def _clean_data(self, X):
        """Очистка и подготовка данных"""
        X = X.replace([np.inf, -np.inf], 0)

        for col in X.columns:
            if X[col].dtype == 'object':
                try:
                    X[col] = pd.to_numeric(X[col], errors='coerce')
                except:
                    print(f"Не удалось преобразовать колонку {col} в числовой формат")

        return X

    def train(self, csv_path, random_state=17):
        X, y = self.load_and_prepare_data(csv_path)

        pipeline = Pipeline([
            ('scaler', self.scaler),
            ('rf', RandomForestClassifier(
                n_estimators=500,
                max_depth=5,
                min_samples_leaf=7,
                class_weight='balanced_subsample',
                random_state=random_state,
                bootstrap=True,
                oob_score=True,
                n_jobs=-1
            ))
        ])

        loo = LeaveOneOut()

        scores = cross_val_score(pipeline, X, y, cv=loo, n_jobs=-1)
        loocv_acc = scores.mean()
        print(f"Честный LOOCV Accuracy: {loocv_acc:.4f}")

        pipeline.fit(X, y)

        oob_acc = pipeline.named_steps['rf'].oob_score_
        print(f"OOB Score: {oob_acc:.4f}")

        self.model = pipeline
        self.save_model()

        return loocv_acc

    def save_model(self):
        """Сохранение модели"""
        if self.model is not None:
            joblib.dump({
                'model': self.model,
                'label_encoder': self.label_encoder,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns
            }, self.model_path)
            print(f"Модель сохранена в {self.model_path}")

    def load_model(self):
        """Загрузка модели"""
        try:
            loaded = joblib.load(self.model_path)
            self.model = loaded['model']
            self.label_encoder = loaded['label_encoder']
            self.scaler = loaded['scaler']
            self.feature_columns = loaded['feature_columns']
            print(f"Модель загружена из {self.model_path}")
            return True
        except Exception as e:
            print(f"Не удалось загрузить модель из {self.model_path}: {e}")
            return False
