"""テクニカル指標の基底クラス"""

import pandas as pd
import hashlib
from abc import ABC, abstractmethod
from src.logger import get_logger

log = get_logger("indicators.base")

class Indicator(ABC):
    """すべての指標の基底クラス"""
    
    def __init__(self, name: str, params: dict = None):
        """初期化
        
        Args:
            name: 指標名
            params: パラメータ辞書
        """
        self.name = name
        self.params = params or {}
        
        # パラメータハッシュを生成（同じパラメータかどうかを判定するため）
        params_str = str(sorted(self.params.items()))
        self.params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        log.debug(f"Initialized indicator: {name}, params={params}, hash={self.params_hash}")
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """指標値を計算
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            計算した指標値Series
        """
        pass
    
    def validate_input(self, data: pd.DataFrame) -> bool:
        """入力データの検証
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            検証結果
        """
        if data is None or len(data) == 0: