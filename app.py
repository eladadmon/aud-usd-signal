import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Get FX data
symbol = 'AUDUSD=X'
data = yf.download(symbol, period='7d', interval='1h')

if data.empty:
    st.error("Could not retrieve FX data.")
    st.stop()

# Get latest close price
latest_price = round(float(data['Close'].iloc[-1]), 5)

# Calculate 50-period SMA
data['SMA_30'] = data['Close'].rolling(window=30).mean()

# Header
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

# FX Rate
st.subheader("Latest FX Rate")
st.metric(label="AUD/USD", value=f"{latest_price}")

# Simple buy USD analysis logic
sma = data['SMA_30'].iloc[-1]
if latest_price < sma and latest_price < 0.6465:
    buy_message = "🟢 It could be a good time to buy USD. AUD is below trend and near the recent pullback zone."
elif latest_price < sma:
    buy_message = "🟡 AUD is slightly below trend. Monitor for further weakness before buying USD."
else:
    buy_message = "🔴 Not ideal — AUD is above trend. Best to wait for a better entry point."

# Advisory section
st.subheader("📌 Should I Buy USD Now?")
st.markdown(buy_message)

# Chart
st.subheader("📈 AUD/USD Price Chart")
fig, ax = plt.subplots()
ax.plot(data.index, data['Close'], label='AUD/USD', color='blue')
ax.plot(data.index, data['SMA_30'], label='50-period SMA', linestyle='--', color='orange')
ax.set_title("AUD/USD with 50-period SMA")
ax.set_ylabel("Exchange Rate")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

# USD Cost Comparison
st.subheader("💱 USD Cost Comparison")
aud_spent = float(round(50000 * latest_price, 2))
st.markdown(f"If you buy 50,000 USD now → it will cost ≈ **{aud_spent:,.2f} AUD**.")

# Timestamp
st.caption(f"Data last updated: {pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M UTC')}")
