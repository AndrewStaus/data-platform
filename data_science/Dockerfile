FROM python:3.10-bullseye AS data_science_builder

    ENV UV_LINK_MODE=copy
    ENV UV_PROJECT_ENVIRONMENT=/usr/local/

    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
    COPY ./pyproject.toml pyproject.toml

    RUN uv sync --no-install-project --no-dev --no-cache --compile-bytecode


FROM python:3.10-slim-bullseye AS data_science

    ARG DESTINATION__PASSWORD

    ENV DESTINATION__PASSWORD=${DESTINATION__PASSWORD}
    ENV DAGSTER_HOME=/opt/dagster/dagster_home
    ENV TARGET=prod
    COPY --from=data_science_builder /usr/local/ /usr/local/
    COPY dagster.yaml $DAGSTER_HOME/dagster.yaml

    WORKDIR /data_science/

    COPY pyproject.toml pyproject.toml
    COPY data_science data_science
    COPY .env.prod .env
    
    EXPOSE 80