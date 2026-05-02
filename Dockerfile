# bookworm: предсказуемая база; без apt — меньше точек отказа на билдерах (Zeabur/CI)
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/scripts/start-api.sh /app/scripts/start-bot.sh

ENV PYTHONPATH=/app

# Локально docker-compose переопределяет command; на Zeabur задай Start Command: /app/scripts/start-api.sh или start-bot.sh
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
