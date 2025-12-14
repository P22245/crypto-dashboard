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

class CryptoTicker: # Reusable ticker component for any cryptocurrency
    def __init__(self, parent, symbol, display_name, on_select_callback=None):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None
        self.on_select_callback = on_select_callback
        self.current_price = 0
        self.price_change = 0
        self.price_change_percent = 0
        self.is_selected = False

        # Create UI frame
        self.frame = tk.Frame(parent, bg="#2d2d2d", relief="flat", bd=1)

        # Make entire frame clickable
        self.frame.bind("<Button-1>", self._on_click)

        # Symbol label
        self.symbol_label = tk.Label(
            self.frame,
            text=display_name,
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        self.symbol_label.pack(pady=(8, 2))
        self.symbol_label.bind("<Button-1>", self._on_click)

        # Price label
        self.price_label = tk.Label(
            self.frame,
            text="--,---.--",
            font=("Segoe UI", 16, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        self.price_label.pack(pady=(0, 2))
        self.price_label.bind("<Button-1>", self._on_click)

        # Change label
        self.change_label = tk.Label(
            self.frame,
            text="--",
            font=("Segoe UI", 9),
            bg="#2d2d2d",
            fg="#888888"
        )
        self.change_label.pack(pady=(0, 8))
        self.change_label.bind("<Button-1>", self._on_click)

    def set_selected(self, selected): # Update visual selection state
        self.is_selected = selected
        bg_color = "#3d5c3d" if selected else "#2d2d2d"
        self.frame.config(bg=bg_color)
        self.symbol_label.config(bg=bg_color)
        self.price_label.config(bg=bg_color)
        self.change_label.config(bg=bg_color)

    def _on_click(self, event=None): # Handle click on ticker
        if self.on_select_callback:
            self.on_select_callback(self.symbol.upper().replace("USDT", ""))

    def start(self): # Start WebSocket connection
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"{self.symbol} error: {err}"),
            on_close=lambda ws, s, m: print(f"{self.symbol} closed"),
            on_open=lambda ws: print(f"{self.symbol} connected")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self): # Stop WebSocket connection
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message): # Handle price updates
        if not self.is_active:
            return

        data = json.loads(message)
        self.current_price = float(data['c'])
        self.price_change = float(data['p'])
        self.price_change_percent = float(data['P'])

        # Schedule GUI update on main thread
        self.parent.after(0, self.update_display)

    def update_display(self): # Update the ticker display
        if not self.is_active:
            return

        color = "#00ff88" if self.price_change >= 0 else "#ff4444"

        # Format price based on magnitude
        if self.current_price >= 1000:
            price_text = f"${self.current_price:,.2f}"
        elif self.current_price >= 1:
            price_text = f"${self.current_price:.2f}"
        else:
            price_text = f"${self.current_price:.4f}"

        self.price_label.config(text=price_text, fg=color)

        sign = "+" if self.price_change >= 0 else ""
        change_text = f"{sign}{self.price_change_percent:.2f}%"
        self.change_label.config(text=change_text, fg=color)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def grid_remove(self):
        self.frame.grid_remove()


