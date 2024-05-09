#!/usr/bin/env sh

# pip の更新
pip install -U pip

# NOTE: requirements.txt ベースから pyproject.tomlベースへ変更
# pip install -r requirements.txt
pip install .
