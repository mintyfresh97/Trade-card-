import streamlit as st
import requests
import os
import random
import sqlite3
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------
# Page Configuration and Directory Setup
# ---------------------------------------------------
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")
JOURNAL_CHART_DIR = "journal_charts"
CHARTS_DIR = "charts"
os.makedirs(JOURNAL_CHART_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# ---------------------------------------------------
# SQLite Persistence Setup
# ---------------------------------------------------
conn = sqlite3.connect("levels_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS asset_levels (
    asset TEXT PRIMARY KEY,
    support TEXT,
    demand TEXT,
    resistance TEXT,
    supply TEXT,
    choch TEXT,
    chart_path TEXT
)
""")
conn.commit()

coinpaprika_ids = {
    'Bitcoin (BTC)': 'btc-bitcoin',
    'Ethereum (ETH)': 'eth-ethereum',
    # ... etc ...
}

# (Your get_levels_from_db, save_levels_to_db, get_coin_data_from_paprika, get_social_sentiment, etc. remain unchanged.)

# ---------------------------------------------------
# 1) Trade Journal Mode
# ---------------------------------------------------
def trade_journal_mode():
    # ... unchanged ...
    pass

# ---------------------------------------------------
# 2) Asset Data Mode
# ---------------------------------------------------
def asset_data_mode():
    # ... unchanged ...
    pass

# ---------------------------------------------------
# 3) Strategy Mode (with reliable CSV save)
# ---------------------------------------------------
def strategy_mode():
    LOG_PATH = "trade_log.csv"

    st.title("Strategy")
    st.markdown("---")

    # Long Strategy Summary
    with st.expander("📋 Long Strategy Summary", expanded=True):
        st.markdown("""
**Timeframe Analysis**: 4H → 1H → 15M  
**Tools Used**: EMA Long Strategy, zones, structure, CHoCH, momentum  

**Entry Criteria**:  
- Price returns to a key zone  
- Wait for breakout with momentum, CHoCH & EMA signal  

**Risk Management**:  
- Stop Loss: 1% or below range lows  
- TP1: 3% (close 25%)  
- TP2: 5% (full exit)  
- Exit early on 5m CHoCH break or momentum shift  
""")

    # Market Behavior Checklist
    with st.expander("📊 Market Behavior Checklist", expanded=False):
        mb1 = st.radio("Is price forming at a price level and ranging?", ["Yes","No"], key="mb1")
        mb2 = st.radio("If ranging, have highs and lows been defined?", ["Yes","No"], key="mb2")
        mb3 = st.radio("Are BTC and ETH both trading in the same direction?", ["Yes","No"], key="mb3")
        mb4 = st.radio("Is there clear momentum in this zone to support the trade?", ["Yes","No"], key="mb4")
        if st.button("Save Market Behavior Check", key="save_mb"):
            st.success("Market behavior saved!")

    st.markdown("---")

    # Load or initialize log DataFrame
    if os.path.exists(LOG_PATH):
        df_log = pd.read_csv(LOG_PATH)
    else:
        df_log = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # Input Form
    with st.form("strategy_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            asset_sym = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat_name = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with right:
            rr = st.text_input("RR Ratio", "1:1")
            notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("Save Trade to Log")
        if submitted:
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Asset": asset_sym.upper(),
                "Strategy": strat_name,
                "RR Ratio": rr,
                "Outcome": outcome,
                "Notes": notes
            }
            df_log = pd.concat([df_log, pd.DataFrame([new_row])], ignore_index=True)
            df_log.to_csv(LOG_PATH, index=False)
            st.success("Trade saved to log!")

    # Display the log
    st.markdown("### Trade History")
    if not df_log.empty:
        st.dataframe(df_log)
    else:
        st.info("No trade log found yet.")

# ---------------------------------------------------
# 4) Mindset Dashboard Mode
# ---------------------------------------------------
def mindset_mode():
    # ... unchanged ...
    pass

# ---------------------------------------------------
# 5) Flip Tracker Mode
# ---------------------------------------------------
def flip_tracker_mode():
    # ... unchanged ...
    pass

# ---------------------------------------------------
# Navigation
# ---------------------------------------------------
mode = st.sidebar.radio("Select App Mode", [
    "Trade Journal & Checklist",
    "Asset Data",
    "Strategy",
    "Mindset Dashboard",
    "Flip Tracker"
])

if mode == "Trade Journal & Checklist":
    trade_journal_mode()
elif mode == "Asset Data":
    asset_data_mode()
elif mode == "Strategy":
    strategy_mode()
elif mode == "Mindset Dashboard":
    mindset_mode()
elif mode == "Flip Tracker":
    flip_tracker_mode()

st.markdown("To get started, select or build a page such as: ✅ Trade Journal, 📈 Strategy Tracker, or 🧠 Mindset Logger.")


