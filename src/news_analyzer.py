"""
News Analyzer
Fetches economic news via RSS and analyzes potential market impact.
"""
import feedparser
import re
from datetime import datetime


# ── High-impact keyword dictionaries ────────────────────────────────────────
BULLISH_KEYWORDS = {
    "USD": ["rate cut", "dovish", "easing", "stimulus", "QE", "liquidity"],
    "XAU": ["rate cut", "inflation", "dovish", "geopolitical", "war", "recession", "safe haven"],
    "EUR": ["ECB hawkish", "GDP beat", "employment rise"],
    "GBP": ["BoE hike", "strong GDP", "employment surge"],
}

BEARISH_KEYWORDS = {
    "USD": ["rate hike", "hawkish", "tightening", "strong CPI", "NFP beat"],
    "XAU": ["rate hike", "hawkish", "USD strength", "risk-on", "strong jobs"],
    "EUR": ["ECB dovish", "recession", "debt crisis", "weaker GDP"],
    "GBP": ["BoE cut", "weak GDP", "Brexit uncertainty"],
}

NEWS_RSS_FEEDS = [
    "https://feeds.feedburner.com/forexlive/rss",
    "https://www.forexfactory.com/rss",
    "https://rss.investing.com/rss/news",
]

MOCK_NEWS = [
    {
        "title": "Fed Officials Signal Caution on Rate Cuts Amid Sticky Inflation",
        "summary": "Federal Reserve officials emphasized a data-dependent approach, suggesting rate cuts may be delayed if CPI remains elevated.",
        "published": "2025-02-18 14:30",
        "source": "Reuters",
        "impact": "HIGH",
        "affects": ["XAU/USD", "EUR/USD", "GBP/USD"],
    },
    {
        "title": "US CPI Rises 0.3% MoM — Above Expectations",
        "summary": "Consumer Price Index rose 0.3% month-over-month, exceeding the 0.2% forecast. Core CPI steady at 3.9% YoY.",
        "published": "2025-02-18 13:00",
        "source": "BLS",
        "impact": "HIGH",
        "affects": ["XAU/USD", "USD/JPY"],
    },
    {
        "title": "ECB Minutes: Policymakers Divided on Pace of Rate Cuts",
        "summary": "European Central Bank minutes revealed divergence among members, with hawks pushing for patience despite slowing inflation.",
        "published": "2025-02-18 12:15",
        "source": "ECB",
        "impact": "MEDIUM",
        "affects": ["EUR/USD"],
    },
    {
        "title": "Gold Demand Surges as Central Banks Continue Buying",
        "summary": "World Gold Council data shows central bank gold purchases hit a multi-decade high, supporting long-term bullish outlook for XAU.",
        "published": "2025-02-18 10:00",
        "source": "World Gold Council",
        "impact": "MEDIUM",
        "affects": ["XAU/USD"],
    },
    {
        "title": "UK GDP Contracts 0.1% in Q4 — Recession Fears Return",
        "summary": "UK economy shrinks for second consecutive quarter. Sterling under pressure as markets price in earlier BoE rate cuts.",
        "published": "2025-02-18 09:30",
        "source": "ONS",
        "impact": "HIGH",
        "affects": ["GBP/USD"],
    },
    {
        "title": "Geopolitical Tensions Escalate in Middle East",
        "summary": "Renewed conflict in the region pushes crude oil higher and lifts safe-haven demand for gold and yen.",
        "published": "2025-02-18 08:00",
        "source": "AP News",
        "impact": "MEDIUM",
        "affects": ["XAU/USD", "USD/JPY"],
    },
]

UPCOMING_EVENTS = [
    {"event": "FOMC Meeting Minutes", "time": "19:00 GMT", "impact": "HIGH",    "forecast": "N/A", "previous": "N/A"},
    {"event": "US Initial Jobless Claims", "time": "13:30 GMT", "impact": "MEDIUM", "forecast": "215K", "previous": "220K"},
    {"event": "ECB President Speech", "time": "15:00 GMT", "impact": "HIGH",    "forecast": "N/A", "previous": "N/A"},
    {"event": "US Retail Sales MoM", "time": "13:30 GMT", "impact": "HIGH",    "forecast": "0.2%", "previous": "-0.4%"},
    {"event": "BoJ Interest Rate Decision", "time": "03:00 GMT", "impact": "HIGH", "forecast": "0.50%", "previous": "0.25%"},
]


def analyze_news_impact(symbol: str, news_items: list) -> list:
    """
    Filter news relevant to a symbol and annotate with market impact analysis.
    """
    base = symbol.split("/")[0] if "/" in symbol else symbol[:3]
    relevant = [n for n in news_items if symbol in n.get("affects", [])]

    for item in relevant:
        title_lower = item["title"].lower() + " " + item["summary"].lower()
        bull_keys   = BULLISH_KEYWORDS.get(base, [])
        bear_keys   = BEARISH_KEYWORDS.get(base, [])

        bull_score = sum(1 for k in bull_keys if k.lower() in title_lower)
        bear_score = sum(1 for k in bear_keys if k.lower() in title_lower)

        if bull_score > bear_score:
            direction = "📈 BULLISH"
            color     = "bullish"
        elif bear_score > bull_score:
            direction = "📉 BEARISH"
            color     = "bearish"
        else:
            direction = "⚖️  NEUTRAL"
            color     = "neutral"

        item["direction"] = direction
        item["color"]     = color

    return relevant


def get_news_and_events(symbol: str):
    """Return news items + upcoming events relevant to the symbol."""
    analyzed = analyze_news_impact(symbol, MOCK_NEWS)
    return analyzed, UPCOMING_EVENTS
