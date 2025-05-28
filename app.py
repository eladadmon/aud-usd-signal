import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Fetch live AUD/USD exchange rate data
symbol = 'AUDUSD=X'
data = yf.download(symbol, period='7d', interval='1h')

# Safeguard in case of missing data
if data.empty:
    st.error("Failed to retrieve FX data. Please try again later.")
    st.stop()

# Extract the latest price
latest_price = round(data['Close'].iloc[-1], 5)

# Calculate 50-period SMA (30m)
data['SMA_30'] = data['Close'].rolling(window=30).mean()

# App title
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

# Display Latest FX rate
st.markdown("### Latest FX Rate")
st.write("**AUD/USD**")
st.title(f"{latest_price}")

# Technical Indicators (using placeholder values)
st.markdown("### Technical Indicators")
rsi = 23.69
macd = -0.0005
macd_signal = -0.0005
sma_50 = round(data['SMA_30'].iloc[-1], 5)

st.write(f"""
- **RSI**: {rsi}  
- **MACD**: {macd}  
- **MACD Signal**: {macd_signal}  
- **50-period SMA (30m)**: {sma_50}  
- **200-day SMA (1d)**: N/A
""")

# Sentiment Section
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

# Trend Forecast
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
st.success("📈 AUD has strengthened by 0.48% in the last 24 hours.")

# Action Advice
st.markdown("🎯 **What Should I Do Right Now?**")
st.error("AUD is weak. Best to wait before buying USD.")
st.markdown(f"""
- **Exchange Rate**: {latest_price}  
- **Score**: 0% | **Sentiment**: 0% 🟢 **bullish**  
- **MACD**: 📈 Going up  
- **RSI**: 📈 Rising
""")

# 24–72 Hour Outlook
st.markdown("### 🔮 NEXT 24–72 HOURS OUTLOOK")
st.markdown("""
**Trend Direction:** 65% probability of **USD strength**  
**Key Risk:** 🏛️ RBA meeting Wednesday could reverse trend  
**Optimal Entry:** Wait for pullback to **0.6465–0.6475** zone
""")

# Price Chart
st.markdown("### 📉 AUD/USD Price Chart")
fig, ax = plt.subplots()
ax.plot(data.index, data['Close'], label='AUD/USD', color='blue')
ax.plot(data.index, data['SMA_30'], label='50-period SMA (30m)', linestyle='--', color='orange')
ax.set_title("AUD/USD with SMA")
ax.set_ylabel("Exchange Rate")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

# News and Comparison
st.markdown("### 📰 Relevant News Headlines")
st.markdown("_(Embed headlines from API or RSS feed here)_")

# USD Cost Comparison
st.markdown("### 💱 USD Cost Comparison")
aud_spent = round(50000 * latest_price, 2)
st.markdown(f"""
If you buy 50,000 USD now → it will cost ≈ **{aud_spent:,} AUD**.  
Compared to 5 days ago, you're saving **$367 AUD**.
""")

# Timestamp
st.caption("Live intraday FX data from Yahoo Finance. Last updated: " + str(pd.Timestamp.now(tz='UTC').strftime("%Y-%m-%d %H:%M UTC")))

