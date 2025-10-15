FROM python:3.12-bullseye AS sling_builder
    # install and compress the latest sling binary for use in other stages.
    # binary will be available in the builder root directory `/sling`.
    RUN apt-get update && apt-get --no-install-recommends -y install binutils upx
    RUN curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz' \
        && tar xf sling_linux_amd64.tar.gz \
        && rm -f sling_linux_amd64.tar.gz \
        && chmod +x sling \
        && strip sling && upx sling

FROM python:3.12-bullseye AS dbt_builder
    # install and compress the latest dbt fusion binary for use in other stages.
    # binary will be available in the builder root directory `/dbt`.
    RUN apt-get update && apt-get --no-install-recommends -y install binutils upx
    RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh \
            | /bin/bash -s -- --update \
        && cd /root/.local/bin/ \
        && strip dbt && upx dbt \
        && mv /root/.local/bin/dbt /dbt

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
    ENV SLING_BINARY=/root/.local/bin/sling
    ENV UV_LINK_MODE=copy

    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
    COPY --from=sling_builder sling $SLING_BINARY
    COPY --from=dbt_builder dbt /root/.local/bin/dbt

    ENV SNOWFLAKE_HOME=/root/.config/snowflake/
    RUN --mount=type=secret,id=env-file,target=/tmp/.env \
        . /tmp/.env \
        && mkdir -p $SNOWFLAKE_HOME \ && cd $SNOWFLAKE_HOME \
        && echo [$DESTINATION__HOST] > connections.toml \
        && echo "account = \"$DESTINATION__HOST\"" >> connections.toml \
        && echo "user = \"$DESTINATION__USER\"" >> connections.toml \
        && echo "authenticator = \"snowflake\"" >> connections.toml \
        && echo "password = \"$DESTINATION__PASSWORD\"" >> connections.toml \
        && echo "database = \"_dev_analytics\"" >> connections.toml \
        && echo "warehouse = \"$DESTINATION__WAREHOUSE\"" >> connections.toml

    RUN uv pip install --system ruff sqlfluff
