import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Supported assets and their logo paths
ASSETS = {
    "BTC": "assets/BTC.png",
    "ETH": "assets/ETH.png",
    "XRP": "assets/XRP.png",
    "ADA": "assets/ADA.png",
    "SOL": "assets/SOL.png",
    "LINK": "assets/LINK.png",
    "ONDO": "assets/ONDO.png",
    "CRV": "assets/CRV.png",
    "CVX": "assets/CVX.png",
    "SUI": "assets/SUI.png",
    "FARTCOIN": "assets/FARTCOIN.png",
}

# Set layout and title
st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")
st.title("PnL & Risk Dashboard")

# Asset selection
col1, col2 = st.columns([1, 6])
with col1:
    asset = st.selectbox("Select Asset", list(ASSETS.keys()))
with col2:
    st.image(ASSETS[asset], width=50)

# Input fields
position = st.number_input("Position Size (£)", value=500)
leverage = st.number_input("Leverage", value=20)
entry = st.number_input("Entry Price")
stop = st.number_input("Stop Loss")
target = st.number_input("Take Profit")

# Autofill live price
if st.button("Fetch Live Price"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset.lower()}&vs_currencies=usd"
        response = requests.get(url).json()
        live_price = response[asset.lower()]["usd"]
        entry = round(live_price, 5)
        st.success(f"Live price for {asset}: ${entry}")
    except Exception as e:
        st.error(f"Error fetching price: {e}")

# Calculations
if entry and stop and target:
    total_exposure = position * leverage
    risk = abs(entry - stop) * total_exposure / entry
    reward = abs(target - entry) * total_exposure / entry
    breakeven = round((entry + stop) / 2, 5)
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    st.subheader("Trade Metrics")
    st.markdown(f"- **Total Exposure**: £{total_exposure}")
    st.markdown(f"- **Risk**: £{risk:.2f}")
    st.markdown(f"- **Reward**: £{reward:.2f}")
    st.markdown(f"- **Breakeven Price**: {breakeven}")
    st.markdown(f"- **Reward-to-Risk Ratio**: {rr_ratio}:1")

    # Trade Card
    st.subheader("Trade Card")

    try:
        card = Image.new("RGB", (600, 300), color="#111111")
        draw = ImageDraw.Draw(card)
        font = ImageFont.load_default()

        draw.text((20, 20), f"{asset} Trade Summary – {datetime.now().strftime('%Y-%m-%d')}", fill="white", font=font)

        details = [
            f"Position: £{position}",
            f"Leverage: {leverage}x",
            f"Entry: {entry}",
            f"Stop Loss: {stop}",
            f"Take Profit: {target}",
            f"RR: {rr_ratio}:1",
            f"Risk: £{risk:.2f}",
            f"Reward: £{reward:.2f}"
        ]

        for i, line in enumerate(details):
            draw.text((20, 60 + i * 28), line, fill="white", font=font)

        buffer = BytesIO()
        card.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        st.image(image_bytes)
        st.download_button("Download Trade Card", data=image_bytes, file_name=f"{asset}_trade_card.png", mime="image/png")
    except Exception as e:
        st.error(f"Error generating trade card: {e}")
