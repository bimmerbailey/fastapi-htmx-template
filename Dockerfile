# BASE
FROM python:3.11.2-slim-bullseye as base

# python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/src" \
    VENV_PATH="/src/.venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# `builder-base`
FROM base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --without dev --no-root
COPY ./src/app ./app


# `DEVELOPMENT`
FROM base as development
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH .
COPY ./src/tests ./tests

# quicker install as runtime deps are already installed
RUN poetry install --with dev

EXPOSE 8000

CMD ["uvicorn", "app:init_app", "--host", "0.0.0.0", \
     "--port", "8000", "--reload", "--no-access-log", "--factory"]


# `PRODUCTION`
FROM base as production

WORKDIR $PYSETUP_PATH

COPY --from=builder-base $PYSETUP_PATH/.venv ./.venv
COPY --from=builder-base $PYSETUP_PATH/app ./app

CMD ["gunicorn", "app:init_app()", "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:80"]

