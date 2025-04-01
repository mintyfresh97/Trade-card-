import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime

st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")
st.title("PnL & Risk Dashboard")

# Precision and CoinGecko icon mapping
precision_map = {
    "BTC": 5, "ETH": 4, "XRP": 3, "ADA": 3, "SOL": 5,
    "LINK": 3, "ONDO": 3, "CRV": 3, "CVX": 3, "SUI": 3, "FARTCOIN": 3
}

coingecko_ids = {
    "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "ADA": "cardano",
    "SOL": "solana", "LINK": "chainlink", "ONDO": "ondo-finance",
    "CRV": "curve-dao-token", "CVX": "convex-finance", "SUI": "sui",
    "FARTCOIN": "fartcoin"
}

# Asset select
asset = st.selectbox("Select Crypto Asset", list(precision_map.keys()))
digits = precision_map[asset]
cg_id = coingecko_ids[asset]

# Icon fetch
icon_url = f"https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
meta = requests.get(f"https://api.coingecko.com/api/v3/coins/{cg_id}").json()
icon_url = meta["image"]["large"]

st.image(icon_url, width=40, caption=asset)

# Live price
price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=gbp"
price_data = requests.get(price_url).json()
live_price = price_data.get(cg_id, {}).get("gbp", None)
entry_price = round(live_price, digits) if live_price else 0

# Inputs
st.markdown("### Trade Setup")
col1, col2 = st.columns(2)
with col1:
    position = st.number_input("Position Size (£)", value=500)
    entry = st.number_input("Entry Price", value=entry_price, format=f"%.{digits}f")
    stop = st.number_input("Stop Loss", value=entry_price * 0.98, format=f"%.{digits}f")
with col2:
    leverage = st.number_input("Leverage", value=20)
    target = st.number_input("Take Profit", value=entry_price * 1.02, format=f"%.{digits}f")

# Calculate
total = position * leverage
risk = abs(entry - stop) * total / entry
reward = abs(target - entry) * total / entry
rr_ratio = round(reward / risk, 2) if risk != 0 else 0
breakeven = round((entry + stop) / 2, digits)
now = datetime.now().strftime("%d %b %Y")

# Submit
if st.button("Generate Trade Card"):
    # Create image
    img = Image.new("RGB", (600, 380), color="#111827")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font_title = font = None

    draw.text((30, 20), "Trade Setup Card", font=font_title, fill="white")
    draw.text((30, 60), f"Asset: {asset}", font=font, fill="white")
    draw.text((30, 90), f"Date: {now}", font=font, fill="white")
    draw.text((30, 120), f"Entry: {entry}", font=font, fill="white")
    draw.text((30, 150), f"Stop: {stop}", font=font, fill="white")
    draw.text((30, 180), f"Target: {target}", font=font, fill="white")
    draw.text((30, 210), f"Leverage: {leverage}x", font=font, fill="white")
    draw.text((30, 240), f"Position: £{position}", font=font, fill="white")
    draw.text((30, 270), f"Risk: £{round(risk, 2)}", font=font, fill="white")
    draw.text((30, 300), f"Reward: £{round(reward, 2)}", font=font, fill="white")
    draw.text((30, 330), f"RR Ratio: {rr_ratio}:1", font=font, fill="white")

    # Add asset logo
    try:
        icon_img = Image.open(requests.get(icon_url, stream=True).raw).convert("RGBA")
        icon_resized = icon_img.resize((48, 48))
        img.paste(icon_resized, (500, 20), icon_resized)
    except:
        pass

    # Display and download
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    st.image(buffer, caption="Trade Card", use_column_width=True)

    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="trade_card.png">📥 Download Trade Card</a>'
    st.markdown(href, unsafe_allow_html=True)
