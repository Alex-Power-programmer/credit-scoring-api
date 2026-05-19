markdown
# Credit Scoring API (Machine Learning Microservice)

Промышленный микросервис для оценки кредитных рисков и предсказания вероятности дефолта заемщика. 

## 🚀 Стек технологий
* **ML**: Python 3.9, LightGBM (Recall: 0.84, Precision: 0.61), Scikit-Learn, Joblib
* **Backend**: FastAPI, Pydantic v2, uvicorn
* **Database & Logging**: PostgreSQL, Psycopg2, RotatingFileHandler
* **DevOps**: Docker, Docker Compose

---

## 🛠 Пошаговый запуск проекта

Проект полностью контейнеризирован. Вам не нужно устанавливать Python, PostgreSQL или библиотеки машинного обучения локально. Всё поднимется автоматически одной командой.

### 1. Клонирование репозитория
Откройте терминал и скачайте проект на свой компьютер:
```bash
git clone https://github.com/Alex-Power-programmer/credit-scoring-api
cd credit-scoring-api
```

### 2. Запуск инфраструктуры через Docker Compose
Убедитесь, что у вас запущен Docker Desktop, и выполните команду:
```bash
docker-compose up -d --build
```
*Эта команда автоматически скачает образ PostgreSQL, соберет образ FastAPI, установит системные C++ зависимости (libgomp) для LightGBM и свяжет контейнеры по внутренней сети.*

### 3. Локальная установка зависимостей и инициализация БД
Если вы хотите запускать вспомогательные скрипты (`init_db.py`, `train_model.py`) локально на своем компьютере, перед запуском необходимо установить библиотеки из файла `requirements.txt`:

```bash
# Создаем и активируем виртуальное окружение (рекомендуется)
python -m venv .venv
source .venv/bin/activate  # Для Linux/macOS
.venv\Scripts\activate     # Для Windows

# Устанавливаем все зависимости одной командой
pip install -r requirements.txt

# Запускаем инициализацию базы данных
python init_db.py
```

### 3.1 Первоначальная инициализация базы данных
Поскольку база данных внутри контейнера поднимается абсолютно чистой, необходимо один раз запустить скрипт для автоматического создания таблиц и заливки исторических данных из CSV:
```bash
python init_db.py
```

---

## 🖥 Использование и проверка

После успешного выполнения команд выше ваше API будет полностью готово к работе по адресу: **`http://127.0.0.1:8000/`**

### Интерактивная документация (Swagger UI)
Перейдите по ссылке для отправки тестовых запросов через браузер:
* **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** — интерактивная панель Swagger UI

### 📝 Примеры запросов и тестирования через cURL

Вы можете протестировать работу запущенного API прямо из терминала вашей операционной системы (Командная строка Windows, PowerShell или Терминал Linux).

#### 1. Тестирование одиночного предсказания (POST `/predict`)

Скопируйте и запустите эту команду в терминале:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/docs#/default/predict_predict_post' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "age": 35,
  "income": 50000,
  "employment_years": 5,
  "credit_score": 700,
  "existing_loans": 2,
  "default_history": 0,
  "loan_amount": 200000,
  "loan_term_months": 24,
  "interest_rate": 12.5,
  "debt_to_income_ratio": 0.3,
  "num_dependents": 1
}'
```

**Пример успешного ответа сервера (Code 200):**
```json
{
  "client_id": null,
  "default_probability": 0.1774,
  "prediction": 0,
  "risk_level": "Низкий",
  "recommendation": "Кредит может быть одобрен на стандартных условиях"
}
```

#### 2. Тестирование пакетного предсказания (POST `/predict_batch`)

Команда для одновременной отправки пачки из двух клиентов (первый — надежный, второй — с высокой вероятностью дефолта):

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/docs#/default/predict_batch_predict_batch_post' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "clients": [
    {
      "age": 40,
      "income": 90000,
      "employment_years": 10,
      "credit_score": 750,
      "existing_loans": 1,
      "default_history": 0,
      "loan_amount": 300000,
      "loan_term_months": 12,
      "interest_rate": 10.5,
      "debt_to_income_ratio": 0.2,
      "num_dependents": 0
    },
    {
      "age": 22,
      "income": 20000,
      "employment_years": 0.5,
      "credit_score": 450,
      "existing_loans": 5,
      "default_history": 1,
      "loan_amount": 500000,
      "loan_term_months": 36,
      "interest_rate": 24.0,
      "debt_to_income_ratio": 0.8,
      "num_dependents": 2
    }
  ]
}'
```

**Пример успешного ответа сервера (Code 200):**
```json
{
  "total_clients": 2,
  "results": [
    {
      "client_index": 0,
      "default_probability": 0.0412,
      "prediction": 0,
      "risk_level": "Низкий",
      "recommendation": "Кредит может быть одобрен на стандартных условиях"
    },
    {
      "client_index": 1,
      "default_probability": 0.9234,
      "prediction": 1,
      "risk_level": "Критический",
      "recommendation": "Рекомендуется отказ в выдаче кредита"
    }
  ]
}
```


### Доступные эндпоинты:
1. **`POST /predict`** — Одиночное предсказание. Принимает JSON с анкетой одного клиента. Возвращает точную вероятность дефолта, категорию риска (`Низкий`, `Средний`, `Высокий`, `Критический`) и рекомендацию банка. Результат автоматически записывается в таблицу `predictions_log` в PostgreSQL.
2. **`POST /predict_batch`** — Пакетное предсказание. Оптимизированная массовая обработка списка клиентов за один запрос с использованием пакетной вставки `execute_values` в базу данных.
3. **`GET /health`** — Проверка здоровья сервиса (проверяет, загружена ли ML-модель в оперативную память контейнера).

---

## 📁 Структура проекта
* `app/main.py` — Маршруты FastAPI и логика обработки входящих запросов.
* `app/model.py` — Инициализация ML-модели (паттерн Singleton), загрузка препроцессоров и масштабирование данных.
* `app/utils.py` — Функции бизнес-логики (определение рисков) и низкоуровневая интеграция с PostgreSQL через `psycopg2`.
* `app/schemas.py` — Строгая валидация входящих и исходящих данных на базе Pydantic v2.
* `app/logger_config.py` — Конфигурация ротационного логирования (авторазделение на `app.log` и `error.log`).
* `train_model.py` — Скрипт обучения градиентного бустинга LightGBM с тюнингом порога классификации.
* `init_db.py` — Скрипт первичной миграции и инициализации СУБД.