FROM node:22-trixie@sha256:2082d2bf902c8835655c6bcfee3594c00ea900498a9f6e2b96d3352536f9e8d8

ARG CODEX_VERSION=0.153.0
ARG GH_VERSION=2.100.0
ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    MISE_DATA_DIR=/home/node/.local/share/mise \
    PATH=/home/node/.local/bin:/home/node/.local/share/mise/shims:${PATH}

RUN npm install --global "@openai/codex@${CODEX_VERSION}" \
    && test "$(command -v codex)" = /usr/local/bin/codex \
    && npm cache clean --force

RUN case "$TARGETARCH" in \
      amd64) gh_arch=amd64 ;; \
      arm64) gh_arch=arm64 ;; \
      *) echo "Unsupported GitHub CLI architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac \
    && gh_archive="gh_${GH_VERSION}_linux_${gh_arch}.tar.gz" \
    && gh_release_url="https://github.com/cli/cli/releases/download/v${GH_VERSION}" \
    && curl --fail --silent --show-error --location --output "/tmp/${gh_archive}" "${gh_release_url}/${gh_archive}" \
    && curl --fail --silent --show-error --location --output /tmp/gh_checksums.txt "${gh_release_url}/gh_${GH_VERSION}_checksums.txt" \
    && grep " ${gh_archive}$" /tmp/gh_checksums.txt | (cd /tmp && sha256sum --check --status -) \
    && tar --extract --gzip --file "/tmp/${gh_archive}" --directory /tmp \
    && install "/tmp/gh_${GH_VERSION}_linux_${gh_arch}/bin/gh" /usr/local/bin/gh \
    && gh --version \
    && rm -rf /tmp/gh_*

USER node

RUN --mount=type=tmpfs,target=/tmp \
    curl --fail --silent --show-error https://mise.run | sh \
    && mise --version \
    && codex --version

USER root

# Docker initializes empty named volumes from these directories on their first
# mount. Keep them credential-free; Codex and GitHub CLI write auth state at runtime.
RUN mkdir -p /home/node/.codex \
    && mkdir -p /home/node/.config/gh \
    && chown -R node:node /home/node/.codex /home/node/.config \
    && git config --system credential.https://github.com.helper '!gh auth git-credential'

USER node

WORKDIR /workspace/symphony-poc
