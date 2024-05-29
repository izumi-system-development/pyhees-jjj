#!/bin/bash

# NOTE: コマンド実行時の注意
# sh ./script.sh のように明示的にシェルを指定して実行しないこと

# NOTE: init_logger() をしているとログファイルへの書き込み処理を行います
# テスト実行を速くするために調査時以外には有効化されないようにするため
# シェルスクリプトでテストディレクトリ内から削除します

# ターゲットコードを含んでいる行ごと消すので注意
target_code="init_logger"
# 削除対象のディレクトリを指定
dir="src/tests/*"

# NOTE: テストを階層的に置かないことを前提としています
find $dir -maxdepth 0 -type f -iname '*.py' | while read file; do

  # ファイル名にスペース含んでいる時 $filename ではなく "${filename}" を使用する
  line_numbers=$(grep -n -F -w "$target_code" "$file" | cut -d : -f 1)
  length=${#line_numbers[@]}

  # 必ず入っている空文字でも
  first_item=$(echo "$line_numbers" | head -n 1)

  if [ -z "$first_item" ]; then
    # 空文字の時 -> 削除不要のファイル
    echo "No need to delete -> $file"
  else
    # 削除した行数
    delete_count=0

    for line_number in $line_numbers; do
      # 後ろの行数から削除したいがリバースでなめるコードが難しい
      # 代わりに通常の若い行番号からの削除に削除した行を引いている

      current_line=$((line_number - delete_count))
      # 削除行指定のテキストを生成 ex. 49d; 60d;
      delete_row_command="${current_line}d"
      # echo "$delete_row_command"

      # 行の削除実行
      sed -i "${delete_row_command}" "$file"
      # 削除した行のインクリメント
      delete_count=$((delete_count + 1))
    done

    # 削除行あるとき
    if [ $delete_count -gt 0 ]; then
      echo "Deleted ${delete_count} rows -> $file"
    fi
  fi
done
