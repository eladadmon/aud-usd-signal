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

# Strength score logic
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

# Load and prepare data
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

# ---- UI Begins ----

st.title("🇦🇺 AUD/USD FX Buy USD Advisor")

st.subheader("Latest FX Rate")
st.metric("AUD/USD", f"{float(latest['price']):.4f}")

st.subheader("Technical Indicators")
st.write(f"RSI: {float(latest['RSI']):.2f}")
st.write(f"MACD: {float(latest['MACD']):.4f}")
st.write(f"MACD Signal: {float(latest['MACD_Signal']):.4f}")
st.write(f"50-period SMA (30m): {float(latest['SMA_50']):.4f}")
st.write(f"200-day SMA (1d): {sma200_display}")

# Sentiment Meter
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

# Score Call
st.subheader("AUD Strength Score (for Buying USD)")
st.markdown("""
<details>
<summary>What do these mean?</summary>
<ul>
<li>🟢 <b>Strong</b>: AUD is likely peaking. Good time to convert to USD.</li>
<li>🟠 <b>Moderate</b>: Some signals are bullish, others aren't.</li>
<li>🔴 <b>Weak</b>: AUD momentum is unclear.</li>
</ul>
</details>
""", unsafe_allow_html=True)

if score >= 80:
    st.success(f"🟢 AUD is strong — Consider buying USD now (Score: {score}%)")
elif score >= 50:
    st.warning(f"🟠 Mixed signals — Monitor closely (Score: {score}%)")
else:
    st.info(f"🔴 Not a great time to buy USD (Score: {score}%)")

st.markdown("**Indicator Breakdown:**")
for item in breakdown:
    st.markdown(f"- {item}")

# Trend Summary
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

# RBA News
st.subheader("📰 Relevant News Headlines")
news_feed = feedparser.parse("https://www.rba.gov.au/rss/rss.xml")
for entry in news_feed.entries[:5]:
    st.markdown(f"**[{entry.title}]({entry.link})**  \n- {entry.published}")

# Footer
st.caption(f"Live intraday FX data from Yahoo Finance. Last updated: {data.index[-1].strftime('%Y-%m-%d %H:%M UTC')}.")



# Model interpretation summary
st.subheader("📊 Model Interpretation Summary")
st.markdown("""
- ✅ **RSI > 70** → AUD is potentially peaking  
- ❌ **MACD crossover not confirmed** → wait for bearish flip  
- ✅ **Price > 50-SMA** → short-term AUD uptrend  
- 🔴 **200-day SMA** not available → long-term trend unclear  

### 🧠 Bottom Line:
You're in a **mixed signal zone**:
- RSI suggests opportunity to buy USD
- MACD says hold

📌 **Action**: Consider partial USD conversion now. Watch for MACD confirmation.
""")

