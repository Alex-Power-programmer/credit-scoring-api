import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score
import os
import lightgbm as lgb

import psycopg2

db_params = {
    "host": 'localhost',
    "database": "credit_db",
    "user": 'postgres',
    'password': '1324',
    "port": 5432
}
print('Connecting to PostgresSQL...')
conn = psycopg2.connect(**db_params)
try:
    query = 'SELECT * FROM clients_history;'
    data = pd.read_sql_query(query, conn)
    print(f'Data successfully loaded! Lines: {data.shape[0]}')
finally:
    conn.close()

if 'id' in data.columns:
    data = data.drop('id', axis=1)

X = data.drop('default', axis=1)
y = data['default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaler = scaler.fit_transform(X_train)
X_test_scaler = scaler.transform(X_test)

classes_weights = (len(y_train) - sum(y_train)) / sum(y_train)

model = lgb.LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    scale_pos_weight=classes_weights,
    random_state=42,
    verbose=-1
)
model.fit(X_train_scaler, y_train)

y_pred_proba = model.predict_proba(X_test_scaler)[:, 1]

custom_threshold = 0.35
y_pred = (y_pred_proba >= custom_threshold).astype(int)

print('\n' + '='*30)
print(f'Recall on test: {recall_score(y_test, y_pred):.4f}')
print(f'Precision on test: {precision_score(y_test, y_pred):.4f}')
print('=' * 30)

os.makedirs('models', exist_ok=True)


joblib.dump(model, 'models/logistic_regression.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

joblib.dump(X.columns.tolist(), 'models/feature_names.pkl')
print('Model and preprocessor successfully saved')