class OrderBookPanel: # Panel showing order book (bids and asks)
    def __init__(self, parent, symbol="BTCUSDT"):
        self.parent = parent
        self.symbol = symbol
        self.is_active = False
        self.ws = None
        self.is_visible = True

        # Main frame
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        # Title
        title_frame = tk.Frame(self.frame, bg="#1e1e1e")
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(
            title_frame,
            text="Order Book",
            font=("Segoe UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(side=tk.LEFT)

        # Create order book display
        book_frame = tk.Frame(self.frame, bg="#1e1e1e")
        book_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Headers
        header_frame = tk.Frame(book_frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame, text="Price", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=12, anchor="e").pack(side=tk.LEFT)
        tk.Label(header_frame, text="Amount", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=12, anchor="e").pack(side=tk.LEFT)
        tk.Label(header_frame, text="Total", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=12, anchor="e").pack(side=tk.LEFT)

        # Asks (sells) - shown in red, reversed order
        self.asks_frame = tk.Frame(book_frame, bg="#1e1e1e")
        self.asks_frame.pack(fill=tk.X, pady=(5, 0))

        # Spread indicator
        self.spread_label = tk.Label(
            book_frame,
            text="Spread: --",
            font=("Segoe UI", 9),
            bg="#2d2d2d",
            fg="#888888"
        )
        self.spread_label.pack(fill=tk.X, pady=3)

        # Bids (buys) - shown in green
        self.bids_frame = tk.Frame(book_frame, bg="#1e1e1e")
        self.bids_frame.pack(fill=tk.X, pady=(0, 5))

        # Store label references
        self.ask_labels = []
        self.bid_labels = []

        # Create rows
        for i in range(10):
            row = self._create_row(self.asks_frame, "#ff4444")
            self.ask_labels.append(row)

        for i in range(10):
            row = self._create_row(self.bids_frame, "#00ff88")
            self.bid_labels.append(row)

    def _create_row(self, parent, color): # Create a row for order book entry
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill=tk.X)

        price_label = tk.Label(frame, text="--", font=("Consolas", 9),
                               bg="#1e1e1e", fg=color, width=12, anchor="e")
        price_label.pack(side=tk.LEFT)

        amount_label = tk.Label(frame, text="--", font=("Consolas", 9),
                                bg="#1e1e1e", fg="#cccccc", width=12, anchor="e")
        amount_label.pack(side=tk.LEFT)

        total_label = tk.Label(frame, text="--", font=("Consolas", 9),
                               bg="#1e1e1e", fg="#888888", width=12, anchor="e")
        total_label.pack(side=tk.LEFT)

        return (price_label, amount_label, total_label)

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

    def start(self): # Start WebSocket for order book updates
        if self.is_active:
            return
        self.is_active = True

        # First get initial snapshot via REST
        self._fetch_initial_depth()

        # Then connect to WebSocket for updates
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@depth10@100ms"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=lambda ws, err: print(f"OrderBook error: {err}"),
            on_close=lambda ws, s, m: None,
            on_open=lambda ws: print(f"OrderBook connected for {self.symbol}")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _fetch_initial_depth(self): # Fetch initial order book snapshot
        try:
            url = "https://api.binance.com/api/v3/depth"
            params = {"symbol": self.symbol, "limit": 10}
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            self.parent.after(0, self._update_display, data['bids'], data['asks'])
        except Exception as e:
            print(f"Error fetching depth: {e}")

    def _on_message(self, ws, message): # Handle order book updates
        if not self.is_active:
            return

        data = json.loads(message)
        bids = data.get('bids', [])
        asks = data.get('asks', [])

        self.parent.after(0, self._update_display, bids, asks)

    def _update_display(self, bids, asks): # Update the order book display
        if not self.is_active:
            return

        # Update asks (reversed so lowest ask is at bottom)
        asks_reversed = list(reversed(asks[:10]))
        for i, row in enumerate(self.ask_labels):
            if i < len(asks_reversed):
                price = float(asks_reversed[i][0])
                amount = float(asks_reversed[i][1])
                total = price * amount
                row[0].config(text=f"{price:,.2f}")
                row[1].config(text=f"{amount:.4f}")
                row[2].config(text=f"{total:,.2f}")
            else:
                row[0].config(text="--")
                row[1].config(text="--")
                row[2].config(text="--")

        # Update bids
        for i, row in enumerate(self.bid_labels):
            if i < len(bids):
                price = float(bids[i][0])
                amount = float(bids[i][1])
                total = price * amount
                row[0].config(text=f"{price:,.2f}")
                row[1].config(text=f"{amount:.4f}")
                row[2].config(text=f"{total:,.2f}")
            else:
                row[0].config(text="--")
                row[1].config(text="--")
                row[2].config(text="--")

        # Update spread
        if bids and asks:
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            spread = best_ask - best_bid
            spread_pct = (spread / best_ask) * 100
            self.spread_label.config(text=f"Spread: {spread:.2f} ({spread_pct:.3f}%)")

    def stop(self): # Stop WebSocket connection
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)