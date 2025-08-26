#!/bin/bash
set -e

PYPROJECT="pyproject.toml"
LINE='"bs_models @ git+https://github.com/dagahan/bs_models.git",'

sed -i "s|^\(\s*${LINE}\)|# \1|" "$PYPROJECT"

uv sync

sed -i "s|^#\s*\(${LINE}\)|\1|" "$PYPROJECT"

uv sync
