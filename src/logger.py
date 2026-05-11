"""ログ設定"""

import logging
import logging.handlers
from pathlib import Path
from src.config import LOG_LEVEL, LOG_FILE

# ログファイルディレクトリを作成
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

# ロガーを作成
logger = logging.getLogger("btc_backtest")
logger.setLevel(LOG_LEVEL)

# フォーマッター
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ファイルハンドラ
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# コンソールハンドラ
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_logger(name: str = None) -> logging.Logger:
    """ロガーを取得"""
    if name:
        return logging.getLogger(f"btc_backtest.{name}")
    return logger

if __name__ == "__main__":
    log = get_logger()
    log.info("Logger initialized")