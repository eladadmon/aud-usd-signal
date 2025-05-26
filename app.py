import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch intraday AUD/USD data from Yahoo Finance
def get_fx_data():
    df = yf.download("AUDUSD=X", period="5d", interval="30m")
    df = df[['Close']].rename(columns={"Close": "price"})
    df["price"] = df["price"].astype(float)
    return df

# Fetch daily AUD/USD data for higher timeframe SMA
def get_daily_data():
    df = yf.download("AUDUSD=X", period="3mo", interval="1d")
    df = df[['Close']].rename(columns={"Close": "price"})
    df["SMA_200"] = df['price'].rolling(window=200).mean()
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

# Scoring logic
def calculate_aud_strength_score(row, prev):
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
        if indicators[5] > indicators[4]:
            score += 30

        return score
    except Exception as e:
        st.warning(f"Scoring error: {e}")
        return 0

# Load and calculate
data = get_fx_data()
data = calculate_indicators(data)

daily_data = get_daily_data()
latest = data.iloc[-1]
prev = data.iloc[-2]
latest_daily = daily_data.iloc[-1]

try:
    above_200_sma = float(latest_daily['price']) > float(latest_daily['SMA_200'])
except:
    above_200_sma = False

score = calculate_aud_strength_score(latest, prev)

# Format 200-day SMA safely
if not pd.isna(latest_daily['SMA_200']):
    sma200_display = f"{float(latest_daily['SMA_200']):.4f}"
else:
    sma200_display = "N/A"

# UI
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

st.subheader("Latest FX Rate")
st.metric("AUD/USD", f"{float(latest['price']):.4f}")

st.subheader("Technical Indicators")
st.write(f"RSI: {float(latest['RSI']):.2f}")
st.write(f"MACD: {float(latest['MACD']):.4f}")
st.write(f"MACD Signal: {float(latest['MACD_Signal']):.4f}")
st.write(f"50-period SMA (30m): {float(latest['SMA_50']):.4f}")
st.write(f"200-day SMA (1d): {sma200_display}")

# Sentiment meter
st.subheader("AUD Sentiment Meter")
with st.expander("How sentiment is scored"):
    st.markdown("""
    - **RSI > 70** → AUD is

