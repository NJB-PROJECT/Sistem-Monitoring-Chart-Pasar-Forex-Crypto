"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          ADVANCED TRADING ANALYZER  —  Professional Edition                 ║
║          Built with Python · Streamlit · Plotly · yfinance · TA-Lib         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

from config.settings import SYMBOLS, TIMEFRAMES, COLORS, PRIORITY_ICONS
from src.data_fetcher       import fetch_ohlcv, get_current_price
from src.technical_analysis import compute_all
from src.pattern_detection  import get_recent_patterns
from src.recommendation_engine import generate_recommendations, format_recommendation_text
from src.news_analyzer      import get_news_and_events
from src.chart_builder      import build_main_chart

# ────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Advanced Trading Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base ─────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  .main { background: #0D1117; }
  section[data-testid="stSidebar"] { background: #161B22 !important; border-right: 1px solid #30363D; }

  /* ── Header ───────────────────────────────────────────── */
  .app-header {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 50%, #161B22 100%);
    border: 1px solid #30363D; border-radius: 12px;
    padding: 20px 28px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 16px;
  }
  .app-title { font-size: 26px; font-weight: 700; color: #E6EDF3; }
  .app-sub   { font-size: 13px; color: #8B949E; margin-top: 2px; }
  .live-badge {
    background: #1A3A1A; border: 1px solid #00C853; border-radius: 20px;
    padding: 4px 12px; font-size: 11px; color: #00C853; font-weight: 600;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; } 50% { opacity: 0.6; }
  }

  /* ── Price Card ────────────────────────────────────────── */
  .price-card {
    background: #161B22; border: 1px solid #30363D; border-radius: 10px;
    padding: 16px 20px; text-align: center;
  }
  .price-main { font-size: 32px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
  .price-change-pos { color: #00C853; font-size: 14px; font-weight: 600; }
  .price-change-neg { color: #FF1744; font-size: 14px; font-weight: 600; }

  /* ── Metric Tile ───────────────────────────────────────── */
  .metric-tile {
    background: #161B22; border: 1px solid #30363D; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 8px;
  }
  .metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #8B949E; }
  .metric-value { font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

  /* ── Trend Badge ───────────────────────────────────────── */
  .trend-bullish { color: #00C853; background: #1A3A1A; border: 1px solid #00C853; border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 15px; display: inline-block; }
  .trend-bearish { color: #FF1744; background: #3A1A1A; border: 1px solid #FF1744; border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 15px; display: inline-block; }
  .trend-sideways { color: #FFD600; background: #3A3A1A; border: 1px solid #FFD600; border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 15px; display: inline-block; }

  /* ── Signal Bar ────────────────────────────────────────── */
  .signal-bar {
    background: #161B22; border: 1px solid #30363D; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
  }
  .signal-label { font-size: 12px; color: #8B949E; }
  .signal-value { font-size: 14px; font-weight: 600; }

  /* ── Recommendation Card ───────────────────────────────── */
  .rec-card {
    border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    border-left: 4px solid;
  }
  .rec-HIGH   { background: rgba(255,109,0,0.08);  border-color: #FF6D00; }
  .rec-MEDIUM { background: rgba(0,176,255,0.08);  border-color: #00B0FF; }
  .rec-LOW    { background: rgba(105,240,174,0.08);border-color: #69F0AE; }
  .rec-action { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
  .rec-reason { font-size: 12px; color: #C9D1D9; margin-bottom: 8px; }
  .rec-meta   { display: flex; gap: 16px; font-size: 12px; font-family: 'JetBrains Mono', monospace; }
  .rec-tp     { color: #00C853; font-weight: 600; }
  .rec-sl     { color: #FF1744; font-weight: 600; }
  .rec-conf   { color: #8B949E; }

  /* ── Pattern Card ──────────────────────────────────────── */
  .pat-card {
    background: #161B22; border: 1px solid #30363D; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
  }
  .pat-bullish { border-left: 3px solid #00C853 !important; }
  .pat-bearish { border-left: 3px solid #FF1744 !important; }
  .pat-neutral { border-left: 3px solid #FFD600 !important; }

  /* ── News Card ─────────────────────────────────────────── */
  .news-card {
    background: #161B22; border: 1px solid #30363D; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px;
  }
  .news-title  { font-size: 14px; font-weight: 600; color: #E6EDF3; margin-bottom: 6px; }
  .news-meta   { font-size: 11px; color: #8B949E; margin-bottom: 8px; }
  .news-summary{ font-size: 12px; color: #C9D1D9; line-height: 1.5; }
  .impact-HIGH  { color: #FF1744; font-weight: 700; }
  .impact-MEDIUM{ color: #FFD600; font-weight: 700; }
  .impact-LOW   { color: #69F0AE; font-weight: 700; }

  /* ── Event Row ─────────────────────────────────────────── */
  .event-row {
    background: #161B22; border: 1px solid #30363D; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
  }

  /* ── Progress Bar ──────────────────────────────────────── */
  .conf-bar-wrap { width: 100%; background: #30363D; border-radius: 4px; height: 5px; margin-top: 4px; }
  .conf-bar-fill { height: 5px; border-radius: 4px; }

  /* ── Section Title ─────────────────────────────────────── */
  .section-title {
    font-size: 14px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #8B949E; border-bottom: 1px solid #30363D;
    padding-bottom: 8px; margin-bottom: 14px;
  }

  /* Streamlit tweaks */
  div[data-testid="stMetric"] { display: none; }
  .stSelectbox label, .stSlider label { color: #8B949E !important; font-size: 12px !important; }
  div.stButton > button {
    background: linear-gradient(135deg, #1C2128, #238636);
    color: #fff; border: 1px solid #238636; border-radius: 8px;
    font-weight: 600; width: 100%; padding: 10px;
    transition: all 0.2s;
  }
  div.stButton > button:hover { background: #2EA043; border-color: #2EA043; }
  .stProgress > div > div > div { background: #238636 !important; }
  div[data-testid="stExpander"] { background: #161B22; border: 1px solid #30363D; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ────────────────────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None
if "data_cache"   not in st.session_state:
    st.session_state.data_cache   = {}


# ────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────────────────────────────────
def trend_badge(trend: str) -> str:
    icons = {"BULLISH": "▲", "BEARISH": "▼", "SIDEWAYS": "◆"}
    return f'<span class="trend-{trend.lower()}">{icons.get(trend,"●")} {trend}</span>'


def rsi_color(val: float) -> str:
    if val >= 70: return "#FF1744"
    if val <= 30: return "#00C853"
    return "#FFD600"


def action_emoji(action: str) -> str:
    return {"BUY": "🟢 BUY", "SELL": "🔴 SELL",
            "HOLD BUY": "🔵 HOLD BUY", "HOLD SELL": "🔵 HOLD SELL"}.get(action, action)


def confidence_bar(conf: int) -> str:
    color = "#00C853" if conf >= 70 else ("#FFD600" if conf >= 50 else "#FF1744")
    return (
        f'<div class="conf-bar-wrap">'
        f'<div class="conf-bar-fill" style="width:{conf}%;background:{color}"></div>'
        f'</div>'
    )


# ────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    symbol = st.selectbox(
        "📌 Symbol",
        list(SYMBOLS.keys()),
        index=0,
    )
    timeframe = st.selectbox(
        "🕐 Timeframe",
        list(TIMEFRAMES.keys()),
        index=3,
    )

    st.markdown("---")
    st.markdown("**📊 Indicator Settings**")
    rsi_period  = st.slider("RSI Period",   7,  21, 14)
    sma_s       = st.slider("SMA Short",   10,  30, 20)
    sma_l       = st.slider("SMA Long",    30, 100, 50)
    bb_std      = st.slider("BB Std Dev",   1.0, 3.0, 2.0, step=0.5)

    st.markdown("---")
    refresh_btn = st.button("🔄 Refresh Data", use_container_width=True)

    if st.session_state.last_refresh:
        st.markdown(
            f'<div style="text-align:center;color:#8B949E;font-size:11px;margin-top:8px">'
            f'Last updated: {st.session_state.last_refresh.strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#8B949E;line-height:1.6;">
    <b style="color:#E6EDF3">How to use:</b><br>
    1. Select a trading symbol<br>
    2. Choose timeframe<br>
    3. Click Refresh Data<br>
    4. Review analysis & recommendations<br><br>
    ⚠️ <b style="color:#FFD600">Disclaimer:</b> For educational use only. Always manage your risk.
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  MAIN HEADER
# ────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div style="font-size:40px">📊</div>
  <div>
    <div class="app-title">Advanced Trading Analyzer</div>
    <div class="app-sub">Professional Technical Analysis · Pattern Recognition · AI Recommendations</div>
  </div>
  <div style="margin-left:auto">
    <span class="live-badge">● LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  LOAD / REFRESH DATA
# ────────────────────────────────────────────────────────────────────────────
cache_key = f"{symbol}_{timeframe}"

if refresh_btn or cache_key not in st.session_state.data_cache:
    with st.spinner(f"⏳ Fetching {symbol} data on {timeframe}..."):
        try:
            df_raw   = fetch_ohlcv(symbol, timeframe)
            ta       = compute_all(df_raw)
            patterns = get_recent_patterns(ta["df"])
            recs     = generate_recommendations(ta, patterns, symbol)
            price_info = get_current_price(symbol)
            news, events = get_news_and_events(symbol)

            st.session_state.data_cache[cache_key] = {
                "ta": ta, "patterns": patterns, "recs": recs,
                "price_info": price_info, "news": news, "events": events,
            }
            st.session_state.last_refresh = datetime.now()
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.stop()

data     = st.session_state.data_cache[cache_key]
ta       = data["ta"]
patterns = data["patterns"]
recs     = data["recs"]
pi       = data["price_info"]
news     = data["news"]
events   = data["events"]
df       = ta["df"]


# ────────────────────────────────────────────────────────────────────────────
#  TOP PRICE BAR
# ────────────────────────────────────────────────────────────────────────────
price      = pi.get("price", ta["price"])
change     = pi.get("change", 0)
change_pct = pi.get("change_pct", 0)
high_24    = pi.get("high_24h", 0)
low_24     = pi.get("low_24h",  0)
change_cls = "price-change-pos" if change >= 0 else "price-change-neg"
change_sign= "+" if change >= 0 else ""

c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.2, 1.2, 1.2])
with c1:
    price_color = COLORS["bullish"] if change >= 0 else COLORS["bearish"]
    st.markdown(f"""
    <div class="price-card">
      <div style="font-size:12px;color:#8B949E;margin-bottom:4px">{symbol}</div>
      <div class="price-main" style="color:{price_color}">{price:,.5g}</div>
      <div class="{change_cls}">{change_sign}{change:.5g} ({change_sign}{change_pct:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-tile">
      <div class="metric-label">Trend</div>
      {trend_badge(ta["trend"])}
      <div style="font-size:11px;color:#8B949E;margin-top:4px">Score: {ta["trend_score"]}/100</div>
    </div>""", unsafe_allow_html=True)
with c3:
    rc = rsi_color(ta["rsi"])
    st.markdown(f"""
    <div class="metric-tile">
      <div class="metric-label">RSI (14)</div>
      <div class="metric-value" style="color:{rc}">{ta["rsi"]:.1f}</div>
      <div style="font-size:11px;color:#8B949E">{ta["rsi_signal"]}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-tile">
      <div class="metric-label">24H High</div>
      <div class="metric-value" style="color:#00C853">{high_24:,.5g}</div>
    </div>
    <div class="metric-tile" style="margin-top:8px">
      <div class="metric-label">24H Low</div>
      <div class="metric-value" style="color:#FF1744">{low_24:,.5g}</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-tile">
      <div class="metric-label">ATR (14)</div>
      <div class="metric-value" style="color:#FFD600">{ta["atr"]:.5g}</div>
    </div>
    <div class="metric-tile" style="margin-top:8px">
      <div class="metric-label">Timeframe</div>
      <div class="metric-value" style="color:#E6EDF3;font-size:18px">{timeframe}</div>
    </div>""", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  MAIN CHART
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Price Chart & Indicators</div>', unsafe_allow_html=True)
fig = build_main_chart(df, ta, patterns, symbol, timeframe)
st.plotly_chart(fig, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
#  ANALYSIS PANELS (Technical | Patterns | Levels)
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Technical Analysis Summary</div>', unsafe_allow_html=True)

col_tech, col_pat, col_lvl = st.columns([1.4, 1.2, 1.4])

# ── Technical Signals ──────────────────────────────────────────────────────
with col_tech:
    def sig_bar(label, value, color="#E6EDF3", sub=""):
        return f"""
        <div class="signal-bar">
          <div>
            <div class="signal-label">{label}</div>
            {f'<div style="font-size:11px;color:#8B949E">{sub}</div>' if sub else ''}
          </div>
          <div class="signal-value" style="color:{color}">{value}</div>
        </div>"""

    sma20_color = "#00C853" if ta["price"] > (ta["sma20"] or 0) else "#FF1744"
    sma50_color = "#00C853" if ta["price"] > (ta["sma50"] or 0) else "#FF1744"
    macd_col    = "#00C853" if ta["macd"] > ta["macd_signal"] else "#FF1744"
    bb_col_map  = {
        "BELOW_LOWER": "#00C853",  "ABOVE_UPPER": "#FF1744",
        "ABOVE_MID":   "#FFD600",  "BELOW_MID":   "#8B949E",
    }

    st.markdown(
        sig_bar("SMA 20", ta["sma20"] or "N/A", sma20_color, f"Price {'above' if ta['price'] > (ta['sma20'] or 0) else 'below'} SMA20") +
        sig_bar("SMA 50", ta["sma50"] or "N/A", sma50_color, f"Price {'above' if ta['price'] > (ta['sma50'] or 0) else 'below'} SMA50") +
        sig_bar("RSI", f"{ta['rsi']:.2f}", rsi_color(ta["rsi"]), ta["rsi_signal"]) +
        sig_bar("MACD", f"{ta['macd']:.5g}", macd_col, f"Signal: {ta['macd_signal']:.5g}") +
        sig_bar("BB Upper", ta["bb_upper"] or "N/A", "#FF7043") +
        sig_bar("BB Mid",   ta["bb_mid"]   or "N/A", "#FFA726") +
        sig_bar("BB Lower", ta["bb_lower"] or "N/A", "#66BB6A") +
        sig_bar("BB Signal", ta["bb_signal"].replace("_", " "), bb_col_map.get(ta["bb_signal"], "#E6EDF3")),
        unsafe_allow_html=True,
    )

# ── Detected Patterns ──────────────────────────────────────────────────────
with col_pat:
    if patterns:
        for p in patterns:
            icon = "▲" if p["type"] == "bullish" else ("▼" if p["type"] == "bearish" else "◆")
            col_ = "#00C853" if p["type"] == "bullish" else ("#FF1744" if p["type"] == "bearish" else "#FFD600")
            stars = "★" * p["strength"] + "☆" * (5 - p["strength"])
            st.markdown(f"""
            <div class="pat-card pat-{p['type']}">
              <div>
                <div style="font-size:13px;font-weight:600;color:{col_}">{icon} {p['name']}</div>
                <div style="font-size:11px;color:#8B949E">{p['desc']}</div>
              </div>
              <div style="text-align:right">
                <div style="font-size:11px;color:#FFD600">{stars}</div>
                <div style="font-size:11px;color:#8B949E">{p['type'].upper()}</div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-tile" style="text-align:center;color:#8B949E">
          🔍 No significant patterns detected<br>
          <span style="font-size:11px">in recent candles</span>
        </div>""", unsafe_allow_html=True)

# ── Support & Resistance ───────────────────────────────────────────────────
with col_lvl:
    st.markdown("**🔴 Resistance Levels**")
    if ta["resistances"]:
        for i, r in enumerate(reversed(ta["resistances"])):
            dist = abs(r - ta["price"]) / ta["price"] * 100
            st.markdown(f"""
            <div class="signal-bar">
              <div>
                <div style="font-size:13px;font-weight:600;color:#FF1744">R{len(ta['resistances'])-i}: {r:,.5g}</div>
                <div style="font-size:11px;color:#8B949E">Dist: {dist:.2f}%</div>
              </div>
              <div style="font-size:16px">🔴</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No resistance levels found")

    st.markdown("**🟢 Support Levels**")
    if ta["supports"]:
        for i, s in enumerate(ta["supports"]):
            dist = abs(s - ta["price"]) / ta["price"] * 100
            st.markdown(f"""
            <div class="signal-bar">
              <div>
                <div style="font-size:13px;font-weight:600;color:#00C853">S{i+1}: {s:,.5g}</div>
                <div style="font-size:11px;color:#8B949E">Dist: {dist:.2f}%</div>
              </div>
              <div style="font-size:16px">🟢</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No support levels found")


st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Trading Recommendations</div>', unsafe_allow_html=True)

if not recs:
    st.warning("⚠️ No strong signals detected. Market may be ranging — wait for confirmation.")
else:
    cols_rec = st.columns(2)
    for i, rec in enumerate(recs):
        col = cols_rec[i % 2]
        with col:
            pri_icon   = PRIORITY_ICONS[rec["priority"]]
            action_col = "#00C853" if "BUY" in rec["action"] else "#FF1744"
            if "HOLD" in rec["action"]:
                action_col = "#00B0FF"

            st.markdown(f"""
            <div class="rec-card rec-{rec['priority']}">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div class="rec-action" style="color:{action_col}">{action_emoji(rec['action'])}</div>
                <div style="font-size:12px;color:#8B949E">{pri_icon} {rec['priority']} PRIORITY</div>
              </div>
              <div style="font-size:13px;color:#8B949E;margin:2px 0 4px">📍 Area: <b style="color:#E6EDF3">{rec['area']}</b></div>
              <div class="rec-reason">{rec['reason']}</div>
              <div class="rec-meta">
                <span class="rec-tp">🎯 TP: {rec['target']}</span>
                <span class="rec-sl">🛡️ SL: {rec['sl']}</span>
                <span class="rec-conf">📊 {rec['confidence']}%</span>
              </div>
              {confidence_bar(rec['confidence'])}
            </div>""", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  NEWS & ECONOMIC CALENDAR
# ────────────────────────────────────────────────────────────────────────────
col_news, col_cal = st.columns([1.6, 1.4])

# ── Market News ────────────────────────────────────────────────────────────
with col_news:
    st.markdown('<div class="section-title">📰 Market News & Analysis</div>', unsafe_allow_html=True)

    if not news:
        st.info(f"No relevant news found for {symbol}.")
    else:
        for item in news:
            imp_cls = f"impact-{item['impact']}"
            dir_str = item.get("direction", "")
            dir_col = (
                "#00C853" if "BULLISH" in dir_str else
                "#FF1744" if "BEARISH" in dir_str else
                "#FFD600"
            )
            st.markdown(f"""
            <div class="news-card">
              <div class="news-title">{item['title']}</div>
              <div class="news-meta">
                🕐 {item['published']} &nbsp;|&nbsp; 📌 {item['source']}
                &nbsp;|&nbsp; Impact: <span class="{imp_cls}">{item['impact']}</span>
              </div>
              <div class="news-summary">{item['summary']}</div>
              <div style="margin-top:8px;font-size:12px;font-weight:600;color:{dir_col}">{dir_str}</div>
            </div>""", unsafe_allow_html=True)

# ── Economic Calendar ──────────────────────────────────────────────────────
with col_cal:
    st.markdown('<div class="section-title">🗓️ Economic Calendar</div>', unsafe_allow_html=True)

    for ev in events:
        imp_col = "#FF1744" if ev["impact"] == "HIGH" else ("#FFD600" if ev["impact"] == "MEDIUM" else "#69F0AE")
        st.markdown(f"""
        <div class="event-row">
          <div>
            <div style="font-size:13px;font-weight:600;color:#E6EDF3">{ev['event']}</div>
            <div style="font-size:11px;color:#8B949E">🕐 {ev['time']}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:12px;font-weight:700;color:{imp_col}">{ev['impact']}</div>
            <div style="font-size:11px;color:#8B949E">Forecast: {ev['forecast']}</div>
          </div>
        </div>""", unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:20px;color:#8B949E;font-size:12px;border-top:1px solid #30363D;margin-top:10px">
  <b style="color:#E6EDF3">⚡ Advanced Trading Analyzer</b> &nbsp;|&nbsp;
  Built with Python · Streamlit · Plotly · yfinance &nbsp;|&nbsp;
  Data: Yahoo Finance &nbsp;|&nbsp;
  Last Update: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.last_refresh else 'N/A'}
  <br><br>
  <span style="color:#FF6D00">⚠️ DISCLAIMER: This application is for educational and informational purposes only.
  It does not constitute financial advice. Always do your own research and manage your risk.</span>
</div>
""", unsafe_allow_html=True)
