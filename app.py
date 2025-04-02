import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd

# CoinGecko ID mapping for Cryptocurrencies
coingecko_ids = {
    'Bitcoin (BTC)': 'bitcoin',
    'Ethereum (ETH)': 'ethereum',
    'XRP (XRP)': 'ripple',
    'Solana (SOL)': 'solana',
    'Cardano (ADA)': 'cardano',
    'Chainlink (LINK)': 'chainlink',
    'Curve (CRV)': 'curve-dao-token',
    'Convex (CVX)': 'convex-finance',
    'Sui (SUI)': 'sui',
    'Fartcoin (FARTCOIN)': 'fartcoin',
    'Ondo (ONDO)': 'ondo-finance'
}

icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png", 
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png", 
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png", 
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png", 
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png", 
    "FARTCOIN": "fartcoin-logo.png"
}

def get_crypto_price_from_coingecko(name):
    try:
        coin_id = coingecko_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinGecko ID")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return round(data[coin_id]['usd'], 2)
    except Exception as e:
        st.error(f"CoinGecko API Error for {name}: {e}")
        return None

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    display_names = list(coingecko_ids.keys())
    asset_display = st.selectbox("Select Asset", display_names)
    asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()

    icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")

position = st.number_input("Position Size (Â£)", value=500.0)
leverage = st.number_input("Leverage", value=20)

try:
    live_price = get_crypto_price_from_coingecko(asset_display)
    if live_price:
        entry = st.number_input("Entry Price", value=live_price, format="%.2f")
    else:
        entry = st.number_input("Entry Price", value=82000.0, format="%.2f")
except:
    entry = st.number_input("Entry Price", value=82000.0, format="%.2f")
    live_price = "Not available"

stop_loss = st.number_input("Stop Loss", value=round(entry * 0.99, 2), format="%.2f")
take_profit = st.number_input("Take Profit", value=round(entry * 1.02, 2), format="%.2f")
profit_target = st.number_input("Profit Target %", min_value=0.0, max_value=500.0, value=2.0)
strategy = st.text_input("Strategy Used")
trade_date = datetime.now().strftime("%Y-%m-%d")

total_exposure = position * leverage
risk = abs(entry - stop_loss) * total_exposure / entry
reward = abs(take_profit - entry) * total_exposure / entry
breakeven = round((entry + stop_loss) / 2, 2)
rr_ratio = round(reward / risk, 2) if risk != 0 else 0

with col2:
    st.subheader("Trade Card")
    st.markdown(f"Asset: {asset_symbol}")
    st.markdown(f"Live Price: {live_price if live_price else 'N/A'}")
    st.markdown(f"Position: Â£{position}")
    st.markdown(f"Leverage: {leverage}x")
    st.markdown(f"Entry: {entry}")
    st.markdown(f"Stop Loss: {stop_loss}")
    st.markdown(f"Take Profit: {take_profit}")
    st.markdown(f"Profit Target: {profit_target}%")
    st.markdown(f"Strategy: {strategy}")
    st.markdown(f"Risk: Â£{risk:.2f}")
    st.markdown(f"Reward: Â£{reward:.2f}")
    st.markdown(f"RR Ratio: {rr_ratio}:1")
    st.markdown(f"Breakeven: {breakeven}")
    st.markdown(f"Date: {trade_date}")

if st.button("Export Trade Journal"):
    journal = {
        "Date": trade_date,
        "Asset": asset_symbol,
        "Live Price": live_price,
        "Entry": entry,
        "Stop Loss": stop_loss,
        "Take Profit": take_profit,
        "Profit Target %": profit_target,
        "Strategy": strategy,
        "Position": position,
        "Leverage": leverage,
        "Risk": round(risk, 2),
        "Reward": round(reward, 2),
        "RR Ratio": rr_ratio,
        "Breakeven": breakeven
    }
    df = pd.DataFrame([journal])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="trade_journal.csv", mime="text/csv")
