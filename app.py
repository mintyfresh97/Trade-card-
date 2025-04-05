import streamlit as st
import requests
import os
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import pandas as pd
import random
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ---------------------------
# 1. User Authentication
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        # Replace with a secure authentication method as needed
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")
    st.stop()

# ---------------------------
# 2. Real-Time Data Updates (Auto Refresh)
# ---------------------------
# Refresh the app every 30 seconds (30,000 ms)
st_autorefresh(interval=30000, limit=100, key="autorefresh")

# ---------------------------
# 3. Data & API Functions
# ---------------------------
# Updated CoinPaprika IDs and icon filenames
coinpaprika_ids = {
    'Bitcoin (BTC)': 'btc-bitcoin',
    'Ethereum (ETH)': 'eth-ethereum',
    'Cardano (ADA)': 'ada-cardano',
    'Solana (SOL)': 'sol-solana',
    'XRP (XRP)': 'xrp-xrp',
    'Chainlink (LINK)': 'link-chainlink',
    'Ondo (ONDO)': 'ondo-ondo',
    'Sui (SUI)': 'sui-sui',
    'Curve DAO Token (CRV)': 'crv-curve-dao-token',
    'Convex Finance (CVX)': 'cvx-convex-finance',
    'Based Fartcoin (FARTCOIN)': 'fartcoin-based-fartcoin'
}

icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png",
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png",
    "FARTCOIN": "fartcoin-logo.png"
}

def get_coin_data_from_paprika(name, vs_currency="USD"):
    """
    Fetches live price and percentage changes (24h, 7d, 30d) for a given coin.
    """
    try:
        coin_id = coinpaprika_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinPaprika ID for coin: " + name)
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        response = requests.get(url, timeout=5)
        data = response.json()
        usd_data = data.get("quotes", {}).get(vs_currency, {})
        price = round(usd_data.get("price", 0), 2)
        daily = round(usd_data.get("percent_change_24h", 0), 2)
        weekly = round(usd_data.get("percent_change_7d", 0), 2)
        monthly = round(usd_data.get("percent_change_30d", 0), 2)
        return price, daily, weekly, monthly
    except Exception as e:
        st.error(f"CoinPaprika API Error for {name}: {e}")
        return None, None, None, None

def get_social_sentiment(coin):
    """
    Dummy function to simulate social sentiment analysis.
    In production, integrate with a service (e.g., LunarCrush, Santiment).
    """
    sentiment_score = random.randint(-100, 100)
    if sentiment_score > 20:
        sentiment = "Positive"
    elif sentiment_score < -20:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, sentiment_score

# ---------------------------
# 4. Layout and Main App
# ---------------------------
st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Create two columns: left for selection/market data, right for charts & preview
col1, col2 = st.columns([1, 2])

# LEFT COLUMN
with col1:
    display_names = list(coinpaprika_ids.keys())
    asset_display = st.selectbox("Select Asset", display_names)
    asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()
    icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")
    
    # Fetch market data from CoinPaprika
    price, daily_change, weekly_change, monthly_change = get_coin_data_from_paprika(asset_display)
    if price is not None:
        st.markdown(f"**Live Price:** ${price}")
        st.markdown(
            f"**Daily (24h):** {daily_change}%  \n"
            f"**Weekly (7d):** {weekly_change}%  \n"
            f"**Monthly (30d):** {monthly_change}%"
        )
    else:
        st.markdown("No market data available.")
    
    # Display Social Sentiment
    sentiment, sentiment_score = get_social_sentiment(asset_display)
    st.markdown(f"**Social Sentiment:** {sentiment} (Score: {sentiment_score})")

