### 旧インプット

```mermaid
flowchart LR

A@{ shape: doc, label: ユーザー入力 }
B[グローバル定数<br>constants.py]
C[変数展開<br>inputs.py<br>○○○○]
D[グローバルデータクラス<br>app_config.py]
E[計算処理]

proc2(全ての変数が別個<br>入力値/計算値が混在<br>○○○●○●●)

note1@{ shape: notch-rect, label: ✘トレースしづらい }
note2@{ shape: notch-rect, label: ✘大量の引数で渡される }

service(ロジックサービス)
subgraph どこからでも利用
    direction LR
    service
    B
    D
end
どこからでも利用 -.- note1

proc2 -.- note2
A --> C --> proc2 --> E
A --> D --> service --> E
A --> B --> E
```

### 比較表

| 観点                 | BEFORE             | AFTER                  |
| -------------------- | ------------------ | ---------------------- |
| 変数の数             | 多い(全てバラバラ) | 少ない(関連でまとまり) |
| フローの数           | ３本(違いが曖昧)   | ２本(違いが明確)       |
| 入力値/計算値の区別  | つかない           | つく                   |
| 入力値が所属する機能 | ロジック内に埋没   | ファイル配置で明確化   |
| グローバル定数の数   | 多い               | 減らしやすい           |

### 新インプット

```mermaid
flowchart LR

A@{ shape: doc, label: ユーザー入力 }
B[グローバル定数<br>constants.py]
E[計算処理]

F[データクラス間整合]
F0[共通データ]
F1[機能①データ]
F2[機能②データ]
subgraph データクラス
    direction LR
    F --> F0
    F --> F1
    F --> F2
end
service1[ロジックサービス1]
service2[ロジックサービス2]
F0 --> service1 --> E
F1 --> service1
F1 --> E
F1 --> service2 --> E
F2 --> service2
A --> F

note1@{ shape: notch-rect, label: 必須でないものを削減予定 }
note2@{ shape: notch-rect, label: まとまりのあるデータ }
note3@{ shape: notch-rect, label: グローバルデータクラスを除去 }

subgraph どこからでも利用
    direction LR
    B
end
note3 -.- どこからでも利用

note1 -.- B
note2 -.- F2
A --> B --> E

```
