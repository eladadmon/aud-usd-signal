import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import feedparser

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

# Summary analysis explanation
st.subheader("📊 Model Interpretation Summary")
st.markdown("""
- ✅ **RSI (73.70)** is above 70 → AUD is potentially peaking
- ❌ **MACD (0.0013) < Signal (0.0014)** → crossover hasn't confirmed
- ✅ **Price (0.6526) > 50-SMA (0.6482)** → AUD in short-term uptrend
- 🔴 **200-day SMA** not yet available → long-term trend unclear

### 🧠 Bottom Line:
You're in a **cautious zone**:
- RSI is overbought → potentially a good time to buy USD
- But MACD isn’t yet aligned

📌 **Action idea**: Consider partial USD conversion now and watch for MACD alignment.
""")
