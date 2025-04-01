
import streamlit as st

# Set up the page
st.set_page_config(page_title="PnL & Risk Dashboard", layout="centered")

# App title
st.title("Live Profit/Loss Calculator")

# Example crypto asset selection (expand later)
asset = st.selectbox("Select Asset", ["BTC", "ETH", "XRP", "SOL", "ADA", "LINK", "SUI", "ONDO"])

# Inputs
st.subheader(f"{asset} Trade Inputs")
position_size = st.number_input("Position Size (Â£)", min_value=0.0, value=500.0)
leverage = st.number_input("Leverage", min_value=1, value=20)
entry_price = st.number_input("Entry Price", min_value=0.0, value=0.15, format="%.5f")
stop_loss = st.number_input("Stop Loss", min_value=0.0, value=0.05, format="%.5f")
take_profit = st.number_input("Take Profit", min_value=0.0, value=0.25, format="%.5f")

# Calculations
exposure = position_size * leverage
risk = abs(entry_price - stop_loss) * exposure / entry_price
reward = abs(take_profit - entry_price) * exposure / entry_price
breakeven = (entry_price + stop_loss) / 2
rr_ratio = reward / risk if risk != 0 else 0

# Output
st.subheader("Trade Summary")
col1, col2 = st.columns(2)
col1.metric("Breakeven", f"{breakeven:.5f}")
col1.metric("Risk (Â£)", f"{risk:.2f}")
col1.metric("Reward/Risk", f"{rr_ratio:.2f}")

col2.metric("Profit (Â£)", f"{reward:.2f}")
col2.metric("Stop Loss (Â£)", f"{risk:.2f}")
col2.metric("Take Profit", f"{take_profit:.5f}")
