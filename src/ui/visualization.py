"""結果可視化モジュール"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List
from pathlib import Path
from src import config
from src.logger import get_logger

log = get_logger("ui.visualization")

class ResultVisualizer:
    """バックテスト結果の可視化"""
    
    @staticmethod
    def create_price_chart(data: pd.DataFrame, title: str = "BTC Price and Indicators") -> go.Figure:
        """価格と指標のチャートを作成
        
        Args:
            data: OHLCV + 指標 DataFrame
            title: チャートタイトル
            
        Returns:
            Plotly Figure
        """
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price and Moving Averages', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # 価格とSMA
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='BTC Price'
            ),
            row=1, col=1
        )
        
        # SMAを追加
        sma_cols = [col for col in data.columns if col.startswith('SMA_')]
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, col in enumerate(sma_cols):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=1)
                ),
                row=1, col=1
            )
        
        # ボリューム
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='Volume',
                marker_color='rgba(158,158,158,0.8)'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_equity_curve_chart(equity_curve: List[float], trades: List[Dict], title: str = "Equity Curve") -> go.Figure:
        """資産推移チャートを作成
        
        Args:
            equity_curve: 資産推移リスト
            trades: 取引リスト
            title: チャートタイトル
            
        Returns:
            Plotly Figure
        """
        fig = go.Figure()
        
        # 資産曲線
        fig.add_trace(
            go.Scatter(
                x=list(range(len(equity_curve))),
                y=equity_curve,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            )
        )
        
        # 取引ポイント
        buy_points = []
        sell_points = []
        
        for i, trade in enumerate(trades):
            if trade.get('side') == 'BUY':
                buy_points.append((i, equity_curve[i]))
            elif trade.get('side') == 'SELL':
                sell_points.append((i, equity_curve[i]))
        
        if buy_points:
            x_buy, y_buy = zip(*buy_points)
            fig.add_trace(
                go.Scatter(
                    x=x_buy,
                    y=y_buy,
                    mode='markers',
                    name='Buy',
                    marker=dict(color='green', size=8, symbol='triangle-up')
                )
            )
        
        if sell_points:
            x_sell, y_sell = zip(*sell_points)
            fig.add_trace(
                go.Scatter(
                    x=x_sell,
                    y=y_sell,
                    mode='markers',
                    name='Sell',
                    marker=dict(color='red', size=8, symbol='triangle-down')
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title="Trade Number",
            yaxis_title="Equity (USD)",
            height=400
        )
        
        return fig
    
    @staticmethod
    def save_charts(data: pd.DataFrame, result: dict, output_dir: Path = None):
        """チャートを保存
        
        Args:
            data: OHLCV + 指標 DataFrame
            result: バックテスト結果
            output_dir: 出力ディレクトリ
        """
        if output_dir is None:
            output_dir = config.REPORTS_DIR
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 価格チャート
            price_chart = ResultVisualizer.create_price_chart(data)
            price_chart.write_html(str(output_dir / "price_chart.html"))
            log.info(f"Price chart saved to {output_dir / 'price_chart.html'}")
            
            # 資産曲線チャート
            equity_chart = ResultVisualizer.create_equity_curve_chart(
                result['equity_curve'],
                result['trades']
            )
            equity_chart.write_html(str(output_dir / "equity_curve.html"))
            log.info(f"Equity curve saved to {output_dir / 'equity_curve.html'}")
            
        except Exception as e:
            log.error(f"Failed to save charts: {e}")
    
    @staticmethod
    def export_to_csv(data: pd.DataFrame, result: dict, output_dir: Path = None):
        """結果をCSVでエクスポート
        
        Args:
            data: OHLCV + 指標 + シグナル DataFrame
            result: バックテスト結果
            output_dir: 出力ディレクトリ
        """
        if output_dir is None:
            output_dir = config.REPORTS_DIR
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # データとシグナル
            data.to_csv(output_dir / "backtest_data.csv")
            
            # 取引履歴
            trades_df = pd.DataFrame(result['trades'])
            trades_df.to_csv(output_dir / "trades.csv", index=False)
            
            # 指標
            metrics_df = pd.DataFrame([result['metrics']])
            metrics_df.to_csv(output_dir / "metrics.csv", index=False)
            
            log.info(f"CSV files exported to {output_dir}")
            
        except Exception as e:
            log.error(f"Failed to export CSV: {e}")