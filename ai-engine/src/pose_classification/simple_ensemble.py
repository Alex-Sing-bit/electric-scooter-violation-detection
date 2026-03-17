import numpy as np


class SimpleEnsemble:
    def __init__(self, classifiers, weights=None):
        self.classifiers = classifiers
        self.weights = weights if weights else [1] * len(classifiers)
        self.label_encoder = classifiers[0].label_encoder

    def predict(self, X_df):
        """X_df - DataFrame со всеми возможными фичами"""
        probas = []

        for classifier, weight in zip(self.classifiers, self.weights):
            # Подготовка фичей для конкретного классификатора
            features_to_use = [col for col in classifier.feature_columns
                               if col in X_df.columns]

            X_subset = X_df[features_to_use].copy()

            # Добавляем недостающие колонки нулями
            for col in classifier.feature_columns:
                if col not in X_subset.columns:
                    X_subset[col] = 0

            X_subset = X_subset[classifier.feature_columns]

            proba = classifier.model.predict_proba(X_subset)
            probas.append(proba * weight)

        # Взвешенное усреднение
        avg_proba = np.sum(probas, axis=0) / np.sum(self.weights)
        return np.argmax(avg_proba, axis=1), avg_proba
