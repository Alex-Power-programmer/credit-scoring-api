import logging
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger("credit_scoring_api.utils")


DB_PARAMS = {
    "host": 'docker host.docker.internal', # docker host.docker.internal или если без docker то localhost
    'database': "credit_db",
    'user': 'postgres',
    'password': '1324',
    'port': 5432
}


def determine_risk_level(probability: float) -> tuple:
    if probability < 0.3:
        return 'Низкий', "Кредит может быть одобрен на стандартных условиях"
    elif probability < 0.6:
        return 'Средний', "Рекомендуется запросить дополнительные гарантии или повышенную ставку"
    elif probability < 0.8:
        return 'Высокий', "Требуется детальный анализ, возможно только под залог"
    else:
        return 'Критический', "Рекомендуется отказ в выдаче кредита"


def save_batch_to_predictions_log(records: list):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # SQL-запрос (без секции VALUES, так как её сформирует execute_values)
        query = """
                INSERT INTO predictions_log (age, income, employment_years, credit_score, existing_loans, \
                                             default_history, loan_amount, loan_term_months, interest_rate, \
                                             debt_to_income_ratio, num_dependents, default_probability, risk_level) \
                VALUES %s; \
                """

        execute_values(cursor, query, records)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Пакет из {len(records)} запросов успешно сохранен в PostgreSQL")
    except Exception as db_error:
        logger.error(f"Не удалось сохранить пакет логов в БД: {str(db_error)}")


def save_to_prediction_log(client_dict: dict, probability: float, risk_level: str):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        insert_query = """
                       INSERT INTO predictions_log (age, income, employment_years, credit_score, existing_loans, \
                                                    default_history, loan_amount, loan_term_months, interest_rate, \
                                                    debt_to_income_ratio, num_dependents, default_probability, \
                                                    risk_level) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); \
                       """

        cursor.execute(insert_query, (
            client_dict['age'], client_dict['income'], client_dict['employment_years'],
            client_dict['credit_score'], client_dict['existing_loans'], client_dict['default_history'],
            client_dict['loan_amount'], client_dict['loan_term_months'], client_dict['interest_rate'],
            client_dict['debt_to_income_ratio'], client_dict['num_dependents'], probability, risk_level
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Данные запроса успешно сохранены в PostgresSQL (predictions_log)")
    except Exception as db_error:
        logger.error(f"Не удалось сохранить лог в БД: {str(db_error)}")