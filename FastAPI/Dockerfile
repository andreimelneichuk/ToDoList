# Dockerfile for FastAPI
FROM python:3.9

# Установите зависимости
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте проект
COPY . /app/

# Команда для запуска
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]