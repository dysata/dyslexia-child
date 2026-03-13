# Используем легкий образ Python 3.11
FROM python:3.12-slim

# Установка переменных окружения для предотвращения создания .pyc файлов и буферизации логов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Переменная окружения для приложения
    PORT=8001 \
    HOST=0.0.0.0

# Рабочая директория внутри контейнера
WORKDIR /app

# Установка системных зависимостей (если понадобятся для компиляции пакетов)
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt сначала для использования кэша Docker
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта и скрипт запуска
COPY . .

# Делаем скрипт запуска исполняемым
#RUN chmod +x run.sh

# Создаем пользователя без прав root для безопасности (рекомендуется)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

RUN mkdir -p /app/data && chown -R appuser:appuser /app/data
USER appuser

WORKDIR /app

# Открываем порт, на котором будет работать сервис
EXPOSE 8001

# Вариант Б (Рекомендуемый): Запуск напрямую через uvicorn с правильными параметрами для Docker
# В prod версии мы переопределяем параметры из run.sh, чтобы слушать 0.0.0.0 и отключить reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

