"""
Data Fetcher - Retrieves OHLCV market data using yfinance
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import SYMBOLS, TIMEFRAMES


SEED_PRICES = {
    "XAU/USD": 2330.00,
    "EUR/USD": 1.08500,
    "GBP/USD": 1.26500,
    "USD/JPY": 151.50,
    "BTC/USD": 67500.0,
    "ETH/USD": 3500.00,
    "NAS100":  18200.0,
    "SP500":   5100.00,
}


def _generate_synthetic_data(symbol_display: str, timeframe: str, n: int = 300) -> pd.DataFrame:
    """
    Generate realistic OHLCV data using geometric Brownian motion.
    Used as fallback when live data is unavailable.
    """
    seed = sum(ord(c) for c in symbol_display + timeframe)
    rng  = np.random.default_rng(seed)

    base  = SEED_PRICES.get(symbol_display, 100.0)
    vol   = 0.001 if base > 100 else 0.0008
    dt    = 1.0
    drift = 0.00005

    closes = [base]
    for _ in range(n - 1):
        ret    = drift * dt + vol * np.sqrt(dt) * rng.standard_normal()
        closes.append(closes[-1] * (1 + ret))
    closes = np.array(closes)

    # Generate OHLV from close
    high_factor = 1 + rng.uniform(0.001, 0.008, n)
    low_factor  = 1 - rng.uniform(0.001, 0.008, n)
    open_noise  = rng.uniform(-0.003, 0.003, n)

    opens   = closes * (1 + open_noise)
    highs   = np.maximum(opens, closes) * high_factor
    lows    = np.minimum(opens, closes) * low_factor
    volumes = (rng.uniform(0.5, 1.5, n) * 1_000_000).astype(int)

    # Create datetime index
    tf_map = {"1M": "1min", "5M": "5min", "15M": "15min",
               "1H": "1h",  "4H": "4h",   "1D":  "1D"}
    freq = tf_map.get(timeframe, "1h")
    index = pd.date_range(end=datetime.now(), periods=n, freq=freq)

    df = pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": volumes,
    }, index=index)
    return df


def fetch_ohlcv(symbol_display: str, timeframe: str) -> pd.DataFrame:
    """Fetch OHLCV data for a given symbol and timeframe.
    Falls back to high-quality synthetic data if live feed is unavailable.
    """
    ticker_symbol = SYMBOLS.get(symbol_display)
    if not ticker_symbol:
        raise ValueError(f"Unknown symbol: {symbol_display}")

    tf_cfg = TIMEFRAMES.get(timeframe)
    if not tf_cfg:
        raise ValueError(f"Unknown timeframe: {timeframe}")

    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=tf_cfg["period"], interval=tf_cfg["interval"])

        if df.empty:
            raise ValueError("Empty response from yfinance")

        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index)
        df = df.dropna()
        return df

    except Exception:
        # Fallback: generate realistic synthetic OHLCV data
        return _generate_synthetic_data(symbol_display, timeframe)


def get_current_price(symbol_display: str) -> dict:
    """Get current price and 24h change."""
    ticker_symbol = SYMBOLS.get(symbol_display)
    if not ticker_symbol:
        return {}

    try:
        ticker = yf.Ticker(ticker_symbol)
        info  = ticker.fast_info
        price = info.last_price
        prev  = info.previous_close
        change     = price - prev if prev else 0
        change_pct = (change / prev * 100) if prev else 0

        return {
            "price":      round(price, 5),
            "prev_close": round(prev, 5),
            "change":     round(change, 5),
            "change_pct": round(change_pct, 3),
            "high_24h":   round(info.day_high or 0, 5),
            "low_24h":    round(info.day_low or 0, 5),
            "volume":     info.three_month_average_volume or 0,
        }
    except Exception:
        return {}
