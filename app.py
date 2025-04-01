import streamlit as st
import requests
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

# Asset configuration
assets = {
    "BTC": {"name": "Bitcoin", "decimals": 5},
    "ETH": {"name": "Ethereum", "decimals": 4},
    "XRP": {"name": "XRP", "decimals": 3},
    "ADA": {"name": "Cardano", "decimals": 3},
    "SOL": {"name": "Solana", "decimals": 5},
    "LINK": {"name": "Chainlink", "decimals": 3},
    "ONDO": {"name": "Ondo", "decimals": 3},
    "CRV": {"name": "Curve", "decimals": 3},
    "CVX": {"name": "Convex", "decimals": 3},
    "SUI": {"name": "Sui", "decimals": 3},
    "FARTCOIN": {"name": "Fartcoin", "decimals": 3}
}

st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

# Select asset
asset = st.selectbox("Select Asset", list(assets.keys()))

# Display icon
icon_path = f"assets/{asset}.png"
try:
    st.image(icon_path, width=64)
except:
    st.warning("Icon not found")

# Get live price
coingecko_id = asset.lower()
price = None
try:
    res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd")
    price = res.json()[coingecko_id]["usd"]
except:
    price = None
    st.error("Live price not available")

# Trade inputs
position = st.number_input("Position Size (£)", value=500.0)
leverage = st.number_input("Leverage", value=20)
entry = st.number_input("Entry Price", value=round(price, assets[asset]["decimals"]) if price else 0.0)
stop = st.number_input("Stop Loss", value=0.0)
target = st.number_input("Take Profit", value=0.0)

# Date input
trade_date = st.date_input("Trade Date", datetime.today())

# Calculations
if entry > 0:
    total_exposure = position * leverage
    risk = abs(entry - stop) * total_exposure / entry
    reward = abs(target - entry) * total_exposure / entry
    breakeven = round((entry + stop) / 2, assets[asset]["decimals"])
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    st.subheader("Trade Summary")
    st.write(f"Live Price: ${price:.{assets[asset]['decimals']}f}" if price else "Live Price: N/A")
    st.write(f"Total Exposure: £{total_exposure:,.2f}")
    st.write(f"Risk: £{risk:,.2f}")
    st.write(f"Reward: £{reward:,.2f}")
    st.write(f"RR Ratio: {rr_ratio}:1")
    st.write(f"Breakeven: {breakeven}")

    # Trade Card Preview
    st.markdown("---")
    st.subheader("Trade Card")

    card = st.empty()
    with card.container():
        st.image(icon_path, width=32)
        st.markdown(f"""
            **{assets[asset]['name']} ({asset})**
            - Date: {trade_date}
            - Entry: {entry}
            - Stop: {stop}
            - Target: {target}
            - Risk: £{risk:,.2f}
            - Reward: £{reward:,.2f}
            - RR: {rr_ratio}:1
        """)

    # Downloadable image (basic HTML)
    trade_summary = f"""
    Trade Summary – {trade_date}
    Asset: {asset}
    Entry: {entry}
    Stop Loss: {stop}
    Take Profit: {target}
    Position: £{position}
    Leverage: {leverage}x
    Risk: £{risk:,.2f}
    Reward: £{reward:,.2f}
    RR Ratio: {rr_ratio}:1
    """

    # Convert to image
    def text_to_image(text):
        from PIL import ImageDraw
        img = Image.new("RGB", (480, 280), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), text, fill=(255, 255, 255))
        return img

    img = text_to_image(trade_summary)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_data = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_data}" download="trade_card.png">Download Trade Card</a>'
    st.markdown(href, unsafe_allow_html=True)
