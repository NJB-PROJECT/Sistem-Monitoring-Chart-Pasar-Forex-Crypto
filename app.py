"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ADVANCED TRADING ANALYZER  —  Professional Edition  v3.0             ║
║        Python · Streamlit · Plotly · yfinance · Twelvedata · AlphaVantage   ║
║        + Google Gemini AI Analyst                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys, os
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

sys.path.insert(0, os.path.dirname(__file__))

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
from src.ai_analyst            import AIAnalyst

# ────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG & CSS
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Advanced Trading Analyzer Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  /* Global Styles */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background-color: #0D1117; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #161B22;
    border-right: 1px solid #30363D;
  }

  /* Custom Scrollbar */
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: #0D1117; }
  ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #58A6FF; }

  /* Header */
  .header-container {
    background: linear-gradient(135deg, #161B22 0%, #0D1117 100%);
    border: 1px solid #30363D;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    display: flex;
    justify_content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  .header-title {
    font-size: 28px;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: -0.5px;
  }
  .header-subtitle {
    font-size: 14px;
    color: #8B949E;
    margin-top: 4px;
  }
  .live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(35, 134, 54, 0.1);
    color: #3FB950;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(35, 134, 54, 0.2);
    font-size: 12px;
    font-weight: 600;
  }
  .live-dot {
    width: 8px; height: 8px;
    background-color: #3FB950;
    border-radius: 50%;
    animation: blink 2s infinite;
  }
  @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

  /* Metrics Cards */
  .metric-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    border-color: #58A6FF;
  }
  .metric-label { font-size: 12px; color: #8B949E; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
  .metric-value { font-size: 24px; font-weight: 700; color: #E6EDF3; font-family: 'JetBrains Mono', monospace; }
  .metric-sub { font-size: 13px; font-weight: 500; margin-top: 4px; }
  .pos-val { color: #3FB950; }
  .neg-val { color: #F85149; }

  /* Signal Cards */
  .signal-card {
    background: #161B22;
    border-left: 4px solid;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
  }
  .sig-HIGH { border-color: #F85149; background: linear-gradient(90deg, rgba(248,81,73,0.05) 0%, rgba(22,27,34,0) 100%); }
  .sig-MEDIUM { border-color: #D29922; background: linear-gradient(90deg, rgba(210,153,34,0.05) 0%, rgba(22,27,34,0) 100%); }
  .sig-LOW { border-color: #3FB950; background: linear-gradient(90deg, rgba(63,185,80,0.05) 0%, rgba(22,27,34,0) 100%); }

  .sig-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .sig-action { font-size: 18px; font-weight: 700; color: #E6EDF3; }
  .sig-meta { font-family: 'JetBrains Mono', monospace; font-size: 13px; display: flex; gap: 16px; color: #C9D1D9; }
  .sig-tp { color: #3FB950; font-weight: 600; }
  .sig-sl { color: #F85149; font-weight: 600; }

  /* Pattern Badge */
  .pattern-badge {
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
  }
  .pat-bullish { background: rgba(63,185,80,0.15); color: #3FB950; border: 1px solid rgba(63,185,80,0.3); }
  .pat-bearish { background: rgba(248,81,73,0.15); color: #F85149; border: 1px solid rgba(248,81,73,0.3); }

  /* Tables */
  .styled-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .styled-table th { text-align: left; color: #8B949E; padding: 8px; border-bottom: 1px solid #30363D; }
  .styled-table td { padding: 8px; color: #E6EDF3; border-bottom: 1px solid #21262D; }

  /* Buttons */
  div.stButton > button {
    background: #238636;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s;
  }
  div.stButton > button:hover { background: #2EA043; box-shadow: 0 0 8px rgba(46,160,67,0.4); }

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
#  SESSION STATE INITIALIZATION
# ────────────────────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None
if "data_cache" not in st.session_state:
    st.session_state.data_cache = {}
if "active_provider" not in st.session_state:
    st.session_state.active_provider = "auto"
if "gemini_response" not in st.session_state:
    st.session_state.gemini_response = None

# ────────────────────────────────────────────────────────────────────────────
#  SIDEBAR SETTINGS
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/chart.png", width=60)
    st.markdown("## Control Panel")

    # Market Selection
    st.markdown("### 🏷️ Market")
    symbol = st.selectbox("Asset Pair", list(SYMBOLS.keys()), index=0)
    timeframe = st.selectbox("⏱️ Timeframe", list(TIMEFRAMES.keys()), index=3)

    # Auto-Refresh Settings
    st.markdown("### 🔄 Auto-Refresh")
    enable_refresh = st.checkbox("Enable Auto-Refresh", value=True)

    refresh_rate = 60 # Default 60s
    if enable_refresh:
        # Smart default based on timeframe
        tf_mins = {
            "1M": 1, "5M": 5, "15M": 15,
            "1H": 60, "4H": 240, "1D": 1440
        }
        default_interval = tf_mins.get(timeframe, 60) * 60

        refresh_mode = st.radio("Refresh Speed", ["Real-time (Fast)", "Timeframe (Candle Close)"], index=0)

        if refresh_mode == "Real-time (Fast)":
            refresh_rate = st.slider("Interval (seconds)", 10, 300, 60, help="Faster refresh consumes more API quota.")
            st_autorefresh(interval=refresh_rate * 1000, key="data_refresh")
        else:
            refresh_rate = default_interval
            st_autorefresh(interval=refresh_rate * 1000, key="candle_refresh")
            st.info(f"Refreshing every {default_interval}s")

    # Strategy Mode
    st.markdown("### 🎯 Signal Strategy")
    strategy_mode = st.radio(
        "Precision Mode",
        ["Standard", "High Precision (Strict)"],
        index=0,
        help="High Precision filters for stronger trends and clearer patterns (fewer signals, higher win-rate potential)."
    )
    strict_mode = (strategy_mode == "High Precision (Strict)")

    # Indicator Params
    with st.expander("⚙️ Technical Settings", expanded=False):
        rsi_period = st.slider("RSI Period", 7, 21, 14)
        sma_s = st.slider("SMA Short", 5, 50, 20)
        sma_l = st.slider("SMA Long", 20, 200, 50)
        bb_std = st.slider("Bollinger Std Dev", 1.0, 3.0, 2.0, 0.1)

    # API Keys
    with st.expander("🔑 API Keys", expanded=False):
        keys = load_api_keys()
        td_key = st.text_input("Twelvedata Key", value=keys.get("twelvedata", ""), type="password")
        av_key = st.text_input("Alpha Vantage Key", value=keys.get("alpha_vantage", ""), type="password")
        gemini_key = st.text_input("Google Gemini API", value=keys.get("gemini_api", ""), type="password")

        if st.button("Save Keys"):
            save_api_keys({
                "twelvedata": td_key,
                "alpha_vantage": av_key,
                "gemini_api": gemini_key,
                "active_provider": "twelvedata" if td_key else "auto"
            })
            st.success("Keys Saved!")
            st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;color:#8B949E'>v3.0.0 Pro • {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
#  DATA FETCHING & PROCESSING
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=refresh_rate if enable_refresh else 3600, show_spinner=False)
def get_market_data(sym, tf):
    df, provider = fetch_ohlcv(sym, tf)
    return df, provider

# Fetch Data
try:
    with st.spinner(f"📡 Fetching live data for {symbol}..."):
        # Fetch OHLCV
        df_raw, provider = get_market_data(symbol, timeframe)

        # Compute Technicals
        ta = compute_all(df_raw)

        # Detect Patterns
        patterns = get_recent_patterns(ta["df"])

        # Generate Recommendations
        recs = generate_recommendations(ta, patterns, symbol, strict_mode=strict_mode)

        # Get Real-time Price (if possible)
        price_info = get_current_price(symbol)

        # Get News
        news, events = get_news_and_events(symbol)

        st.session_state.active_provider = provider
        st.session_state.last_refresh = datetime.now()

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
    st.stop()

# Unpack Data
df = ta["df"]
latest = df.iloc[-1]
current_price = price_info.get("price", latest["close"])
price_change = price_info.get("change", 0)
price_pct = price_info.get("change_pct", 0)

# ────────────────────────────────────────────────────────────────────────────
#  MAIN LAYOUT
# ────────────────────────────────────────────────────────────────────────────

# Header
prov_icon = PROVIDERS.get(provider, PROVIDERS["synthetic"])["icon"]
prov_name = PROVIDERS.get(provider, PROVIDERS["synthetic"])["name"]

st.markdown(f"""
<div class="header-container">
    <div>
        <div class="header-title">{symbol} <span style="font-size:16px;color:#8B949E;font-weight:400">/ USD</span></div>
        <div class="header-subtitle">Timeframe: <b>{timeframe}</b> • Source: <b>{prov_name}</b></div>
    </div>
    <div style="text-align:right">
        <div class="live-indicator"><div class="live-dot"></div> LIVE MONITORING</div>
        <div style="font-size:12px;color:#8B949E;margin-top:6px">Last update: {st.session_state.last_refresh.strftime('%H:%M:%S')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)

with c1:
    color_cls = "pos-val" if price_change >= 0 else "neg-val"
    sign = "+" if price_change >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Current Price</div>
        <div class="metric-value">${current_price:,.2f}</div>
        <div class="metric-sub {color_cls}">{sign}{price_change:.2f} ({sign}{price_pct:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    trend = ta["trend"]
    score = ta["trend_score"]
    trend_color = "#3FB950" if trend == "BULLISH" else "#F85149" if trend == "BEARISH" else "#E6EDF3"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Market Trend</div>
        <div class="metric-value" style="color:{trend_color}">{trend}</div>
        <div class="metric-sub" style="color:#8B949E">Strength: {score}/100</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    rsi = ta["rsi"]
    rsi_sig = ta["rsi_signal"]
    rsi_col = "#F85149" if rsi >= 70 else "#3FB950" if rsi <= 30 else "#E6EDF3"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">RSI (14)</div>
        <div class="metric-value" style="color:{rsi_col}">{rsi:.1f}</div>
        <div class="metric-sub" style="color:#8B949E">{rsi_sig}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    vol_24h = price_info.get("volume", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">24h Volume</div>
        <div class="metric-value">{vol_24h:,.0f}</div>
        <div class="metric-sub" style="color:#8B949E">Shares/Contracts</div>
    </div>
    """, unsafe_allow_html=True)

# Tabs for Main Content
tab_chart, tab_ai, tab_signals, tab_analysis, tab_news = st.tabs([
    "📊 Live Chart", "🤖 AI Analyst", "⚡ Signals", "🔍 Technicals", "📰 News"
])

# ─── TAB 1: CHART ───────────────────────────────────────────────────────────
with tab_chart:
    st.markdown("### Interactive Market Chart")
    fig = build_main_chart(df, ta, patterns, symbol, timeframe)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Active Patterns
    if patterns:
        st.markdown("##### Detected Patterns (Recent)")
        cols = st.columns(4)
        for i, pat in enumerate(patterns[:4]):
            p_cls = "pat-bullish" if pat["type"] == "bullish" else "pat-bearish" if pat["type"] == "bearish" else "pat-neutral"
            with cols[i]:
                st.markdown(f"""
                <div style="background:#161B22;border:1px solid #30363D;padding:10px;border-radius:8px">
                    <span class="pattern-badge {p_cls}">{pat['type']}</span>
                    <div style="font-weight:600;margin-top:6px;font-size:13px">{pat['name']}</div>
                    <div style="font-size:11px;color:#8B949E">{pat['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

# ─── TAB 2: AI ANALYST ──────────────────────────────────────────────────────
with tab_ai:
    st.markdown("### 🤖 Google Gemini Market Analysis")
    gemini_key = load_api_keys().get("gemini_api")

    if not gemini_key:
        st.warning("⚠️ Google Gemini API Key is missing. Please add it in the Sidebar > API Keys.")
    else:
        col_ai_btn, col_ai_res = st.columns([1, 4])
        with col_ai_btn:
            if st.button("✨ Generate AI Analysis", use_container_width=True):
                with st.spinner("🤖 AI is reading the charts..."):
                    analyst = AIAnalyst(gemini_key)
                    # Prepare data for AI
                    ta_summary = {
                        "price": current_price,
                        "trend": trend,
                        "trend_score": score,
                        "rsi": rsi, "rsi_signal": rsi_sig,
                        "macd": ta["macd"], "macd_signal": ta["macd_signal"], "macd_hist": ta["macd_hist"],
                        "bb_upper": ta["bb_upper"], "bb_lower": ta["bb_lower"], "bb_signal": ta["bb_signal"],
                        "atr": ta["atr"],
                        "supports": ta["supports"], "resistances": ta["resistances"]
                    }
                    st.session_state.gemini_response = analyst.analyze_market(
                        symbol, timeframe, ta_summary, patterns, news
                    )

        with col_ai_res:
            if st.session_state.gemini_response:
                st.markdown(f"""
                <div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;line-height:1.6">
                    {st.session_state.gemini_response}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Click 'Generate AI Analysis' to get insights from Gemini 2.0 Flash Lite.")

# ─── TAB 3: SIGNALS ─────────────────────────────────────────────────────────
with tab_signals:
    c_sig, c_info = st.columns([2, 1])

    with c_sig:
        st.markdown("### ⚡ Algorithmic Recommendations")
        if not recs:
            st.info("No strong signals detected at the moment. Market might be ranging or undecided.")
        else:
            for rec in recs:
                p_cls = f"sig-{rec['priority']}"
                action_icon = "🟢" if "BUY" in rec["action"] else "🔴" if "SELL" in rec["action"] else "🔵"
                st.markdown(f"""
                <div class="signal-card {p_cls}">
                    <div class="sig-header">
                        <div class="sig-action">{action_icon} {rec['action']}</div>
                        <div style="font-size:12px;font-weight:700;color:#8B949E">{rec['priority']} PRIORITY</div>
                    </div>
                    <div style="color:#C9D1D9;margin-bottom:8px;font-size:14px">{rec['reason']}</div>
                    <div class="sig-meta">
                        <span>📍 Entry: {rec['area']}</span>
                        <span class="sig-tp">🎯 TP: {rec['target']}</span>
                        <span class="sig-sl">🛡️ SL: {rec['sl']}</span>
                        <span>⚡ Conf: {rec['confidence']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with c_info:
        st.markdown("### Signal Logic")
        st.info("""
        **Strategy Overview:**
        - **Trend Following:** Uses SMA20/50 & MACD crossovers.
        - **Reversals:** Uses RSI Overbought/Oversold & Bollinger Bands.
        - **Pattern Recognition:** Validates entries with Candlestick patterns.
        - **Risk Management:** SL is dynamically calculated using ATR (Volatility).

        **Note:** Always verify signals with your own analysis.
        """)

# ─── TAB 4: ANALYSIS ────────────────────────────────────────────────────────
with tab_analysis:
    c_ta1, c_ta2 = st.columns(2)

    with c_ta1:
        st.markdown("#### Moving Averages & Trend")
        ma_data = {
            "Indicator": ["SMA 20", "SMA 50", "EMA 20", "Bollinger Upper", "Bollinger Lower"],
            "Value": [
                f"{latest['sma20']:.5f}" if latest.get('sma20') else "-",
                f"{latest['sma50']:.5f}" if latest.get('sma50') else "-",
                f"{latest['ema20']:.5f}" if latest.get('ema20') else "-",
                f"{latest['bb_upper']:.5f}" if latest.get('bb_upper') else "-",
                f"{latest['bb_lower']:.5f}" if latest.get('bb_lower') else "-",
            ],
            "Signal": [
                "Bullish" if current_price > (latest.get('sma20') or 999999) else "Bearish",
                "Bullish" if current_price > (latest.get('sma50') or 999999) else "Bearish",
                "-",
                "Overbought" if current_price > (latest.get('bb_upper') or 999999) else "Neutral",
                "Oversold" if current_price < (latest.get('bb_lower') or 0) else "Neutral",
            ]
        }
        st.table(pd.DataFrame(ma_data))

    with c_ta2:
        st.markdown("#### Oscillators & Volatility")
        osc_data = {
            "Indicator": ["RSI (14)", "MACD", "MACD Signal", "ATR (Volatility)", "Trend Strength"],
            "Value": [
                f"{latest['rsi']:.2f}",
                f"{latest['macd']:.5f}",
                f"{latest['macd_signal']:.5f}",
                f"{latest['atr']:.5f}",
                f"{ta['trend_score']}/100"
            ],
            "Signal": [
                ta['rsi_signal'],
                "Bullish" if latest['macd'] > latest['macd_signal'] else "Bearish",
                "-",
                "High Volatility" if latest['atr'] > (current_price * 0.01) else "Normal",
                ta['trend']
            ]
        }
        st.table(pd.DataFrame(osc_data))

    st.markdown("#### Support & Resistance Levels (Pivot Based)")
    res_cols = st.columns(len(ta['resistances']) if ta['resistances'] else 1)
    if ta['resistances']:
        for i, r in enumerate(reversed(ta['resistances'])):
            with res_cols[i]:
                st.metric(f"Resistance {len(ta['resistances'])-i}", f"{r:.5f}")

    sup_cols = st.columns(len(ta['supports']) if ta['supports'] else 1)
    if ta['supports']:
        for i, s in enumerate(ta['supports']):
            with sup_cols[i]:
                st.metric(f"Support {i+1}", f"{s:.5f}")

# ─── TAB 5: NEWS ────────────────────────────────────────────────────────────
with tab_news:
    cn1, cn2 = st.columns([1.5, 1])
    with cn1:
        st.markdown("#### 📰 Latest Market News")
        if news:
            for n in news:
                st.markdown(f"""
                <div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #30363D">
                    <a href="{n.get('url','#')}" style="color:#58A6FF;font-weight:600;text-decoration:none;font-size:15px">{n['title']}</a>
                    <div style="font-size:12px;color:#8B949E;margin-top:4px">{n['source']} • {n['published']}</div>
                    <div style="font-size:13px;color:#C9D1D9;margin-top:4px">{n['summary']}</div>
                    <div style="margin-top:6px">
                        <span style="font-size:11px;background:#21262D;padding:2px 8px;border-radius:4px;color:{'#3FB950' if 'BULLISH' in n.get('direction','') else '#F85149'}">{n.get('direction','NEUTRAL')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent news found for this asset.")

    with cn2:
        st.markdown("#### 🗓️ Economic Calendar")
        if events:
            for ev in events:
                imp_color = "#F85149" if ev['impact'] == 'HIGH' else "#D29922" if ev['impact'] == 'MEDIUM' else "#3FB950"
                st.markdown(f"""
                <div style="background:#161B22;padding:10px;border-radius:6px;margin-bottom:8px;border-left:3px solid {imp_color}">
                    <div style="font-weight:600;font-size:13px">{ev['event']}</div>
                    <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:12px;color:#8B949E">
                        <span>{ev['time']}</span>
                        <span style="color:{imp_color};font-weight:700">{ev['impact']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No major economic events scheduled shortly.")
