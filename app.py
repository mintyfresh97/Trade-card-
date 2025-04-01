import streamlit as st from PIL import Image import os

--- CONFIG ---

st.set_page_config("PnL & Risk Dashboard", layout="centered")

--- DATA ---

ASSETS = { "BTC": {"symbol": "€", "decimals": 5, "icon": "assets/btc.png"}, "ETH": {"symbol": "€", "decimals": 4, "icon": "assets/eth.png"}, "XRP": {"symbol": "€", "decimals": 3, "icon": "assets/xrp.png"}, }

def format_value(val, decimals): return f"{val:.{decimals}f}"

--- UI ---

st.title("Live Profit/Loss Calculator")

--- ASSET SELECTOR ---

asset = st.selectbox("Select Asset", list(ASSETS.keys())) icon_path = ASSETS[asset]["icon"] decimals = ASSETS[asset]["decimals"] currency = ASSETS[asset]["symbol"]

cols = st.columns([0.15, 0.85]) with cols[0]: st.image(icon_path, width=40) with cols[1]: st.subheader(f"{asset} Current Price: [manual entry]")

--- INPUTS ---

pos = st.number_input("Position Size (£)", min_value=0.0, value=500.00) lev = st.number_input("Leverage", min_value=1, value=20) entry = st.number_input("Entry Price", value=0.15) stop = st.number_input("Stop Loss", value=0.05) target = st.number_input("Take Profit", value=0.25)

--- CALCULATIONS ---

exposure = pos * lev risk = abs(entry - stop) * exposure / entry reward = abs(target - entry) * exposure / entry breakeven = (entry + stop) / 2 rr_ratio = reward / risk if risk != 0 else 0

--- DISPLAY ---

col1, col2 = st.columns(2)

with col1: st.markdown("### Breakeven / Current Price") st.write(format_value(breakeven, decimals)) st.markdown("### Stop Loss") st.write(f"{currency} {format_value(stop, decimals)}") st.markdown("### Reward / Risk") st.write(f"{rr_ratio:.2f}")

with col2: st.markdown("### Profit / Loss") st.write(f"£ {format_value(reward, 2)}") st.markdown("### Stop Loss") st.write(f"£ {format_value(risk, 2)}") st.markdown("### Reward / Risk") st.write(f"{rr_ratio:.2f}")

