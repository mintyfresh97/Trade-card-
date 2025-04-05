import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import pandas as pd

# Define CoinGecko IDs and icon filenames
coingecko_ids = {
    'Bitcoin (BTC)': 'bitcoin',
    'Ethereum (ETH)': 'ethereum',
    'XRP (XRP)': 'ripple',
    'Solana (SOL)': 'solana',
    'Cardano (ADA)': 'cardano',
    'Chainlink (LINK)': 'chainlink',
    'Curve (CRV)': 'curve-dao-token',
    'Convex (CVX)': 'convex-finance',
    'Sui (SUI)': 'sui',
    'Fartcoin (FARTCOIN)': 'fartcoin',
    'Ondo (ONDO)': 'ondo-finance'
}

icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png",
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png",
    "FARTCOIN": "fartcoin-logo.png"
}

# Function to fetch live price (and optionally 24h change) from CoinGecko
def get_crypto_price_from_coingecko(name, vs_currency="usd", include_24hr_change=False):
    try:
        coin_id = coingecko_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinGecko ID")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
        if include_24hr_change:
            url += "&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        if coin_id not in data or vs_currency not in data[coin_id]:
            raise ValueError(f"Unexpected API response: {data}")
        price = round(data[coin_id][vs_currency], 2)
        if include_24hr_change:
            change_key = f"{vs_currency}_24h_change"
            if change_key in data[coin_id]:
                change = round(data[coin_id][change_key], 2)
                return price, change
            else:
                st.warning("24h change data not available")
                return price, None
        return price
    except Exception as e:
        st.error(f"CoinGecko API Error for {name}: {e}")
        return None

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    display_names = list(coingecko_ids.keys())
    asset_display = st.selectbox("Select Asset", display_names)
    asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()
    icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")

# --- Fetch Live Price with 24h Change ---
try:
    result = get_crypto_price_from_coingecko(asset_display, include_24hr_change=True)
    if result is None:
        live_price = None
        change_24h = None
        entry_price_default = 82000.0
    elif isinstance(result, tuple):
        live_price, change_24h = result
        entry_price_default = float(live_price) if live_price is not None else 82000.0
    else:
        live_price = result
        change_24h = None
        entry_price_default = float(live_price) if live_price is not None else 82000.0
except Exception as e:
    st.warning(f"Price fetch error: {e}")
    live_price = None
    change_24h = None
    entry_price_default = 82000.0

entry = st.number_input("Entry Price", value=entry_price_default, format="%.2f")

# Other trade inputs
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

# Hide Trade Card Preview by default using an expander
with col2:
    with st.expander("Show Trade Card Preview", expanded=False):
        st.subheader("Trade Card")
        st.markdown(f"Asset: {asset_symbol}")
        if live_price is not None:
            st.markdown(f"Live Price: {live_price}")
            if change_24h is not None:
                st.markdown(f"24h Change: {change_24h}%")
        else:
            st.markdown("Live Price: N/A")
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
    lines.append(f"Live Price: {live_price}")

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

    # Centered heading
    asset_name = asset_display.split("(")[0].strip()
    title = f"{asset_name} Risk Setup"
    bbox = heading_font.getbbox(title)
    title_w = bbox[2] - bbox[0]
    title_h = bbox[3] - bbox[1]
    draw.text(((700 - title_w) // 2, 30), title, font=heading_font, fill=(255, 255, 255))

    # Logo
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
        text = line.replace("===", "").strip() if line.startswith("===") else line
        draw.text((30, y), text, fill=color, font=font)
        y += line_height

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="Download Image",
        data=buf.getvalue(),
        file_name=f"trade_card_{asset_symbol}_{trade_date}.png",
        mime="image/png"
    )

st.markdown("---")
st.header("Strategy Tracker")

# Strategy logging inputs
track_col1, track_col2 = st.columns(2)
with track_col1:
    strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
    trade_result = st.selectbox("Trade Outcome", ["Win", "Loss", "Break-even"])
with track_col2:
    rr_logged = st.text_input("RR Ratio", value=f"{rr_ratio}:1")
    notes = st.text_area("Additional Notes")

# Save trade log
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

# Show history
if os.path.exists("trade_log.csv"):
    st.markdown("### Trade History")
    df_hist = pd.read_csv("trade_log.csv")
    st.dataframe(df_hist)

    # Stats
    st.markdown("### Performance Summary")
    total = len(df_hist)
    wins = len(df_hist[df_hist["Outcome"] == "Win"])
    losses = len(df_hist[df_hist["Outcome"] == "Loss"])
    win_rate = round((wins / total) * 100, 1) if total > 0 else 0
    st.write(f"Total Trades: {total}")
    st.write(f"Win Rate: {win_rate}%")
    st.write(f"Most Used Strategy: {df_hist['Strategy'].mode()[0] if total > 0 else '-'}")

# --- Streamlit Charts and Export ---
if os.path.exists("trade_log.csv"):
    st.markdown("### Trade Analytics")

    df_hist = pd.read_csv("trade_log.csv")
    df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')

    # Outcome bar chart
    st.subheader("Trade Outcomes")
    outcome_counts = df_hist['Outcome'].value_counts()
    st.bar_chart(outcome_counts)

    # RR ratio line chart
    try:
        df_hist['RR Numeric'] = df_hist['RR Ratio'].str.extract('([0-9\.]+)').astype(float)
        df_hist_sorted = df_hist.sort_values("Date")
        rr_data = df_hist_sorted.set_index("Date")[["RR Numeric"]]
        st.subheader("RR Ratio Over Time")
        st.line_chart(rr_data)
    except Exception as e:
        st.warning(f"Could not plot RR Ratio chart: {e}")

    # CSV export
    st.download_button(
        label="Download Trade History CSV",
        data=df_hist.to_csv(index=False),
        file_name="trade_log.csv",
        mime="text/csv"
    )
