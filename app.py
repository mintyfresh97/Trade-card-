import streamlit as st
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

import requests
import os
import random
import sqlite3
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =============================================================================
# QUERY-PARAMETER BASED SUB-PAGES
# =============================================================================
params = st.experimental_get_query_params()
if "page" in params:
    page = params["page"][0]
    if page == "orderbook":
        st.title("Order Book Dashboard")
        st.write("Fetching KuCoin Level‑2 order book data...")
        def fetch_orderbook(symbol: str):
            api_url = f"https://api.kucoin.com/api/v1/market/orderbook/level2?symbol={symbol}-USDT"
            try:
                response = requests.get(api_url, timeout=5)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                return {"error": str(e), "symbol": symbol}
        ASSETS = ["BTC", "ETH", "ADA", "SOL", "LINK", "XRP", "ONDO", "SUI", "CVX", "CRV", "FARTCOIN"]
        orderbooks = {asset: fetch_orderbook(asset) for asset in ASSETS}
        st.json(orderbooks)
        st.stop()
    elif page == "buy":
        st.title("Where and How to Buy")
        st.write("Coming soon!")
        st.stop()
    elif page == "sell":
        st.title("Where to Sell")
        st.write("Coming soon!")
        st.stop()
    elif page == "market_sell":
        st.title("Selling the Market (How/Where to Sell)")
        st.write("Coming soon!")
        st.stop()

# =============================================================================
# DATABASE PERSISTENCE SETUP
# =============================================================================
conn = sqlite3.connect("levels_data.db", check_same_thread=False)
cursor = conn.cursor()
# Asset levels table
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
# Trade log table
cursor.execute("""
CREATE TABLE IF NOT EXISTS trade_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    asset TEXT,
    strategy TEXT,
    rr_ratio TEXT,
    outcome TEXT,
    notes TEXT
)
""")
conn.commit()
# Pre-populate assets
coinpaprika_ids = {
    'Bitcoin (BTC)': 'btc-bitcoin', 'Ethereum (ETH)': 'eth-ethereum',
    'Cardano (ADA)': 'ada-cardano', 'Solana (SOL)': 'sol-solana',
    'XRP (XRP)': 'xrp-xrp', 'Chainlink (LINK)': 'link-chainlink',
    'Ondo (ONDO)': 'ondo-ondo', 'Sui (SUI)': 'sui-sui',
    'Curve DAO Token (CRV)': 'crv-curve-dao-token', 'Convex Finance (CVX)': 'cvx-convex-finance',
    'Based Fartcoin (FARTCOIN)': 'fartcoin-based-fartcoin'
}
for asset in coinpaprika_ids:
    cursor.execute(
        "INSERT OR IGNORE INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path) VALUES (?, '', '', '', '', '', '')",
        (asset,)
    )
conn.commit()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_levels_from_db(asset_name):
    cursor.execute(
        "SELECT support, demand, resistance, supply, choch, chart_path FROM asset_levels WHERE asset = ?",
        (asset_name,)
    )
    row = cursor.fetchone()
    if row:
        return dict(zip(["support","demand","resistance","supply","choch","chart_path"], [val or "" for val in row]))
    return {k: "" for k in ["support","demand","resistance","supply","choch","chart_path"]}

def save_levels_to_db(asset_name, levels):
    cursor.execute(
        "INSERT INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path) VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(asset) DO UPDATE SET support=excluded.support, demand=excluded.demand, resistance=excluded.resistance, "
        "supply=excluded.supply, choch=excluded.choch, chart_path=excluded.chart_path",
        (
            asset_name,
            levels.get('support',''), levels.get('demand',''),
            levels.get('resistance',''), levels.get('supply',''),
            levels.get('choch',''), levels.get('chart_path','')
        )
    )
    conn.commit()

def get_levels_for_asset(asset_name):
    levels = get_levels_from_db(asset_name)
    st.session_state.setdefault('levels_data', {})[asset_name] = levels
    return levels

def save_levels_for_asset(asset_name, levels):
    st.session_state.setdefault('levels_data', {})[asset_name] = levels
    save_levels_to_db(asset_name, levels)

icon_map = {"BTC":"bitcoin-btc-logo.png","ETH":"ethereum-eth-logo.png", "ADA":"cardano-ada-logo.png",
            "SOL":"solana-sol-logo.png","LINK":"chainlink-link-logo.png","XRP":"xrp-xrp-logo.png",
            "ONDO":"ondo-finance-ondo-logo.png","SUI":"sui-sui-logo.png","CRV":"curve-dao-token-crv-logo.png",
            "CVX":"convex-finance-cvx-logo.png","FARTCOIN":"fartcoin-logo.png"}

# =============================================================================
# MODE DEFINITIONS
# =============================================================================
def trade_journal_mode():
    st.title("🧾 Trade Journal & Checklist")
    # Full trade_journal_mode implementation from original script
    # ... [paste original code here] ...

def asset_data_mode():
    st.markdown("""
    <div class=\"asset-data-banner\">... your banner HTML ...</div>
    """, unsafe_allow_html=True)
    st_autorefresh(interval=30000, limit=100, key="autorefresh")
    # Full asset_data_mode implementation
    # ... [paste original code here] ...

def mindset_mode():
    st.title("🧠 Mindset Dashboard")
    # Full mindset_mode implementation from original script
    # ... [paste original code here] ...

def strategy_mode():
    st.title("Strategy")
    # Strategy tracker and logging using SQLite
    strat_col1, strat_col2 = st.columns(2)
    with strat_col1:
        asset_for_strategy = st.text_input("Asset Symbol", placeholder="e.g. BTC")
        strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
        trade_result = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
    with strat_col2:
        rr_logged = st.text_input("RR Ratio", value="1:1")
        notes = st.text_area("Additional Notes")
    if st.button("Save Trade to Log"):
        cursor.execute(
            "INSERT INTO trade_log (date, asset, strategy, rr_ratio, outcome, notes) VALUES (?,?,?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d"), asset_for_strategy.upper(), strategy_used, rr_logged, trade_result, notes)
        )
        conn.commit()
        st.success("Trade saved to database!")
    df_hist = pd.read_sql("SELECT date AS 'Date', asset AS 'Asset', strategy AS 'Strategy', rr_ratio AS 'RR Ratio', outcome AS 'Outcome', notes AS 'Notes' FROM trade_log ORDER BY date", conn)
    if not df_hist.empty:
        st.markdown("### Trade History")
        st.dataframe(df_hist)
    else:
        st.info("No trade log found yet.")

# =============================================================================
# NAVIGATION
# =============================================================================
mode = st.sidebar.radio("Select App Mode", ["Asset Data","Strategy","Mindset Dashboard","Trade Journal & Checklist"])
if mode == "Asset Data":
    asset_data_mode()
elif mode == "Strategy":
    strategy_mode()
elif mode == "Mindset Dashboard":
    mindset_mode()
elif mode == "Trade Journal & Checklist":
    trade_journal_mode()