# RIGHT COLUMN
with col2:
    # ---------------------------
    # Plotly Chart: 24h % Change Heatmap
    # ---------------------------
    # Prepare a dummy DataFrame for the snapshot chart (replace with live multi‑coin data as needed)
    df = pd.DataFrame({
        "Symbol": ["BTC", "ETH", "ADA", "FARTCOIN", "SUI", "LINK", "ONDO", "CRV"],
        "Change (%)": [2.4, -1.3, 3.1, 11.7, 6.3, 5.6, -4.2, -2.8]
    })
    fig = px.bar(
        df,
        x="Symbol",
        y="Change (%)",
        color="Change (%)",
        color_continuous_scale="RdYlGn",
        title="24h % Change Heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ---------------------------
    # Collapsible Trade Card Preview
    # ---------------------------
    with st.expander("Show Trade Card Preview", expanded=False):
        st.subheader("Trade Card")
        st.markdown(f"Asset: {asset_symbol}")
        if price is not None:
            st.markdown(f"Live Price: ${price}")
            st.markdown(f"24h Change: {daily_change}%")
        else:
            st.markdown("Live Price: N/A")
        
        # Trade inputs & details
        entry_price_default = price if price is not None else 82000.0
        entry = st.number_input("Entry Price", value=entry_price_default, format="%.2f")
        position = st.number_input("Position Size (£)", value=500.0)
        leverage = st.number_input("Leverage", value=20)
        stop_loss = st.number_input("Stop Loss", value=round(entry * 0.99, 2), format="%.2f")
        take_profit = st.number_input("Take Profit", value=round(entry * 1.02, 2), format="%.2f")
        timeframes = ["1m", "5m", "15m", "1h", "4h", "Daily"]
        entry_tf = st.selectbox("Entry Timeframe", options=timeframes, index=1)
        analysis_tf = st.selectbox("Analysis Timeframe", options=timeframes, index=2)
        st.markdown("### Trade Notes")
        strategy = st.text_input("Trade Strategy", placeholder="e.g. EMA Bounce, Breakout Rejection")
        news = st.text_input("News Catalyst", placeholder="e.g. FOMC, ETF Approval, CPI Report")
        execution = st.text_input("Execution Plan", placeholder="e.g. Enter on candle close, SL below wick")
        psychology = st.text_input("Psychology Reminder", placeholder="e.g. Stick to plan, avoid revenge trading")
        tags = st.multiselect("Tags", options=["Scalp", "Swing", "Long", "Short", "1H", "4H", "Daily", "Breakout", "Rejection"])
        
        trade_date = datetime.now().strftime("%Y-%m-%d")
        total_exposure = position * leverage
        risk = abs(entry - stop_loss) * total_exposure / entry
        reward = abs(take_profit - entry) * total_exposure / entry
        breakeven = round((entry + stop_loss) / 2, 2)
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0
        
        st.markdown(f"Position: £{position}")
        st.markdown(f"Leverage: {leverage}x")
        st.markdown(f"Entry: {entry}")
        st.markdown(f"Stop Loss: {stop_loss}")
        st.markdown(f"Take Profit: {take_profit}")
        st.markdown(f"Risk: £{risk:.2f}")
        st.markdown(f"Reward: £{reward:.2f}")
        st.markdown(f"RR Ratio: {rr_ratio}:1")
        st.markdown(f"Breakeven: {breakeven}")
        st.markdown(f"Date: {trade_date}")
        st.markdown(f"Entry TF: {entry_tf}")
        st.markdown(f"Analysis TF: {analysis_tf}")
        if strategy:
            st.markdown(f"**Strategy:** {strategy}")
        if news:
            st.markdown(f"**News Catalyst:** {news}")
        if execution:
            st.markdown(f"**Execution Plan:** {execution}")
        if psychology:
            st.markdown(f"**Psychology Reminder:** {psychology}")
        if tags:
            st.markdown(f"**Tags:** {', '.join(tags)}")
        
        if st.button("Download Trade Card"):
            lines = []
            lines.append("=== Trade Info ===")
            lines.append(f"Asset: {asset_symbol}")
            lines.append(f"Date: {trade_date}")
            lines.append(f"Live Price: ${price}")
            lines.append("")
            lines.append("=== Entry Setup ===")
            lines.append(f"Entry: {entry}")
            lines.append(f"Stop: {stop_loss}")
            lines.append(f"Target: {take_profit}")
            lines.append(f"Risk: £{risk:.2f}")
            lines.append(f"Reward: £{reward:.2f}")
            lines.append(f"RR Ratio: {rr_ratio}:1")
            lines.append(f"Breakeven: {breakeven}")
            lines.append("")
            lines.append("=== Timeframes ===")
            lines.append(f"Entry TF: {entry_tf}")
            lines.append(f"Analysis TF: {analysis_tf}")
            lines.append("")
            lines.append("=== Notes ===")
            if strategy:
                lines.extend(textwrap.wrap(f"Strategy: {strategy}", width=50))
            if news:
                lines.extend(textwrap.wrap(f"News: {news}", width=50))
            if execution:
                lines.extend(textwrap.wrap(f"Execution Plan: {execution}", width=50))
            if psychology:
                lines.extend(textwrap.wrap(f"Mindset: {psychology}", width=50))
            if tags:
                lines.extend(textwrap.wrap(f"Tags: {', '.join(tags)}", width=50))
            
            line_height = 34
            image_height = 140 + line_height * len(lines)
            img = Image.new("RGB", (700, image_height), color=(20, 20, 20))
            draw = ImageDraw.Draw(img)
            try:
                heading_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
                body_font = ImageFont.truetype("DejaVuSans.ttf", 18)
            except:
                heading_font = body_font = ImageFont.load_default()
            asset_name = asset_display.split("(")[0].strip()
            title = f"{asset_name} Risk Setup"
            bbox = heading_font.getbbox(title)
            title_w = bbox[2] - bbox[0]
            draw.text(((700 - title_w) // 2, 30), title, font=heading_font, fill=(255, 255, 255))
            logo_path = f"assets/{icon_map.get(asset_symbol, '')}"
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path).convert("RGBA").resize((64, 64))
                    img.paste(logo, (620, 20), logo)
                except Exception as e:
                    st.warning(f"Could not load logo: {e}")
            y = 100
            for line in lines:
                font = heading_font if line.startswith("===") else body_font
                color = (255, 165, 0) if line.startswith("===") else (255, 255, 255)
                text_line = line.replace("===", "").strip() if line.startswith("===") else line
                draw.text((30, y), text_line, fill=color, font=font)
                y += line_height
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name=f"trade_card_{asset_symbol}_{trade_date}.png",
                mime="image/png"
            )

# ---------------------------
# 5. Trade Log & Advanced Analytics
# ---------------------------
st.markdown("---")
st.header("Strategy Tracker")
track_col1, track_col2 = st.columns(2)
with track_col1:
    strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
    trade_result = st.selectbox("Trade Outcome", ["Win", "Loss", "Break-even"])
with track_col2:
    rr_logged = st.text_input("RR Ratio", value=f"{rr_ratio}:1")
    notes = st.text_area("Additional Notes")

if st.button("Save Trade to Log"):
    trade_data = {
        "Date": [trade_date],
        "Asset": [asset_symbol],
        "Strategy": [strategy_used],
        "RR Ratio": [rr_logged],
        "Outcome": [trade_result],
        "Notes": [notes],
    }
    df_new = pd.DataFrame(trade_data)
    log_path = "trade_log.csv"
    if os.path.exists(log_path):
        df_existing = pd.read_csv(log_path)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(log_path, index=False)
    st.success("Trade saved to log!")

if os.path.exists("trade_log.csv"):
    st.markdown("### Trade History")
    df_hist = pd.read_csv("trade_log.csv")
    st.dataframe(df_hist)
    st.sidebar.header("Filter Trade History")
    date_filter = st.sidebar.date_input("Select Date Range", [])
    if date_filter and len(date_filter) == 2:
        start_date, end_date = date_filter
        df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
        df_filtered = df_hist[(df_hist['Date'] >= pd.to_datetime(start_date)) & (df_hist['Date'] <= pd.to_datetime(end_date))]
        st.write("Filtered Trade History:")
        st.dataframe(df_filtered)
    st.markdown("### Performance Summary")
    total = len(df_hist)
    wins = len(df_hist[df_hist["Outcome"] == "Win"])
    losses = len(df_hist[df_hist["Outcome"] == "Loss"])
    win_rate = round((wins / total) * 100, 1) if total > 0 else 0
    st.write(f"Total Trades: {total}")
    st.write(f"Win Rate: {win_rate}%")
    st.write(f"Most Used Strategy: {df_hist['Strategy'].mode()[0] if total > 0 else '-'}")

if os.path.exists("trade_log.csv"):
    st.markdown("### Trade Analytics")
    df_hist = pd.read_csv("trade_log.csv")
    df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
    st.subheader("Trade Outcomes")
    outcome_counts = df_hist['Outcome'].value_counts()
    st.bar_chart(outcome_counts)
    try:
        df_hist['RR Numeric'] = df_hist['RR Ratio'].str.extract('([0-9\.]+)').astype(float)
        df_hist_sorted = df_hist.sort_values("Date")
        rr_data = df_hist_sorted.set_index("Date")[["RR Numeric"]]
        st.subheader("RR Ratio Over Time")
        st.line_chart(rr_data)
    except Exception as e:
        st.warning(f"Could not plot RR Ratio chart: {e}")
    st.download_button(
        label="Download Trade History CSV",
        data=df_hist.to_csv(index=False),
        file_name="trade_log.csv",
        mime="text/csv"
    )
