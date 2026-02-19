"""
Technical Analysis Engine
Computes: SMA, EMA, RSI, Bollinger Bands, MACD, ATR, Support/Resistance
"""
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT, SMA_SHORT, SMA_LONG, BB_PERIOD, BB_STD


def add_sma(df: pd.DataFrame, period: int, col: str = "close") -> pd.Series:
    return df[col].rolling(window=period).mean()


def add_ema(df: pd.DataFrame, period: int, col: str = "close") -> pd.Series:
    return df[col].ewm(span=period, adjust=False).mean()


def add_rsi(df: pd.DataFrame, period: int = 14, col: str = "close") -> pd.Series:
    delta = df[col].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs  = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def add_bollinger_bands(df: pd.DataFrame, period: int = BB_PERIOD, std: float = BB_STD, col: str = "close"):
    mid   = df[col].rolling(window=period).mean()
    sigma = df[col].rolling(window=period).std()
    upper = mid + std * sigma
    lower = mid - std * sigma
    return upper, mid, lower


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, col: str = "close"):
    ema_fast   = df[col].ewm(span=fast, adjust=False).mean()
    ema_slow   = df[col].ewm(span=slow, adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram   = macd_line - signal_line
    return macd_line, signal_line, histogram


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    hl  = df["high"] - df["low"]
    hc  = (df["high"] - df["close"].shift()).abs()
    lc  = (df["low"]  - df["close"].shift()).abs()
    tr  = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def find_support_resistance(df: pd.DataFrame, lookback: int = 20, num_levels: int = 3):
    """
    Identify key support and resistance levels using pivot points
    and price clustering.
    """
    highs  = df["high"].rolling(lookback, center=True).max()
    lows   = df["low"].rolling(lookback, center=True).min()

    resistance_candidates = df["high"][df["high"] == highs].dropna()
    support_candidates    = df["low"][df["low"]  == lows].dropna()

    def cluster(series, tolerance=0.002):
        levels = []
        for price in sorted(series.values):
            if not levels or abs(price - levels[-1]) / levels[-1] > tolerance:
                levels.append(price)
        return levels

    resistances = cluster(resistance_candidates)[-num_levels:]
    supports    = cluster(support_candidates)[:num_levels]

    return sorted(supports), sorted(resistances)


def compute_all(df: pd.DataFrame) -> dict:
    """Run all indicators and return enriched DataFrame + summary dict."""
    df = df.copy()

    df["sma20"]  = add_sma(df, SMA_SHORT)
    df["sma50"]  = add_sma(df, SMA_LONG)
    df["ema20"]  = add_ema(df, SMA_SHORT)
    df["rsi"]    = add_rsi(df)
    df["bb_upper"], df["bb_mid"], df["bb_lower"] = add_bollinger_bands(df)
    df["macd"], df["macd_signal"], df["macd_hist"] = add_macd(df)
    df["atr"]    = add_atr(df)

    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 2 else latest

    supports, resistances = find_support_resistance(df)

    # ── Trend Detection ──────────────────────────────────────────────────────
    price      = latest["close"]
    sma20      = latest["sma20"]
    sma50      = latest["sma50"]
    rsi_val    = latest["rsi"] if not pd.isna(latest["rsi"]) else 50
    macd_val   = latest["macd"] if not pd.isna(latest["macd"]) else 0
    macd_sig   = latest["macd_signal"] if not pd.isna(latest["macd_signal"]) else 0
    atr_val    = latest["atr"] if not pd.isna(latest["atr"]) else 0

    if pd.isna(sma20) or pd.isna(sma50):
        trend = "SIDEWAYS"
    elif price > sma20 > sma50 and macd_val > macd_sig:
        trend = "BULLISH"
    elif price < sma20 < sma50 and macd_val < macd_sig:
        trend = "BEARISH"
    else:
        trend = "SIDEWAYS"

    # Trend strength 0-100
    score = 0
    if trend == "BULLISH":
        if not pd.isna(sma20) and price > sma20:  score += 25
        if not pd.isna(sma20) and not pd.isna(sma50) and sma20  > sma50: score += 25
        if macd_val > macd_sig: score += 25
        if rsi_val > 50:   score += 25
    elif trend == "BEARISH":
        if not pd.isna(sma20) and price < sma20:  score += 25
        if not pd.isna(sma20) and not pd.isna(sma50) and sma20  < sma50: score += 25
        if macd_val < macd_sig: score += 25
        if rsi_val < 50:   score += 25

    # ── RSI Signal ───────────────────────────────────────────────────────────
    if rsi_val <= RSI_OVERSOLD:
        rsi_signal = "OVERSOLD"
    elif rsi_val >= RSI_OVERBOUGHT:
        rsi_signal = "OVERBOUGHT"
    else:
        rsi_signal = "NEUTRAL"

    # ── BB Position ──────────────────────────────────────────────────────────
    bb_upper = latest["bb_upper"]
    bb_lower = latest["bb_lower"]
    bb_mid   = latest["bb_mid"]

    if price >= bb_upper:
        bb_signal = "ABOVE_UPPER"
    elif price <= bb_lower:
        bb_signal = "BELOW_LOWER"
    elif price > bb_mid:
        bb_signal = "ABOVE_MID"
    else:
        bb_signal = "BELOW_MID"

    return {
        "df":           df,
        "price":        round(price, 5),
        "atr":          round(atr_val, 5),
        "trend":        trend,
        "trend_score":  score,
        "sma20":        round(sma20,  5) if not pd.isna(sma20)  else None,
        "sma50":        round(sma50,  5) if not pd.isna(sma50)  else None,
        "rsi":          round(rsi_val, 2),
        "rsi_signal":   rsi_signal,
        "macd":         round(macd_val, 5),
        "macd_signal":  round(macd_sig, 5),
        "macd_hist":    round(latest["macd_hist"], 5),
        "bb_upper":     round(bb_upper, 5) if not pd.isna(bb_upper) else None,
        "bb_mid":       round(bb_mid,   5) if not pd.isna(bb_mid)   else None,
        "bb_lower":     round(bb_lower, 5) if not pd.isna(bb_lower) else None,
        "bb_signal":    bb_signal,
        "supports":     [round(s, 5) for s in supports],
        "resistances":  [round(r, 5) for r in resistances],
    }
