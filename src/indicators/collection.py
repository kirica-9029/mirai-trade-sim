"""複数指標の一括計算"""

import pandas as pd
from .base import Indicator
from src.logger import get_logger

log = get_logger("indicators.collection")

class IndicatorCollection:
    """複数の指標を管理・計算"""
    
    def __init__(self):
        """初期化"""
        self.indicators = {}
    
    def add_indicator(self, name: str, indicator: Indicator) -> None:
        """指標を追加
        
        Args:
            name: 指標キー（列名に使用）
            indicator: Indicator インスタンス
        """
        self.indicators[name] = indicator
        log.debug(f"Added indicator: {name} = {indicator.get_name_with_params()}")
    
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """すべての指標を計算し、DataFrameに追加
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            元のDataFrameに指標列を追加したもの
        """
        result = data.copy()
        
        for name, indicator in self.indicators.items():
            try:
                values = indicator.calculate(result)
                result[name] = values
                log.debug(f"Calculated {name}: {len(values)} values")
            except Exception as e:
                log.error(f"Error calculating {name}: {e}")
                result[name] = float('nan')
        
        log.info(f"Calculated {len(self.indicators)} indicators")
        
        return result
    
    def get_indicator(self, name: str) -> Indicator:
        """指標を取得
        
        Args:
            name: 指標キー
            
        Returns:
            Indicator インスタンス
        """
        return self.indicators.get(name)
    
    def list_indicators(self) -> dict:
        """登録されている指標一覧を取得
        
        Returns:
            {name: indicator} 辞書
        """
        return self.indicators.copy()