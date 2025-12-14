import json
import os

CONFIG_FILE = "dashboard_config.json"

def load_preferences():
    default_prefs = {
        "visible_panels": {
            "order_book": True,
            "trades": True,
            "chart": True,
            "price_table": True
        },
        "enabled_cryptos": {
            "BTC": True,
            "ETH": True,
            "SOL": True,
            "DOGE": True,
            "XRP": True,
            "ADA": False,
            "MATIC": False
        },
        "selected_symbol": "BTC"
    }

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    return default_prefs


def save_preferences(prefs):
    with open(CONFIG_FILE, "w") as f:
        json.dump(prefs, f, indent=2)