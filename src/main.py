"""BTC Backtest PoC - メインエントリーポイント"""

import sys
import os
from pathlib import Path

# パスを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src import config
from src.logger import get_logger
from src.data import DataLoader, DataCleaner, DataRepository
from src.indicators import IndicatorCollection, SMA
from src.strategy import SMACrossoverStrategy
from src.backtest import BacktestEngine, MetricsCalculator
from src.ui import ConsoleFormatter, SafetyMessages

log = get_logger("main")

def generate_sample_data(days: int = 365, start_price: float = 40000) -> pd.DataFrame:
    """サンプルデータを生成（デモ用）
    
    Args:
        days: 日数
        start_price: 開始価格
        
    Returns:
        OHLCV DataFrame
    """
    log.info(f"Generating sample data: {days} days, start_price=${start_price:,.2f}")
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='1D')
    data = []
    
    price = start_price
    for date in dates:
        # ランダムな価格変動
        change = np.random.normal(0.002, 0.03)  # 平均+0.2%, 標準偏差3%
        price = price * (1 + change)
        
        o = price * (1 + np.random.uniform(-0.01, 0.01))
        h = max(price, o) * (1 + np.random.uniform(0, 0.02))
        l = min(price, o) * (1 - np.random.uniform(0, 0.02))
        c = price
        v = np.random.uniform(1000, 5000)  # ボリューム
        
        data.append({
            'timestamp': date,
            'open': o,
            'high': h,
            'low': l,
            'close': c,
            'volume': v,
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    log.info(f"Generated {len(df)} candles: ${df['close'].min():,.2f} - ${df['close'].max():,.2f}")
    
    return df

def main():
    """メイン処理"""
    
    # 1. 安全免責事項を表示
    print(SafetyMessages.get_disclaimer())
    input("Press Enter to continue...")
    
    # 2. 設定表示
    config.print_config()
    
    ConsoleFormatter.print_section("STEP 1: Data Loading")
    
    # 3. サンプルデータを生成または読み込む
    try:
        loader = DataLoader()
        sample_data_path = config.SAMPLE_DATA_DIR / "sample_btc_daily.csv"
        
        if sample_data_path.exists():
            log.info(f"Loading existing sample data: {sample_data_path}")
            data = loader.load_csv(str(sample_data_path))
        else:
            log.info("Generating new sample data")
            data = generate_sample_data(days=365)
            # サンプルデータを保存
            data.to_csv(sample_data_path)
            log.info(f"Sample data saved to {sample_data_path}")
    
    except Exception as e:
        log.error(f"Failed to load data: {e}")
        return 1
    
    # 4. データ品質チェック
    ConsoleFormatter.print_section("STEP 2: Data Validation")