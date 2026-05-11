"""売買戦略の基底クラス"""

import pandas as pd
from abc import ABC, abstractmethod
from src.logger import get_logger

log = get_logger("strategy.base")

class Strategy(ABC):
    """すべての戦略の基底クラス"""
    
    def __init__(self, name: str, params: dict = None):
        """初期化
        
        Args:
            name: 戦略名
            params: パラメータ辞書
        """
        self.name = name
        self.params = params or {}
        log.info(f"Initialized strategy: {name}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """売買シグナルを生成
        
        Args:
            data: OHLCV + 指標 DataFrame
            
        Returns:
            シグナル情報DataFrame
            必要な列:
              - timestamp (index)
              - signal: "BUY", "SELL", "HOLD"
              - price: シグナル時点の価格
              - reason: シグナルの理由（JSON文字列）
        """
        pass
    
    def get_info(self) -> dict:
        """戦略情報を取得
        
        Returns:
            {name, params} 辞書
        """
        return {
            "name": self.name,
            "params": self.params,
        }