import streamlit as st
import requests
from datetime import datetime

# Set page config
st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Helper to map asset to logo file
def get_logo_filename(asset):
    logos = {
        "BTC": "bitcoin-btc-logo.png",
        "ETH": "ethereum-eth-logo.png",
        "XRP": "xrp-xrp-logo.png",
        "ADA": "cardano-ada-logo.png",
        "SOL": "solana-sol-logo.png",
        "LINK": "chainlink-link-logo.png",
        "ONDO": "ondo-finance-ondo-logo.png",
        "CRV": "curve-dao-token-crv-logo.png",
        "CVX": "convex-finance-cvx-logo.png",
        "SUI": "sui-sui-logo.png",
    }
    return f"assets/{logos.get(asset, 'bitcoin-btc-logo.png')}"

# Asset selector
assets = ["BTC", "ETH", "XRP", "ADA", "SOL", "LINK", "ONDO", "CRV", "CVX", "SUI"]
asset = st.selectbox("Select Asset", assets)

# Show logo and live price
logo_path = get_logo_filename(asset)
col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo_path, width=40)
with col2:
    # Fetch price
    try:
        price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={asset.lower()}&vs_currencies=eur").json()
        live_price = price[asset.lower()]["eur"]
    except:
        live_price = 0.0
    st.markdown(f"**{asset}** €{live_price}")

# User inputs
position = st.number_input("Position Size (£)", value=500.0)
leverage = st.number_input("Leverage", value=20)
entry = st.number_input("Entry Price", value=round(live_price, 4))
stop_loss = st.number_input("Stop Loss", value=round(entry * 0.9, 4))
take_profit = st.number_input("Take Profit", value=round(entry * 1.1, 4))
date = st.date_input("Trade Date", value=datetime.now().date())

# Calculations
total_exposure = position * leverage
risk = abs(entry - stop_loss) * total_exposure / entry
reward = abs(take_profit - entry) * total_exposure / entry
breakeven = round((entry + stop_loss) / 2, 5)
rr_ratio = round(reward / risk, 2) if risk != 0 else 0
pnl = reward if take_profit > entry else -risk

# Trade Card
st.markdown("### Trade Summary")
trade_card = f"""
**Asset:** {asset}  
**Date:** {date.strftime('%Y-%m-%d')}  
**Entry:** {entry}  
**Stop Loss:** {stop_loss}  
**Take Profit:** {take_profit}  
**Size:** £{position}  
**Leverage:** {leverage}  
**Exposure:** £{total_exposure}  
**Risk:** £{risk:.2f}  
**Reward:** £{reward:.2f}  
**PnL:** £{pnl:.2f}  
**RR Ratio:** {rr_ratio}:1  
**Breakeven:** {breakeven}
"""
st.code(trade_card, language="markdown")

# Downloadable Trade Card
st.download_button("Download Trade Card", trade_card, file_name=f"{asset}_trade_card.txt")
