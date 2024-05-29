#!/bin/bash

# NOTE: init_logger() をしているとログファイルへの書き込み処理を行います
# テスト実行を速くするために調査時以外には有効化されないようにするため
# シェルスクリプトでテストディレクトリ内から削除します

# ターゲットコードを含んでいる行ごと消すので注意
target_code="init_logger"
# 削除対象のディレクトリを指定
dir="src/tests/*"

# NOTE: テストを階層的に置かないことを前提としています
find $dir -maxdepth 0 -type f -iname '*.py' | while read file; do
  filename="$file"

  # ファイル名にスペース含んでいる時 $filename ではなく "${filename}" を使用する
  # line_numbers=$(grep -n "$target_code" "$filename" | cut -d: -f1)
  line_numbers=($(grep -n "$target_code" "$filename" | cut -d: -f1))
  length=${#line_numbers[@]}
  echo "$length"

  if [ "$length" -eq 0 ]; then
    echo "No need to delete"
  else
    # 削除行指定のテキストを生成 ex. 49d; 60d;
    delete_count=0
    echo "$line_numbers"

    # 後ろの行数から削除するため
    for ((i = ${length}; i > 0; i--)); do
      delete_count=$((delete_count + 1))  # インクリメント

      current_line="${line_numbers[i]}";
      delete_row_command="${current_line}d";
      sed -i "${delete_row_command}" "$filename"
    done

    # 削除行あるとき
    if [ $delete_count -gt 0 ]; then
      # 指定行を削除してファイルを上書き
      echo "Deleted ${delete_count} rows in $filename"
    fi
  fi
done
