# 📊 Advanced Trading Analyzer

> **Professional-grade technical analysis platform built with Python, Streamlit, and Plotly.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

### 🔍 Technical Analysis
| Indicator | Description |
|-----------|-------------|
| **Trend Detection** | Bullish / Bearish / Sideways with strength score (0–100) |
| **SMA 20 & 50** | Simple Moving Averages for trend following |
| **EMA 20** | Exponential Moving Average — reactive to recent price |
| **RSI (14)** | Overbought (>70) / Oversold (<30) detection |
| **Bollinger Bands** | Upper / Mid / Lower with price position signal |
| **MACD** | Histogram + crossover signal |
| **ATR (14)** | Average True Range for volatility and SL sizing |
| **Support & Resistance** | Pivot-based key price levels |

### 📊 Pattern Detection
- **Doji** — Indecision / Reversal signal
- **Hammer** — Bullish reversal
- **Shooting Star** — Bearish reversal
- **Bullish / Bearish Engulfing** — Strong reversal patterns
- **Morning Star / Evening Star** — 3-candle reversal patterns
- **Marubozu** — Strong momentum candle
- **Spinning Top** — Market indecision
- **Inverted Hammer** — Potential bullish reversal

### 💡 Smart Recommendations
- Buy / Sell / Hold with specific price area
- Take Profit (TP) and Stop Loss (SL) levels
- Confidence score (0–100%)
- Priority system: 🔴 HIGH · 🟡 MEDIUM · 🟢 LOW
- Based on RSI, MACD, BB, trend, support/resistance + patterns

### 📰 News & Calendar
- Market news with bullish/bearish impact analysis per symbol
- Economic calendar with event impact ratings

---

## 🖥️ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/NJB-PROJECT/Sistem-Monitoring-Chart-Pasar-Forex-Crypto
cd advanced-trading-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
advanced-trading-analyzer/
├── app.py                      # Main Streamlit application
├── requirements.txt
├── README.md
├── config/
│   └── settings.py             # Global configuration (symbols, timeframes, colors)
└── src/
    ├── __init__.py
    ├── data_fetcher.py          # yfinance OHLCV data retrieval
    ├── technical_analysis.py   # Indicator computation engine
    ├── pattern_detection.py    # Candlestick pattern recognition
    ├── recommendation_engine.py# Signal → recommendation logic
    ├── news_analyzer.py        # News fetching & market impact analysis
    └── chart_builder.py        # Plotly interactive chart builder
```

---

## 🎯 Supported Symbols & Timeframes

**Symbols:** XAU/USD · EUR/USD · GBP/USD · USD/JPY · BTC/USD · ETH/USD · NAS100 · SP500

**Timeframes:** 1M · 5M · 15M · 1H · 4H · 1D

---

## 📸 Screenshots

> Chart with Bollinger Bands, SMA, RSI, and MACD panels.  
> Recommendation cards with TP/SL and confidence scores.  
> Economic calendar and news analysis per symbol.

---

## ⚙️ Configuration

Edit `config/settings.py` to:
- Add more symbols (any yfinance-supported ticker)
- Change indicator defaults (RSI period, BB std, SMA periods)
- Adjust RSI overbought/oversold thresholds

---

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**.  
It does **not** constitute financial advice. Always conduct your own research and manage your risk appropriately.

---

## 📄 License

MIT License — feel free to fork, modify, and share.
