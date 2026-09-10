#!/bin/sh

set -eu

cd /workspace/symphony-poc/.symphony/elixir

mise install

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

mise exec -- mix build
