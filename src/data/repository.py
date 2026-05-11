"""データリポジトリ（DB保存・読み込み）"""

import pandas as pd
from pathlib import Path
from src.logger import get_logger

log = get_logger("data.repository")

class DataRepository:
    """ローカルDBまたはファイルへのデータ保存・読み込み"""
    
    def __init__(self, db_type: str = "sqlite", db_path: str = None):
        """初期化
        
        Args:
            db_type: "sqlite" または "parquet"
            db_path: DB/ファイルパス
        """
        self.db_type = db_type
        self.db_path = Path(db_path) if db_path else None
        log.info(f"Repository initialized: type={db_type}, path={db_path}")
    
    def save_candles(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
    ) -> int:
        """OHLCVデータを保存
        
        Args:
            symbol: "BTC/USDT"
            timeframe: "1d", "4h"
            data: OHLCV DataFrame
            
        Returns:
            保存した行数
        """
        log.info(f"Saving {len(data)} candles: {symbol} {timeframe}")
        
        if self.db_type == "parquet":
            # Parquetに保存
            filename = f"{symbol.replace('/', '_')}_{timeframe}.parquet"
            filepath = self.db_path.parent / filename if self.db_path else Path(filename)
            data.to_parquet(filepath)
            log.info(f"Saved to {filepath}")
        
        elif self.db_type == "csv":
            # CSVに保存
            filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
            filepath = self.db_path.parent / filename if self.db_path else Path(filename)
            data.to_csv(filepath)
            log.info(f"Saved to {filepath}")
        
        # sqlite はここでは実装スキップ（将来拡張）
        
        return len(data)
    
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
    ) -> pd.DataFrame:
        """保存したOHLCVデータを読み込む
        
        Args:
            symbol: "BTC/USDT"
            timeframe: "1d", "4h"
            
        Returns:
            OHLCV DataFrame
        """
        log.info(f"Loading candles: {symbol} {timeframe}")
        
        if self.db_type == "parquet":
            filename = f"{symbol.replace('/', '_')}_{timeframe}.parquet"
            filepath = self.db_path.parent / filename if self.db_path else Path(filename)
            data = pd.read_parquet(filepath)
        
        elif self.db_type == "csv":
            filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
            filepath = self.db_path.parent / filename if self.db_path else Path(filename)
            data = pd.read_csv(filepath, index_col=0)
            data.index = pd.to_datetime(data.index)
        
        log.info(f"Loaded {len(data)} rows")
        return data