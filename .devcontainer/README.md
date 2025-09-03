# .devcontainer を使用した環境構築手順

## 概要

WSL2 + Docker + VSCode を使用した環境構築の手順です。

参考記事: https://learn.microsoft.com/ja-jp/windows/wsl/tutorials/wsl-containers


## 手順

1. Windows で WSL2 を使用できるようにする。(Ubuntuを想定しています)
2. Windows に Docker をインストールする。Docker Desktop から「Use the WSL 2 based engine」を有効になっていることを確認
3. Windows に VSCode をインストールする。拡張「Remote Development」を検索してインストールする
4. WSL2 にデフォルトで Git が入っていることを確認し、config を設定する（Dockerコンテナに引き継がれます）
5. WSL2 からプロジェクトを clone して、`code .` すると VSCode で開かれる
6. VSCode のコマンドパレットから 「Build and Re-Open in Container」を実行
7. WSL2 内に開発環境用のコンテナがビルドされ、VSCode 経由で編集・実行可能となる


## 終了手順

1. 左下の「Dev Container」から、「Close Remote Connection」でコンテナを止めることができる。
2. VSCode を閉じて終了
