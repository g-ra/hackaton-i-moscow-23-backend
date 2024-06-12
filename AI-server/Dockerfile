# Используем официальный базовый образ Python
FROM python:3.8-slim

# Установка рабочей директории в контейнере
WORKDIR /usr/src/app

# Обновление списка пакетов и установка необходимых библиотек
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Задание переменной окружения, которая определяет адрес, на котором будет запущен сервер
ENV FLASK_APP=main.py

# Запуск приложения при старте контейнера
CMD ["flask", "run", "--host=0.0.0.0"]