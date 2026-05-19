from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ClientData(BaseModel):
    age: float = Field(..., description='Возраст Клиента', examples=[35])
    income: float = Field(..., description='Доход', examples=[50_000])
    employment_years: float = Field(..., description='Стаж работы (лет)', examples=[5])
    credit_score: float = Field(..., description='Кредитный рейтинг', examples=[700])
    existing_loans: int = Field(..., description='Количество действующих кредиторов', examples=[2])
    default_history: int = Field(..., description='История просрочек (0/1)', examples=[0])
    loan_amount: float = Field(..., description='Сумма запрашиваемого кредита', examples=[200_000])
    loan_term_months: int = Field(..., description='Срок кредита в месяцах', examples=[24])
    interest_rate: float = Field(..., description='Процентная ставка', examples=[12.5])
    debt_to_income_ratio: float = Field(..., description='Отношение долга к доходу', examples=[0.3])
    num_dependents: int = Field(..., description='Количество иждивенцев', examples=[1])

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "age": 35,
                "income": 50_000,
                "employment_years": 5,
                "credit_score": 700,
                "existing_loans": 2,
                "default_history": 0,
                "loan_amount": 200_000,
                "loan_term_months": 24,
                "interest_rate": 12.5,
                "debt_to_income_ratio": 0.3,
                "num_dependents": 1
            }
        }
    )


class PredictionResponse(BaseModel):
    client_id: Optional[int] = None
    default_probability: float = Field(..., description='Вероятность просрочки (0-1)')
    prediction: int = Field(..., description='Предсказание: 0 - не просрочит, 1 - просрочит')
    risk_level: str = Field(..., description='Уровень риска')
    recommendation: str = Field(..., description='Рекомендация банка')

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "client_id": 12345,
                "default_probability": 0.23,
                "prediction": 0,
                "risk_level": 'Низкий',
                "recommendation": "Кредит может быть одобрен"
            }
        }
    )


class BatchPredictionRequest(BaseModel):
    clients: List[ClientData] = Field(..., description='Список клиентов')
