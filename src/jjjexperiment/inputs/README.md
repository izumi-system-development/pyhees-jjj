### 旧インプット

```mermaid
flowchart LR

A@{ shape: doc, label: ユーザー入力 }
B[グローバル定数<br>constants.py]
C[変数展開<br>inputs.py<br>○○○○]
D[グローバルDIコンテナ<br>app_config.py]
E[計算処理]

proc1(どこからでも利用)
proc2(全ての変数が別個<br>入力値/計算値が混在<br>○○○●○●●)

note1@{ shape: notch-rect, label: ✘トレースしづらい }
note2@{ shape: notch-rect, label: ✘大量の引数で渡される }

proc2 --- note2
A --> C --> proc2 --> E
A --> D --- proc1 -.-> E
A --> B --- proc1
proc1 --- note1
```

### 新インプット

```mermaid
flowchart LR

A@{ shape: doc, label: ユーザー入力 }
B[グローバル定数<br>constants.py]
E[計算処理]

F[OBJ間整合]
F0[共通データ]
F1[機能1用データ]
F2[機能2用データ]
subgraph DIコンテナ
    direction LR
    F --> F0
    F --> F1
    F --> F2
end
F0 -.-> E
F1 -.-> E
F2 -.-> E
A ---> F

proc1(どこからでも利用)
note1@{ shape: notch-rect, label: 必須でないものを削減予定 }
note2@{ shape: notch-rect, label: まとまりのあるデータ }

note1 -.- B
note2 -.- F2
A --> B --- proc1 -.-> E

```

### 比較表

| 観点                 | BEFORE             | AFTER                  |
| -------------------- | ------------------ | ---------------------- |
| 変数の数             | 多い(全てバラバラ) | 少ない(関連でまとまり) |
| 入力値/計算値の区別  | つかない           | つく                   |
| 入力値が所属する機能 | コードから読取     | ファイルで分割         |
| グローバル定数の数   | 多い               | 少ない                 |
