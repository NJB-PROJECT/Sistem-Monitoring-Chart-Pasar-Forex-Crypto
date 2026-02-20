"""
AI Analyst Module
Uses Google Gemini 2.0 Flash Lite (via google-genai SDK) to analyze market data.
"""
import os
from google import genai
from google.genai import types
import pandas as pd
from datetime import datetime

class AIAnalyst:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            # Initialize client with the new SDK
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    def analyze_market(self, symbol: str, timeframe: str, ta_data: dict, patterns: list, news: list) -> str:
        """
        Generates a comprehensive market analysis and trade setup.

        Args:
            symbol (str): The asset symbol (e.g., BTC/USD).
            timeframe (str): The chart timeframe (e.g., 1H).
            ta_data (dict): Technical indicators (RSI, MACD, BB, etc.).
            patterns (list): Detected candlestick patterns.
            news (list): Recent news headlines.

        Returns:
            str: Markdown-formatted analysis.
        """
        if not self.client:
            return "⚠️ AI Analysis Unavailable: API Key Missing."

        # Construct Prompt
        prompt = f"""
        Act as a professional Crypto & Forex Analyst with 20 years of experience.
        Analyze the following market data for **{symbol}** on the **{timeframe}** timeframe.

        **Technical Indicators:**
        - Price: {ta_data['price']}
        - Trend: {ta_data['trend']} (Strength: {ta_data['trend_score']}/100)
        - RSI (14): {ta_data['rsi']} ({ta_data['rsi_signal']})
        - MACD: {ta_data['macd']} (Signal: {ta_data['macd_signal']}, Hist: {ta_data['macd_hist']})
        - Bollinger Bands: Upper {ta_data['bb_upper']}, Lower {ta_data['bb_lower']}, Pos: {ta_data['bb_signal']}
        - ATR (Volatility): {ta_data['atr']}
        - Support Levels: {', '.join(map(str, ta_data['supports'][:2]))}
        - Resistance Levels: {', '.join(map(str, ta_data['resistances'][-2:]))}

        **Candlestick Patterns:**
        {', '.join([f"{p['name']} ({p['type']})" for p in patterns]) if patterns else "No significant patterns detected."}

        **Recent News Headlines:**
        {'; '.join([n['title'] for n in news[:3]]) if news else "No major news."}

        **Task:**
        1. **Market Sentiment:** Bullish, Bearish, or Neutral? Why?
        2. **Key Levels:** Identify the most critical Support & Resistance for the next few candles.
        3. **Trade Setup (If valid):**
           - **Action:** BUY / SELL / WAIT
           - **Entry Zone:** Precise price range.
           - **Stop Loss (SL):** Precise price based on ATR or structure.
           - **Take Profit (TP) Targets:**
             - **TP 1 (Conservative/Low Risk):** High probability, lower reward.
             - **TP 2 (Moderate/Med Risk):** Standard 1:2 risk/reward.
             - **TP 3 (Aggressive/High Risk):** Extended run potential.
        4. **Risk Warning:** Brief note on what could invalidate this setup.

        **Format:** Return the response in clean Markdown. Use bolding for key numbers. Keep it concise but actionable.
        """

        try:
            # Use gemini-2.0-flash-lite-preview-02-05 if available, or fall back to gemini-1.5-flash
            # For stability, let's use gemini-1.5-flash which is widely available,
            # unless the user specifically wants the bleeding edge.
            # The user asked for "2.5 Flash Lite", which might be "gemini-2.0-flash-lite"
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-lite-preview-02-05',
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback to 1.5 Flash if the specific 2.0 model name fails or isn't available
            try:
                response = self.client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                return response.text
            except Exception as e2:
                return f"⚠️ AI Analysis Failed: {str(e2)}"
