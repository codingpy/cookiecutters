FROM python:3

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Copy poetry.lock in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --without dev ; fi"

COPY ./app ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
