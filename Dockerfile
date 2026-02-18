# Используем базовый образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для mysqlclient и других библиотек
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями Python
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 8000

# Команда для запуска сервера разработки Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
