FROM node:22-trixie@sha256:2082d2bf902c8835655c6bcfee3594c00ea900498a9f6e2b96d3352536f9e8d8

ARG CODEX_VERSION=0.153.0

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    MISE_DATA_DIR=/home/node/.local/share/mise \
    PATH=/home/node/.local/bin:/home/node/.local/share/mise/shims:${PATH}

RUN npm install --global "@openai/codex@${CODEX_VERSION}" \
    && test "$(command -v codex)" = /usr/local/bin/codex \
    && npm cache clean --force

USER node

RUN --mount=type=tmpfs,target=/tmp \
    curl --fail --silent --show-error https://mise.run | sh \
    && mise --version \
    && codex --version

USER root

# Docker initializes empty named volumes from these directories on their first
# mount. Keep them credential-free; Codex and Git write credentials at runtime.
RUN ln -s /home/node/.local/share/mise/installs/erlang/28.5/bin/erl /usr/local/bin/erl \
    && ln -s /home/node/.local/share/mise/installs/erlang/28.5/bin/erlc /usr/local/bin/erlc \
    && ln -s /home/node/.local/share/mise/installs/erlang/28.5/bin/escript /usr/local/bin/escript \
    && ln -s /home/node/.local/share/mise/installs/erlang/28.5/bin/epmd /usr/local/bin/epmd \
    && ln -s /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/elixir /usr/local/bin/elixir \
    && ln -s /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/iex /usr/local/bin/iex \
    && ln -s /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/mix /usr/local/bin/mix \
    && mkdir -p /home/node/.codex \
    && mkdir -p /home/node/.config/git \
    && chown -R node:node /home/node/.codex /home/node/.config \
    && git config --system credential.helper 'store --file=/home/node/.config/git/credentials'

USER node

WORKDIR /workspace/symphony-poc
