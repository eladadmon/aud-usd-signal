import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch AUD/USD FX data using Yahoo Finance
def get_fx_data():
    df = yf.download("AUDUSD=X", period="90d", interval="1d")
    df = df[['Close']].rename(columns={"Close": "price"})
    df["price"] = df["price"].astype(float)
    return df

# Calculate technical indicators
def calculate_indicators(df):
    price = df['price']
    delta = price.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    ema_12 = price.ewm(span=12, adjust=False).mean()
    ema_26 = price.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    sma_50 = price.rolling(window=50).mean()

    df['RSI'] = rsi
    df['MACD'] = macd
    df['MACD_Signal'] = macd_signal
    df['SMA_50'] = sma_50
    return df

# Score logic
def calculate_score(row, prev):
    score = 0
    if row['RSI'] > 70:
        score += 40
    if prev['MACD'] > prev['MACD_Signal'] and row['MACD'] < row['MACD_Signal']:
        score += 30
    if row['price'] < row['SMA_50']:
        score += 30
    return score

# Load data
data = get_fx_data()
data = calculate_indicators(data)

latest = data.iloc[-1]
prev = data.iloc[-2]
score = calculate_score(latest, prev)

# UI
st.title("🇦🇺 AUD/USD FX Buy Signal Dashboard")

st.subheader("Latest FX Rate")
st.metric("AUD/USD", f"{latest['price']:.4f}")

st.subheader("Technical Indicators")
st.write(f"RSI: {latest['RSI']:.2f}")
st.write(f"MACD: {latest['MACD']:.4f}")
st.write(f"MACD Signal: {latest['MACD_Signal']:.4f}")
st.write(f"50-day SMA: {latest['SMA_50']:.4f}")

st.subheader("Buy USD Signal Confidence")
if score >= 80:
    st.success(f"💵 Strong signal to buy USD now (Score: {score}%)")
elif score >= 60:
    st.warning(f"🟠 Moderate signal to buy USD (Score: {score}%)")
else:
    st.info(f"🧊 No buy signal (Score: {score}%)")

# Chart
st.subheader("AUD/USD Price Chart")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['price'], label='AUD/USD')
ax.plot(data.index, data['SMA_50'], label='50-day SMA', linestyle='--')
ax.set_ylabel("Exchange Rate")
ax.set_title("AUD/USD with SMA")
ax.legend()
st.pyplot(fig)

st.caption("Live FX data from Yahoo Finance. Score based on overbought conditions, MACD crossovers, and trend structure.")
