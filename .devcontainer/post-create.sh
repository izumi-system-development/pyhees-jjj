#!/usr/bin/env sh

# pip の更新
pip install -U pip

# Poetry をインストール
pip install poetry

# プロジェクトのルートに仮想環境を作成
poetry config virtualenvs.in-project true

# 開発用の依存関係をインストール
poetry install --with dev
