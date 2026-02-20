"""
Recommendation Engine
Generates Buy / Sell / Hold recommendations from technical signals.
"""
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT, PRIORITY_ICONS


def _fmt(price: float, symbol: str) -> str:
    """Format price based on symbol precision."""
    if "JPY" in symbol:
        return f"{price:.3f}"
    return f"{price:.5f}" if price < 10 else f"{price:.2f}"


def generate_recommendations(ta: dict, patterns: list, symbol: str, strict_mode: bool = False) -> list:
    """
    Build a prioritized list of trading recommendations.

    Args:
        strict_mode (bool): If True, applies stricter filters for higher accuracy (High Precision Mode).
                            - RSI must be more extreme (<25 / >75)
                            - Trend Score > 75 required for trend trades
                            - Pattern confirmation required for reversals
                            - Only HIGH priority signals shown
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
    ts         = ta["trend_score"]

    # --- Strict Mode Settings ---
    rsi_buy_thresh = 25 if strict_mode else RSI_OVERSOLD
    rsi_sell_thresh = 75 if strict_mode else RSI_OVERBOUGHT
    trend_min_score = 75 if strict_mode else 50
    has_bullish_pattern = any(p["type"] == "bullish" and p["strength"] >= 3 for p in patterns)
    has_bearish_pattern = any(p["type"] == "bearish" and p["strength"] >= 3 for p in patterns)

    # ── RSI Oversold → BUY ───────────────────────────────────────────────────
    if rsi_val <= rsi_buy_thresh:
        # Strict Mode check: Must have bullish pattern OR very extreme RSI (<20)
        if not strict_mode or (strict_mode and (has_bullish_pattern or rsi_val < 20)):
            entry = price
            tp    = round(bb_mid or (price + 2 * atr), 5)
            sl    = round(price - 1.5 * atr, 5)
            conf  = 85 if (strict_mode and has_bullish_pattern) else 78
            recs.append({
                "action":     "BUY",
                "priority":   "HIGH",
                "area":       _fmt(entry, symbol),
                "reason":     f"RSI oversold ({rsi_val:.1f}) {'+ Bullish Pattern' if has_bullish_pattern else ''} — Strong Reversal",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": conf,
            })

    # ── RSI Overbought → SELL ────────────────────────────────────────────────
    if rsi_val >= rsi_sell_thresh:
        # Strict Mode check: Must have bearish pattern OR very extreme RSI (>80)
        if not strict_mode or (strict_mode and (has_bearish_pattern or rsi_val > 80)):
            entry = price
            tp    = round(bb_mid or (price - 2 * atr), 5)
            sl    = round(price + 1.5 * atr, 5)
            conf  = 85 if (strict_mode and has_bearish_pattern) else 75
            recs.append({
                "action":     "SELL",
                "priority":   "HIGH",
                "area":       _fmt(entry, symbol),
                "reason":     f"RSI overbought ({rsi_val:.1f}) {'+ Bearish Pattern' if has_bearish_pattern else ''} — Bearish Exhaustion",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": conf,
            })

    # ── Price at BB Lower Band → BUY ─────────────────────────────────────────
    if bb_signal == "BELOW_LOWER" and trend != "BEARISH":
        if not strict_mode or (strict_mode and has_bullish_pattern):
            entry = price
            tp    = round(bb_mid, 5)
            sl    = round(price - atr, 5)
            recs.append({
                "action":     "BUY",
                "priority":   "MEDIUM" if not strict_mode else "HIGH",
                "area":       _fmt(entry, symbol),
                "reason":     f"Price below Bollinger Lower Band — Mean Reversion",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 65 + (10 if has_bullish_pattern else 0),
            })

    # ── Price at BB Upper Band → SELL ────────────────────────────────────────
    if bb_signal == "ABOVE_UPPER" and trend != "BULLISH":
        if not strict_mode or (strict_mode and has_bearish_pattern):
            entry = price
            tp    = round(bb_mid, 5)
            sl    = round(price + atr, 5)
            recs.append({
                "action":     "SELL",
                "priority":   "MEDIUM" if not strict_mode else "HIGH",
                "area":       _fmt(entry, symbol),
                "reason":     f"Price above Bollinger Upper Band — Overbought Zone",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 63 + (10 if has_bearish_pattern else 0),
            })

    # ── MACD Crossover (Trend Following) ─────────────────────────────────────
    if macd > macd_sig and ta["macd_hist"] > 0:
        if ts >= trend_min_score:
            entry = price
            tp    = round(price + 2.5 * atr, 5)
            sl    = round(price - 1.5 * atr, 5)
            p     = "HIGH" if ts >= 80 else "MEDIUM"
            recs.append({
                "action":     "BUY",
                "priority":   p,
                "area":       _fmt(entry, symbol),
                "reason":     f"MACD Bullish Crossover + Strong Trend ({ts}/100)",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 60 + (ts // 4),
            })
    elif macd < macd_sig and ta["macd_hist"] < 0:
        if ts >= trend_min_score:
            entry = price
            tp    = round(price - 2.5 * atr, 5)
            sl    = round(price + 1.5 * atr, 5)
            p     = "HIGH" if ts >= 80 else "MEDIUM"
            recs.append({
                "action":     "SELL",
                "priority":   p,
                "area":       _fmt(entry, symbol),
                "reason":     f"MACD Bearish Crossover + Strong Trend ({ts}/100)",
                "target":     _fmt(tp, symbol),
                "sl":         _fmt(sl, symbol),
                "confidence": 60 + (ts // 4),
            })

    # ── Trend Hold Recommendations ────────────────────────────────────────────
    # In strict mode, we prioritize entries over holds, but if trend is SUPER strong (>85), we show HOLD.
    if trend == "BULLISH" and ts >= trend_min_score:
        tp = resistances[-1] if resistances else round(price + 3 * atr, 5)
        recs.append({
            "action":     "HOLD BUY",
            "priority":   "MEDIUM" if ts < 80 else "HIGH",
            "area":       _fmt(price, symbol),
            "reason":     f"Strong Bullish Trend ({ts}/100) — Ride the Trend",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(round(sma20 - atr, 5) if sma20 else round(price - 2*atr, 5), symbol),
            "confidence": 55 + ts // 5,
        })
    elif trend == "BEARISH" and ts >= trend_min_score:
        tp = supports[0] if supports else round(price - 3 * atr, 5)
        recs.append({
            "action":     "HOLD SELL",
            "priority":   "MEDIUM" if ts < 80 else "HIGH",
            "area":       _fmt(price, symbol),
            "reason":     f"Strong Bearish Trend ({ts}/100) — Follow Downside Momentum",
            "target":     _fmt(tp, symbol),
            "sl":         _fmt(round(sma20 + atr, 5) if sma20 else round(price + 2*atr, 5), symbol),
            "confidence": 55 + ts // 5,
        })

    # ── Support/Resistance Rejection (Counter-Trend) ─────────────────────────
    # Only in Standard Mode or if Pattern Confirmed in Strict Mode
    if supports:
        nearest_sup = min(supports, key=lambda s: abs(s - price))
        if abs(nearest_sup - price) / price < 0.005:
            if not strict_mode or (strict_mode and has_bullish_pattern):
                tp = round(price + 3 * atr, 5)
                sl = round(nearest_sup - atr, 5)
                recs.append({
                    "action":     "BUY",
                    "priority":   "MEDIUM",
                    "area":       _fmt(nearest_sup, symbol),
                    "reason":     f"Price bouncing off Key Support {_fmt(nearest_sup, symbol)}",
                    "target":     _fmt(tp, symbol),
                    "sl":         _fmt(sl, symbol),
                    "confidence": 62 + (10 if has_bullish_pattern else 0),
                })

    if resistances:
        nearest_res = min(resistances, key=lambda r: abs(r - price))
        if abs(nearest_res - price) / price < 0.005:
            if not strict_mode or (strict_mode and has_bearish_pattern):
                tp = round(price - 3 * atr, 5)
                sl = round(nearest_res + atr, 5)
                recs.append({
                    "action":     "SELL",
                    "priority":   "MEDIUM",
                    "area":       _fmt(nearest_res, symbol),
                    "reason":     f"Price rejecting Key Resistance {_fmt(nearest_res, symbol)}",
                    "target":     _fmt(tp, symbol),
                    "sl":         _fmt(sl, symbol),
                    "confidence": 60 + (10 if has_bearish_pattern else 0),
                })

    # ── Pattern-Based Only (If no other signal) ──────────────────────────────
    for p in patterns[:1]: # Check only strongest pattern
        if p["strength"] >= 4: # Strong patterns (Engulfing, Morning/Evening Star)
            target_conf = 50 + p["strength"] * 5

            if p["type"] == "bullish":
                if not strict_mode or (strict_mode and rsi_val < 45): # Filter bad pattern signals
                    tp = round(price + 2.5 * atr, 5)
                    sl = round(price - 1.5 * atr, 5)
                    recs.append({
                        "action":     "BUY",
                        "priority":   "HIGH",
                        "area":       _fmt(price, symbol),
                        "reason":     f"Strong Pattern '{p['name']}' Detected",
                        "target":     _fmt(tp, symbol),
                        "sl":         _fmt(sl, symbol),
                        "confidence": target_conf,
                    })
            elif p["type"] == "bearish":
                if not strict_mode or (strict_mode and rsi_val > 55):
                    tp = round(price - 2.5 * atr, 5)
                    sl = round(price + 1.5 * atr, 5)
                    recs.append({
                        "action":     "SELL",
                        "priority":   "HIGH",
                        "area":       _fmt(price, symbol),
                        "reason":     f"Strong Pattern '{p['name']}' Detected",
                        "target":     _fmt(tp, symbol),
                        "sl":         _fmt(sl, symbol),
                        "confidence": target_conf,
                    })

    # Deduplicate & Sort
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    seen   = set()
    unique = []

    # Filter for Strict Mode: Only show HIGH priority or Confidence > 70
    final_recs = []
    for r in recs:
        key = (r["action"], r["priority"])
        if key not in seen:
            seen.add(key)
            if strict_mode:
                if r["priority"] == "HIGH" or r["confidence"] >= 75:
                    final_recs.append(r)
            else:
                final_recs.append(r)

    final_recs.sort(key=lambda x: (priority_order[x["priority"]], -x["confidence"]))
    return final_recs[:5]
