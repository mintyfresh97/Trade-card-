import streamlit as st
import requests
from datetime import datetime
from PIL import Image
import os
from io import BytesIO

# App config
st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")
st.title("PnL & Risk Dashboard")

# Asset details
assets = {
    "BTC": {"id": "bitcoin", "decimals": 5},
    "ETH": {"id": "ethereum", "decimals": 4},
    "XRP": {"id": "ripple", "decimals": 3},
    "ADA": {"id": "cardano", "decimals": 3},
    "SOL": {"id": "solana", "decimals": 5},
    "LINK": {"id": "chainlink", "decimals": 3},
    "ONDO": {"id": "ondo-finance", "decimals": 3},
    "CRV": {"id": "curve-dao-token", "decimals": 3},
    "CVX": {"id": "convex-finance", "decimals": 3},
    "SUI": {"id": "sui", "decimals": 3}
}

# Select asset
asset = st.selectbox("Select Asset", options=list(assets.keys()))
asset_id = assets[asset]["id"]
decimals = assets[asset]["decimals"]

# Display logo if exists
logo_path = f"assets/{asset_id}.png"
if os.path.exists(logo_path):
    st.image(Image.open(logo_path), width=50)

# Inputs
position = st.number_input("Position Size (Â£)", value=500.00, step=100.00)
leverage = st.number_input("Leverage", value=20, step=1)
entry = st.number_input("Entry Price", value=0.0, format=f"%.{decimals}f")
stop_loss = st.number_input("Stop Loss", value=0.0, format=f"%.{decimals}f")
take_profit = st.number_input("Take Profit", value=0.0, format=f"%.{decimals}f")

# Autofill live price
if st.button("Autofill Live Price as Entry"):
    try:
        res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=gbp")
        price = res.json()[asset_id]["gbp"]
        st.session_state["entry"] = price
        entry = price
        st.success(f"Fetched live price: Â£{price:.{decimals}f}")
    except:
        st.error(f"Could not fetch live price for: '{asset}'")

# Perform calculation
if all(val > 0 for val in [entry, stop_loss, take_profit]):
    total_exposure = position * leverage
    risk = abs(entry - stop_loss) * total_exposure / entry
    reward = abs(take_profit - entry) * total_exposure / entry
    breakeven = round((entry + stop_loss) / 2, decimals)
    rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    # Trade card display
    st.markdown("---")
    st.subheader("Trade Summary")
    st.write(f"**Asset**: {asset}")
    st.write(f"**Entry**: Â£{entry:.{decimals}f}")
    st.write(f"**Stop Loss**: Â£{stop_loss:.{decimals}f}")
    st.write(f"**Take Profit**: Â£{take_profit:.{decimals}f}")
    st.write(f"**Breakeven**: Â£{breakeven:.{decimals}f}")
    st.write(f"**Profit (Reward)**: Â£{reward:.2f}")
    st.write(f"**Loss (Risk)**: Â£{risk:.2f}")
    st.write(f"**Reward-to-Risk Ratio**: {rr_ratio}:1")

    # Downloadable trade card
    trade_summary = f"""Trade Summary â€“ {datetime.now().strftime('%Y-%m-%d')}
Asset: {asset}
Position: Â£{position}
Leverage: {leverage}x
Entry: Â£{entry:.{decimals}f}
Stop Loss: Â£{stop_loss:.{decimals}f}
Take Profit: Â£{take_profit:.{decimals}f}
Breakeven: Â£{breakeven:.{decimals}f}
Profit (Reward): Â£{reward:.2f}
Loss (Risk): Â£{risk:.2f}
R:R Ratio: {rr_ratio}:1
"""
    st.download_button(
        label="Download Trade Card",
        data=trade_summary,
        file_name=f"{asset}_trade_summary.txt",
        mime="text/plain"
    )
