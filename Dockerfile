# 1. Скачиваем официальный готовый образ с Python 3.9
FROM python:3.9-slim

# 2. Создаем рабочую папку внутри виртуального контейнера
WORKDIR /code

# 3. Копируем файл со списком библиотек внутрь контейнера
COPY ./requirements.txt /code/requirements.txt

# 4. ИСПРАВЛЕНИЕ: Устанавливаем системную библиотеку libgomp1 (OpenMP) для LightGBM
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# 5. Устанавливаем все библиотеки Python внутри контейнера
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 6. Указываем Python, что текущая папка /code — это корень проекта
ENV PYTHONPATH=/code

# 7. Копируем папки с кодом и обученной моделью в контейнер
COPY ./app /code/app
COPY ./models /code/models

# 8. Команда для автоматического запуска сервера при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
