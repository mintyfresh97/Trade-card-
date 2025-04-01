import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io


# CoinGecko ID mapping
coingecko_ids = {
    'Bitcoin (BTC)': 'bitcoin',
    'Ethereum (ETH)': 'ethereum',
    'XRP': 'ripple',
    'Solana (SOL)': 'solana',
    'Cardano (ADA)': 'cardano',
    'Chainlink (LINK)': 'chainlink',
    'Curve (CRV)': 'curve-dao-token',
    'Convex (CVX)': 'convex-finance',
    'Sui (SUI)': 'sui',
    'Fartcoin': 'fartcoin',
    'Ondo (ONDO)': 'ondo-finance'
}

# Asset precision and icon filenames
precision_map = {
    "BTC": 5, "ETH": 4, "XRP": 3, "ADA": 3, "SOL": 5, "LINK": 3,
    "ONDO": 3, "CRV": 3, "CVX": 3, "SUI": 3, "FARTCOIN": 3
}

icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png", 
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png", 
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png", 
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png", 
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png", 
    "FARTCOIN": "fartcoin-logo.png"
}

# Function to get cryptocurrency price from CoinGecko
def get_crypto_price_from_coingecko(name):
    try:
        coin_id = coingecko_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinGecko ID")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data[coin_id]['usd']
    except Exception as e:
        st.error(f"CoinGecko API Error for {name}: {e}")
        return None

# Function to get stock price using Yahoo Finance
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        return data['Close'].iloc[-1]
    except Exception as e:
        st.error(f"Yahoo Finance Error for {symbol}: {e}")
        return None

# Set page layout
st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# --- Input fields ---
col1, col2 = st.columns([1, 2])

with col1: 
    asset = st.selectbox("Select Asset", list(precision_map.keys())) 
    icon_path = f"assets/{icon_map.get(asset, '')}" 
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")

position = st.number_input("Position Size (£)", value=500.0)
leverage = st.number_input("Leverage", value=20)

# Auto-fetch price
try:
    api_id = asset.lower()
    res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={api_id}&vs_currencies=usd")
    live_price = res.json().get(api_id, {}).get("usd", None)
    if live_price:
        entry = st.number_input("Entry Price", value=float(live_price))
    else:
        entry = st.number_input("Entry Price", value=82000.0)
except:
    entry = st.number_input("Entry Price", value=82000.0)
    live_price = "Not available"

stop_loss = st.number_input("Stop Loss", value=81000.0)
take_profit = st.number_input("Take Profit", value=83000.0)
trade_date = datetime.now().strftime("%Y-%m-%d")

# --- Calculations ---
digits = precision_map[asset]
total_exposure = position * leverage
risk = abs(entry - stop_loss) * total_exposure / entry
reward = abs(take_profit - entry) * total_exposure / entry
breakeven = round((entry + stop_loss) / 2, digits)
rr_ratio = round(reward / risk, 2) if risk != 0 else 0

# --- Display Trade Card ---
with col2: 
    st.subheader("Trade Card")
    st.markdown(f"Asset: {asset}")
    st.markdown(f"Live Price: {live_price if live_price else 'N/A'}")
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

# --- Downloadable Image ---
if st.button("Download Trade Card"):
    img = Image.new("RGB", (600, 400), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    lines = [
        f"Asset: {asset}",
        f"Date: {trade_date}",
        f"Live Price: {live_price}",
        f"Entry: {entry}",
        f"Stop: {stop_loss}",
        f"Target: {take_profit}",
        f"Risk: £{risk:.2f}",
        f"Reward: £{reward:.2f}",
        f"RR Ratio: {rr_ratio}:1",
        f"Breakeven: {breakeven}"
    ]

    for i, line in enumerate(lines):
        draw.text((20, 20 + i * 30), line, fill=(255, 255, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="Download Image",
        data=buf.getvalue(),
        file_name=f"trade_card_{asset}_{trade_date}.png",
        mime="image/png"
    )
