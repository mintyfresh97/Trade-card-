import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

# Supported assets and logo filenames (match your assets folder)
ASSETS = {
    "BTC": "bitcoin-btc-logo.png",
    "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png",
    "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png",
    "LINK": "chainlink-link-logo.png",
    "CRV": "curve-dao-token-logo.png",
    "CVX": "convex-finance-cvx-logo.png",
    "SUI": "sui-sui-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png"
}

st.title("PnL & Risk Dashboard")

# Asset selection
col1, col2 = st.columns([2, 1])
with col1:
    asset = st.selectbox("Choose Asset", options=list(ASSETS.keys()))
with col2:
    logo_path = f"assets/{ASSETS[asset]}"
    try:
        st.image(logo_path, width=48)
    except:
        st.warning("Icon not found.")

# Inputs
position = st.number_input("Position Size (£)", value=100.0)
leverage = st.number_input("Leverage", value=20)
entry = st.number_input("Entry Price", value=0.0, format="%.5f")
stop = st.number_input("Stop Loss", value=0.0, format="%.5f")
target = st.number_input("Take Profit", value=0.0, format="%.5f")

# Autofill button
if st.button("Autofill Live Price as Entry"):
    try:
        coingecko_id = asset.lower()
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=gbp")
        price = r.json()[coingecko_id]["gbp"]
        st.session_state["entry"] = price
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Could not fetch live price: '{asset.lower()}'")

# Calculation
if entry and stop and target:
    exposure = position * leverage
    risk = abs(entry - stop) * exposure / entry
    reward = abs(target - entry) * exposure / entry
    rr = round(reward / risk, 2) if risk != 0 else 0
    breakeven = round((entry + stop) / 2, 5)

    st.subheader("Trade Summary")
    st.markdown(f"""
    - **Breakeven / Current Price:** {breakeven}
    - **Profit if TP Hit:** £{reward:.2f}
    - **Loss if SL Hit:** £{risk:.2f}
    - **Reward / Risk Ratio:** {rr}:1
    """)

    # Trade card preview
    st.subheader("Trade Card")
    trade_card = Image.new("RGB", (600, 300), color="#111111")
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(trade_card)
    draw.text((20, 20), f"{asset} Trade Summary – {datetime.now().strftime('%Y-%m-%d')}", fill="white")

    details = [
        f"Position: £{position}",
        f"Leverage: {leverage}x",
        f"Entry: {entry}",
        f"Stop Loss: {stop}",
        f"Take Profit: {target}",
        f"RR: {rr}:1",
        f"Risk: £{risk:.2f}",
        f"Reward: £{reward:.2f}"
    ]

    for i, line in enumerate(details):
        draw.text((20, 60 + i * 28), line, fill="white")

    buf = BytesIO()
    trade_card.save(buf, format="PNG")
    st.image(buf.getvalue())
    st.download_button("Download Trade Card", buf.getvalue(), file_name=f"{asset}_trade_card.png", mime="image/png")
