import plotly.graph_objects as go
import pandas as pd
import os
import uuid

class ChartEngine:
    def __init__(self):
        self.output_dir = "temp_charts"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_signal_chart(self, df: pd.DataFrame, signal_data: dict):
        """
        Generates a candlestick chart with Entry, SL, and TP levels marked.
        """
        symbol = signal_data['symbol']
        
        # Create Candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])

        # Add Entry, SL, TP Lines
        fig.add_hline(y=signal_data['entry'], line_dash="dash", line_color="white", annotation_text="ENTRY")
        fig.add_hline(y=signal_data['stop_loss'], line_dash="dash", line_color="red", annotation_text="SL")
        fig.add_hline(y=signal_data['take_profit_1'], line_dash="dash", line_color="green", annotation_text="TP1")

        # Layout Adjustments
        fig.update_layout(
            title=f"{symbol} {signal_data['direction']} Signal",
            yaxis_title="Price",
            template="plotly_dark",
            showlegend=False,
            xaxis_rangeslider_visible=False
        )

        # Save to file
        filename = f"{self.output_dir}/{uuid.uuid4()}.png"
        fig.write_image(filename)
        return filename

chart_engine = ChartEngine()
