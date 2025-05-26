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

# Calculate strength score
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
            breakdown.append(f"{'✅' if passed else '❌'} {label}")
            score += 30 if passed else 0
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

# Score + breakdown
score, breakdown = calculate_aud_strength_score(latest, prev)

# UI begins
st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

st.subheader("Latest FX Rate")
st.metric("AUD/USD", f"{float(latest['price']):.4f}")

st.subheader("Technical Indicators")
st.write(f"RSI: {float(latest['RSI']):.2f}")
st.write(f"MACD: {float(latest['MACD']):.4f}")
st.write(f"MACD Signal: {float(latest['MACD_Signal']):.4f}")
st.write(f"50-period SMA (30m): {float(latest['SMA_50']):.4f}")
st.write(f"200-day SMA (1d): {sma200_display}")

# Sentiment
sentiment_signals = [
    float(latest['RSI']) > 70,
    float(prev['MACD']) > float(prev['MACD_Signal']) and float(latest['MACD']) < float(latest['MACD_Signal']),
    float(latest['price']) > float(latest['SMA_50']),
    above_200_sma
]
sentiment_strength = int((sum(sentiment_signals) / 4) * 100)
st.subheader("AUD Sentiment Meter")
st.progress(sentiment_strength, text=f"AUD bullish sentiment: {sentiment_strength}%")

# Score bar
st.subheader("📊 AUD Strength Score (for Buying USD)")
col1, col2 = st.columns([1, 4])
col1.markdown("**Score**")
col2.progress(score, text=f"{score}%")

# Labels
if score >= 80:
    st.success("🟢 Great time to buy USD (AUD is strong)")
elif score >= 50:
    st.warning("🟠 Moderate zone — Monitor closely")
else:
    st.info("🔴 Not ideal — AUD is weak")

# Breakdown
st.markdown("**🔍 Indicator Breakdown:**")
for item in breakdown:
    st.markdown(f"- {item}")

# Pre-Buy Alert
st.subheader("📡 Pre-Buy Alert Zone")
try:
    macd_diff = float(latest['MACD']) - float(latest['MACD_Signal'])
    if float(latest['RSI']) > 70 and 0 < macd_diff < 0.001:
        st.warning("⚠️ AUD is strong but momentum is fading. Consider buying USD now before MACD crossover.")
    elif float(latest['RSI']) > 68 and -0.0005 < macd_diff < 0.0005:
        st.info("🕒 RSI is elevated and MACD is flattening — last chance zone to buy USD.")
except:
    st.caption("Could not calculate MACD divergence.")

# Trend Forecast
st.subheader("🔮 Trend Forecast")
try:
    short_data = data.tail(20).copy()
    short_data["MACD_hist"] = short_data["MACD"] - short_data["MACD_Signal"]
    price_slope = np.polyfit(range(len(short_data)), short_data["price"], 1)[0]
    sma_slope = np.polyfit(range(len(short_data)), short_data["SMA_50"], 1)[0]
    macd_slope = np.polyfit(range(len(short_data)), short_data["MACD_hist"], 1)[0]

    if price_slope < 0 and sma_slope < 0:
        st.markdown("- 📉 AUD price and trend slope down — weakening expected")
    elif price_slope > 0 and sma_slope > 0:
        st.markdown("- 📈 AUD is trending up — continuation likely")
    else:
        st.markdown("- 🟰 Price trend is uncertain — watch key indicators")

    if macd_slope < 0:
        st.markdown("- 📉 MACD histogram falling — bearish momentum building")
    elif macd_slope > 0:
        st.markdown("- 📈 MACD histogram rising — bullish pressure increasing")
except:
    st.warning("⚠️ Unable to calculate trend forecast.")

# Trend summary
try:
    change = float((data['price'].iloc[-1] - data['price'].iloc[0]) / data['price'].iloc[0] * 100)
    st.markdown(f"📊 **AUD has {'strengthened' if change > 0 else 'weakened'} by {abs(change):.2f}%** over the last 5 days.")
except:
    st.markdown("⚠️ Unable to calculate price trend.")

# What should I do right now?
st.subheader("🎯 What Should I Do Right Now?")
try:
    hist = data["MACD"] - data["MACD_Signal"]
    macd_dir = np.sign(hist.diff().iloc[-1])
    rsi_dir = np.sign(data['RSI'].diff().iloc[-1])
    if score >= 80:
        action_text = "✅ AUD is strong. This is a great time to buy USD."
    elif score >= 50:
        action_text = "⚠️ AUD is somewhat strong. You could buy some USD now, but keep an eye on MACD."
    else:
        action_text = "🚫 AUD is weak. Best to wait before buying USD."

    st.markdown(f"""
**{action_text}**

- **Exchange Rate**: `{float(latest['price']):.4f}`
- **Score**: `{score}%` | **Sentiment**: `{sentiment_strength}% bullish`
- **MACD**: `{'⬆️ Going up' if macd_dir > 0 else '⬇️ Falling' if macd_dir < 0 else '➡️ Flat'}`
- **RSI**: `{'⬆️ Rising' if rsi_dir > 0 else '⬇️ Dropping' if rsi_dir < 0 else '➡️ Flat'}`
""")
except:
    st.markdown("⚠️ Could not generate FX action summary.")

# Chart
st.subheader("AUD/USD Price Chart")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['price'], label='AUD/USD')
ax.plot(data.index, data['SMA_50'], label='50-period SMA (30m)', linestyle='--')
ax.set_ylabel("Exchange Rate")
ax.set_title("AUD/USD with SMA")
ax.legend()
st.pyplot(fig)

# News headlines
st.subheader("📰 Relevant News Headlines")
news_feed = feedparser.parse("https://www.rba.gov.au/rss/rss.xml")
for entry in news_feed.entries[:5]:
    st.markdown(f"**[{entry.title}]({entry.link})**  \n- {entry.published}")

# Footer
st.caption(f"Live intraday FX data from Yahoo Finance. Last updated: {data.index[-1].strftime('%Y-%m-%d %H:%M UTC')}.")
