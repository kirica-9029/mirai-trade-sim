"""BTC Backtest PoC - メインエントリーポイント"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple

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

def load_or_generate_data() -> Tuple[pd.DataFrame, bool]:
    """データを読み込みまたは生成
    
    Returns:
        (data, is_generated): データと生成フラグ
    """
    try:
        loader = DataLoader()
        sample_data_path = config.SAMPLE_DATA_DIR / "sample_btc_daily.csv"
        
        if sample_data_path.exists():
            log.info(f"Loading existing sample data: {sample_data_path}")
            data = loader.load_csv(str(sample_data_path))
            return data, False
        else:
            log.info("Generating new sample data")
            data = generate_sample_data(days=365)
            # サンプルデータを保存
            data.to_csv(sample_data_path)
            log.info(f"Sample data saved to {sample_data_path}")
            return data, True
    
    except Exception as e:
        log.error(f"Failed to load/generate data: {e}")
        raise

def validate_data(data: pd.DataFrame) -> None:
    """データ品質チェック
    
    Args:
        data: 検証するDataFrame
        
    Raises:
        ValueError: 検証失敗時
    """
    cleaner = DataCleaner()
    is_valid, details = cleaner.validate_all(data)
    
    if not is_valid:
        log.error("Data validation failed")
        raise ValueError("Data validation failed")
    
    print("✓ Data validation passed")
    print(f"  Rows: {len(data)}")
    print(f"  Columns: {list(data.columns)}")
    print(f"  Date range: {data.index[0]} to {data.index[-1]}")

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """テクニカル指標を計算
    
    Args:
        data: OHLCV DataFrame
        
    Returns:
        指標追加済みDataFrame
    """
    indicators = IndicatorCollection()
    indicators.add_indicator("SMA_9", SMA(9))
    indicators.add_indicator("SMA_21", SMA(21))
    
    data_with_indicators = indicators.calculate_all(data)
    log.info(f"Calculated indicators, new columns: {[c for c in data_with_indicators.columns if 'SMA' in c]}")
    
    return data_with_indicators

def generate_signals(data: pd.DataFrame) -> pd.DataFrame:
    """売買シグナルを生成
    
    Args:
        data: 指標付きDataFrame
        
    Returns:
        シグナル付きDataFrame
        
    Raises:
        ValueError: シグナル生成失敗時
    """
    strategy = SMACrossoverStrategy(sma_short=9, sma_long=21)
    signals = strategy.generate_signals(data)
    
    if signals.empty:
        log.error("No signals generated")
        raise ValueError("No signals generated")
    
    # シグナルをデータに追加
    data_with_signals = data.join(signals[['signal', 'reason']], how='left')
    data_with_signals['signal'].fillna('HOLD', inplace=True)
    data_with_signals['reason'].fillna('No signal', inplace=True)
    
    buy_signals = len(data_with_signals[data_with_signals['signal'] == 'BUY'])
    sell_signals = len(data_with_signals[data_with_signals['signal'] == 'SELL'])
    log.info(f"Generated signals: {buy_signals} BUY, {sell_signals} SELL")
    
    return data_with_signals

def run_backtest(data: pd.DataFrame) -> dict:
    """バックテストを実行
    
    Args:
        data: シグナル付きDataFrame
        
    Returns:
        バックテスト結果
    """
    strategy = SMACrossoverStrategy(sma_short=9, sma_long=21)
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=config.BACKTEST_INITIAL_CAPITAL,
        fee_rate=config.BACKTEST_FEE_RATE,
        slippage_rate=config.BACKTEST_SLIPPAGE_RATE,
    )
    
    result = engine.run(data)
    return result

def save_results(data: pd.DataFrame, result: dict, strategy) -> Path:
    """結果を保存
    
    Args:
        data: バックテストデータ
        result: バックテスト結果
        strategy: 戦略インスタンス
        
    Returns:
        保存ファイルパス
    """
    import json
    from src.ui import ResultVisualizer
    
    result_file = config.BACKTEST_RESULTS_DIR / f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    result_to_save = {
        'strategy': strategy.get_info(),
        'metrics': result['metrics'],
        'trades': result['trades'],
        'timestamp': datetime.now().isoformat(),
    }
    
    with open(result_file, 'w') as f:
        json.dump(result_to_save, f, indent=2, default=str)
    
    log.info(f"Results saved to {result_file}")
    
    # 可視化
    try:
        ResultVisualizer.save_charts(data, result)
        ResultVisualizer.export_to_csv(data, result)
        log.info("Charts and CSV exported")
    except Exception as e:
        log.error(f"Failed to create visualizations: {e}")
    
    return result_file

def main() -> int:
    """メイン処理
    
    Returns:
        終了コード (0: 成功, 1: エラー)
    """
    
    # 1. 安全免責事項を表示
    print(SafetyMessages.get_disclaimer())
    input("Press Enter to continue...")
    
    # 2. 設定表示
    config.print_config()
    
    try:
        # 3. データ読み込み/生成
        ConsoleFormatter.print_section("STEP 1: Data Loading")
        data, is_generated = load_or_generate_data()
        
        # 4. データ品質チェック
        ConsoleFormatter.print_section("STEP 2: Data Validation")
        validate_data(data)
        
        # 5. 指標計算
        ConsoleFormatter.print_section("STEP 3: Indicator Calculation")
        data = calculate_indicators(data)
        
        # 6. 戦略シグナル生成
        ConsoleFormatter.print_section("STEP 4: Signal Generation")
        data = generate_signals(data)
        
        # 7. バックテスト実行
        ConsoleFormatter.print_section("STEP 5: Backtest Execution")
        result = run_backtest(data)
        
        # 8. 結果表示
        ConsoleFormatter.print_section("STEP 6: Results")
        metrics = result['metrics']
        
        # シグナル要約を計算
        signals_summary = {
            'buy': len(data[data['signal'] == 'BUY']),
            'sell': len(data[data['signal'] == 'SELL']),
            'hold': len(data[data['signal'] == 'HOLD']),
        }
        
        ConsoleFormatter.print_metrics(metrics, signals_summary)
        ConsoleFormatter.print_trades(result['trades'], limit=10)
        
        # 9. 結果保存
        ConsoleFormatter.print_section("STEP 7: Saving Results")
        strategy = SMACrossoverStrategy(sma_short=9, sma_long=21)
        result_file = save_results(data, result, strategy)
        
        # 10. 免責事項を再度表示
        ConsoleFormatter.print_section("IMPORTANT NOTICE")
        print(SafetyMessages.get_simulation_notice())
        
        print("\n✓ Backtest completed successfully!")
        print(f"Output directory: {config.OUTPUT_DIR}")
        print(f"Report file: {result_file}")
        
        return 0
        
    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nBacktest interrupted by user")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)