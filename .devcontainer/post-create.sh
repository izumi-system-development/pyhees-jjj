#!/usr/bin/env sh

# pip の更新
pip install -U pip

# NOTE: requirements.txt ベースから pyproject.tomlベースへ変更
# 参考: https://stackoverflow.com/a/77134290
# pip install -r requirements.txt
pip install '.[dev]'
