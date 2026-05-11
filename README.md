# BTC Backtest PoC - Proof of Concept

> **免責事項**: このツールはシミュレーション・検証用です。将来の成績を保証しません。すべての投資判断は自己責任でお願いします。

## 概要

BTCの過去価格データを用いた、SMA（Simple Moving Average）ゴールデンクロス・デッドクロス戦略の **バックテストシステム** です。

- ✓ 実売買なし（検証・学習用）
- ✓ APIキー不要（公開データのみ）
- ✓ 単純で拡張しやすい設計
- ✓ 詳細なログと結果保存

## プロジェクト構成

```
btc-backtest-poc/
├── docs/
│   ├── investment-simulation-research.md    # 調査資料
│   ├── poc-requirements.md                  # 要件定義
│   └── poc-design.md                        # 基本設計
│
├── src/
│   ├── config.py                 # 設定管理
│   ├── logger.py                 # ログ設定
│   ├── main.py                   # エントリーポイント
│   ├── data/                     # データ取得・処理
│   ├── indicators/               # テクニカル指標
│   ├── strategy/                 # 売買戦略
│   ├── backtest/                 # バックテスト実行
│   ├── ui/                       # UI・出力
│   └── mirofish/                 # MiroFish連携（将来）
│
├── data/                         # 入力データ
├── outputs/                      # 結果出力
├── logs/                         # ログファイル
│
├── requirements.txt              # Python依存パッケージ
├── .env.example                  # 環境変数テンプレート
└── README.md                     # このファイル
```

## セットアップ

### 前提条件

- Python 3.11 以上
- pip

### インストール手順

#### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd btc-backtest-poc
```

#### 2. 仮想環境を作成

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

#### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

#### 4. 環境変数を設定

```bash
# .env.example をコピー
cp .env.example .env

# .env を編集（必要に応じてAPIキーなど設定）
# ただし、初回実行時はAPIキーは不要です
```

## 使用方法

### 最小実行（サンプルデータ使用）

```bash
cd <project-root>

# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 実行
python src/main.py
```

実行すると以下が行われます：

1. 安全免責事項を表示
2. 設定情報を表示
3. サンプルデータを生成（初回）または読み込み
4. データ品質チェック
5. テクニカル指標（SMA 9, 21）を計算
6. SMA クロスオーバーシグナルを生成
7. バックテストを実行
8. 損益指標と取引履歴を表示
9. 結果をJSON形式で保存

### 出力例

```
==================================================
  STEP 1: Data Loading
==================================================
Generating sample data: 365 days, start_price=$40,000.00
Generated 365 candles: $38,500.23 - $45,200.50

==================================================
  STEP 5: Backtest Execution
==================================================
Running backtest on 365 candles

==================================================
  STEP 6: Results
==================================================
==================================================
BACKTEST RESULTS
==================================================

Capital:
  Initial Capital           $10,000.00
  Final Value              $12,500.00
  Realized P&L              $2,500.00
  Total Return                +25.00%

Trades:
  Total Trades                     12
  Buy Count                         6
  Sell Count                        6
  Round Trips                       6

Performance:
  Win Count                         4
  Loss Count                        2
  Win Rate                      66.67%
  Avg Win                     $850.50
  Avg Loss                   -$450.25

Risk:
  Max Drawdown              -8.50%
  Max Loss                 -$850.00
  Profit Factor               2.55

==================================================
```

## PoC 機能

### 実装済み機能

- ✓ BTCサンプルデータ生成・読み込み
- ✓ データ品質チェック（欠損、重複、OHLC関係検証）
- ✓ SMA（9日、21日）計算
- ✓ SMA クロスオーバーシグナル生成
- ✓ バックテスト実行
  - 仮想注文、約定シミュレーション
  - 手数料・スリッページ適用
  - ポジション管理、損益計算
- ✓ 損益指標計算
  - 損益率、勝率、最大ドローダウン
  - Profit Factor、平均勝ち負け
- ✓ 結果の保存（JSON形式）
- ✓ コンソール出力・ログ記録

### 実装予定機能（Phase 2以降）

- ☐ 複数戦略対応（RSI, Bollinger Bands等）
- ☐ ペーパートレード（ライブ/リアルタイム価格対応）
- ☐ MiroFish連携（市場シナリオ分析）
- ☐ Webダッシュボード
- ☐ BTC以外の銘柄対応（株、FX）
- ☐ 実売買API連携（手動承認付き）

## 設定

### `.env` 環境変数

重要な設定項目：

```env
# データソース（初回はlocalで自動生成）
DATA_SOURCE=local

