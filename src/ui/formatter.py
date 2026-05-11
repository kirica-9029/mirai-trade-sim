"""コンソール出力フォーマッター"""

import pandas as pd
from typing import Dict, List

class ConsoleFormatter:
    """コンソール出力をフォーマット"""
    
    @staticmethod
    def print_section(title: str):
        """セクションタイトルを表示"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    @staticmethod
    def print_metrics(metrics: Dict, signals_summary: Dict = None):
        """指標をテーブル形式で表示
        
        Args:
            metrics: 指標辞書
            signals_summary: シグナル要約 (buy_count, sell_count, hold_count)
        """
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        
        # カテゴリ別に表示
        categories = {
            "Capital": ["initial_capital", "final_value", "realized_pnl", "total_return_pct"],
            "Trades": ["total_trades", "buy_count", "sell_count", "round_trips"],
            "Performance": ["win_count", "loss_count", "win_rate", "avg_win", "avg_loss"],
            "Risk": ["max_drawdown_pct", "max_loss", "profit_factor"],
        }
        
        for category, keys in categories.items():
            print(f"\n{category}:")
            for key in keys:
                if key in metrics:
                    value = metrics[key]
                    
                    # フォーマット
                    if "pct" in key:
                        formatted = f"{value:.2f}%"
                    elif "$" in key or "capital" in key or "pnl" in key or "win" in key or "loss" in key:
                        formatted = f"${value:,.2f}"
                    elif isinstance(value, float):
                        formatted = f"{value:.4f}"
                    else:
                        formatted = str(value)
                    
                    # キーをきれいにする
                    display_key = key.replace("_", " ").title()
                    print(f"  {display_key:<25} {formatted:>15}")
        
        # シグナル要約
        if signals_summary:
            print(f"\nSignals:")
            print(f"  Buy Signals:<25 {signals_summary.get('buy', 0):>15}")
            print(f"  Sell Signals:<25 {signals_summary.get('sell', 0):>15}")
            print(f"  Hold Signals:<25 {signals_summary.get('hold', 0):>15}")
        
        print("\n" + "=" * 50)
    
    @staticmethod
    def print_trades(trades: List[Dict], limit: int = 20):
        """取引履歴を表示
        
        Args:
            trades: 取引リスト
            limit: 表示する最大行数
        """
        if not trades:
            print("\nNo trades")
            return
        
        print(f"\nTrades ({len(trades)} total, showing {min(limit, len(trades))}):")
        print("-" * 90)
        print(f"{'#':<5} {'Timestamp':<20} {'Side':<6} {'Price':<12} {'Size':<12} {'Fee':<10}")
        print("-" * 90)
        
        for i, trade in enumerate(trades[:limit]):
            timestamp = str(trade.get('timestamp', '')).split('+')[0][:19]
            side = trade.get('side', '?')
            price = trade.get('price', 0)
            size = trade.get('size', 0)
            fee = trade.get('fee', 0)
            
            print(f"{i+1:<5} {timestamp:<20} {side:<6} ${price:<11,.2f} {size:<12.6f} ${fee:<9,.2f}")
        
        if len(trades) > limit:
            print(f"... and {len(trades) - limit} more trades")
        
        print("-" * 90)
    
    @staticmethod
    def print_summary(summary: Dict):
        """概要を表示"""
        print("\nSummary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")