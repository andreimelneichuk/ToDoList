# Dockerfile for Telegram Bot
FROM python:3.9

# Установите зависимости
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте проект
COPY . /app/

# Команда для запуска
CMD ["python", "bot.py"]