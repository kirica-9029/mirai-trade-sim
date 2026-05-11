"""データ品質チェック"""

import pandas as pd
from typing import List, Tuple
from src.logger import get_logger

log = get_logger("data.cleaner")

class DataCleaner:
    """OHLCV データの品質チェック"""
    
    REQUIRED_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
    
    @classmethod
    def validate_columns(cls, data: pd.DataFrame) -> bool:
        """必要な列が揃っているか確認"""
        missing = [col for col in cls.REQUIRED_COLUMNS if col not in data.columns]
        
        if missing:
            log.error(f"Missing columns: {missing}")
            return False
        
        log.debug(f"Columns OK: {list(data.columns)}")
        return True
    
    @classmethod
    def check_missing(cls, data: pd.DataFrame) -> Tuple[bool, List[int]]:
        """NaN値を検出
        
        Returns:
            (all_ok, missing_row_indices)
        """
        missing_mask = data[cls.REQUIRED_COLUMNS].isna().any(axis=1)
        missing_indices = data[missing_mask].index.tolist()
        
        if len(missing_indices) > 0:
            log.warning(f"Found {len(missing_indices)} rows with missing values: {missing_indices[:5]}...")
            return False, missing_indices
        
        log.debug("No missing values")
        return True, []
    
    @classmethod
    def check_duplicates(cls, data: pd.DataFrame) -> Tuple[bool, List[int]]:
        """重複するタイムスタンプを検出
        
        Returns:
            (all_ok, duplicate_indices)
        """
        if data.index.has_duplicates:
            dup_mask = data.index.duplicated(keep=False)
            dup_indices = data[dup_mask].index.tolist()
            log.warning(f"Found {len(dup_indices)} duplicate timestamps")
            return False, dup_indices
        
        log.debug("No duplicate timestamps")
        return True, []
    
    @classmethod
    def validate_ohlc_relations(cls, data: pd.DataFrame) -> bool:
        """OHLC関係をチェック: O < H, L < H, L < C など
        
        Returns:
            True if all valid, False otherwise
        """
        invalid_rows = []
        
        for idx, row in data.iterrows():
            o, h, l, c = row['open'], row['high'], row['low'], row['close']
            
            # High >= Open, Close
            if not (h >= o and h >= c):
                invalid_rows.append((idx, f"High({h}) < Open({o}) or Close({c})"))
            
            # Low <= Open, Close
            if not (l <= o and l <= c):
                invalid_rows.append((idx, f"Low({l}) > Open({o}) or Close({c})"))
        
        if invalid_rows:
            log.error(f"Found {len(invalid_rows)} invalid OHLC relations:")
            for idx, msg in invalid_rows[:5]:
                log.error(f"  {idx}: {msg}")
            return False
        
        log.debug("OHLC relations valid")
        return True
    
    @classmethod
    def check_volume(cls, data: pd.DataFrame) -> Tuple[bool, List[int]]:
        """出来高が0以上か確認
        
        Returns:
            (all_ok, zero_volume_indices)
        """
        zero_volume = data[data['volume'] <= 0].index.tolist()
        
        if len(zero_volume) > 0:
            log.warning(f"Found {len(zero_volume)} rows with zero or negative volume")
            return False, zero_volume
        
        log.debug("Volume check passed")
        return True, []
    
    @classmethod
    def validate_all(cls, data: pd.DataFrame) -> Tuple[bool, dict]:
        """すべての検証を実行
        
        Args:
            data: 検証するDataFrame
            
        Returns:
            (all_ok, details_dict)
        """
        details = {}
        all_ok = True
        
        # 列チェック
        if not cls.validate_columns(data):
            all_ok = False
            details['columns'] = 'Missing required columns'
        
        # 欠損値チェック
        ok, indices = cls.check_missing(data)
        if not ok:
            all_ok = False
            details['missing'] = f"{len(indices)} rows with missing values"
        
        # 重複チェック
        ok, indices = cls.check_duplicates(data)
        if not ok:
            all_ok = False
            details['duplicates'] = f"{len(indices)} duplicate timestamps"
        
        # OHLC関係チェック
        if not cls.validate_ohlc_relations(data):
            all_ok = False
            details['ohlc'] = 'Invalid OHLC relations found'
        
        # 出来高チェック
        ok, indices = cls.check_volume(data)
        if not ok:
            all_ok = False
            details['volume'] = f"{len(indices)} rows with invalid volume"
        
        return all_ok, details