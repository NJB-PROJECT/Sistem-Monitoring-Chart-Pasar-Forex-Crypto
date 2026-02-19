"""
Configuration settings for Advanced Trading Analyzer
"""

SYMBOLS = {
    "XAU/USD": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "NAS100": "NQ=F",
    "SP500": "ES=F",
}

TIMEFRAMES = {
    "1M":  {"interval": "1m",  "period": "1d",  "label": "1 Minute"},
    "5M":  {"interval": "5m",  "period": "5d",  "label": "5 Minutes"},
    "15M": {"interval": "15m", "period": "5d",  "label": "15 Minutes"},
    "1H":  {"interval": "60m", "period": "1mo", "label": "1 Hour"},
    "4H":  {"interval": "1h",  "period": "3mo", "label": "4 Hours"},
    "1D":  {"interval": "1d",  "period": "1y",  "label": "1 Day"},
}

RSI_OVERSOLD    = 30
RSI_OVERBOUGHT  = 70
RSI_NEUTRAL_LOW  = 40
RSI_NEUTRAL_HIGH = 60

BB_PERIOD = 20
BB_STD    = 2

SMA_SHORT = 20
SMA_LONG  = 50

COLORS = {
    "bullish":   "#00C853",
    "bearish":   "#FF1744",
    "neutral":   "#FFD600",
    "high":      "#FF6D00",
    "medium":    "#00B0FF",
    "low":       "#69F0AE",
    "bg":        "#0D1117",
    "card":      "#161B22",
    "border":    "#30363D",
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
}

PRIORITY_ICONS = {
    "HIGH":   "🔴",
    "MEDIUM": "🟡",
    "LOW":    "🟢",
}
