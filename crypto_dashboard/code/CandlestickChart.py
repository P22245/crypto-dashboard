import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import requests
from datetime import datetime
from collections import deque
import os

# For candlestick chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

class CandlestickChart: # Panel showing candlestick chart with matplotlib
    def __init__(self, parent, symbol="BTCUSDT"):
        self.parent = parent
        self.symbol = symbol
        self.is_active = False
        self.ws = None
        self.candles = []
        self.current_candle = None
        self.is_visible = True

        # Main frame
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 4), facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')

        # Style the chart
        self.ax.tick_params(colors='#888888')
        self.ax.spines['bottom'].set_color('#444444')
        self.ax.spines['top'].set_color('#444444')
        self.ax.spines['left'].set_color('#444444')
        self.ax.spines['right'].set_color('#444444')

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Volume subplot
        self.ax_volume = self.ax.twinx()
        self.ax_volume.set_facecolor('#1e1e1e')
        self.ax_volume.tick_params(colors='#888888')

    def set_symbol(self, symbol): # Change the symbol being tracked
        was_active = self.is_active
        if was_active:
            self.stop()
        self.symbol = symbol.upper() + "USDT"
        self.candles = []
        self.current_candle = None
        if was_active:
            self.start()

    def show(self): # Show the panel
        self.is_visible = True
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self): # Hide the panel
        self.is_visible = False
        self.frame.pack_forget()

    def start(self): # Start fetching candlestick data
        if self.is_active:
            return
        self.is_active = True

        # Fetch historical data first
        self._fetch_historical()

        # Connect to kline websocket for real-time updates
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@kline_1m"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=lambda ws, err: print(f"Chart error: {err}"),
            on_close=lambda ws, s, m: None,
            on_open=lambda ws: print(f"Chart connected for {self.symbol}")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _fetch_historical(self): # Fetch historical candlestick data
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": self.symbol,
                "interval": "1m",
                "limit": 50
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            self.candles = []
            for candle in data:
                self.candles.append({
                    'time': datetime.fromtimestamp(candle[0] / 1000),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                })

            self.parent.after(0, self._update_chart)
        except Exception as e:
            print(f"Error fetching klines: {e}")

    def _on_message(self, ws, message): # Handle kline updates
        if not self.is_active:
            return

        data = json.loads(message)
        k = data['k']

        candle = {
            'time': datetime.fromtimestamp(k['t'] / 1000),
            'open': float(k['o']),
            'high': float(k['h']),
            'low': float(k['l']),
            'close': float(k['c']),
            'volume': float(k['v']),
            'closed': k['x']
        }

        # Update or add candle
        if self.candles and self.candles[-1]['time'] == candle['time']:
            self.candles[-1] = candle
        else:
            self.candles.append(candle)
            if len(self.candles) > 50:
                self.candles.pop(0)

        self.parent.after(0, self._update_chart)

    def _update_chart(self): # Redraw the candlestick chart
        if not self.is_active or not self.candles:
            return

        self.ax.clear()
        self.ax_volume.clear()

        # Set colors
        self.ax.set_facecolor('#1e1e1e')
        self.ax_volume.set_facecolor('#1e1e1e')

        times = [c['time'] for c in self.candles]
        opens = [c['open'] for c in self.candles]
        highs = [c['high'] for c in self.candles]
        lows = [c['low'] for c in self.candles]
        closes = [c['close'] for c in self.candles]
        volumes = [c['volume'] for c in self.candles]

        # Draw candlesticks
        width = 0.0006  # Width of candlestick

        for i, (t, o, h, l, c, v) in enumerate(zip(times, opens, highs, lows, closes, volumes)):
            color = '#00ff88' if c >= o else '#ff4444'

            # Draw wick
            self.ax.plot([t, t], [l, h], color=color, linewidth=1)

            # Draw body
            body_low = min(o, c)
            body_high = max(o, c)
            body_height = body_high - body_low
            if body_height == 0:
                body_height = 0.01

            rect = plt.Rectangle((mdates.date2num(t) - width/2, body_low),
                                  width, body_height,
                                  facecolor=color, edgecolor=color)
            self.ax.add_patch(rect)

            # Draw volume bar
            vol_color = '#00ff8844' if c >= o else '#ff444444'
            self.ax_volume.bar(t, v, width=0.0004, color=vol_color, alpha=0.5)

        # Style axes
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.tick_params(colors='#888888', labelsize=8)
        self.ax_volume.tick_params(colors='#888888', labelsize=8)

        for spine in self.ax.spines.values():
            spine.set_color('#444444')
        for spine in self.ax_volume.spines.values():
            spine.set_color('#444444')

        # Add current price line
        if closes:
            current_price = closes[-1]
            self.ax.axhline(y=current_price, color='#ffaa00', linestyle='--',
                           linewidth=1, alpha=0.7)
            self.ax.text(times[-1], current_price, f' ${current_price:,.2f}',
                        color='#ffaa00', fontsize=8, va='center')

        # Set title
        self.ax.set_title(f'{self.symbol} 1m Chart', color='#ffffff', fontsize=10)

        # Adjust volume axis
        self.ax_volume.set_ylim(0, max(volumes) * 4 if volumes else 1)
        self.ax_volume.set_ylabel('Volume', color='#888888', fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw()

    def stop(self): # Stop WebSocket connection
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)