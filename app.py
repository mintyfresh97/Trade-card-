import streamlit as st
from datetime import datetime
from PIL import Image
import os
import base64

# --- App Config ---
st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# --- Asset Settings ---
asset_options = {
    "BTC": 5, "ETH": 4, "XRP": 3, "ADA": 3, "SOL": 5,
    "LINK": 3, "ONDO": 3, "CRV": 3, "CVX": 3, "SUI": 3, "FARTCOIN": 3
}

asset = st.selectbox("Select Asset", list(asset_options.keys()), index=0)

# --- Load Logo ---
logo_path = f"assets/{asset}.png"
if os.path.exists(logo_path):
    st.image(Image.open(logo_path), width=50)

# --- User Inputs ---
position = st.number_input("Position Size (£)", min_value=0.0, value=500.0)
leverage = st.number_input("Leverage", min_value=1, value=20)
entry = st.number_input("Entry Price", min_value=0.0)
stop_loss = st.number_input("Stop Loss", min_value=0.0)
take_profit = st.number_input("Take Profit", min_value=0.0)
decimals = asset_options[asset]

# --- Live Price Autofill ---
if st.button("Autofill Live Price as Entry"):
    try:
        import requests
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={asset.lower()}&vs_currencies=usd")
        live_price = response.json()[asset.lower()]["usd"]
        st.success(f"Live price fetched: ${live_price}")
        entry = round(live_price, decimals)
    except Exception as e:
        st.error(f"Could not fetch live price: {e}")

# --- Calculations ---
if entry and stop_loss and take_profit:
    total_exposure = position * leverage
    risk = abs(entry - stop_loss) * total_exposure / entry
    reward = abs(take_profit - entry) * total_exposure / entry
    breakeven = round((entry + stop_loss) / 2, decimals)
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    # --- Display Summary ---
    st.markdown("### Trade Summary")
    st.write(f"**Asset:** {asset}")
    st.write(f"**Entry:** ${entry}")
    st.write(f"**Stop Loss:** ${stop_loss}")
    st.write(f"**Take Profit:** ${take_profit}")
    st.write(f"**Risk:** £{risk:.2f}")
    st.write(f"**Reward:** £{reward:.2f}")
    st.write(f"**RR Ratio:** {rr_ratio}:1")
    st.write(f"**Breakeven Price:** {breakeven}")

    # --- Trade Card Download ---
    st.markdown("---")
    trade_summary = f"""
    <h3>{asset} Trade Card</h3>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
    <p><strong>Position:</strong> £{position}</p>
    <p><strong>Leverage:</strong> {leverage}x</p>
    <p><strong>Entry:</strong> ${entry}</p>
    <p><strong>Stop Loss:</strong> ${stop_loss}</p>
    <p><strong>Take Profit:</strong> ${take_profit}</p>
    <p><strong>Total Exposure:</strong> £{total_exposure}</p>
    <p><strong>Risk:</strong> £{risk:.2f}</p>
    <p><strong>Reward:</strong> £{reward:.2f}</p>
    <p><strong>Breakeven:</strong> {breakeven}</p>
    <p><strong>RR Ratio:</strong> {rr_ratio}:1</p>
    """
    b64 = base64.b64encode(trade_summary.encode("utf-8")).decode("utf-8")
    href = f'<a href="data:text/html;base64,{b64}" download="{asset}_trade_card.html">📥 Download Trade Card</a>'
    st.markdown(href, unsafe_allow_html=True)
