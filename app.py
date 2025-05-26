import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch intraday AUD/USD data using Yahoo Finance
def get_fx_data():
    df = yf.download("AUDUSD=X", period="5d", interval="30m")
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

# Score logic with robust error handling
def calculate_score(row, prev):
    score = 0
    try:
        indicators = [
            float(row['RSI']),
            float(prev['MACD']),
            float(prev['MACD_Signal']),
            float(row['MACD']),
            float(row['SMA_50']),
            float(row['price'])
        ]
        if any(np.isnan(ind) or not np.isfinite(ind) for ind in indicators):
            return 0

        if indicators[0] > 70:
            score += 40
        if indicators[1] > indicators[2] and indicators[3] < indicators[2]:
            score += 30
        if indicators[5] < indicators[4]:
            score += 30

        return score
    except Exception as e:
        st.warning(f"Scoring error: {e}")
        return 0

# Load and calculate
data = get_fx_data()
data = calculate_indicators(data)

latest = data.iloc[-1]
prev = data.iloc[-2]
score = calculate_score(latest, prev)

# Streamlit UI
st.title("🇦🇺 AUD/USD FX Buy Signal Dashboard")

st.subheader("Latest FX Rate")
st.metric("AUD/USD", f"{float(latest['price']):.4f}")

st.subheader("Technical Indicators")
st.write(f"RSI: {float(latest['RSI']):.2f}")
st.write(f"MACD: {float(latest['MACD']):.4f}")
st.write(f"MACD Signal: {float(latest['MACD_Signal']):.4f}")
st.write(f"50-period SMA: {float(latest['SMA_50']):.4f}")

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
ax.plot(data.index, data['SMA_50'], label='50-period SMA', linestyle='--')
ax.set_ylabel("Exchange Rate")
ax.set_title("AUD/USD with SMA")
ax.legend()
st.pyplot(fig)

# Last updated time
st.caption(f"Live FX data from Yahoo Finance. Last updated: {data.index[-1].strftime('%Y-%m-%d %H:%M UTC')}")

