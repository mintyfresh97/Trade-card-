
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

# CoinGecko asset ID mapping
coingecko_ids = {
    "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "ADA": "cardano",
    "SOL": "solana", "LINK": "chainlink", "ONDO": "ondo-finance", "CRV": "curve-dao-token",
    "CVX": "convex-finance", "SUI": "sui", "FARTCOIN": "bitcoin"
}

assets = list(coingecko_ids.keys())

st.set_page_config("PnL & Risk Dashboard", layout="centered")
st.title("PnL & Risk Dashboard")

# Asset selection
asset = st.selectbox("Select Asset", assets, index=2)
logo_path = f"assets/{asset.lower()}.png"
try:
    st.image(logo_path, width=60)
except:
    st.warning("Logo not found.")

# Inputs
position = st.number_input("Position Size (Â£)", value=500.0)
leverage = st.number_input("Leverage", value=20)
entry = st.number_input("Entry Price", value=0.0)
stop_loss = st.number_input("Stop Loss", value=0.0)
take_profit = st.number_input("Take Profit", value=0.0)

# Autofill button
if st.button("Autofill Live Price as Entry"):
    coin_id = coingecko_ids.get(asset)
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        live_price = response.json()[coin_id]["usd"]
        st.success(f"Live price for {asset}: ${live_price}")
        entry = live_price
    except Exception as e:
        st.error(f"Could not fetch live price: '{asset.lower()}'")

# Calculations
if entry > 0 and stop_loss > 0 and take_profit > 0:
    total_exposure = position * leverage
    risk = abs(entry - stop_loss) * total_exposure / entry
    reward = abs(take_profit - entry) * total_exposure / entry
    breakeven = round((entry + stop_loss) / 2, 5)
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Breakeven", breakeven)
        st.metric("Risk (Â£)", f"Â£{risk:.2f}")
        st.metric("Reward / Risk", f"{rr_ratio} : 1")
    with col2:
        st.metric("Profit (Â£)", f"Â£{reward:.2f}")
        st.metric("Loss (Â£)", f"Â£{risk:.2f}")

    # Trade card
    st.markdown("---")
    st.subheader("Downloadable Trade Card")
    card_text = (
        f"Trade Summary â€“ {datetime.now().strftime('%Y-%m-%d')}
"
        f"Asset: {asset}
"
        f"Entry: {entry}
"
        f"Stop Loss: {stop_loss}
"
        f"Take Profit: {take_profit}
"
        f"Risk: Â£{risk:.2f}  |  Reward: Â£{reward:.2f}
"
        f"Reward/Risk: {rr_ratio} : 1
"
        f"Breakeven: {breakeven}
"
    )
    st.code(card_text)

    # Download button
    st.download_button(
        label="Download Trade Card",
        data=card_text,
        file_name=f"trade_card_{asset}.txt",
        mime="text/plain"
    )
