"""設定管理"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルを読み込み
load_dotenv()

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent

# ========== Data Source ==========
DATA_SOURCE = os.getenv("DATA_SOURCE", "local")  # binance, ccxt, local

# ========== Binance API（読み取り専用のみ） ==========
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_BASE_URL = "https://api.binance.com"

# ========== Database ==========
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "data" / "backtest.db"))

# ========== Logging ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(PROJECT_ROOT / "logs" / "backtest.log"))

# ========== Backtest Parameters ==========
BACKTEST_INITIAL_CAPITAL = float(os.getenv("BACKTEST_INITIAL_CAPITAL", "10000"))
BACKTEST_FEE_RATE = float(os.getenv("BACKTEST_FEE_RATE", "0.001"))  # 0.1%
BACKTEST_SLIPPAGE_RATE = float(os.getenv("BACKTEST_SLIPPAGE_RATE", "0.0005"))  # 0.05%

# ========== Output Directory ==========
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(PROJECT_ROOT / "outputs")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# サブディレクトリ
BACKTEST_RESULTS_DIR = OUTPUT_DIR / "backtest_results"
TRADE_LOGS_DIR = OUTPUT_DIR / "trade_logs"
REPORTS_DIR = OUTPUT_DIR / "reports"
MIROFISH_INPUTS_DIR = OUTPUT_DIR / "mirofish_inputs"
MIROFISH_OUTPUTS_DIR = OUTPUT_DIR / "mirofish_outputs"

for d in [BACKTEST_RESULTS_DIR, TRADE_LOGS_DIR, REPORTS_DIR, MIROFISH_INPUTS_DIR, MIROFISH_OUTPUTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ========== Data Directory ==========
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_DATA_DIR = DATA_DIR / "samples"
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ========== MiroFish（将来）==========
MIROFISH_ENABLED = os.getenv("MIROFISH_ENABLED", "false").lower() == "true"
MIROFISH_CLI_PATH = os.getenv("MIROFISH_CLI_PATH", "mirofish")
MIROFISH_API_URL = os.getenv("MIROFISH_API_URL", "http://localhost:5001")

# ========== 安全制約（固定） ==========
# 実売買APIキーは絶対に使用しない
TRADING_ENABLED = False
REAL_TRADING_API_KEY = None  # 常に None

# ========== テンプレートメッセージ ==========
DISCLAIMER = """
⚠️  免責事項 ⚠️

このツールはシミュレーション・検証用です。

- 過去データ上の結果であり、将来の成績を保証しません
- 実売買の判断の参考として使用してください
- すべての投資判断は自己責任でお願いします
- 損失を被る可能性があります
"""

def print_config():
    """設定情報を出力（デバッグ用）"""
    print("=" * 50)
    print("BTC Backtest PoC - Configuration")
    print("=" * 50)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Source: {DATA_SOURCE}")
    print(f"DB Type: {DB_TYPE}")
    print(f"DB Path: {DB_PATH}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Output Dir: {OUTPUT_DIR}")
    print(f"Initial Capital: ${BACKTEST_INITIAL_CAPITAL:,.2f}")
    print(f"Fee Rate: {BACKTEST_FEE_RATE * 100:.2f}%")
    print(f"Slippage Rate: {BACKTEST_SLIPPAGE_RATE * 100:.2f}%")
    print("=" * 50)

if __name__ == "__main__":
    print_config()