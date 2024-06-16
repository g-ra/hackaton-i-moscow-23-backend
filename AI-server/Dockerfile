FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda && \
    rm -f Miniconda3-latest-Linux-x86_64.sh

ENV PATH=/miniconda/bin:$PATH

# Update Conda
RUN conda update -n base -c defaults conda

# Create a new environment
RUN conda create -n env python=3.10 -y
# Install packages with Conda
# It uses a shell form to activate the environment for the installation commands.
SHELL ["conda", "run", "-n", "env", "/bin/bash", "-c"]
RUN conda install -n env pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Revert to the default shell
SHELL ["/bin/bash", "-c"]
# Добавление необходимых библиотек, которые лучше устанавливать через системный менеджер
RUN apt-get update && apt-get install -y \
    python3-opencv \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    ffmpeg \
    x264 \
    libx264-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/yolov10
RUN git clone -q https://github.com/THU-MIG/yolov10.git .
RUN conda run -n env pip install .

# Копирование файла зависимостей и установка зависимостей
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN conda run -n env pip install -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Задание переменной окружения, которая определяет адрес, на котором будет запущен сервер
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
# Использование базового образа с поддержкой CUDA

# Запуск приложения при старте контейнера
CMD ["conda", "run", "-n", "env", "flask", "run", "--host=0.0.0.0", "--debug"]