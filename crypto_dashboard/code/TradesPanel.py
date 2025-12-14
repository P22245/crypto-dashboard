import tkinter as tk
from collections import deque
import websocket
import json
import threading
from datetime import datetime

class TradesPanel: # Panel showing recent trades
    def __init__(self, parent, symbol="BTCUSDT"):
        self.parent = parent
        self.symbol = symbol
        self.is_active = False
        self.ws = None
        self.trades = deque(maxlen=20)
        self.is_visible = True

        # Main frame
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        # Title
        tk.Label(
            self.frame,
            text="Recent Trades",
            font=("Segoe UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Headers
        header_frame = tk.Frame(self.frame, bg="#1e1e1e")
        header_frame.pack(fill=tk.X, padx=10)

        tk.Label(header_frame, text="Price", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=10, anchor="e").pack(side=tk.LEFT)
        tk.Label(header_frame, text="Amount", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=10, anchor="e").pack(side=tk.LEFT)
        tk.Label(header_frame, text="Time", font=("Segoe UI", 9, "bold"),
                 bg="#1e1e1e", fg="#888888", width=10, anchor="e").pack(side=tk.LEFT)

        # Trades list
        self.trades_frame = tk.Frame(self.frame, bg="#1e1e1e")
        self.trades_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create trade rows
        self.trade_labels = []
        for i in range(15):
            row = self._create_trade_row()
            self.trade_labels.append(row)

    def _create_trade_row(self): # Create a row for trade entry
        frame = tk.Frame(self.trades_frame, bg="#1e1e1e")
        frame.pack(fill=tk.X)

        price_label = tk.Label(frame, text="--", font=("Consolas", 9),
                               bg="#1e1e1e", fg="#ffffff", width=10, anchor="e")
        price_label.pack(side=tk.LEFT)

        amount_label = tk.Label(frame, text="--", font=("Consolas", 9),
                                bg="#1e1e1e", fg="#cccccc", width=10, anchor="e")
        amount_label.pack(side=tk.LEFT)

        time_label = tk.Label(frame, text="--", font=("Consolas", 9),
                              bg="#1e1e1e", fg="#888888", width=10, anchor="e")
        time_label.pack(side=tk.LEFT)

        return (price_label, amount_label, time_label)

    def set_symbol(self, symbol): # Change the symbol being tracked
        was_active = self.is_active
        if was_active:
            self.stop()
        self.symbol = symbol.upper() + "/USDT"
        self.trades.clear()
        if was_active:
            self.start()

    def show(self): # Show the panel
        self.is_visible = True
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self): # Hide the panel
        self.is_visible = False
        self.frame.pack_forget()

    def start(self): # Start WebSocket for trade updates
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@trade"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=lambda ws, err: print(f"Trades error: {err}"),
            on_close=lambda ws, s, m: None,
            on_open=lambda ws: print(f"Trades connected for {self.symbol}")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _on_message(self, ws, message): # Handle trade updates
        if not self.is_active:
            return

        data = json.loads(message)
        trade = {
            'price': float(data['p']),
            'amount': float(data['q']),
            'time': datetime.fromtimestamp(data['T'] / 1000),
            'is_buyer_maker': data['m']
        }
        self.trades.appendleft(trade)

        self.parent.after(0, self._update_display)

    def _update_display(self): # Update the trades display
        if not self.is_active:
            return

        for i, row in enumerate(self.trade_labels):
            if i < len(self.trades):
                trade = self.trades[i]
                color = "#ff4444" if trade['is_buyer_maker'] else "#00ff88"
                row[0].config(text=f"{trade['price']:,.2f}", fg=color)
                row[1].config(text=f"{trade['amount']:.4f}")
                row[2].config(text=trade['time'].strftime("%H:%M:%S"))
            else:
                row[0].config(text="--", fg="#ffffff")
                row[1].config(text="--")
                row[2].config(text="--")

    def stop(self): # Stop WebSocket connection
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)