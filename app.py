"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ADVANCED TRADING ANALYZER  —  Professional Edition  v2.0             ║
║        Python · Streamlit · Plotly · yfinance · Twelvedata · AlphaVantage   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from config.settings import (
    SYMBOLS, TIMEFRAMES, COLORS, PRIORITY_ICONS,
    PROVIDERS, load_api_keys, save_api_keys,
)
from src.data_fetcher          import fetch_ohlcv, get_current_price
from src.technical_analysis    import compute_all
from src.pattern_detection     import get_recent_patterns
from src.recommendation_engine import generate_recommendations
from src.news_analyzer         import get_news_and_events
from src.chart_builder         import build_main_chart

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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"]   { font-family: 'Inter', sans-serif !important; }
  .main                        { background: #0D1117; }
  section[data-testid="stSidebar"] {
    background: #161B22 !important;
    border-right: 1px solid #30363D;
  }

  /* ── App Header ── */
  .app-header {
    background: linear-gradient(135deg,#161B22 0%,#1C2128 50%,#161B22 100%);
    border:1px solid #30363D; border-radius:12px;
    padding:20px 28px; margin-bottom:20px;
    display:flex; align-items:center; gap:16px;
  }
  .app-title { font-size:26px; font-weight:700; color:#E6EDF3; }
  .app-sub   { font-size:13px; color:#8B949E; margin-top:2px; }
  .live-badge {
    background:#1A3A1A; border:1px solid #00C853; border-radius:20px;
    padding:4px 12px; font-size:11px; color:#00C853; font-weight:600;
    animation:pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.55} }

  /* ── Cards ── */
  .price-card {
    background:#161B22; border:1px solid #30363D; border-radius:10px;
    padding:16px 20px; text-align:center;
  }
  .price-main      { font-size:32px; font-weight:700; font-family:'JetBrains Mono',monospace; }
  .price-change-pos{ color:#00C853; font-size:14px; font-weight:600; }
  .price-change-neg{ color:#FF1744; font-size:14px; font-weight:600; }

  .metric-tile {
    background:#161B22; border:1px solid #30363D; border-radius:10px;
    padding:14px 18px; margin-bottom:8px;
  }
  .metric-label{ font-size:11px; text-transform:uppercase; letter-spacing:.8px; color:#8B949E; }
  .metric-value{ font-size:20px; font-weight:700; font-family:'JetBrains Mono',monospace; }

  /* ── Trend Badges ── */
  .trend-bullish  { color:#00C853;background:#1A3A1A;border:1px solid #00C853;border-radius:8px;padding:6px 14px;font-weight:700;font-size:15px;display:inline-block; }
  .trend-bearish  { color:#FF1744;background:#3A1A1A;border:1px solid #FF1744;border-radius:8px;padding:6px 14px;font-weight:700;font-size:15px;display:inline-block; }
  .trend-sideways { color:#FFD600;background:#3A3A1A;border:1px solid #FFD600;border-radius:8px;padding:6px 14px;font-weight:700;font-size:15px;display:inline-block; }

  /* ── Signal Bar ── */
  .signal-bar {
    background:#161B22; border:1px solid #30363D; border-radius:10px;
    padding:12px 16px; margin-bottom:6px;
    display:flex; justify-content:space-between; align-items:center;
  }
  .signal-label{ font-size:12px; color:#8B949E; }
  .signal-value{ font-size:14px; font-weight:600; }

  /* ── Rec Cards ── */
  .rec-card { border-radius:10px; padding:14px 18px; margin-bottom:10px; border-left:4px solid; }
  .rec-HIGH   { background:rgba(255,109,0,.08);  border-color:#FF6D00; }
  .rec-MEDIUM { background:rgba(0,176,255,.08);  border-color:#00B0FF; }
  .rec-LOW    { background:rgba(105,240,174,.08);border-color:#69F0AE; }
  .rec-action { font-size:16px; font-weight:700; margin-bottom:4px; }
  .rec-reason { font-size:12px; color:#C9D1D9; margin-bottom:8px; }
  .rec-meta   { display:flex; gap:16px; font-size:12px; font-family:'JetBrains Mono',monospace; }
  .rec-tp     { color:#00C853; font-weight:600; }
  .rec-sl     { color:#FF1744; font-weight:600; }

  /* ── Pattern Cards ── */
  .pat-card {
    background:#161B22; border:1px solid #30363D; border-radius:8px;
    padding:10px 14px; margin-bottom:6px;
    display:flex; justify-content:space-between; align-items:center;
  }
  .pat-bullish{ border-left:3px solid #00C853!important; }
  .pat-bearish{ border-left:3px solid #FF1744!important; }
  .pat-neutral{ border-left:3px solid #FFD600!important; }

  /* ── News / Events ── */
  .news-card {
    background:#161B22; border:1px solid #30363D; border-radius:10px;
    padding:14px 18px; margin-bottom:10px;
  }
  .news-title  { font-size:14px; font-weight:600; color:#E6EDF3; margin-bottom:6px; }
  .news-meta   { font-size:11px; color:#8B949E; margin-bottom:8px; }
  .news-summary{ font-size:12px; color:#C9D1D9; line-height:1.5; }
  .impact-HIGH  { color:#FF1744; font-weight:700; }
  .impact-MEDIUM{ color:#FFD600; font-weight:700; }
  .impact-LOW   { color:#69F0AE; font-weight:700; }

  .event-row {
    background:#161B22; border:1px solid #30363D; border-radius:8px;
    padding:10px 14px; margin-bottom:6px;
    display:flex; justify-content:space-between; align-items:center;
  }

  /* ── Misc ── */
  .conf-bar-wrap { width:100%; background:#30363D; border-radius:4px; height:5px; margin-top:4px; }
  .conf-bar-fill { height:5px; border-radius:4px; }

  .section-title {
    font-size:14px; font-weight:700; text-transform:uppercase;
    letter-spacing:1px; color:#8B949E;
    border-bottom:1px solid #30363D; padding-bottom:8px; margin-bottom:14px;
  }

  /* Streamlit overrides */
  div[data-testid="stMetric"]  { display:none; }
  .stSelectbox label, .stSlider label { color:#8B949E!important; font-size:12px!important; }
  div.stButton > button {
    background:linear-gradient(135deg,#1C2128,#238636);
    color:#fff; border:1px solid #238636; border-radius:8px;
    font-weight:600; width:100%; padding:10px; transition:all .2s;
  }
  div.stButton > button:hover { background:#2EA043; border-color:#2EA043; }
  div[data-testid="stExpander"] {
    background:#161B22; border:1px solid #30363D!important; border-radius:8px;
  }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ────────────────────────────────────────────────────────────────────────────
for _k, _v in {
    "last_refresh":    None,
    "data_cache":      {},
    "active_provider": "synthetic",
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


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
    return {"BUY":"🟢 BUY","SELL":"🔴 SELL",
            "HOLD BUY":"🔵 HOLD BUY","HOLD SELL":"🔵 HOLD SELL"}.get(action, action)

def confidence_bar(conf: int) -> str:
    c = "#00C853" if conf >= 70 else ("#FFD600" if conf >= 50 else "#FF1744")
    return (f'<div class="conf-bar-wrap">'
            f'<div class="conf-bar-fill" style="width:{conf}%;background:{c}"></div>'
            f'</div>')


# ────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Trading Analyzer")
    st.markdown("---")

    # Symbol & Timeframe
    symbol    = st.selectbox("📌 Symbol",    list(SYMBOLS.keys()),    index=0)
    timeframe = st.selectbox("🕐 Timeframe", list(TIMEFRAMES.keys()), index=3)

    st.markdown("---")
    st.markdown("**📐 Indicator Settings**")
    rsi_period = st.slider("RSI Period",  7,  21,  14)
    sma_s      = st.slider("SMA Short",  10,  30,  20)
    sma_l      = st.slider("SMA Long",   30, 100,  50)
    bb_std_val = st.slider("BB Std Dev", 1.0, 3.0, 2.0, step=0.5)

    st.markdown("---")
    refresh_btn = st.button("🔄 Refresh Data", use_container_width=True)

    # Active provider badge (shown after first load)
    if st.session_state.last_refresh:
        prov_name = st.session_state.active_provider
        pc        = PROVIDERS.get(prov_name, PROVIDERS["synthetic"])
        ts_str    = st.session_state.last_refresh.strftime("%H:%M:%S")
        st.markdown(
            f'<div style="text-align:center;margin-top:6px">'
            f'<div style="font-size:11px;color:#8B949E">Last update: {ts_str}</div>'
            f'<div style="margin-top:4px;font-size:11px;padding:3px 10px;border-radius:12px;display:inline-block;'
            f'background:{pc["color"]}22;color:{pc["color"]};border:1px solid {pc["color"]}55">'
            f'{pc["icon"]} {pc["name"]}</div></div>',
            unsafe_allow_html=True,
        )

    # ── API Key Settings ──────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔑 API Key Settings", expanded=False):
        cur_keys = load_api_keys()

        st.markdown(
            '<div style="font-size:12px;color:#8B949E;margin-bottom:10px">'
            'Prioritas otomatis: <b style="color:#7C4DFF">Twelvedata</b> → '
            '<b style="color:#FF6D00">Alpha Vantage</b> → '
            '<b style="color:#720E9E">yfinance</b></div>',
            unsafe_allow_html=True,
        )

        # Provider selector
        prov_options = list(PROVIDERS.keys())
        prov_labels  = [f"{v['icon']} {v['name']}" for v in PROVIDERS.values()]
        cur_prov_idx = prov_options.index(cur_keys.get("active_provider", "auto"))
        sel_label    = st.selectbox(
            "🔧 Data Provider", prov_labels, index=cur_prov_idx,
            help="Auto = pakai provider terbaik yang tersedia",
        )
        sel_provider = prov_options[prov_labels.index(sel_label)]

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

        # Twelvedata key
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#7C4DFF;margin-bottom:4px">'
            '📡 Twelvedata API Key</div>', unsafe_allow_html=True)
        td_input = st.text_input(
            "td_key", value=cur_keys.get("twelvedata",""),
            type="password", placeholder="e.g. e51267ecb483...",
            label_visibility="collapsed",
        )
        st.markdown(
            '<div style="font-size:10px;color:#8B949E;margin-bottom:10px">'
            '✅ Gratis 800 req/day · Forex/Crypto/Stock real-time<br>'
            '🔗 <a href="https://twelvedata.com/register" target="_blank" '
            'style="color:#7C4DFF">Daftar di twelvedata.com</a></div>',
            unsafe_allow_html=True,
        )

        # Alpha Vantage key
        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#FF6D00;margin-bottom:4px">'
            '📊 Alpha Vantage API Key</div>', unsafe_allow_html=True)
        av_input = st.text_input(
            "av_key", value=cur_keys.get("alpha_vantage",""),
            type="password", placeholder="e.g. XZLEREJGO3A0...",
            label_visibility="collapsed",
        )
        st.markdown(
            '<div style="font-size:10px;color:#8B949E;margin-bottom:12px">'
            '✅ Gratis 25 req/day · Forex/Crypto/Stock<br>'
            '🔗 <a href="https://www.alphavantage.co/support/#api-key" target="_blank" '
            'style="color:#FF6D00">Daftar di alphavantage.co</a></div>',
            unsafe_allow_html=True,
        )

        if st.button("💾 Simpan API Keys", use_container_width=True):
            save_api_keys({
                "twelvedata":      td_input.strip(),
                "alpha_vantage":   av_input.strip(),
                "active_provider": sel_provider,
            })
            st.session_state.data_cache = {}   # force re-fetch with new keys
            st.success("✅ Tersimpan! Klik Refresh Data.")

        # Status badges
        td_ok = bool(cur_keys.get("twelvedata","").strip())
        av_ok = bool(cur_keys.get("alpha_vantage","").strip())
        st.markdown(f"""
        <div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap">
          <span style="font-size:10px;padding:2px 8px;border-radius:10px;
            background:{'#1A3A1A' if td_ok else '#3A1A1A'};
            color:{'#00C853' if td_ok else '#FF1744'};
            border:1px solid {'#00C85344' if td_ok else '#FF174444'}">
            📡 Twelvedata {'✓ Active' if td_ok else '✗ No Key'}
          </span>
          <span style="font-size:10px;padding:2px 8px;border-radius:10px;
            background:{'#1A3A1A' if av_ok else '#3A1A1A'};
            color:{'#00C853' if av_ok else '#FF1744'};
            border:1px solid {'#00C85344' if av_ok else '#FF174444'}">
            📊 Alpha Vantage {'✓ Active' if av_ok else '✗ No Key'}
          </span>
        </div>
        """, unsafe_allow_html=True)

    # Help
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#8B949E;line-height:1.7">
    <b style="color:#E6EDF3">📖 Cara Pakai:</b><br>
    1. Buka 🔑 API Settings, masukkan key<br>
    2. Klik 💾 Simpan API Keys<br>
    3. Pilih Symbol &amp; Timeframe<br>
    4. Klik 🔄 Refresh Data<br><br>
    ⚠️ <b style="color:#FFD600">Disclaimer:</b><br>
    Hanya untuk edukasi. Kelola risiko Anda!
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  LOAD / REFRESH DATA   ← must happen BEFORE rendering main content
# ────────────────────────────────────────────────────────────────────────────
cache_key = f"{symbol}_{timeframe}"

if refresh_btn or cache_key not in st.session_state.data_cache:
    with st.spinner(f"⏳ Mengambil data {symbol} ({timeframe})..."):
        try:
            df_raw, used_provider = fetch_ohlcv(symbol, timeframe)
            ta          = compute_all(df_raw)
            patterns    = get_recent_patterns(ta["df"])
            recs        = generate_recommendations(ta, patterns, symbol)
            price_info  = get_current_price(symbol)
            news, events = get_news_and_events(symbol)

            st.session_state.data_cache[cache_key] = {
                "ta": ta, "patterns": patterns, "recs": recs,
                "price_info": price_info, "news": news, "events": events,
                "provider": used_provider,
            }
            st.session_state.last_refresh    = datetime.now()
            st.session_state.active_provider = used_provider

        except Exception as e:
            st.error(f"❌ Gagal mengambil data: {e}")
            st.stop()

# Unpack from cache
_cache       = st.session_state.data_cache[cache_key]
ta           = _cache["ta"]
patterns     = _cache["patterns"]
recs         = _cache["recs"]
pi           = _cache["price_info"]
news         = _cache["news"]
events       = _cache["events"]
df           = ta["df"]
used_provider = _cache.get("provider", "synthetic")
prov_cfg      = PROVIDERS.get(used_provider, PROVIDERS["synthetic"])


# ────────────────────────────────────────────────────────────────────────────
#  APP HEADER  (rendered AFTER data is loaded — prov_cfg is defined)
# ────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div style="font-size:40px">📊</div>
  <div>
    <div class="app-title">Advanced Trading Analyzer</div>
    <div class="app-sub">Professional Technical Analysis · Pattern Recognition · AI Recommendations</div>
  </div>
  <div style="margin-left:auto;display:flex;flex-direction:column;align-items:flex-end;gap:6px">
    <span class="live-badge">● LIVE</span>
    <span style="font-size:11px;background:{prov_cfg['color']}22;color:{prov_cfg['color']};
      border:1px solid {prov_cfg['color']}55;border-radius:12px;padding:3px 10px;display:inline-block">
      {prov_cfg['icon']} Data: {prov_cfg['name']}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  TOP PRICE BAR
# ────────────────────────────────────────────────────────────────────────────
price       = pi.get("price",      ta["price"])
change      = pi.get("change",     0)
change_pct  = pi.get("change_pct", 0)
high_24     = pi.get("high_24h",   price)
low_24      = pi.get("low_24h",    price)
chg_cls     = "price-change-pos" if change >= 0 else "price-change-neg"
chg_sign    = "+" if change >= 0 else ""
price_color = COLORS["bullish"] if change >= 0 else COLORS["bearish"]

c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.2, 1.2, 1.2])

with c1:
    st.markdown(f"""
    <div class="price-card">
      <div style="font-size:12px;color:#8B949E;margin-bottom:4px">{symbol}</div>
      <div class="price-main" style="color:{price_color}">{price:,.5g}</div>
      <div class="{chg_cls}">{chg_sign}{change:.5g} ({chg_sign}{change_pct:.2f}%)</div>
    </div>""", unsafe_allow_html=True)

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
    <div class="metric-tile" style="margin-top:0">
      <div class="metric-label">24H Low</div>
      <div class="metric-value" style="color:#FF1744">{low_24:,.5g}</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-tile">
      <div class="metric-label">ATR (14)</div>
      <div class="metric-value" style="color:#FFD600">{ta["atr"]:.5g}</div>
    </div>
    <div class="metric-tile" style="margin-top:0">
      <div class="metric-label">Timeframe</div>
      <div class="metric-value" style="font-size:18px;color:#E6EDF3">{timeframe}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  PRICE CHART
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Price Chart & Indicators</div>', unsafe_allow_html=True)
fig = build_main_chart(df, ta, patterns, symbol, timeframe)
st.plotly_chart(fig, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
#  TECHNICAL ANALYSIS SUMMARY
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Technical Analysis Summary</div>', unsafe_allow_html=True)

col_tech, col_pat, col_lvl = st.columns([1.4, 1.2, 1.4])

# ── Indicator signals ─────────────────────────────────────────────────────
with col_tech:
    def sig_bar(label, value, color="#E6EDF3", sub=""):
        sub_html = f'<div style="font-size:11px;color:#8B949E">{sub}</div>' if sub else ""
        return f"""
        <div class="signal-bar">
          <div><div class="signal-label">{label}</div>{sub_html}</div>
          <div class="signal-value" style="color:{color}">{value}</div>
        </div>"""

    sma20_c = "#00C853" if ta["price"] > (ta["sma20"] or 0) else "#FF1744"
    sma50_c = "#00C853" if ta["price"] > (ta["sma50"] or 0) else "#FF1744"
    macd_c  = "#00C853" if ta["macd"]  > ta["macd_signal"] else "#FF1744"
    bb_col  = {"BELOW_LOWER":"#00C853","ABOVE_UPPER":"#FF1744",
               "ABOVE_MID":"#FFD600","BELOW_MID":"#8B949E"}

    sma20_val = f"{ta['sma20']:,.5g}" if ta["sma20"] else "N/A"
    sma50_val = f"{ta['sma50']:,.5g}" if ta["sma50"] else "N/A"
    sma20_sub = f"Price {'above' if ta['price'] > (ta['sma20'] or 0) else 'below'} SMA20"
    sma50_sub = f"Price {'above' if ta['price'] > (ta['sma50'] or 0) else 'below'} SMA50"

    bb_upper_val = f"{ta['bb_upper']:,.5g}" if ta["bb_upper"] else "N/A"
    bb_mid_val   = f"{ta['bb_mid']:,.5g}"   if ta["bb_mid"]   else "N/A"
    bb_lower_val = f"{ta['bb_lower']:,.5g}" if ta["bb_lower"] else "N/A"

    st.markdown(
        sig_bar("SMA 20",    sma20_val, sma20_c, sma20_sub) +
        sig_bar("SMA 50",    sma50_val, sma50_c, sma50_sub) +
        sig_bar("RSI",       f"{ta['rsi']:.2f}", rsi_color(ta["rsi"]), ta["rsi_signal"]) +
        sig_bar("MACD",      f"{ta['macd']:.5g}", macd_c, f"Signal: {ta['macd_signal']:.5g}") +
        sig_bar("BB Upper",  bb_upper_val, "#FF7043") +
        sig_bar("BB Mid",    bb_mid_val,   "#FFA726") +
        sig_bar("BB Lower",  bb_lower_val, "#66BB6A") +
        sig_bar("BB Signal", ta["bb_signal"].replace("_"," "),
                bb_col.get(ta["bb_signal"], "#E6EDF3")),
        unsafe_allow_html=True,
    )

# ── Pattern detection ─────────────────────────────────────────────────────
with col_pat:
    if patterns:
        for p in patterns:
            icon  = "▲" if p["type"] == "bullish" else ("▼" if p["type"] == "bearish" else "◆")
            col_  = "#00C853" if p["type"] == "bullish" else ("#FF1744" if p["type"] == "bearish" else "#FFD600")
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
        <div class="metric-tile" style="text-align:center;color:#8B949E;padding:24px">
          🔍 No significant patterns<br>
          <span style="font-size:11px">detected in recent candles</span>
        </div>""", unsafe_allow_html=True)

# ── Support & Resistance ──────────────────────────────────────────────────
with col_lvl:
    st.markdown("**🔴 Resistance Levels**")
    if ta["resistances"]:
        for i, r in enumerate(reversed(ta["resistances"])):
            dist = abs(r - ta["price"]) / ta["price"] * 100
            lbl  = len(ta["resistances"]) - i
            st.markdown(f"""
            <div class="signal-bar">
              <div>
                <div style="font-size:13px;font-weight:600;color:#FF1744">R{lbl}: {r:,.5g}</div>
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
#  TRADING RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Trading Recommendations</div>', unsafe_allow_html=True)

if not recs:
    st.warning("⚠️ Tidak ada sinyal kuat saat ini. Market sedang ranging — tunggu konfirmasi.")
else:
    cols_rec = st.columns(2)
    for i, rec in enumerate(recs):
        with cols_rec[i % 2]:
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
              <div style="font-size:13px;color:#8B949E;margin:2px 0 4px">
                📍 Area: <b style="color:#E6EDF3">{rec['area']}</b>
              </div>
              <div class="rec-reason">{rec['reason']}</div>
              <div class="rec-meta">
                <span class="rec-tp">🎯 TP: {rec['target']}</span>
                <span class="rec-sl">🛡️ SL: {rec['sl']}</span>
                <span style="color:#8B949E">📊 {rec['confidence']}%</span>
              </div>
              {confidence_bar(rec['confidence'])}
            </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  NEWS & ECONOMIC CALENDAR
# ────────────────────────────────────────────────────────────────────────────
col_news, col_cal = st.columns([1.6, 1.4])

with col_news:
    st.markdown('<div class="section-title">📰 Market News & Analysis</div>', unsafe_allow_html=True)
    if not news:
        st.info(f"Tidak ada berita relevan untuk {symbol}.")
    else:
        for item in news:
            dir_str = item.get("direction", "")
            dir_col = ("#00C853" if "BULLISH" in dir_str else
                       "#FF1744" if "BEARISH" in dir_str else "#FFD600")
            st.markdown(f"""
            <div class="news-card">
              <div class="news-title">{item['title']}</div>
              <div class="news-meta">
                🕐 {item['published']} &nbsp;|&nbsp; 📌 {item['source']}
                &nbsp;|&nbsp; Impact: <span class="impact-{item['impact']}">{item['impact']}</span>
              </div>
              <div class="news-summary">{item['summary']}</div>
              <div style="margin-top:8px;font-size:12px;font-weight:600;color:{dir_col}">{dir_str}</div>
            </div>""", unsafe_allow_html=True)

with col_cal:
    st.markdown('<div class="section-title">🗓️ Economic Calendar</div>', unsafe_allow_html=True)
    for ev in events:
        imp_col = ("#FF1744" if ev["impact"] == "HIGH" else
                   "#FFD600" if ev["impact"] == "MEDIUM" else "#69F0AE")
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
last_upd = (st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")
            if st.session_state.last_refresh else "N/A")
st.markdown(f"""
<div style="text-align:center;padding:20px;color:#8B949E;font-size:12px;
  border-top:1px solid #30363D;margin-top:10px">
  <b style="color:#E6EDF3">⚡ Advanced Trading Analyzer v2.0</b> &nbsp;|&nbsp;
  Python · Streamlit · Plotly · Twelvedata · Alpha Vantage &nbsp;|&nbsp;
  Provider: {prov_cfg['icon']} {prov_cfg['name']} &nbsp;|&nbsp;
  Last Update: {last_upd}
  <br><br>
  <span style="color:#FF6D00">⚠️ DISCLAIMER: Aplikasi ini hanya untuk tujuan edukasi dan informasi.
  Bukan merupakan saran keuangan. Selalu lakukan riset sendiri dan kelola risiko Anda.</span>
</div>
""", unsafe_allow_html=True)
