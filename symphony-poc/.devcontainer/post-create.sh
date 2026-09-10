#!/bin/sh

set -eu

ensure_runtime_link() {
  target=$1
  link=$2

  if [ ! -x "$target" ]; then
    echo "Missing required mise runtime executable: $target" >&2
    exit 1
  fi

  if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then
    return
  fi

  rm -f "$link"
  ln -s "$target" "$link"
}

cd /workspace/symphony-poc/.symphony/elixir

mise install

mkdir -p /home/node/.local/bin /home/node/.config/gh /home/node/.codex

ensure_runtime_link /home/node/.local/share/mise/installs/erlang/28.5/bin/erl /home/node/.local/bin/erl
ensure_runtime_link /home/node/.local/share/mise/installs/erlang/28.5/bin/erlc /home/node/.local/bin/erlc
ensure_runtime_link /home/node/.local/share/mise/installs/erlang/28.5/bin/escript /home/node/.local/bin/escript
ensure_runtime_link /home/node/.local/share/mise/installs/erlang/28.5/bin/epmd /home/node/.local/bin/epmd
ensure_runtime_link /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/elixir /home/node/.local/bin/elixir
ensure_runtime_link /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/iex /home/node/.local/bin/iex
ensure_runtime_link /home/node/.local/share/mise/installs/elixir/1.19.5-otp-28/bin/mix /home/node/.local/bin/mix

git config --global user.name "Arunkumar Ganesan"
git config --global user.email "arunkumar.ganesan@lmnas.com"

if ! git config --global --get-all safe.directory | grep -Fx /workspace/symphony-poc >/dev/null 2>&1; then
  git config --global --add safe.directory /workspace/symphony-poc
fi

if gh auth status >/dev/null 2>&1; then
  gh auth setup-git
fi

if [ ! -d deps ] || [ ! -d _build ]; then
  attempt=1
  max_attempts=3
  while :; do
    if HEX_HTTP_TIMEOUT=120000 HEX_HTTP_CONCURRENCY=2 mise exec -- mix setup; then
      break
    fi

    if [ "$attempt" -ge "$max_attempts" ]; then
      echo "mix setup failed after $max_attempts attempts" >&2
      exit 1
    fi

    delay=$((attempt * 5))
    echo "mix setup failed; retrying in ${delay}s (attempt $((attempt + 1))/$max_attempts)" >&2
    sleep "$delay"
    attempt=$((attempt + 1))
  done
else
  mise exec -- mix deps
fi

mise exec -- mix build
