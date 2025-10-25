FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye AS sling_builder
    # install the latest sling binary for use in other stages.
    # binary will be available in the builder root directory `/sling`.
    RUN curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz' \
        && tar xf sling_linux_amd64.tar.gz \
        && rm -f sling_linux_amd64.tar.gz \
        && chmod +x sling

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye AS dbt_builder
    # install the latest dbt fusion binary for use in other stages.
    # binary will be available in the builder root directory `/dbt`.
    RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh \
        | /bin/bash -s -- --update \
        && mv /root/.local/bin/dbt /dbt

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye AS data_platform_dev_container
    ENV SLING_BINARY=/usr/local/bin/sling
    ENV DBT_BINARY=/home/vscode/.local/bin/dbt

    ENV UV_CACHE_DIR=/home/vscode/.cache/uv
    ENV UV_LINK_MODE=copy
    ENV SNOWFLAKE_HOME=/home/vscode/.config/snowflake/
    ENV PATH="/home/vscode/.local/bin/:$PATH"

    COPY --from=sling_builder sling $SLING_BINARY
    COPY --from=dbt_builder dbt $DBT_BINARY

    RUN --mount=type=secret,id=env-file,target=/home/vscode/.tmp/.env \
        . /home/vscode/.tmp/.env \
        && mkdir -p $SNOWFLAKE_HOME \ && cd $SNOWFLAKE_HOME \
        && echo [$DESTINATION__HOST] > connections.toml \
        && echo "account = /"$DESTINATION__HOST/"" >> connections.toml \
        && echo "user = /"$DESTINATION__USER/"" >> connections.toml \
        && echo "authenticator = /"snowflake/"" >> connections.toml \
        && echo "password = /"$DESTINATION__PASSWORD/"" >> connections.toml \
        && echo "database = /"_dev_analytics/"" >> connections.toml \
        && echo "warehouse = /"$DESTINATION__WAREHOUSE/"" >> connections.toml

    RUN pip install uv \
        && uv pip install --system ruff sqlfluff \
        && mkdir -p /home/vscode/.vscode-server/extensions \
        && mkdir -p /home/vscode/.local/bin/ \
        && echo 'alias dbtf=/home/vscode/.local/bin/dbt' >> /home/vscode/.bashrc \
        # && echo '. .venv/bin/activate' >> /home/vscode/.bashrc \
        && chown -R vscode /home/vscode/

        