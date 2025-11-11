FROM python:3.12-slim

WORKDIR /app

# Копируем файлы зависимостей и readme
COPY pyproject.toml poetry.lock backend-README.md ./

# Копируем исходный код приложения
COPY app /app/app
COPY alembic /app/alembic

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && chmod +x /usr/local/bin/poetry \
    && chmod -R a+rx /root/.local/

# Ставим зависимости и проект (уже с кодом в /app/app)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# Копируем служебные файлы, если есть (.env и пр.)
COPY .env .env


EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
