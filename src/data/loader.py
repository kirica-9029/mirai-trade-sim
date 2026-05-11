"""価格データの読み込み"""

import pandas as pd
from pathlib import Path
from typing import Optional
from src.logger import get_logger

log = get_logger("data.loader")

class DataLoader:
    """CSVやParquetからOHLCVデータを読み込む"""
    
    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """CSVファイルからOHLCVデータを読み込む
        
        Args:
            filepath: CSVファイルパス
            
        Returns:
            OHLCV DataFrame
            
        Expected columns: timestamp, open, high, low, close, volume
        """
        log.info(f"Loading CSV: {filepath}")
        
        df = pd.read_csv(filepath)
        
        # タイムスタンプをインデックスに設定
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        log.info(f"Loaded {len(df)} rows from {filepath}")
        return df
    
    @staticmethod
    def load_parquet(filepath: str) -> pd.DataFrame:
        """Parquetファイルからデータを読み込む
        
        Args:
            filepath: Parquetファイルパス
            
        Returns:
            OHLCV DataFrame
        """
        log.info(f"Loading Parquet: {filepath}")
        
        df = pd.read_parquet(filepath)
        log.info(f"Loaded {len(df)} rows from {filepath}")
        return df
    
    @staticmethod
    def load_json(filepath: str) -> pd.DataFrame:
        """JSONファイルから(Orient='records')データを読み込む
        
        Args:
            filepath: JSONファイルパス
            
        Returns:
            OHLCV DataFrame
        """
        log.info(f"Loading JSON: {filepath}")
        
        df = pd.read_json(filepath, orient='records')
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        log.info(f"Loaded {len(df)} rows from {filepath}")
        return df