# バックテストパラメータ
BACKTEST_INITIAL_CAPITAL=10000      # 初期資金
BACKTEST_FEE_RATE=0.001             # 手数料率（0.1%）
BACKTEST_SLIPPAGE_RATE=0.0005       # スリッページ率（0.05%）

# ログレベル
LOG_LEVEL=INFO

# 出力ディレクトリ
OUTPUT_DIR=./outputs
```

## ログ

実行ログは以下に保存されます：

```
logs/backtest.log
```

コンソールとファイルの両方に出力されます。

## バックテスト結果

バックテスト結果は以下に保存されます：

```
outputs/backtest_results/backtest_YYYYMMDD_HHMMSS.json
```

JSON形式の結果：

```json
{
  "strategy": {
    "name": "SMA_CROSSOVER",
    "params": {
      "sma_short": 9,
      "sma_long": 21
    }
  },
  "metrics": {
    "initial_capital": 10000,
    "final_value": 12500,
    "realized_pnl": 2500,
    "total_return_pct": 25.0,
    "total_trades": 12,
    "win_rate": 0.6667,
    "max_drawdown": -0.085,
    ...
  },
  "trades": [
    {
      "timestamp": "2024-01-15T00:00:00",
      "side": "BUY",
      "price": 42500.00,
      "size": 0.235,
      "fee": 9.99,
      "reason": "Golden Cross: ..."
    },
    ...
  ]
}
```

## 安全制約

本PoCで必ず守られている制約：

1. ✓ 実売買APIは実装されていない
2. ✓ ユーザーのAPIキー・シークレットを扱わない
3. ✓ すべての出力に「シミュレーション用」と明記
4. ✓ UI には投資助言・利益保証表現は含まれない
5. ✓ ログに秘密情報は出力されない

禁止表現（UIに使用しない）：

- 「買い推奨」「売り推奨」
- 「勝てる」「稼げる」
- 「確度が高い」「安全」
- 「AIが予測」「利益見込み」

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'pandas'`

依存パッケージがインストールされていません。実行してください：

```bash
pip install -r requirements.txt
```

### エラー: `PermissionError` ログファイルが開けない

`logs` ディレクトリの権限を確認してください：

```bash
mkdir -p logs
chmod 755 logs
```

### サンプルデータが生成されない

`data/samples` ディレクトリが書き込み可能か確認してください：

```bash
mkdir -p data/samples
chmod 755 data/samples
```

## 開発・拡張

### 新しい指標を追加する

`src/indicators/` 配下にクラスを作成：

```python
from src.indicators.base import Indicator
import pandas as pd

class RSI(Indicator):
    def __init__(self, period: int = 14):
        super().__init__("RSI", {"period": period})
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 計算ロジック
        return rsi_values
```

`main.py` で使用：

```python
indicators.add_indicator("RSI_14", RSI(14))
```

### 新しい戦略を追加する

`src/strategy/` 配下に戦略クラスを作成：

```python
from src.strategy.base import Strategy
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self):
        super().__init__("MY_STRATEGY", {})
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # シグナル生成ロジック
        return signals_df
```

## 参考ドキュメント

- [調査資料](docs/investment-simulation-research.md) - プロジェクト背景、技術検討
- [要件定義](docs/poc-requirements.md) - PoC仕様、受け入れ条件
- [基本設計](docs/poc-design.md) - アーキテクチャ、モジュール設計

## ライセンス

（プロジェクト固有のライセンスを指定してください）

## 貢献

改善提案やバグ報告は、Issue を作成してください。

## 注意事項

### 投資に関する免責事項

本システムは以下の目的で設計されています：

- ✓ 投資戦略の検証・学習
- ✓ バックテストの実施
- ✓ シミュレーション結果の確認

以下の目的には設計されていません：

- ✗ 投資助言・推奨
- ✗ 利益保証
- ✗ 自動売買実行
- ✗ リアルマネーの管理

**実売買を行う場合は、自己の判断と責任において実施してください。**

### 規制上の注意事項

国によって投資・暗号資産に関する規制が異なります。実売買を行う場合は、必ず以下を確認してください：

- 地域の金融規制
- 取引所の利用規約
- 税務上の義務

詳細は各自治体の金融監督機関に問い合わせてください。

---

**最終更新**: 2026-05-11
