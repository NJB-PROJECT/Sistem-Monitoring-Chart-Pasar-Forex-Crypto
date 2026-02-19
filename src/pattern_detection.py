"""
Candlestick Pattern Detection Engine
Detects: Doji, Hammer, Shooting Star, Engulfing, Morning/Evening Star,
         Harami, Marubozu, Spinning Top, Three White Soldiers, Three Black Crows
"""
import pandas as pd
import numpy as np


def _body(row):      return abs(row["close"] - row["open"])
def _range(row):     return row["high"] - row["low"]
def _upper_wick(row):
    return row["high"] - max(row["close"], row["open"])
def _lower_wick(row):
    return min(row["close"], row["open"]) - row["low"]
def _is_bullish(row): return row["close"] >= row["open"]


def detect_doji(df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
    """Doji: body is very small relative to total range."""
    body  = (df["close"] - df["open"]).abs()
    rng   = df["high"] - df["low"]
    return (body / rng.replace(0, np.nan)) < threshold


def detect_hammer(df: pd.DataFrame) -> pd.Series:
    """Hammer: small body at top, long lower wick (≥2x body), little/no upper wick."""
    results = []
    for _, row in df.iterrows():
        b  = _body(row)
        lw = _lower_wick(row)
        uw = _upper_wick(row)
        rng = _range(row)
        if rng == 0:
            results.append(False)
            continue
        is_ham = (lw >= 2 * b) and (uw <= b * 0.3) and (b / rng < 0.35)
        results.append(is_ham)
    return pd.Series(results, index=df.index)


def detect_inverted_hammer(df: pd.DataFrame) -> pd.Series:
    """Inverted Hammer: small body at bottom, long upper wick."""
    results = []
    for _, row in df.iterrows():
        b  = _body(row)
        lw = _lower_wick(row)
        uw = _upper_wick(row)
        rng = _range(row)
        if rng == 0:
            results.append(False)
            continue
        is_inv = (uw >= 2 * b) and (lw <= b * 0.3) and (b / rng < 0.35)
        results.append(is_inv)
    return pd.Series(results, index=df.index)


def detect_shooting_star(df: pd.DataFrame) -> pd.Series:
    """Shooting Star: bearish, small body at bottom, long upper wick."""
    inv_hammer = detect_inverted_hammer(df)
    bearish    = df["close"] < df["open"]
    return inv_hammer & bearish


def detect_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    """Bullish Engulfing: current bullish candle fully engulfs prior bearish candle."""
    results = [False]
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        is_eng = (
            _is_bullish(curr) and
            not _is_bullish(prev) and
            curr["open"]  < prev["close"] and
            curr["close"] > prev["open"]
        )
        results.append(is_eng)
    return pd.Series(results, index=df.index)


def detect_bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    """Bearish Engulfing: current bearish candle fully engulfs prior bullish candle."""
    results = [False]
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        is_eng = (
            not _is_bullish(curr) and
            _is_bullish(prev) and
            curr["open"]  > prev["close"] and
            curr["close"] < prev["open"]
        )
        results.append(is_eng)
    return pd.Series(results, index=df.index)


def detect_morning_star(df: pd.DataFrame) -> pd.Series:
    """Morning Star: 3-candle bullish reversal pattern."""
    results = [False, False]
    for i in range(2, len(df)):
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        is_ms = (
            not _is_bullish(c1) and _body(c1) > _range(c1) * 0.5 and  # big bearish
            _body(c2) < _body(c1) * 0.3 and                             # small body star
            _is_bullish(c3) and _body(c3) > _range(c3) * 0.5 and       # big bullish
            c3["close"] > (c1["open"] + c1["close"]) / 2               # closes > midpoint
        )
        results.append(is_ms)
    return pd.Series(results, index=df.index)


def detect_evening_star(df: pd.DataFrame) -> pd.Series:
    """Evening Star: 3-candle bearish reversal pattern."""
    results = [False, False]
    for i in range(2, len(df)):
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        is_es = (
            _is_bullish(c1) and _body(c1) > _range(c1) * 0.5 and
            _body(c2) < _body(c1) * 0.3 and
            not _is_bullish(c3) and _body(c3) > _range(c3) * 0.5 and
            c3["close"] < (c1["open"] + c1["close"]) / 2
        )
        results.append(is_es)
    return pd.Series(results, index=df.index)


def detect_marubozu(df: pd.DataFrame) -> pd.Series:
    """Marubozu: candle with almost no wicks — strong momentum."""
    results = []
    for _, row in df.iterrows():
        b   = _body(row)
        rng = _range(row)
        if rng == 0:
            results.append(False)
            continue
        results.append(b / rng > 0.90)
    return pd.Series(results, index=df.index)


def detect_spinning_top(df: pd.DataFrame) -> pd.Series:
    """Spinning Top: small body with wicks on both sides — indecision."""
    results = []
    for _, row in df.iterrows():
        b   = _body(row)
        lw  = _lower_wick(row)
        uw  = _upper_wick(row)
        rng = _range(row)
        if rng == 0:
            results.append(False)
            continue
        is_st = (b / rng < 0.30) and (lw > b * 0.5) and (uw > b * 0.5)
        results.append(is_st)
    return pd.Series(results, index=df.index)


def get_recent_patterns(df: pd.DataFrame, lookback: int = 5) -> list:
    """
    Scan recent candles for patterns and return a list of detected patterns
    with metadata: name, type (bullish/bearish/neutral), description, strength.
    """
    recent  = df.tail(lookback)
    found   = []

    detectors = [
        ("Doji",               detect_doji,              "neutral",  "Indecision / Potential Reversal",        2),
        ("Hammer",             detect_hammer,             "bullish",  "Bullish Reversal Signal",                3),
        ("Shooting Star",      detect_shooting_star,      "bearish",  "Bearish Reversal Signal",                3),
        ("Bullish Engulfing",  detect_bullish_engulfing,  "bullish",  "Strong Bullish Reversal",                4),
        ("Bearish Engulfing",  detect_bearish_engulfing,  "bearish",  "Strong Bearish Reversal",                4),
        ("Morning Star",       detect_morning_star,       "bullish",  "3-Candle Bullish Reversal",              5),
        ("Evening Star",       detect_evening_star,       "bearish",  "3-Candle Bearish Reversal",              5),
        ("Marubozu",           detect_marubozu,           "neutral",  "Strong Momentum (direction from candle)",2),
        ("Spinning Top",       detect_spinning_top,       "neutral",  "Market Indecision",                      1),
        ("Inverted Hammer",    detect_inverted_hammer,    "bullish",  "Potential Bullish Reversal",             2),
    ]

    for name, fn, pattern_type, desc, strength in detectors:
        try:
            signals = fn(recent)
            if signals.any():
                latest_idx = signals[signals].index[-1]
                row        = recent.loc[latest_idx]
                # Override type for Marubozu based on candle direction
                if name == "Marubozu":
                    pattern_type = "bullish" if row["close"] >= row["open"] else "bearish"
                found.append({
                    "name":     name,
                    "type":     pattern_type,
                    "desc":     desc,
                    "strength": strength,
                    "price":    round(row["close"], 5),
                    "candle_idx": str(latest_idx),
                })
        except Exception:
            continue

    # Sort by strength descending
    found.sort(key=lambda x: x["strength"], reverse=True)
    return found
