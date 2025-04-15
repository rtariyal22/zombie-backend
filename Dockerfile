FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

RUN chmod +x /app/entrypoint.sh
ENV DJANGO_SETTINGS_MODULE "django_server.settings"
ENTRYPOINT ["/app/entrypoint.sh"]
