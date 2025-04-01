import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

# Supported crypto assets and icons
assets = {
    "BTC": "assets/BTC.png",
    "ETH": "assets/ETH.png",
    "XRP": "assets/XRP.png",
    "SOL": "assets/SOL.png",
    "ADA": "assets/ADA.png",
    "LINK": "assets/LINK.png",
    "CRV": "assets/CRV.png",
    "CVX": "assets/CVX.png",
    "SUI": "assets/SUI.png",
    "ONDO": "assets/ONDO.png",
    "FARTCOIN": "assets/FARTCOIN.png",
}

st.title("PnL & Risk Dashboard")

# --- Sidebar ---
st.sidebar.header("Trade Input")

asset = st.sidebar.selectbox("Select Crypto Asset", list(assets.keys()))
position = st.sidebar.number_input("Position Size (£)", value=500.0)
leverage = st.sidebar.number_input("Leverage", value=20)
entry = st.sidebar.number_input("Entry Price", value=0.0)
stop_loss = st.sidebar.number_input("Stop Loss", value=0.0)
take_profit = st.sidebar.number_input("Take Profit", value=0.0)

# --- Trade Card Display ---
st.subheader("Trade Card")

col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists(assets[asset]):
        st.image(assets[asset], width=50)
with col2:
    st.markdown(f"### {asset}")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")

st.markdown(f"**Position:** £{position} | **Leverage:** {leverage}x")

# Validate inputs
if entry and stop_loss and take_profit and position and leverage:
    try:
        entry = float(entry)
        stop_loss = float(stop_loss)
        take_profit = float(take_profit)
        position = float(position)
        leverage = float(leverage)

        # Calculations
        total_exposure = position * leverage
        risk = abs(entry - stop_loss) * total_exposure / entry
        reward = abs(take_profit - entry) * total_exposure / entry
        breakeven = round((entry + stop_loss) / 2, 5)
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0

        st.success("Calculation complete!")

        st.markdown("---")
        st.markdown(f"**Live Entry:** ${entry}")
        st.markdown(f"**Stop Loss:** ${stop_loss}")
        st.markdown(f"**Take Profit:** ${take_profit}")
        st.markdown(f"**Total Exposure:** £{total_exposure}")
        st.markdown(f"**Risk:** £{risk:.2f}")
        st.markdown(f"**Reward:** £{reward:.2f}")
        st.markdown(f"**Breakeven:** {breakeven}")
        st.markdown(f"**Reward:Risk Ratio:** {rr_ratio}:1")

    except Exception as e:
        st.error(f"Error during calculation: {e}")
else:
    st.warning("Please fill in all inputs before calculating.")
