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

# Score logic
def calculate_aud_strength_score(row, prev):
    score = 0
    breakdown = []
    try:
        indicators = {
            "RSI > 70 (AUD overbought)": float(row['RSI']) > 70,
            "MACD crossover bearish": float(prev['MACD']) > float(prev['MACD_Signal']) and float(row['MACD']) < float(row['MACD_Signal']),
            "Price > 50-SMA (uptrend)": float(row['price']) > float(row['SMA_50'])
        }
        for label, passed in indicators.items():
            if passed:
                breakdown.append(f"✅ {label}")
                score += 30
            else:
                breakdown.append(f"❌ {label}")
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

# Handle SMA_200
try:
    sma200_value = float(latest_daily['SMA_200'])
    sma200_display = f"{sma200_value:.4f}" if np.isfinite(sma200_value) else "N/A"
    above_200_sma = float(latest_daily['price']) > sma200_value
except:
    sma200_display = "N/A"
    above_200_sma = False

score, breakdown = calculate_aud_strength_score(latest, prev)

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
    - **RSI > 70** → AUD is overbought
    - **MACD crossover bearish**
    - **Price above 50-SMA**
    - **Price above 200-SMA**
    """)

sentiment_signals = [
    float(latest['RSI']) > 70,
    float(prev['MACD']) > float(prev['MACD_Signal']) and float(latest['MACD']) < float(latest['MACD_Signal']),
    float(latest['price']) > float(latest['SMA_50']),
    above_200_sma
]
sentiment_strength = int((sum(sentiment_signals) / 4) * 100)
st.progress(sentiment_strength, text=f"AUD bullish sentiment: {sentiment_strength}%")

# Score summary
st.subheader("📊 AUD Strength Score (for Buying USD)")
col1, col2 = st.columns([1, 4])
col1.markdown("**Score**")
col2.progress(score, text=f"{score}%")

if score >= 80:
    st.success("🟢 Great time to buy USD (AUD is strong)")
elif score >= 50:
    st.warning("🟠 Moderate zone — Monitor closely")
else:
    st.info("🔴 Not ideal — AUD is weak")

st.markdown("**🔍 Indicator Breakdown:**")
for item in breakdown:
    icon = "✅" if "✅" in item else "❌"
    label = item.replace("✅ ", "").replace("❌ ", "")
    st.markdown(f"- {icon} **{label}**")

# Pre-buy alert
st.subheader("📡 Pre-Buy Alert Zone")
try:
    macd_diff = float(latest['MACD']) - float(latest['MACD_Signal'])
    if float(latest['RSI']) > 70 and macd_diff > 0 and macd_diff < 0.001:
        st.warning("⚠️ AUD is strong but momentum is fading. Consider buying USD now before MACD crossover.")
    elif float(latest['RSI']) > 68 and macd_diff > -0.0005 and macd_diff < 0.0005:
        st.info("🕒 RSI is elevated and MACD is flattening — last chance zone to buy USD.")
except:
    st.caption("Could not calculate MACD divergence.")

# Trend forecast
st.subheader("🔮 Trend Forecast")
try:
    short_data = data.tail(20).copy()
    short_data["MACD_hist"] = short_data["MACD"] - short_data["MACD_Signal"]
    price_slope = np.polyfit(range(len(short_data)), short_data["price"], 1)[0]
    sma_slope = np.polyfit(range(len(short_data)), short_data["SMA_50"], 1)[0]
    macd_slope = np.polyfit(range(len(short_data)), short_data["MACD_hist"], 1)[0]

    trend_signals = []
    if price_slope < 0 and sma_slope < 0:
        trend_signals.append("📉 AUD price and trend slope down — weakening expected")
    elif price_slope > 0 and sma_slope > 0:
        trend_signals.append("📈 AUD is trending up — continuation likely")
    else:
        trend_signals.append("🟰 Price trend is uncertain — watch key indicators")

    if macd_slope < 0:
        trend_signals.append("📉 MACD histogram falling — bearish momentum building")
    elif macd_slope > 0:
        trend_signals.append("📈 MACD histogram risi_
