# SLDL言語リファレンス

SLDL文書は型付きのソースファイルです。通常の文書構造に加えて、主張・根拠・結論などの論理関係を明示できます。

## 基本形

```sldl
document "research_report_ja" : JapaneseResearchReport {
    meta {
        title: "タイトル"@ja;
        author: "Author"@en;
        date: Date("2026-05-02");
        lang: "ja-JP";
        version: "1.0.0";
    }

    section intro : Section {
        title: "はじめに"@ja;
        paragraph { text: "本文。"@ja; }
    }
}
```

## 主な要素

- `document`: 文書IDと文書型を宣言する。
- `meta`: タイトル、著者、日付、言語、版などを記述する。
- `section`: 文書の章・節に相当する構造を作る。
- `paragraph`: 本文を書く。
- `claim`, `evidence`, `conclusion`: 論理関係を表す。
- `table`, `flowchart`: 表や図をソースとして記述する。

詳しい英語版の正式説明は `docs/sldl_language_reference.md` を参照してください。
