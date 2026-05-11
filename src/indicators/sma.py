"""Simple Moving Average (SMA) 指標"""

import pandas as pd
from .base import Indicator
from src.logger import get_logger

log = get_logger("indicators.sma")

class SMA(Indicator):
    """Simple Moving Average（単純移動平均）"""
    
    def __init__(self, period: int):
        """初期化
        
        Args:
            period: 期間（日数）
        """
        super().__init__("SMA", {"period": period})
        self.period = period
        
        if period < 1:
            raise ValueError("Period must be >= 1")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """SMAを計算
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            SMA Series
        """
        if not self.validate_input(data):
            return pd.Series(index=data.index, dtype=float)
        
        log.debug(f"Calculating SMA({self.period})")
        
        sma = data['close'].rolling(window=self.period).mean()
        
        log.debug(f"SMA({self.period}) calculated: {len(sma)} values")
        
        return sma