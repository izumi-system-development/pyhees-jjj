### IBECs2025の大まかなスケジュール

```mermaid
gantt

title IBECs 2025
dateFormat YYYY-MM

section pyhees_Ver.UP
    追従対応 :active, verup, 2025-08-15, 1w

section ドキュメント
    最低V&E整理 :active, doc1, after verup, 3M
    その他ロジックDiagram : after doc1, 2026-03
    コードクリーン : , 2025-08-15, 2026-03

section 前年度修正
    確認修正 : bu2024, 2025-08-15, 3M

section 最低V&E
    ロジック仮組 :active, minve_try, after verup, 3M
    検証 :active, minve_check, after minve_try, 2026-03

section 全体
    納品後検収 :active, after minve_check, 2w

```

大まかな作業予定を図化しました。
昨年度のプロジェクトのレビューで提案された、仮納品のような考え方を組込んでいます。

追加機能の最低風量電力機能ですが、年末までに、ロジックの仮組が完了する予定で
一旦実行できるようになりましたら仮納品として検証作業に入れます。
つまり納品後の検収2週間とは別に、検証期間を設けていますがいかがでしょうか。
今期は昨年より速くスタートを切れるためこれが可能になっています。

