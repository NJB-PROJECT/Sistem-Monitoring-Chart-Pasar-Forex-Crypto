"""
Chart Builder
Produces interactive Plotly charts: Candlestick + Indicators + Volume
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import COLORS


def build_main_chart(df: pd.DataFrame, ta: dict, patterns: list, symbol: str, timeframe: str) -> go.Figure:
    """
    Build a multi-panel chart:
      Panel 1 (60%): Candlestick + SMA20 + SMA50 + Bollinger Bands + S/R
      Panel 2 (20%): RSI
      Panel 3 (20%): MACD histogram + line
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=[f"{symbol} — {timeframe}", "RSI (14)", "MACD (12,26,9)"],
    )

    # ── Panel 1: Candlestick ──────────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="OHLC",
        increasing_line_color=COLORS["bullish"],
        decreasing_line_color=COLORS["bearish"],
        increasing_fillcolor=COLORS["bullish"],
        decreasing_fillcolor=COLORS["bearish"],
    ), row=1, col=1)

    # SMA20
    if "sma20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["sma20"], name="SMA 20",
            line=dict(color="#FFD600", width=1.5),
        ), row=1, col=1)

    # SMA50
    if "sma50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["sma50"], name="SMA 50",
            line=dict(color="#00B0FF", width=1.5),
        ), row=1, col=1)

    # Bollinger Bands
    if "bb_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["bb_upper"], name="BB Upper",
            line=dict(color="rgba(255,100,0,0.6)", width=1, dash="dot"),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["bb_lower"], name="BB Lower",
            line=dict(color="rgba(255,100,0,0.6)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(255,100,0,0.05)",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["bb_mid"], name="BB Mid",
            line=dict(color="rgba(255,100,0,0.4)", width=1),
        ), row=1, col=1)

    # Support levels
    for s in ta.get("supports", []):
        fig.add_hline(
            y=s, line_dash="dash", line_color="rgba(0,200,83,0.5)",
            line_width=1, annotation_text=f"S {s:.2f}",
            annotation_font_color="rgba(0,200,83,0.8)",
            row=1, col=1,
        )

    # Resistance levels
    for r in ta.get("resistances", []):
        fig.add_hline(
            y=r, line_dash="dash", line_color="rgba(255,23,68,0.5)",
            line_width=1, annotation_text=f"R {r:.2f}",
            annotation_font_color="rgba(255,23,68,0.8)",
            row=1, col=1,
        )

    # Pattern markers
    for pat in patterns:
        try:
            pat_time = pd.Timestamp(pat["candle_idx"])
            if pat_time in df.index:
                row_data = df.loc[pat_time]
                marker_y  = row_data["high"] * 1.002
                marker_sym = "triangle-up" if pat["type"] == "bullish" else ("triangle-down" if pat["type"] == "bearish" else "circle")
                marker_col = COLORS["bullish"] if pat["type"] == "bullish" else (COLORS["bearish"] if pat["type"] == "bearish" else COLORS["neutral"])
                fig.add_trace(go.Scatter(
                    x=[pat_time], y=[marker_y],
                    mode="markers+text",
                    marker=dict(symbol=marker_sym, size=14, color=marker_col),
                    text=[pat["name"]],
                    textposition="top center",
                    textfont=dict(size=9, color=marker_col),
                    name=pat["name"],
                    showlegend=False,
                ), row=1, col=1)
        except Exception:
            continue

    # ── Panel 2: RSI ─────────────────────────────────────────────────────────
    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["rsi"], name="RSI",
            line=dict(color="#AB47BC", width=1.5),
        ), row=2, col=1)

        fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,23,68,0.6)",  line_width=1, row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(0,200,83,0.6)",   line_width=1, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(150,150,150,0.3)", line_width=1, row=2, col=1)

        # Shade overbought/oversold
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,23,68,0.05)",  layer="below", row=2, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,200,83,0.05)",   layer="below", row=2, col=1)

    # ── Panel 3: MACD ─────────────────────────────────────────────────────────
    if "macd" in df.columns:
        colors = [COLORS["bullish"] if v >= 0 else COLORS["bearish"] for v in df["macd_hist"]]
        fig.add_trace(go.Bar(
            x=df.index, y=df["macd_hist"], name="MACD Hist",
            marker_color=colors, opacity=0.7,
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["macd"], name="MACD",
            line=dict(color="#FFD600", width=1.5),
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["macd_signal"], name="Signal",
            line=dict(color="#FF7043", width=1.5),
        ), row=3, col=1)

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(family="Inter, sans-serif", size=11, color=COLORS["text"]),
        legend=dict(
            bgcolor="rgba(22,27,34,0.8)", bordercolor=COLORS["border"],
            borderwidth=1, orientation="h", y=1.02,
        ),
        margin=dict(l=50, r=30, t=60, b=20),
        height=680,
        xaxis_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
    )

    for i in range(1, 4):
        fig.update_xaxes(
            gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
            showspikes=True, spikecolor=COLORS["subtext"],
            spikethickness=1, spikedash="dot",
            row=i, col=1,
        )
        fig.update_yaxes(
            gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
            showspikes=True, spikecolor=COLORS["subtext"],
            spikethickness=1, spikedash="dot",
            row=i, col=1,
        )

    return fig
