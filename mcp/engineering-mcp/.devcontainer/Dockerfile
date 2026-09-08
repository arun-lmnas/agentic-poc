FROM python:3.12-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash vscode

USER vscode
