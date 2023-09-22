FROM python:3

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Copy poetry.lock in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock ./

ENV C_FORCE_ROOT=1

COPY ./app ./

CMD ["celery", "worker", "-A", "app", "-l", "info", "-Q", "main-queue", "-c", "1"]
