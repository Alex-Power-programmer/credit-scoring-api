import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class CreditScoringModel:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CreditScoringModel, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        model_path = Path(__file__).parent.parent / 'models'
        print('Загрузка модели...')
        self.model = joblib.load(model_path / 'logistic_regression.pkl')
        self.scaler = joblib.load(model_path / 'scaler.pkl')
        self.feature_names = joblib.load(model_path / 'feature_names.pkl')
        print('Модель успешно загружена')

    def preprocess(self, data_dict):
        df = pd.DataFrame([data_dict])

        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0

        df = df[self.feature_names]

        scaled_data = self.scaler.transform(df)
        scaled_df = pd.DataFrame(scaled_data, columns=self.feature_names)
        return scaled_df

    def predict(self, data_dict):
        processed = self.preprocess(data_dict)
        probability = float(self.model.predict_proba(processed)[0][1])
        prediction = int(self.model.predict(processed)[0])
        return probability, prediction

    def predict_batch(self, clients_list):
        results = []
        for client in clients_list:
            prob, pred = self.predict(client)
            results.append({
                'probability': prob,
                'prediction': pred
            })

        return results

model_instance = CreditScoringModel()
