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
latest_price = round(data['Close'].iloc[-1], 5)

# Calculate SMA
data['SMA_30'] = data['Close'].rolling(window=30).mean()

# Header
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

# FX Rate
st.subheader("Latest FX Rate")
st.metric(label="AUD/USD", value=f"{latest_price}")

# Chart
st.subheader("📈 AUD/USD Price Chart")
fig, ax = plt.subplots()
ax.plot(data.index, data['Close'], label='AUD/USD', color='blue')
ax.plot(data.index, data['SMA_30'], label='50-period SMA', linestyle='--', color='orange')
ax.set_title("AUD/USD with 50-period SMA")
ax.legend()
st.pyplot(fig)

# USD Cost Comparison
st.subheader("💱 USD Cost Comparison")
aud_spent = round(50000 * latest_price, 2)
st.markdown(f"If you buy 50,000 USD now → it will cost ≈ **{aud_spent:,} AUD**.")

# Timestamp
st.caption(f"Data last updated: {pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M UTC')}")

