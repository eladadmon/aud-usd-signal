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

# Safe 200-day SMA check
try:
    sma200_value = float(latest_daily['SMA_200'])
    sma200_display = f"{sma200_value:.4f}" if np.isfinite(sma200_value) else "N/A"
    above_200_sma = float(latest_daily['price']) > sma200_value
except:
    sma200_display = "N/A"
    above_200_sma = False

score = calculate_aud_strength_score(latest, prev)

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
    - **RSI > 70** → AUD is overbought (bullish AUD)
    - **MACD crossover** → Bearish signal forming
    - **Price > 50-SMA** → AUD trending up
    - **Price > 200-SMA** → AUD long-term bullish
    """)

sentiment_signals = [
    float(latest['RSI']) > 70,
    float(prev['MACD']) > float(prev['MACD_Signal']) and float(latest['MACD']) < float(latest['MACD_Signal']),
    float(latest['price']) > float(latest['SMA_50']),
    above_200_sma
]
sentiment_strength = int((sum(sentiment_signals) / 4) * 100)
st.progress(sentiment_strength, text=f"AUD bullish sentiment: {sentiment_strength}%")

# Buy signal score
st.subheader("AUD Strength Score (for Buying USD)")
st.markdown("""
<details>
<summary>What do these mean?</summary>
<ul>
<li>🟢 <b>Strong</b>: AUD is likely peaking. Good time to convert to USD.</li>
<li>🟠 <b>Neutral</b>: AUD is firm, but not all signals align. Monitor closely.</li>
<li>🔴 <b>Weak</b>: AUD likely to weaken further. Hold off if possible.</li>
</ul>
</details>
""", unsafe_allow_html=True)

if score >= 80:
    st.success(f"🟢 AUD is strong — Consider buying USD now (Score: {score}%)")
elif score >= 60:
    st.warning(f"🟠 AUD is neutral — Monitor closely (Score: {score}%)")
else:
    st.info(f"🔴 AUD is weak — Hold off if possible (Score: {score}%)")

# Trend summary
try:
    change = float((data['price'].iloc[-1] - data['price'].iloc[0]) / data['price'].iloc[0] * 100)
    if change > 0:
        st.markdown(f"📈 AUD has strengthened by **{change:.2f}%** over the last 5 days.")
    else:
        st.markdown(f"📉 AUD has weakened by **{abs(change):.2f}%** over the last 5 days.")
except:
    st.markdown("⚠️ Unable to calculate price change trend.")

# Chart
st.subheader("AUD/USD Price Chart")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['price'], label='AUD/USD')
ax.plot(data.index, data['SMA_50'], label='50-period SMA (30m)', linestyle='--')
ax.set_ylabel("Exchange Rate")
ax.set_title("AUD/USD with SMA")
ax.legend()
st.pyplot(fig)

# Footer
st.caption(f"Live intraday FX data from Yahoo Finance. Last updated: {data.index[-1].strftime('%Y-%m-%d %H:%M UTC')}.")
