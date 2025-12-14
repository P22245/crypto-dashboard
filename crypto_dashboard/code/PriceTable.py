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

class PriceTable: # Panel showing price statistics table
    def __init__(self, parent, symbol="BTCUSDT"):
        self.parent = parent
        self.symbol = symbol
        self.is_active = False
        self.ws = None
        self.is_visible = True

        # Main frame
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        # Title
        tk.Label(
            self.frame,
            text="24h Statistics",
            font=("Segoe UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Stats grid
        stats_frame = tk.Frame(self.frame, bg="#1e1e1e")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create stat rows
        self.stats = {}
        stats_config = [
            ("24h High", "high"),
            ("24h Low", "low"),
            ("24h Volume", "volume"),
            ("24h Change", "change"),
            ("Open Price", "open"),
            ("Last Price", "last")
        ]

        for i, (label, key) in enumerate(stats_config):
            row = tk.Frame(stats_frame, bg="#1e1e1e")
            row.pack(fill=tk.X, pady=2)

            tk.Label(row, text=label, font=("Segoe UI", 9),
                    bg="#1e1e1e", fg="#888888", width=12, anchor="w").pack(side=tk.LEFT)

            value_label = tk.Label(row, text="--", font=("Consolas", 9),
                                   bg="#1e1e1e", fg="#ffffff", anchor="e")
            value_label.pack(side=tk.RIGHT)

            self.stats[key] = value_label

    def set_symbol(self, symbol): # Change the symbol being tracked
        was_active = self.is_active
        if was_active:
            self.stop()
        self.symbol = symbol.upper() + "/USDT"
        if was_active:
            self.start()

    def show(self): # Show the panel
        self.is_visible = True
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self): # Hide the panel
        self.is_visible = False
        self.frame.pack_forget()

    def start(self): # Start WebSocket for ticker updates
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@ticker"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=lambda ws, err: print(f"Stats error: {err}"),
            on_close=lambda ws, s, m: None,
            on_open=lambda ws: print(f"Stats connected for {self.symbol}")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _on_message(self, ws, message): # Handle ticker updates
        if not self.is_active:
            return

        data = json.loads(message)
        self.parent.after(0, self._update_display, data)

    def _update_display(self, data): # Update the stats display
        if not self.is_active:
            return

        high = float(data['h'])
        low = float(data['l'])
        volume = float(data['v'])
        change = float(data['p'])
        change_pct = float(data['P'])
        open_price = float(data['o'])
        last = float(data['c'])

        self.stats['high'].config(text=f"${high:,.2f}")
        self.stats['low'].config(text=f"${low:,.2f}")
        self.stats['volume'].config(text=f"{volume:,.2f}")

        change_color = "#00ff88" if change >= 0 else "#ff4444"
        sign = "+" if change >= 0 else ""
        self.stats['change'].config(
            text=f"{sign}${change:,.2f} ({sign}{change_pct:.2f}%)",
            fg=change_color
        )

        self.stats['open'].config(text=f"${open_price:,.2f}")
        self.stats['last'].config(text=f"${last:,.2f}")

    def stop(self): # Stop WebSocket connection
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)