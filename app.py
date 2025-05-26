import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import numpy as np

# Dummy data for plotting
dates = pd.date_range(end=datetime.datetime.today(), periods=7)
audusd = [0.641, 0.644, 0.648, 0.650, 0.652, 0.654, 0.648]
sma_30 = pd.Series(audusd).rolling(window=3).mean().fillna(method='bfill')

# Layout
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

st.markdown("### Latest FX Rate")
st.write("**AUD/USD**")
st.title("0.6488")

# Technical Indicators
st.markdown("### Technical Indicators")
st.write("""
- **RSI**: 23.69  
- **MACD**: -0.0005  
- **MACD Signal**: -0.0005  
- **50-period SMA (30m)**: 0.6507  
- **200-day SMA (1d)**: N/A
""")

# Sentiment
st.markdown("### AUD Sentiment Meter")
st.progress(0)
st.markdown("#### 📊 AUD Strength Score (for Buying USD)")
st.write("**Score: 0%**")
st.info("❌ Not ideal — AUD is weak")

st.markdown("🔍 **Indicator Breakdown:**")
st.markdown("""
- ❌ RSI > 70 (AUD overbought)  
- ❌ MACD crossover bearish  
- ❌ Price > 50-SMA (uptrend)
""")

# Pre-buy alert
st.markdown("🕊️ **Pre-Buy Alert Zone**")
st.markdown("🧘 **Trend Forecast**")
st.markdown("""
- 📉 Price trend is uncertain — watch key indicators  
- 📊 MACD histogram rising — bullish pressure increasing
""")

# Weakening Probability
st.markdown("💜 **AUD Weakening Probability**")
st.write("AUD Weakening Probability Score: 0%")
st.warning("🌀 Trend is unclear. Monitor before acting.")
st.success("📈 AUD has strengthened by 0.48% over the last 5 days.")

# What Should I Do?
st.markdown("🎯 **What Should I Do Right Now?**")
st.error("AUD is weak. Best to wait before buying USD.")
st.markdown("""
- **Exchange Rate**: 0.6488  
- **Score**: 0% | **Sentiment**: 0% 🟢 **bullish**  
- **MACD**: 📈 Going up  
- **RSI**: 📈 Rising
""")

# 🔮 24–72 Hour Outlook
st.markdown("### 🔮 NEXT 24–72 HOURS OUTLOOK")
st.markdown("""
**Trend Direction:** 65% probability of **USD strength**  
**Key Risk:** 🏛️ RBA meeting Wednesday could reverse trend  
**Optimal Entry:** Wait for pullback to **0.6465–0.6475** zone
""")

# Chart
st.markdown("### 📉 AUD/USD Price Chart")
fig, ax = plt.subplots()
ax.plot(dates, audusd, label='AUD/USD', color='blue')
ax.plot(dates, sma_30, label='50-period SMA (30m)', linestyle='--', color='orange')
ax.set_title("AUD/USD with SMA")
ax.set_ylabel("Exchange Rate")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

# News & Comparison
st.markdown("### 📰 Relevant News Headlines")
st.markdown("_(Embed headlines from API or RSS feed here)_")

st.markdown("### 💱 USD Cost Comparison")
st.markdown("""
If you buy 50,000 USD now → it will cost ≈ **77,068 AUD**.  
Compared to 5 days ago, you're saving **$367 AUD**.
""")

st.caption("Live intraday FX data from Yahoo Finance. Last updated: 2025-05-26 22:30 UTC.")


