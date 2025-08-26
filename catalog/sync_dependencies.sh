#!/usr/bin/env bash
set -Eeuo pipefail

PYPROJECT="pyproject.toml"
LINE='"bs_models @ git+https://github.com/dagahan/bs_models.git",'
IN_DOCKER="${RUNNING_INSIDE_DOCKER:-0}"

uv_sync() {
  if [[ "$IN_DOCKER" == "1" ]]; then
    uv sync 
  else
    if ! uv sync --extra dev >/dev/null 2>&1; then
      uv sync --extra dev
    fi
  fi
}

sed -i "s|^\(\s*${LINE}\)|# \1|" "$PYPROJECT"

uv_sync

sed -i "s|^#\s*\(${LINE}\)|\1|" "$PYPROJECT"

uv_sync


