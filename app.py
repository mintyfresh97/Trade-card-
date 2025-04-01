
import streamlit as st
from PIL import Image
import requests
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

# Asset options
assets = {
    "BTC": "btc.png", "ETH": "eth.png", "XRP": "xrp.png", "ADA": "ada.png",
    "SOL": "sol.png", "LINK": "link.png", "ONDO": "ondo.png",
    "CRV": "crv.png", "CVX": "cvx.png", "SUI": "sui.png"
}
precision_map = {
    "BTC": 5, "ETH": 4, "XRP": 3, "ADA": 3, "SOL": 5,
    "LINK": 3, "ONDO": 3, "CRV": 3, "CVX": 3, "SUI": 3
}

# Sidebar
st.title("PnL & Risk Dashboard")
asset = st.selectbox("Choose Asset", list(assets.keys()))
icon_path = f"assets/{assets[asset]}"
try:
    st.image(icon_path, width=64)
except:
    st.warning("Icon not found.")

# Live price fetch
def get_live_price(asset_id):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id.lower()}&vs_currencies=usd", timeout=5)
        return r.json()[asset_id.lower()]["usd"]
    except:
        return None

# Inputs
position = st.number_input("Position Size (Â£)", 100, 1_000_000, step=50)
leverage = st.number_input("Leverage", 1, 100, value=20)
entry = st.number_input("Entry Price", value=0.0, format="%.5f")
stop = st.number_input("Stop Loss", value=0.0, format="%.5f")
target = st.number_input("Take Profit", value=0.0, format="%.5f")

# Autofill button
if st.button("Autofill Live Price as Entry"):
    price = get_live_price(asset.lower())
    if price:
        st.experimental_rerun()  # this resets state
    else:
        st.error(f"Could not fetch live price: '{asset.lower()}'")

# Trade calculation
if entry > 0 and stop > 0 and target > 0:
    exposure = position * leverage
    risk = abs(entry - stop) * exposure / entry
    reward = abs(target - entry) * exposure / entry
    breakeven = round((entry + stop) / 2, precision_map[asset])
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0
    live_price = get_live_price(asset.lower())

    # Card
    st.subheader("Trade Summary")
    st.markdown(f"**Asset:** {asset}")
    if live_price:
        st.markdown(f"**Live Price:** ${live_price}")
    st.markdown(f"**Entry:** {entry}")
    st.markdown(f"**Stop Loss:** {stop}")
    st.markdown(f"**Take Profit:** {target}")
    st.markdown(f"**Risk:** Â£{risk:.2f}")
    st.markdown(f"**Reward:** Â£{reward:.2f}")
    st.markdown(f"**RR Ratio:** {rr_ratio}:1")
    st.markdown(f"**Breakeven:** {breakeven}")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Downloadable card
    if st.button("Download Trade Card"):
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Trade Summary â€“ {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(200, 10, txt=f"Asset: {asset}", ln=True)
        pdf.cell(200, 10, txt=f"Entry: {entry}", ln=True)
        pdf.cell(200, 10, txt=f"Stop: {stop}", ln=True)
        pdf.cell(200, 10, txt=f"Target: {target}", ln=True)
        pdf.cell(200, 10, txt=f"Risk: Â£{risk:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Reward: Â£{reward:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"RR Ratio: {rr_ratio}:1", ln=True)
        pdf.cell(200, 10, txt=f"Breakeven: {breakeven}", ln=True)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        st.download_button("Download PDF", buffer, file_name="trade_card.pdf", mime="application/pdf")
