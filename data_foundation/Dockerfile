FROM python:3.13-bullseye AS data_foundation_builder

    ENV UV_COMPILE_BYTECODE=1
    ENV UV_LINK_MODE=copy
    ENV UV_PROJECT_ENVIRONMENT=/usr/local/
    ENV UV_CACHE_DIR=/var/cache/uv

    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
    COPY ./pyproject.toml pyproject.toml

    RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | /bin/bash -s -- --update && \
        uv sync --no-install-project --no-dev --no-cache --compile-bytecode && \
        python -c 'from sling.bin import *; download_binary(get_sling_version())'
    
    RUN apt-get update && apt-get -y install binutils upx && \
        cd /root/.sling/bin/sling/ && cd $(ls -d */|head -n 1) && \
        mv sling /usr/local/bin/sling && \
        mv /root/.local/bin/dbt /usr/local/bin/dbt && \
        cd /usr/local/bin/  && \
        strip sling && upx sling && \
        strip dbt && upx dbt

FROM python:3.13-slim-bullseye AS dbt_builder
    ARG DESTINATION__PASSWORD
    ENV DESTINATION__PASSWORD=${DESTINATION__PASSWORD}
    ENV TARGET=prod
    COPY dbt dbt
    COPY .env.prod .env
    COPY --from=data_foundation_builder /usr/local/bin/dbt/ /usr/local/bin/dbt

    RUN cd dbt && \
        dbt clean && \
        dbt deps && \
        dbt parse && \
        dbt compile

FROM python:3.13-slim-bullseye AS data_foundation

    ARG DESTINATION__PASSWORD

    ENV DESTINATION__PASSWORD=${DESTINATION__PASSWORD}
    ENV DAGSTER_HOME=/opt/dagster/dagster_home
    ENV TARGET=prod
    ENV SLING_BINARY=/usr/local/bin/sling

    COPY --from=data_foundation_builder /usr/local/ /usr/local/
    COPY dagster.yaml $DAGSTER_HOME/dagster.yaml

    WORKDIR /data_foundation/

    COPY pyproject.toml pyproject.toml
    COPY data_foundation data_foundation
    COPY --from=dbt_builder dbt dbt
    COPY .env.prod .env
    
    EXPOSE 80