import streamlit as st
import requests
import os
import io
import textwrap
import random
import sqlite3
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------
# Page Configuration and Directory Setup
# ---------------------------------------------------
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

JOURNAL_CHART_DIR = "journal_charts"
if not os.path.exists(JOURNAL_CHART_DIR):
    os.makedirs(JOURNAL_CHART_DIR)
CHARTS_DIR = "charts"
if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)

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
    'Cardano (ADA)': 'ada-cardano',
    'Solana (SOL)': 'sol-solana',
    'XRP (XRP)': 'xrp-xrp',
    'Chainlink (LINK)': 'link-chainlink',
    'Ondo (ONDO)': 'ondo-ondo',
    'Sui (SUI)': 'sui-sui',
    'Curve DAO Token (CRV)': 'crv-curve-dao-token',
    'Convex Finance (CVX)': 'cvx-convex-finance',
    'Based Fartcoin (FARTCOIN)': 'fartcoin-based-fartcoin'
}
for asset in coinpaprika_ids:
    cursor.execute("INSERT OR IGNORE INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path) VALUES (?, '', '', '', '', '', '')", (asset,))
conn.commit()

def get_levels_from_db(asset_name):
    cursor.execute("SELECT support, demand, resistance, supply, choch, chart_path FROM asset_levels WHERE asset = ?", (asset_name,))
    row = cursor.fetchone()
    if row:
        return {"support": row[0] or "", "demand": row[1] or "", "resistance": row[2] or "", "supply": row[3] or "", "choch": row[4] or "", "chart_path": row[5] or ""}
    return {k: "" for k in ["support","demand","resistance","supply","choch","chart_path"]}

def save_levels_to_db(asset_name, levels):
    cursor.execute("""
        INSERT INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset) DO UPDATE SET
            support=excluded.support,
            demand=excluded.demand,
            resistance=excluded.resistance,
            supply=excluded.supply,
            choch=excluded.choch,
            chart_path=excluded.chart_path
    """, (asset_name, levels.get("support",""), levels.get("demand",""), levels.get("resistance",""), levels.get("supply",""), levels.get("choch",""), levels.get("chart_path","")))
    conn.commit()

def get_levels_for_asset(asset_name):
    levels = get_levels_from_db(asset_name)
    st.session_state.setdefault("levels_data", {})[asset_name] = levels
    return levels

def save_levels_for_asset(asset_name, levels):
    st.session_state.setdefault("levels_data", {})[asset_name] = levels
    save_levels_to_db(asset_name, levels)

# Shared assets
icon_map = {"BTC":"bitcoin-btc-logo.png","ETH":"ethereum-eth-logo.png","XRP":"xrp-xrp-logo.png","ADA":"cardano-ada-logo.png","SOL":"solana-sol-logo.png","LINK":"chainlink-link-logo.png","ONDO":"ondo-finance-ondo-logo.png","CRV":"curve-dao-token-crv-logo.png","CVX":"convex-finance-cvx-logo.png","SUI":"sui-sui-logo.png","FARTCOIN":"fartcoin-logo.png"}

def get_coin_data_from_paprika(name, vs_currency="USD"):
    try:
        cid = coinpaprika_ids.get(name)
        r = requests.get(f"https://api.coinpaprika.com/v1/tickers/{cid}", timeout=5).json()
        q = r.get("quotes", {}).get(vs_currency, {})
        return round(q.get("price",0),2), round(q.get("percent_change_24h",0),2), round(q.get("percent_change_7d",0),2), round(q.get("percent_change_30d",0),2)
    except Exception as e:
        st.error(f"API Error: {e}")
        return None, None, None, None

def get_social_sentiment(coin):
    s = random.randint(-100,100)
    return ("Positive" if s>20 else "Negative" if s<-20 else "Neutral", s)

# 1) Trade Journal Mode (unchanged)
def trade_journal_mode():
    # ... your existing code
    pass

# 2) Asset Data Mode (unchanged)
def asset_data_mode():
    # ... your existing code
    pass

# 3) Strategy Mode

