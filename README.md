# 📊 Advanced Trading Analyzer Pro v3.0

> **Professional-grade technical analysis platform built with Python, Streamlit, and Plotly.**
> **Enhanced with Real-time Auto-Refresh & AI Signals.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 New Features in v3.0

### 🔄 Real-time Monitoring
- **Auto-Refresh**: Automatically updates charts and signals based on your timeframe or custom interval.
- **Multi-Source Data**: Prioritizes **Twelvedata** for high accuracy, with automatic fallback to Alpha Vantage and yfinance.
- **Smart Caching**: Optimizes API usage while ensuring data freshness.

### 🤖 AI Signals & Risk Management
- **Take Profit (TP) & Stop Loss (SL)**: Dynamic levels calculated using ATR and Support/Resistance.
- **Confidence Score**: AI-driven confidence rating (0-100%) for every signal.
- **Pattern Recognition**: Detects 10+ candlestick patterns (Doji, Hammer, Engulfing, etc.).

### 🎨 Modern UI/UX
- **Pro Dashboard**: Clean, dark-mode interface with interactive tabs.
- **Signal Cards**: High-priority opportunities highlighted instantly.
- **Integrated News**: Real-time market news and economic calendar events.

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
├── app.py                      # Main Streamlit application (v3.0)
├── requirements.txt
├── README.md
├── config/
│   ├── settings.py             # Global configuration
│   └── api_keys.json           # API Keys (Twelvedata / Alpha Vantage)
└── src/
    ├── __init__.py
    ├── data_fetcher.py          # robust multi-provider data retrieval
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

## ⚙️ Configuration

### API Keys
For best results (Real-time data), add your API keys in the **Sidebar > API Keys** section or edit `config/api_keys.json`:
- **Twelvedata** (Recommended for Forex/Crypto)
- **Alpha Vantage** (Backup)

---

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**.  
It does **not** constitute financial advice. Always conduct your own research and manage your risk appropriately.

---

## 📄 License

MIT License — feel free to fork, modify, and share.
