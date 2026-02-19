"""
Recommendation Engine
Generates Buy / Sell / Hold recommendations from technical signals.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT, PRIORITY_ICONS


def _fmt(price: float, symbol: str) -> str:
    """Format price based on symbol precision."""
    if "JPY" in symbol:
        return f"{price:.3f}"
    return f"{price:.5f}" if price < 10 else f"{price:.2f}"


def generate_recommendations(ta: dict, patterns: list, symbol: str) -> list:
    """
    Build a prioritized list of trading recommendations.
    Each recommendation is a dict:
        action, priority, area, reason, target, sl, confidence
    """
    recs  = []
    price = ta["price"]
    atr   = ta["atr"] or (price * 0.001)

    trend      = ta["trend"]
    rsi_val    = ta["rsi"]
    rsi_signal = ta["rsi_signal"]
    bb_signal  = ta["bb_signal"]
    bb_upper   = ta["bb_upper"]
    bb_lower   = ta["bb_lower"]
    bb_mid     = ta["bb_mid"]
    supports   = ta["supports"]
    resistances= ta["resistances"]
    macd       = ta["macd"]
    macd_sig   = ta["macd_signal"]
    sma20      = ta["sma20"]
    sma50      = ta["sma50"]
    ts         = ta["trend_score"]

    # ── RSI Oversold → BUY ───────────────────────────────────────────────────
    if rsi_signal == "OVERSOLD":
        entry = price
        tp    = round(bb_mid or (price + 2 * atr), 5)
        sl    = round(price - 1.5 * atr, 5)
        recs.append({
            "action":     "BUY",
            "priority":   "HIGH",
            "area":       _fmt(entry, symbol),
            "reason":     f"RSI oversold ({rsi_val:.1f}) — strong reversal signal",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 78,
        })

    # ── RSI Overbought → SELL ────────────────────────────────────────────────
    if rsi_signal == "OVERBOUGHT":
        entry = price
        tp    = round(bb_mid or (price - 2 * atr), 5)
        sl    = round(price + 1.5 * atr, 5)
        recs.append({
            "action":     "SELL",
            "priority":   "HIGH",
            "area":       _fmt(entry, symbol),
            "reason":     f"RSI overbought ({rsi_val:.1f}) — bearish exhaustion",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 75,
        })

    # ── Price at BB Lower Band → BUY ─────────────────────────────────────────
    if bb_signal == "BELOW_LOWER" and trend != "BEARISH":
        entry = price
        tp    = round(bb_mid, 5)
        sl    = round(price - atr, 5)
        recs.append({
            "action":     "BUY",
            "priority":   "MEDIUM",
            "area":       _fmt(entry, symbol),
            "reason":     f"Price below Bollinger Lower Band — mean reversion expected",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 65,
        })

    # ── Price at BB Upper Band → SELL ────────────────────────────────────────
    if bb_signal == "ABOVE_UPPER" and trend != "BULLISH":
        entry = price
        tp    = round(bb_mid, 5)
        sl    = round(price + atr, 5)
        recs.append({
            "action":     "SELL",
            "priority":   "MEDIUM",
            "area":       _fmt(entry, symbol),
            "reason":     f"Price above Bollinger Upper Band — overbought zone",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 63,
        })

    # ── MACD Crossover ───────────────────────────────────────────────────────
    if macd > macd_sig and ta["macd_hist"] > 0:
        entry = price
        tp    = round(price + 2 * atr, 5)
        sl    = round(price - 1.2 * atr, 5)
        p     = "HIGH" if ts >= 75 else "MEDIUM"
        recs.append({
            "action":     "BUY",
            "priority":   p,
            "area":       _fmt(entry, symbol),
            "reason":     "MACD bullish crossover confirmed",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 60 + (ts // 5),
        })
    elif macd < macd_sig and ta["macd_hist"] < 0:
        entry = price
        tp    = round(price - 2 * atr, 5)
        sl    = round(price + 1.2 * atr, 5)
        p     = "HIGH" if ts >= 75 else "MEDIUM"
        recs.append({
            "action":     "SELL",
            "priority":   p,
            "area":       _fmt(entry, symbol),
            "reason":     "MACD bearish crossover confirmed",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(sl, symbol),
            "confidence": 60 + (ts // 5),
        })

    # ── Trend Hold Recommendations ────────────────────────────────────────────
    if trend == "BULLISH" and ts >= 50:
        tp = resistances[-1] if resistances else round(price + 3 * atr, 5)
        recs.append({
            "action":     "HOLD BUY",
            "priority":   "MEDIUM" if ts < 75 else "HIGH",
            "area":       _fmt(price, symbol),
            "reason":     f"Bullish trend kuat (skor {ts}/100) — ride the trend",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(round(sma20 - atr, 5) if sma20 else round(price - 2*atr, 5), symbol),
            "confidence": 55 + ts // 5,
        })
    elif trend == "BEARISH" and ts >= 50:
        tp = supports[0] if supports else round(price - 3 * atr, 5)
        recs.append({
            "action":     "HOLD SELL",
            "priority":   "MEDIUM" if ts < 75 else "HIGH",
            "area":       _fmt(price, symbol),
            "reason":     f"Bearish trend kuat (skor {ts}/100) — ikuti momentum turun",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(round(sma20 + atr, 5) if sma20 else round(price + 2*atr, 5), symbol),
            "confidence": 55 + ts // 5,
        })

    # ── Support Bounce ────────────────────────────────────────────────────────
    if supports:
        nearest_sup = min(supports, key=lambda s: abs(s - price))
        if abs(nearest_sup - price) / price < 0.005:
            tp = round(price + 3 * atr, 5)
            sl = round(nearest_sup - atr, 5)
            recs.append({
                "action":     "BUY",
                "priority":   "MEDIUM",
                "area":       _fmt(nearest_sup, symbol),
                "reason":     f"Harga mendekati support kunci {_fmt(nearest_sup, symbol)}",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 62,
            })

    # ── Resistance Rejection ─────────────────────────────────────────────────
    if resistances:
        nearest_res = min(resistances, key=lambda r: abs(r - price))
        if abs(nearest_res - price) / price < 0.005:
            tp = round(price - 3 * atr, 5)
            sl = round(nearest_res + atr, 5)
            recs.append({
                "action":     "SELL",
                "priority":   "MEDIUM",
                "area":       _fmt(nearest_res, symbol),
                "reason":     f"Harga mendekati resistance kunci {_fmt(nearest_res, symbol)}",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 60,
            })

    # ── Pattern-Based Recommendations ────────────────────────────────────────
    for p in patterns[:2]:
        if p["type"] == "bullish":
            tp = round(price + 2.5 * atr, 5)
            sl = round(price - 1.5 * atr, 5)
            recs.append({
                "action":     "BUY",
                "priority":   "MEDIUM" if p["strength"] < 4 else "HIGH",
                "area":       _fmt(price, symbol),
                "reason":     f"Pattern '{p['name']}' terdeteksi — {p['desc']}",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 50 + p["strength"] * 5,
            })
        elif p["type"] == "bearish":
            tp = round(price - 2.5 * atr, 5)
            sl = round(price + 1.5 * atr, 5)
            recs.append({
                "action":     "SELL",
                "priority":   "MEDIUM" if p["strength"] < 4 else "HIGH",
                "area":       _fmt(price, symbol),
                "reason":     f"Pattern '{p['name']}' terdeteksi — {p['desc']}",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 50 + p["strength"] * 5,
            })

    # Deduplicate & sort by priority → confidence
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    seen   = set()
    unique = []
    for r in recs:
        key = (r["action"], r["priority"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    unique.sort(key=lambda x: (priority_order[x["priority"]], -x["confidence"]))
    return unique[:6]  # return top-6


def format_recommendation_text(rec: dict, symbol: str) -> str:
    """Format a recommendation into a human-readable Indonesian string."""
    icon = PRIORITY_ICONS[rec["priority"]]
    action_map = {
        "BUY":       "🟢 Lebih baik BUY",
        "SELL":      "🔴 Lebih baik SELL",
        "HOLD BUY":  "🔵 Lebih baik HOLD BUY anda",
        "HOLD SELL": "🔵 Lebih baik HOLD SELL anda",
    }
    verb = action_map.get(rec["action"], rec["action"])
    return (
        f"{icon} {verb} di area **{rec['area']}** — {rec['reason']} | "
        f"TP: {rec['target']} | SL: {rec['sl']} | Confidence: {rec['confidence']}%"
    )
