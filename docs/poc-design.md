# BTC Backtest PoC — 基本設計書

作成日: 2026-05-11

---

## 1. ディレクトリ構成案

```
btc-backtest-poc/
├── README.md                          # セットアップ・実行方法
├── requirements.txt                   # Python依存パッケージ
├── .env.example                       # 環境変数テンプレート（APIキー等）
├── .gitignore                         # API秘密情報除外
│
├── docs/
│   ├── investment-simulation-research.md
│   ├── poc-requirements.md
│   ├── poc-design.md                 # 本ドキュメント
│   ├── sample_result_report.md       # サンプル実行結果レポート
│   └── API_NOTES.md                  # API取得ノート
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # エントリーポイント
│   ├── config.py                     # 設定管理
│   ├── logger.py                     # ログ設定
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py                # 価格データ取得（API）
│   │   ├── loader.py                 # CSVやParquetからの読み込み
│   │   ├── cleaner.py                # データ品質チェック、欠損検出
│   │   └── repository.py             # DB保存（ローカルDB想定）
│   │
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── base.py                   # 指標計算の基底クラス
│   │   ├── sma.py                    # SMA計算
│   │   ├── rsi.py                    # RSI計算（将来拡張）
│   │   └── collection.py             # 複数指標の一括計算
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── base.py                   # 戦略の基底クラス
│   │   ├── sma_crossover.py          # SMA クロス戦略
│   │   └── registry.py               # 戦略登録・管理
│   │
│   ├── backtest/
│   │   ├── __init__.py
│   │   ├── engine.py                 # バックテスト実行エンジン
│   │   ├── order.py                  # 仮想注文、約定シミュレーション
│   │   ├── portfolio.py              # ポジション・残高管理
│   │   ├── metrics.py                # 損益指標計算
│   │   └── report.py                 # バックテスト結果レポート
│   │
│   ├── mirofish/
│   │   ├── __init__.py
│   │   ├── connector.py              # MiroFish CLI/API連携
│   │   ├── prompt_builder.py         # 入力Markdown生成
│   │   ├── output_parser.py          # 出力JSON解析
│   │   └── storage.py                # MiroFish結果保存
│   │
│   └── ui/
│       ├── __init__.py
│       ├── formatter.py              # コンソール出力形式
│       ├── report_generator.py       # Markdownレポート生成
│       └── messages.py               # 安全警告文言
│
├── data/
│   ├── .gitkeep
│   ├── sample_btc_daily.csv          # サンプルOHLCVデータ
│   └── cache/                         # APIキャッシュ、DL済みデータ
│
├── outputs/
│   ├── .gitkeep
│   ├── backtest_results/             # バックテスト結果JSON
│   ├── trade_logs/                   # 取引ログ
│   ├── mirofish_inputs/              # MiroFish投入テキスト
│   ├── mirofish_outputs/              # MiroFish生成結果
│   └── reports/                      # Markdownレポート
│
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_indicators.py
│   ├── test_strategy.py
│   ├── test_backtest_engine.py
│   └── fixtures.py                   # テスト用ダミーデータ
│
└── migrations/
    ├── .gitkeep
    └── 001_initial_schema.sql        # DB初期スキーマ（SQLite想定）
```

---

## 2. データ取得処理 (`src/data/`)

### 2.1 `fetcher.py` — API経由取得