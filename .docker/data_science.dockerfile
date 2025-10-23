FROM python:3.12-slim-bullseye AS data_science
    ENV PATH="/opt/dagster/app/.venv/bin:$PATH"
    ENV DAGSTER_HOME=/opt/dagster/dagster_home/
    ENV TARGET=prod
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
    
    # copy libs and configs
    WORKDIR /opt/
    COPY .docker/dagster.yaml $DAGSTER_HOME
    COPY /libs/data_platform_utils libs/data_platform_utils
    
    # install user code
    WORKDIR /opt/dagster/app
    COPY /packages/data_science/src src
    COPY /packages/data_science/pyproject.toml pyproject.toml
    RUN --mount=type=cache,target=/root/.cache/uv,id=science_uv_cache \
        uv sync --no-dev --compile-bytecode --link-mode=copy

    # this is for keyvault stub will be removed in real deployment
    COPY .env .env
    
    EXPOSE 5000

    CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "5000", "-m", "data_science.definitions"]
