"""
Data Fetcher — Multi-Provider with Auto-Fallback
Priority (auto): Twelvedata → Alpha Vantage → yfinance → Synthetic
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    SYMBOLS, SYMBOLS_TWELVEDATA, SYMBOLS_ALPHAVANTAGE,
    TIMEFRAMES, TWELVEDATA_INTERVALS, AV_INTERVALS, AV_OUTPUTSIZE,
    load_api_keys,
)

SEED_PRICES = {
    "XAU/USD": 2950.00,
    "EUR/USD": 1.08200,
    "GBP/USD": 1.26300,
    "USD/JPY": 151.80,
    "BTC/USD": 97500.0,
    "ETH/USD": 3480.00,
    "NAS100":  22200.0,
    "SP500":   5700.00,
}


# ─── TWELVEDATA ──────────────────────────────────────────────────────────────
def _fetch_twelvedata(symbol: str, timeframe: str, api_key: str) -> pd.DataFrame:
    td_symbol   = SYMBOLS_TWELVEDATA.get(symbol)
    td_interval = TWELVEDATA_INTERVALS.get(timeframe)
    if not td_symbol or not td_interval:
        raise ValueError(f"Twelvedata: unsupported {symbol}/{timeframe}")

    resp = requests.get(
        "https://api.twelvedata.com/time_series",
        params={
            "symbol":     td_symbol,
            "interval":   td_interval,
            "outputsize": 500,
            "apikey":     api_key,
            "format":     "JSON",
            "order":      "ASC",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") == "error":
        raise ValueError(f"Twelvedata: {data.get('message','unknown error')}")

    values = data.get("values", [])
    if not values:
        raise ValueError("Twelvedata: empty response")

    df = pd.DataFrame(values)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce").fillna(0)
    return df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])


# ─── ALPHA VANTAGE ───────────────────────────────────────────────────────────
def _fetch_alphavantage(symbol: str, timeframe: str, api_key: str) -> pd.DataFrame:
    sym_info = SYMBOLS_ALPHAVANTAGE.get(symbol)
    if not sym_info:
        raise ValueError(f"Alpha Vantage: unsupported symbol {symbol}")
    asset_type, from_sym, to_sym = sym_info
    av_func, av_interval         = AV_INTERVALS.get(timeframe, (None, None))
    outputsize                   = AV_OUTPUTSIZE.get(timeframe, "full")
    BASE = "https://www.alphavantage.co/query"

    if asset_type == "forex":
        if timeframe == "1D":
            func, extra = "FX_DAILY", {}
            ts_key = "Time Series FX (Daily)"
        else:
            func    = "FX_INTRADAY"
            extra   = {"interval": av_interval}
            ts_key  = f"Time Series FX ({av_interval})"
        params = {"function": func, "from_symbol": from_sym,
                  "to_symbol": to_sym, "outputsize": outputsize,
                  "apikey": api_key, **extra}
        key_suffix = ""

    elif asset_type == "crypto":
        if timeframe != "1D":
            raise ValueError("Alpha Vantage crypto: only daily candles on free plan")
        func, params = "DIGITAL_CURRENCY_DAILY", {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": from_sym, "market": "USD", "apikey": api_key,
        }
        ts_key     = "Time Series (Digital Currency Daily)"
        key_suffix = " (USD)"
    else:  # stock/ETF
        if timeframe == "1D":
            func   = "TIME_SERIES_DAILY"
            ts_key = "Time Series (Daily)"
            extra  = {}
        else:
            func   = av_func
            ts_key = f"Time Series ({av_interval})"
            extra  = {"interval": av_interval}
        params     = {"function": func, "symbol": from_sym,
                      "outputsize": outputsize, "apikey": api_key, **extra}
        key_suffix = ""

    resp = requests.get(BASE, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    ts = data.get(ts_key, {})
    if not ts:
        note = data.get("Information", data.get("Note", data.get("Error Message", "")))
        raise ValueError(f"Alpha Vantage: {note[:150] if note else 'empty data'}")

    rows = []
    for dt_str, vals in ts.items():
        def _v(k1, k2=None):
            return float(vals.get(k1 + key_suffix, vals.get(k1, vals.get(k2 or k1, 0))))
        try:
            rows.append({
                "datetime": pd.to_datetime(dt_str),
                "open":  _v("1. open"),
                "high":  _v("2. high"),
                "low":   _v("3. low"),
                "close": _v("4. close"),
                "volume": float(vals.get("5. volume", 0)),
            })
        except Exception:
            continue

    if not rows:
        raise ValueError("Alpha Vantage: no rows parsed")

    df = pd.DataFrame(rows).set_index("datetime").sort_index()
    return df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])


# ─── YFINANCE ────────────────────────────────────────────────────────────────
def _fetch_yfinance(symbol: str, timeframe: str) -> pd.DataFrame:
    tc  = SYMBOLS.get(symbol)
    tfc = TIMEFRAMES.get(timeframe)
    if not tc or not tfc:
        raise ValueError("yfinance: unsupported symbol/timeframe")
    ticker = yf.Ticker(tc)
    df     = ticker.history(period=tfc["period"], interval=tfc["interval"])
    if df.empty:
        raise ValueError("yfinance: empty response")
    df = df[["Open","High","Low","Close","Volume"]].copy()
    df.columns = ["open","high","low","close","volume"]
    df.index   = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df.dropna(subset=["close"])


# ─── SYNTHETIC ───────────────────────────────────────────────────────────────
def _generate_synthetic(symbol: str, timeframe: str, n: int = 350) -> pd.DataFrame:
    seed  = sum(ord(c) for c in symbol + timeframe)
    rng   = np.random.default_rng(seed)
    base  = SEED_PRICES.get(symbol, 100.0)
    vol, drift = 0.0008, 0.00003

    closes = [base]
    for _ in range(n - 1):
        closes.append(closes[-1] * (1 + drift + vol * rng.standard_normal()))
    closes = np.array(closes)

    hf = 1 + rng.uniform(0.0005, 0.006, n)
    lf = 1 - rng.uniform(0.0005, 0.006, n)
    on = rng.uniform(-0.002, 0.002, n)
    opens   = closes * (1 + on)
    highs   = np.maximum(opens, closes) * hf
    lows    = np.minimum(opens, closes) * lf
    volumes = (rng.uniform(0.5, 1.5, n) * 500_000).astype(int)

    tf_map = {"1M":"1min","5M":"5min","15M":"15min","1H":"1h","4H":"4h","1D":"1D"}
    index  = pd.date_range(end=datetime.now(), periods=n, freq=tf_map.get(timeframe,"1h"))
    return pd.DataFrame(
        {"open":opens,"high":highs,"low":lows,"close":closes,"volume":volumes},
        index=index,
    )


# ─── MAIN (Auto-Fallback) ────────────────────────────────────────────────────
def fetch_ohlcv(symbol: str, timeframe: str,
                provider_override: str = None) -> tuple:
    """
    Returns: (DataFrame, provider_name_used: str)
    Auto priority: Twelvedata → Alpha Vantage → yfinance → Synthetic
    """
    keys     = load_api_keys()
    provider = provider_override or keys.get("active_provider", "auto")
    td_key   = keys.get("twelvedata", "").strip()
    av_key   = keys.get("alpha_vantage", "").strip()

    # Manual provider
    if provider == "twelvedata":
        if not td_key:
            raise ValueError("⚠️ Twelvedata API key belum diset. Buka ⚙️ API Settings di sidebar.")
        return _fetch_twelvedata(symbol, timeframe, td_key), "twelvedata"

    if provider == "alpha_vantage":
        if not av_key:
            raise ValueError("⚠️ Alpha Vantage API key belum diset. Buka ⚙️ API Settings di sidebar.")
        return _fetch_alphavantage(symbol, timeframe, av_key), "alpha_vantage"

    if provider == "yfinance":
        return _fetch_yfinance(symbol, timeframe), "yfinance"

    if provider == "synthetic":
        return _generate_synthetic(symbol, timeframe), "synthetic"

    # AUTO mode: try best available
    if td_key:
        try:
            return _fetch_twelvedata(symbol, timeframe, td_key), "twelvedata"
        except Exception:
            pass

    if av_key:
        try:
            return _fetch_alphavantage(symbol, timeframe, av_key), "alpha_vantage"
        except Exception:
            pass

    try:
        return _fetch_yfinance(symbol, timeframe), "yfinance"
    except Exception:
        pass

    return _generate_synthetic(symbol, timeframe), "synthetic"


# ─── CURRENT PRICE ───────────────────────────────────────────────────────────
def get_current_price(symbol: str) -> dict:
    keys   = load_api_keys()
    td_key = keys.get("twelvedata", "").strip()

    # Twelvedata real-time price
    if td_key:
        try:
            td_sym = SYMBOLS_TWELVEDATA.get(symbol)
            r = requests.get(
                "https://api.twelvedata.com/quote",
                params={"symbol": td_sym, "apikey": td_key},
                timeout=10,
            )
            d = r.json()
            if "close" in d:
                price  = float(d["close"])
                prev   = float(d.get("previous_close", price))
                change = price - prev
                chg_pct= (change / prev * 100) if prev else 0
                return {
                    "price":      round(price, 5),
                    "prev_close": round(prev, 5),
                    "change":     round(change, 5),
                    "change_pct": round(chg_pct, 3),
                    "high_24h":   round(float(d.get("high", price)), 5),
                    "low_24h":    round(float(d.get("low",  price)), 5),
                    "volume":     int(float(d.get("volume", 0))),
                    "source":     "twelvedata",
                }
        except Exception:
            pass

    # yfinance fallback
    try:
        ticker = yf.Ticker(SYMBOLS.get(symbol, ""))
        info   = ticker.fast_info
        price  = info.last_price
        prev   = info.previous_close
        change = (price - prev) if prev else 0
        return {
            "price":      round(price, 5),
            "prev_close": round(prev, 5),
            "change":     round(change, 5),
            "change_pct": round((change / prev * 100) if prev else 0, 3),
            "high_24h":   round(info.day_high or 0, 5),
            "low_24h":    round(info.day_low  or 0, 5),
            "volume":     int(info.three_month_average_volume or 0),
            "source":     "yfinance",
        }
    except Exception:
        pass

    base = SEED_PRICES.get(symbol, 0)
    return {
        "price": base, "prev_close": base, "change": 0,
        "change_pct": 0, "high_24h": base, "low_24h": base,
        "volume": 0, "source": "synthetic",
    }
