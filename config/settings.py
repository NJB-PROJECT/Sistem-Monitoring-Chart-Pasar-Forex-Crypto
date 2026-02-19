"""
Configuration settings for Advanced Trading Analyzer
"""
import os
import json

# ── API Keys (loaded from api_keys.json or environment) ─────────────────────
_KEY_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")

def load_api_keys() -> dict:
    """Load API keys from persistent JSON file."""
    defaults = {
        "twelvedata":    "",
        "alpha_vantage": "",
        "active_provider": "auto",
    }
    if os.path.exists(_KEY_FILE):
        try:
            with open(_KEY_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_api_keys(keys: dict):
    """Persist API keys to JSON file."""
    try:
        with open(_KEY_FILE, "w") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save API keys: {e}")

# ── Symbol Maps per Provider ─────────────────────────────────────────────────
SYMBOLS = {
    "XAU/USD": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "NAS100":  "NQ=F",
    "SP500":   "ES=F",
}

# Twelvedata symbol format
SYMBOLS_TWELVEDATA = {
    "XAU/USD": "XAU/USD",
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "BTC/USD": "BTC/USD",
    "ETH/USD": "ETH/USD",
    "NAS100":  "NDX",
    "SP500":   "SPX",
}

# Alpha Vantage symbol format
SYMBOLS_ALPHAVANTAGE = {
    "XAU/USD": ("forex",  "XAU", "USD"),
    "EUR/USD": ("forex",  "EUR", "USD"),
    "GBP/USD": ("forex",  "GBP", "USD"),
    "USD/JPY": ("forex",  "USD", "JPY"),
    "BTC/USD": ("crypto", "BTC", "USD"),
    "ETH/USD": ("crypto", "ETH", "USD"),
    "NAS100":  ("stock",  "QQQ", None),
    "SP500":   ("stock",  "SPY", None),
}

# Twelvedata interval mapping
TWELVEDATA_INTERVALS = {
    "1M":  "1min",
    "5M":  "5min",
    "15M": "15min",
    "1H":  "1h",
    "4H":  "4h",
    "1D":  "1day",
}

# Alpha Vantage interval mapping
AV_INTERVALS = {
    "1M":  ("TIME_SERIES_INTRADAY",  "1min"),
    "5M":  ("TIME_SERIES_INTRADAY",  "5min"),
    "15M": ("TIME_SERIES_INTRADAY",  "15min"),
    "1H":  ("TIME_SERIES_INTRADAY",  "60min"),
    "4H":  ("TIME_SERIES_INTRADAY",  "60min"),  # AV doesn't have 4H, use 1H
    "1D":  ("TIME_SERIES_DAILY",     None),
}

# Outputsize per timeframe for AV
AV_OUTPUTSIZE = {
    "1M": "compact", "5M": "compact", "15M": "full",
    "1H": "full", "4H": "full", "1D": "full",
}

TIMEFRAMES = {
    "1M":  {"interval": "1m",  "period": "1d",  "label": "1 Minute"},
    "5M":  {"interval": "5m",  "period": "5d",  "label": "5 Minutes"},
    "15M": {"interval": "15m", "period": "5d",  "label": "15 Minutes"},
    "1H":  {"interval": "60m", "period": "1mo", "label": "1 Hour"},
    "4H":  {"interval": "1h",  "period": "3mo", "label": "4 Hours"},
    "1D":  {"interval": "1d",  "period": "1y",  "label": "1 Day"},
}

# Provider display info
PROVIDERS = {
    "auto":          {"name": "Auto (Best Available)",  "icon": "🤖", "color": "#00B0FF"},
    "twelvedata":    {"name": "Twelve Data",            "icon": "📡", "color": "#7C4DFF"},
    "alpha_vantage": {"name": "Alpha Vantage",          "icon": "📊", "color": "#FF6D00"},
    "yfinance":      {"name": "Yahoo Finance",          "icon": "🟣", "color": "#720E9E"},
    "synthetic":     {"name": "Demo (Synthetic)",       "icon": "🔬", "color": "#546E7A"},
}


# ─────────────────────────────────────────────────────────────────────────────
RSI_OVERSOLD    = 30
RSI_OVERBOUGHT  = 70
RSI_NEUTRAL_LOW  = 40
RSI_NEUTRAL_HIGH = 60

BB_PERIOD = 20
BB_STD    = 2

SMA_SHORT = 20
SMA_LONG  = 50

COLORS = {
    "bullish":   "#00C853",
    "bearish":   "#FF1744",
    "neutral":   "#FFD600",
    "high":      "#FF6D00",
    "medium":    "#00B0FF",
    "low":       "#69F0AE",
    "bg":        "#0D1117",
    "card":      "#161B22",
    "border":    "#30363D",
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
}

PRIORITY_ICONS = {
    "HIGH":   "🔴",
    "MEDIUM": "🟡",
    "LOW":    "🟢",
}
