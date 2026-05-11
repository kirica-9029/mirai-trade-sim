"""SMA クロスオーバー戦略"""

import pandas as pd
import json
from .base import Strategy
from src.logger import get_logger

log = get_logger("strategy.sma_crossover")

class SMACrossoverStrategy(Strategy):
    """SMA短期・長期のゴールデンクロス・デッドクロス戦略"""
    
    def __init__(self, sma_short: int = 9, sma_long: int = 21):
        """初期化
        
        Args:
            sma_short: 短期SMA期間
            sma_long: 長期SMA期間
        """
        super().__init__("SMA_CROSSOVER", {
            "sma_short": sma_short,
            "sma_long": sma_long,
        })
        self.sma_short = sma_short
        self.sma_long = sma_long
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """SMAクロスシグナルを生成
        
        ロジック:
        1. SMA短期, SMA長期を取得
        2. 前足と現足を比較
        3. ゴールデンクロス(短期 > 長期) → BUY
        4. デッドクロス(短期 < 長期) → SELL
        5. 継続中 → HOLD
        
        Args:
            data: OHLCV + 指標 DataFrame
                  必須列: close, SMA_{sma_short}, SMA_{sma_long}
            
        Returns:
            シグナルDataFrame
        """
        col_short = f"SMA_{self.sma_short}"
        col_long = f"SMA_{self.sma_long}"
        
        # 必要な列の確認
        if col_short not in data.columns or col_long not in data.columns:
            log.error(f"Missing indicator columns: {col_short}, {col_long}")
            return pd.DataFrame()
        
        sma_short = data[col_short]
        sma_long = data[col_long]
        
        # 前足の値を取得
        prev_short = sma_short.shift(1)
        prev_long = sma_long.shift(1)
        
        # クロスを判定
        golden_cross = (prev_short <= prev_long) & (sma_short > sma_long)
        dead_cross = (prev_short >= prev_long) & (sma_short < sma_long)
        
        signals = []
        
        for i, row in data.iterrows():
            if pd.isna(sma_short[i]) or pd.isna(sma_long[i]):
                # 指標計算期間中はスキップ
                continue
            
            close_price = row['close']
            
            if golden_cross[i]:
                signal = "BUY"
                reason = f"Golden Cross: SMA{self.sma_short}({sma_short[i]:.2f}) > SMA{self.sma_long}({sma_long[i]:.2f})"
            elif dead_cross[i]:
                signal = "SELL"
                reason = f"Dead Cross: SMA{self.sma_short}({sma_short[i]:.2f}) < SMA{self.sma_long}({sma_long[i]:.2f})"
            else:
                signal = "HOLD"
                reason = f"No crossover: SMA{self.sma_short}({sma_short[i]:.2f}) vs SMA{self.sma_long}({sma_long[i]:.2f})"
            
            signals.append({
                "timestamp": i,
                "signal": signal,
                "price": close_price,
                "reason": reason,
                "sma_short": sma_short[i],
                "sma_long": sma_long[i],
            })
        
        result = pd.DataFrame(signals)
        if not result.empty:
            result.set_index('timestamp', inplace=True)
        
        log.info(f"Generated {len(signals)} signals")
        return result