def strategy_mode():
    LOG_PATH = "trade_log.csv"

    st.title("📈 Strategy Tracker")
    st.markdown("---")

    # --- Example Trades (Persistent) ---
    EXAMPLES_DIR = "strategy_examples"
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    st.subheader("📁 Example Trades")
    uploaded_examples = st.file_uploader(
        "Upload Example Trade Image(s)", type=["png","jpg","jpeg"], accept_multiple_files=True, key="example_upload"
    )
    if uploaded_examples:
        for ex in uploaded_examples:
            save_path = os.path.join(EXAMPLES_DIR, ex.name)
            with open(save_path, "wb") as f:
                f.write(ex.getbuffer())
        st.success("Example(s) saved!")
    # Display saved examples
    example_files = []
    try:
        example_files = os.listdir(EXAMPLES_DIR)
    except Exception:
        pass
    if example_files:
        cols = st.columns(min(3, len(example_files)))
        for idx, fname in enumerate(example_files):
            with cols[idx % len(cols)]:
                st.image(os.path.join(EXAMPLES_DIR, fname), caption=fname, use_column_width=True)
    else:
        st.info("No example trades uploaded yet.")

    st.markdown("---")

    # — Long Strategy Summary + Risk Management
    with st.expander("📋 Long Strategy Summary", expanded=True):
        st.markdown("""
        **Timeframe Analysis**: 4H → 1H → 15M  
        **Tools Used**:  
        - EMA Long Strategy  
        - Manually drawn zones  
        - Previous market structure  
        - CHoCH (Change of Character)  
        - Momentum

        **Entry Criteria**:
        - Price returns to a key structure level (forms new zone)
        - Wait for confirmation:
          - ✅ Breakout of the zone  
          - ✅ Momentum shift  
          - ✅ CHoCH confirmation  
          - ✅ EMA signal printed

        **Risk Management**:
        - **Stop Loss**:  
          - 1% fixed  
          - or below the lows of the trading range

        - **Take Profit**:  
          - **TP1**: 3% → close 25% of the position  
          - **TP2**: 5% → full exit  
          
        - **Exit Early If**:  
          - 5M CHoCH break against position  
          - Momentum shifts or reversal signs
        """)

    # — Market Behavior Checklist
    with st.expander("📊 Market Behavior Checklist", expanded=False):
        mb1 = st.radio("Is price forming at a price level and ranging?", ["Yes","No"], key="mb1")
        mb2 = st.radio("If ranging, have highs and lows been defined?", ["Yes","No"], key="mb2")
        mb3 = st.radio("Are BTC and ETH both trading in the same direction?", ["Yes","No"], key="mb3")
        mb4 = st.radio("Is there clear momentum in this zone to support the trade?", ["Yes","No"], key="mb4")
        if st.button("Save Market Behavior Check", key="save_mb"):
            st.success("Saved!")

    st.markdown("---")

    # — Prepare / Load the log
    if os.path.exists(LOG_PATH):
        df_log = pd.read_csv(LOG_PATH)
    else:
        df_log = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # — Input Form
    with st.form("strategy_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            asset_sym = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat_name = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with c2:
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

    # — Display the log
    st.markdown("### Trade History")
    if not df_log.empty:
        st.dataframe(df_log)
    else:
        st.info("No trade log found yet.")

# 4) Mindset Mode (unchanged)
def mindset_mode():
    pass

# 5) Flip Tracker Mode (unchanged)
def flip_tracker_mode():
    pass

# Navigation
mode = st.sidebar.radio("Select App Mode", [
    "Trade Journal & Checklist","Asset Data","Strategy","Mindset Dashboard","Flip Tracker"
])
if mode=="Trade Journal & Checklist": trade_journal_mode()
elif mode=="Asset Data": asset_data_mode()
elif mode=="Strategy": strategy_mode()
elif mode=="Mindset Dashboard": mindset_mode()
elif mode=="Flip Tracker": flip_tracker_mode()

st.markdown("To get started, select or build a page such as: ✅ Trade Journal, 📈 Strategy Tracker, or 🧠 Mindset Logger.")


