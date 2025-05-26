import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch intraday AUD/USD data
def get_fx_data():
    df = yf.download("AUDUSD=X", period="5d", interval="30m")
    df = df[['Close']].rename(columns={"Close": "price"})
    df["price"] = df["price"].astype(float)
    return df

# Fetch daily AUD/USD data for 200-day SMA
def get_daily_data():
    df = yf.download("AUDUSD=X", period="3mo", interval="1d")
    df = df[['Close']].rename(columns={"Close": "price"})
    df["SMA_200"] = df['price'].rolling(window=200).mean()
    return df

# Calculate indicators
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
    breakdown = []
    try:
        indicators = {
            "RSI > 70 (AUD overbought)": float(row['RSI']) > 70,
            "MACD crossover bearish": float(prev['MACD']) > float(prev['MACD_Signal']) and float(row['MACD']) < float(row['MACD_Signal']),
            "Price > 50-SMA (uptrend)": float(row['price']) > float(row['SMA_50'])
        }
        for name, passed in indicators.items():
            if passed:
                breakdown.append(f"✅ {name}")
                score += 30
            else:
                breakdown.append(f"❌ {name}")
        return score, breakdown
    except Exception as e:
        st.warning(f"Scoring error: {e}")
        return 0, [f"⚠️ Scoring error: {e}"]

# Load data
data = get_fx_data()
data = calculate_indicators(data)

daily_data = get_daily_data()
latest = data.iloc[-1]
prev = data.iloc[-2]
latest_daily = daily_data.iloc[-1]

# Safely compare to SMA_200
try:
    sma200_value = float(latest_daily['SMA_200'])
    sma200_display = f"{sma200_value:.4f}" if np.isfinite(sma200_value) else "N/A"
    above_200_sma = float(latest_daily['price']) > sma200_value
except:
    sma200_display = "N/A"
    above_200_sma = False

# Calculate score
score, breakdown = calculate_aud_strength_score(latest, prev)

# UI
st

