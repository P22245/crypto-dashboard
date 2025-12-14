import tkinter as tk

from utils import load_preferences, save_preferences
from ticker import CryptoTicker
from orderbook import OrderBookPanel
from TradesPanel import TradesPanel
from CandlestickChart import CandlestickChart
from PriceTable import PriceTable

class CryptoDashboard: # Main cryptocurrency dashboard application
    AVAILABLE_CRYPTOS = [
        ("btcusdt", "BTC/USDT", "BTC"),
        ("ethusdt", "ETH/USDT", "ETH"),
        ("solusdt", "SOL/USDT", "SOL"),
        ("dogeusdt", "DOGE/USDT", "DOGE"),
        ("xrpusdt", "XRP/USDT", "XRP"),
        ("adausdt", "ADA/USDT", "ADA"),
        ("maticusdt", "MATIC/USDT", "MATIC"),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("1400x850")
        self.root.configure(bg="#121212")

        # Load saved preferences
        self.preferences = load_preferences()
        self.selected_symbol = self.preferences.get("selected_symbol", "BTC")
        self.is_closing = False

        # Toggle button references
        self.panel_toggle_buttons = {}
        self.crypto_toggle_buttons = {}

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=2)
        self.root.grid_rowconfigure(2, weight=1)

        # Create UI components
        self._create_header()
        self._create_control_panel()
        self._create_left_panel()
        self._create_middle_panel()
        self._create_right_panel()

        # Apply saved visibility preferences
        self._apply_preferences()

        # Start all components
        self._start_all()

    def _create_header(self): # Create the header bar
        header = tk.Frame(self.root, bg="#2d2d2d", height=60)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_propagate(False)

        # Title
        tk.Label(
            header,
            text="Crypto Dashboard",
            font=("Segoe UI", 20, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Connection status
        self.status_label = tk.Label(
            header,
            text="LIVE",
            font=("Segoe UI", 10, "bold"),
            bg="#00ff88",
            fg="#000000",
            padx=10,
            pady=3
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # Selected symbol display
        self.selected_label = tk.Label(
            header,
            text=f"Selected: {self.selected_symbol}/USDT",
            font=("Segoe UI", 12),
            bg="#2d2d2d",
            fg="#888888"
        )
        self.selected_label.pack(side=tk.RIGHT, padx=20, pady=15)

    def _create_control_panel(self): # Create control panel with toggle buttons
        control_frame = tk.Frame(self.root, bg="#252525", height=50)
        control_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 0))

        # Panel toggles section
        panel_section = tk.Frame(control_frame, bg="#252525")
        panel_section.pack(side=tk.LEFT, padx=10, pady=8)

        tk.Label(
            panel_section,
            text="Panels:",
            font=("Segoe UI", 10, "bold"),
            bg="#252525",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Panel toggle buttons
        panels = [
            ("Order Book", "order_book"),
            ("Trades", "trades"),
            ("Chart", "chart"),
            ("Statistics", "price_table")
        ]

        for label, key in panels:
            is_visible = self.preferences["visible_panels"].get(key, True)
            btn = tk.Button(
                panel_section,
                text=f"{'Hide' if is_visible else 'Show'} {label}",
                font=("Segoe UI", 9),
                bg="#00ff88" if is_visible else "#444444",
                fg="#000000" if is_visible else "#ffffff",
                relief="flat",
                padx=10,
                pady=3,
                command=lambda k=key, l=label: self._toggle_panel(k, l)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.panel_toggle_buttons[key] = btn

        # Separator
        tk.Frame(control_frame, bg="#444444", width=2).pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=5)

        # Crypto toggles section
        crypto_section = tk.Frame(control_frame, bg="#252525")
        crypto_section.pack(side=tk.LEFT, padx=10, pady=8)

        tk.Label(
            crypto_section,
            text="Cryptos:",
            font=("Segoe UI", 10, "bold"),
            bg="#252525",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Crypto toggle buttons
        for symbol, display_name, short in self.AVAILABLE_CRYPTOS:
            is_enabled = self.preferences["enabled_cryptos"].get(short, True)
            btn = tk.Button(
                crypto_section,
                text=short,
                font=("Segoe UI", 9, "bold"),
                bg="#00ff88" if is_enabled else "#444444",
                fg="#000000" if is_enabled else "#ffffff",
                relief="flat",
                width=6,
                pady=3,
                command=lambda s=short: self._toggle_crypto(s)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.crypto_toggle_buttons[short] = btn

    def _toggle_panel(self, panel_key, panel_label): # Toggle visibility of a panel
        current_state = self.preferences["visible_panels"].get(panel_key, True)
        new_state = not current_state
        self.preferences["visible_panels"][panel_key] = new_state

        # Update button appearance
        btn = self.panel_toggle_buttons[panel_key]
        btn.config(
            text=f"{'Hide' if new_state else 'Show'} {panel_label}",
            bg="#00ff88" if new_state else "#444444",
            fg="#000000" if new_state else "#ffffff"
        )

        # Show/hide the actual panel
        panel_map = {
            "order_book": self.order_book,
            "trades": self.trades_panel,
            "chart": self.chart,
            "price_table": self.price_table
        }

        panel = panel_map.get(panel_key)
        if panel:
            if new_state:
                panel.show()
            else:
                panel.hide()

        # Save preferences
        save_preferences(self.preferences)

    def _toggle_crypto(self, crypto_short): # Toggle visibility of a cryptocurrency ticker
        current_state = self.preferences["enabled_cryptos"].get(crypto_short, True)
        new_state = not current_state
        self.preferences["enabled_cryptos"][crypto_short] = new_state

        # Update button appearance
        btn = self.crypto_toggle_buttons[crypto_short]
        btn.config(
            bg="#00ff88" if new_state else "#444444",
            fg="#000000" if new_state else "#ffffff"
        )

        # Show/hide the ticker
        symbol_key = f"{crypto_short.lower()}usdt"
        if symbol_key in self.tickers:
            ticker = self.tickers[symbol_key]
            if new_state:
                ticker.pack(fill=tk.X, pady=3)
                ticker.start()
            else:
                ticker.stop()
                ticker.pack_forget()

        # Save preferences
        save_preferences(self.preferences)

    def _create_left_panel(self): # Create the left panel with order book
        self.left_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.left_frame.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=10)

        # Order Book
        self.order_book = OrderBookPanel(self.left_frame, f"{self.selected_symbol}USDT")
        self.order_book.pack(fill=tk.BOTH, expand=True)

    def _create_middle_panel(self): # Create the middle panel with trades and selection
        self.middle_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.middle_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=10)

        # Trades Panel
        self.trades_panel = TradesPanel(self.middle_frame, f"{self.selected_symbol}USDT")
        self.trades_panel.pack(fill=tk.BOTH, expand=True)

        # Separator
        tk.Frame(self.middle_frame, bg="#444444", height=2).pack(fill=tk.X, pady=10)

        # Selection Panel (Tickers)
        selection_frame = tk.Frame(self.middle_frame, bg="#1e1e1e")
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(
            selection_frame,
            text="Select Crypto",
            font=("Segoe UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(anchor="w", padx=10, pady=(5, 10))

        # Scrollable tickers frame
        tickers_container = tk.Frame(selection_frame, bg="#1e1e1e")
        tickers_container.pack(fill=tk.BOTH, expand=True, padx=10)

        self.tickers_frame = tk.Frame(tickers_container, bg="#1e1e1e")
        self.tickers_frame.pack(fill=tk.BOTH, expand=True)

        # Create tickers for all available cryptos
        self.tickers = {}
        for symbol, display_name, short in self.AVAILABLE_CRYPTOS:
            ticker = CryptoTicker(
                self.tickers_frame,
                symbol,
                display_name,
                on_select_callback=self._on_symbol_select
            )
            self.tickers[symbol] = ticker

    def _create_right_panel(self): # Create the right panel with chart and price table
        self.right_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.right_frame.grid(row=2, column=2, sticky="nsew", padx=(5, 10), pady=10)

        # Configure right panel grid
        self.right_frame.grid_rowconfigure(0, weight=3)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Candlestick Chart
        self.chart_frame = tk.Frame(self.right_frame, bg="#1e1e1e")
        self.chart_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.chart = CandlestickChart(self.chart_frame, f"{self.selected_symbol}USDT")
        self.chart.pack(fill=tk.BOTH, expand=True)

        # Price Table
        self.table_frame = tk.Frame(self.right_frame, bg="#1e1e1e")
        self.table_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        self.price_table = PriceTable(self.table_frame, f"{self.selected_symbol}USDT")
        self.price_table.pack(fill=tk.BOTH, expand=True)

    def _apply_preferences(self): # Apply saved preferences for panel and crypto visibility
        panel_map = {
            "order_book": self.order_book,
            "trades": self.trades_panel,
            "chart": self.chart,
            "price_table": self.price_table
        }

        for key, panel in panel_map.items():
            if not self.preferences["visible_panels"].get(key, True):
                panel.hide()

        # Apply crypto visibility - pack enabled ones
        for symbol, display_name, short in self.AVAILABLE_CRYPTOS:
            ticker = self.tickers[symbol]
            if self.preferences["enabled_cryptos"].get(short, True):
                ticker.pack(fill=tk.X, pady=3)

        # Highlight selected crypto
        selected_symbol_key = f"{self.selected_symbol.lower()}usdt"
        for symbol, ticker in self.tickers.items():
            ticker.set_selected(symbol == selected_symbol_key)

    def _on_symbol_select(self, symbol): # Handle symbol selection from ticker click
        if symbol == self.selected_symbol:
            return

        # Update selection highlight
        old_symbol_key = f"{self.selected_symbol.lower()}usdt"
        new_symbol_key = f"{symbol.lower()}usdt"

        if old_symbol_key in self.tickers:
            self.tickers[old_symbol_key].set_selected(False)
        if new_symbol_key in self.tickers:
            self.tickers[new_symbol_key].set_selected(True)

        self.selected_symbol = symbol
        self.selected_label.config(text=f"Selected: {symbol}/USDT")

        # Save preference
        self.preferences["selected_symbol"] = symbol
        save_preferences(self.preferences)

        # Update all panels
        self.order_book.set_symbol(symbol)
        self.trades_panel.set_symbol(symbol)
        self.chart.set_symbol(symbol)
        self.price_table.set_symbol(symbol)

    def _start_all(self):
        """Start all WebSocket connections."""
        # Start enabled tickers
        for symbol, display_name, short in self.AVAILABLE_CRYPTOS:
            if self.preferences["enabled_cryptos"].get(short, True):
                self.tickers[symbol].start()

        # Start panels
        self.order_book.start()
        self.trades_panel.start()
        self.chart.start()
        self.price_table.start()

    def _stop_all(self): # Stop all WebSocket connections
        for ticker in self.tickers.values():
            ticker.stop()

        self.order_book.stop()
        self.trades_panel.stop()
        self.chart.stop()
        self.price_table.stop()

    def on_closing(self): # Clean up when closing the application
        self.is_closing = True
        self._stop_all()
        save_preferences(self.preferences)
        self.root.destroy()