from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings
warnings.filterwarnings('ignore')
import time
import logging
from app.schemas import ClientData, PredictionResponse, BatchPredictionRequest
from app.model import model_instance
from app.logger_cofig import setup_logging
import psycopg2
from app.utils import determine_risk_level, save_to_prediction_log, save_batch_to_predictions_log


setup_logging()
logger = logging.getLogger('credit_scoring_api.main')


app = FastAPI(
    title='Credit Scoring API',
    description='API для предсказания просрочки по кредиту',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root():
    return {
        "message": "Credit Scoring API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - предсказание для одного клиент",
            "/predict_batch": "POST - Пакетное предсказание",
            "/health": "GET - Проверка здоровья сервиса"
        }
    }

@app.get('/health')
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_instance.model is not None,
        "timestamp": time.time()
    }

@app.post('/predict', response_model=PredictionResponse)
async def predict(client: ClientData):
    client_dict = client.model_dump()
    try:
        logger.info(f'Получен запрос на предсказание для клиента. Данные: {client_dict}')

        probability, prediction = model_instance.predict(client_dict)
        risk_level, recommendation = determine_risk_level(probability)

        logger.info(f'Предсказание вероятность={probability}, risk={risk_level}')

        save_to_prediction_log(client_dict, probability, risk_level)

        return PredictionResponse(
            default_probability=round(probability, 4),
            prediction=prediction,
            risk_level=risk_level,
            recommendation=recommendation
        )
    except Exception as e:
        logger.error(f'Критическая ошибка при скоринге данных {client_dict}. Текст ошибки: {str(e)}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при обработке запроса: {str(e)}'
        )

@app.post('/predict_batch')
async def predict_batch(request: BatchPredictionRequest):
    try:
        logger.info(f'Получен пакетный запрос на {len(request.clients)} клиентов')

        # Переводим список Pydantic-объектов в список обычных словарей Python
        clients_list = [client.model_dump() for client in request.clients]

        # Передаем всю пачку в оптимизированный метод модели
        raw_results = model_instance.predict_batch(clients_list)

        # Обогащаем результаты расчетом уровня риска и рекомендаций
        final_results = []
        db_records = []
        for i, res in enumerate(raw_results):
            prob = res['probability']
            pred = res['prediction']
            risk_level, recommendation = determine_risk_level(prob)

            final_results.append({
                "client_index": i,
                "default_probability": round(prob, 4),
                "prediction": pred,
                "risk_level": risk_level,
                "recommendation": recommendation
            })

            c = clients_list[i]

            record = (
                c['age'], c['income'], c['employment_years'], c['credit_score'],
                c['existing_loans'], c['default_history'], c['loan_amount'],
                c['loan_term_months'], c['interest_rate'], c['debt_to_income_ratio'],
                c['num_dependents'], prob, risk_level
            )
            db_records.append(record)

        save_batch_to_predictions_log(db_records)

        # Убедитесь, что return находится СНАРУЖИ цикла for
        return {
            "total_clients": len(request.clients),
            "results": final_results
        }

    except Exception as e:
        logger.error(f"Ошибка при пакетном предсказании: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get('/model_info')
async def model_info():
    return {
        "model_type": type(model_instance).__name__,
        "feature_names": model_instance.feature_names,
        "n_features": len(model_instance.feature_names)
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host='0.0.0.0',
        port=8000,
        reload=True
    )

