import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# 1. Параметры подключения к вашему серверу PostgreSQL
# Указа здесь свой актуальный пароль от пользователя postgres!
db_params = {
    "host": 'localhost',
    'database': "postgres",
    "user": "postgres",
    "password": "1324",
    "port": 5432
}

def init_database():
    print('Reading file CVS-file')
    df = pd.read_csv('data/dataset_321.csv')

    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    if 'employment_year' in df.columns:
        df = df.rename(columns={'employment_year': 'employment_years'})

    # 2. Создаем новую базу данных "credit_db", если её еще нет
    conn = psycopg2.connect(**db_params)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'credit_db';")
    exists = cursor.fetchone()
    if not exists:
        print('Создание базы данных credit_db')
        cursor.execute('CREATE DATABASE credit_db;')

    cursor.close()
    conn.close()

    # 3. Подключаемся уже к созданной базе credit_db
    db_params['database'] = 'credit_db'
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()


    try:
        # 4. Создаем таблицу для исторических данных обучения
        print('Creating table clients_history...')
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS clients_history
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           age
                           REAL,
                           income
                           REAL,
                           employment_years
                           REAL,
                           credit_score
                           REAL,
                           existing_loans
                           INT,
                           default_history
                           INT,
                           loan_amount
                           REAL,
                           loan_term_months
                           INT,
                           interest_rate
                           REAL,
                           debt_to_income_ratio
                           REAL,
                           num_dependents
                           INT,
                           "default"
                           INT
                       );
                       """)
        # 5. Создаем таблицу для логирования будущих предсказаний из API
        print('Creating table predictions_log...')
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS predictions_log
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       age
                       REAL,
                       income
                       REAL,
                       employment_years
                       REAL,
                       credit_score
                       REAL,
                       existing_loans
                       INT,
                       default_history
                       INT,
                       loan_amount
                       REAL,
                       loan_term_months
                       INT,
                       interest_rate
                       REAL,
                       debt_to_income_ratio
                       REAL,
                       num_dependents
                       INT,
                       default_probability
                       REAL,
                       risk_level
                       VARCHAR
                   (
                       50
                   )
                       );
                   """)

        # 6. Быстрая пакетная вставка данных из DataFrame в Postgres
        print("Заливка данных из CSV в таблицу clients_history (это может занять немного времени)...")

        # ИСПРАВЛЕНИЕ: метод .tolist() конвертирует типы NumPy (np.float64)
        # в чистые типы Python (float/int), которые база данных примет без ошибок
        values = [tuple(x) for x in df.to_numpy().tolist()]

        # Экранируем имена колонок двойными кавычками
        escaped_columns = ', '.join([f'"{col}"' for col in df.columns])
        query = f"INSERT INTO clients_history ({escaped_columns}) VALUES %s"

        execute_values(cursor, query, values)

        conn.commit()
        print("База данных успешно инициализирована и заполнена данными!")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_database()



