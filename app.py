import streamlit as st
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

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

# =============================================================================
# DATABASE PERSISTENCE SETUP
# =============================================================================
conn = sqlite3.connect("levels_data.db", check_same_thread=False)
cursor = conn.cursor()

# Table for key levels
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

# Table for trade logs
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

# Pre-populate DB with asset keys if not present.
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
for asset in coinpaprika_ids.keys():
    cursor.execute("""
        INSERT OR IGNORE INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path)
        VALUES (?, '', '', '', '', '', '')
    """, (asset,))
conn.commit()

# Helper functions for levels persistence

def get_levels_from_db(asset_name):
    cursor.execute(
        "SELECT support, demand, resistance, supply, choch, chart_path FROM asset_levels WHERE asset = ?", 
        (asset_name,)
    )
    row = cursor.fetchone()
    if row:
        return {"support": row[0] or "",
                "demand": row[1] or "",
                "resistance": row[2] or "",
                "supply": row[3] or "",
                "choch": row[4] or "",
                "chart_path": row[5] or ""}
    return {k: "" for k in ["support","demand","resistance","supply","choch","chart_path"]}


def save_levels_to_db(asset_name, levels):
    cursor.execute("""
        INSERT INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset) DO UPDATE SET
            support = excluded.support,
            demand = excluded.demand,
            resistance = excluded.resistance,
            supply = excluded.supply,
            choch = excluded.choch,
            chart_path = excluded.chart_path
    """, (
        asset_name,
        levels.get("support", ""),
        levels.get("demand", ""),
        levels.get("resistance", ""),
        levels.get("supply", ""),
        levels.get("choch", ""),
        levels.get("chart_path", "")
    ))
    conn.commit()


def get_levels_for_asset(asset_name):
    levels = get_levels_from_db(asset_name)
    st.session_state.setdefault("levels_data", {})[asset_name] = levels
    return levels


def save_levels_for_asset(asset_name, levels):
    st.session_state.setdefault("levels_data", {})[asset_name] = levels
    save_levels_to_db(asset_name, levels)

# Shared Assets
icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png",
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png",
    "FARTCOIN": "fartcoin-logo.png"
}

# Include all original mode definitions here (trade_journal_mode, asset_data_mode, mindset_mode)...
# For brevity, these functions remain unchanged from your previous implementation.

# ---------------------------------------------------
# Strategy Mode (Trade Logging & Analytics)
# ---------------------------------------------------
def strategy_mode():
    st.title("Strategy")
    st.markdown("---")
    st.header("Strategy Tracker")
    strat_col1, strat_col2 = st.columns(2)
    with strat_col1:
        asset_for_strategy = st.text_input("Asset Symbol", placeholder="e.g. BTC")
        strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
        trade_result = st.selectbox("Trade Outcome", ["Win", "Loss", "Break-even"])
    with strat_col2:
        rr_logged = st.text_input("RR Ratio", value="1:1")
        notes = st.text_area("Additional Notes")

    if st.button("Save Trade to Log"):
        cursor.execute("""
            INSERT INTO trade_log (date, asset, strategy, rr_ratio, outcome, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d"),
            asset_for_strategy.upper(),
            strategy_used,
            rr_logged,
            trade_result,
            notes
        ))
        conn.commit()
        st.success("Trade saved to database!")

    df_hist = pd.read_sql("SELECT date AS 'Date', asset AS 'Asset', strategy AS 'Strategy', rr_ratio AS 'RR Ratio', outcome AS 'Outcome', notes AS 'Notes' FROM trade_log ORDER BY date", conn)
    if not df_hist.empty:
        st.markdown("### Trade History")
        st.dataframe(df_hist)
        st.sidebar.header("Filter Trade History")
        date_filter = st.sidebar.date_input("Select Date Range", [])
        if date_filter and len(date_filter) == 2:
            start_date, end_date = date_filter
            df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
            df_filtered = df_hist[(df_hist['Date'] >= pd.to_datetime(start_date)) & (df_hist['Date'] <= pd.to_datetime(end_date))]
            st.write("Filtered Trade History:")
            st.dataframe(df_filtered)

        st.markdown("### Performance Summary")
        total = len(df_hist)
        wins = len(df_hist[df_hist['Outcome'] == "Win"])
        losses = len(df_hist[df_hist['Outcome'] == "Loss"])
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0
        st.write(f"Total Trades: {total}")
        st.write(f"Win Rate: {win_rate}%")
        if total > 0:
            st.write(f"Most Used Strategy: {df_hist['Strategy'].mode()[0]}")

        st.markdown("### Trade Analytics")
        st.subheader("Trade Outcomes")
        outcome_counts = df_hist['Outcome'].value_counts()
        st.bar_chart(outcome_counts)
        try:
            df_hist['RR Numeric'] = df_hist['RR Ratio'].str.extract('([0-9\.]+)').astype(float)
            rr_data = df_hist.set_index('Date')[['RR Numeric']]
            st.subheader("RR Ratio Over Time")
            st.line_chart(rr_data)
        except Exception as e:
            st.warning(f"Could not plot RR Ratio chart: {e}")

        st.download_button(
            label="Download Trade History CSV",
            data=df_hist.to_csv(index=False),
            file_name="trade_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No trade log found yet.")

# ---------------------------------------------------
# Navigation
# ---------------------------------------------------
mode = st.sidebar.radio(
    "Select App Mode",
    [
        "Asset Data",
        "Strategy",
        "Mindset Dashboard",
        "Trade Journal & Checklist"
    ]
)

if mode == "Asset Data":
    asset_data_mode()
elif mode == "Strategy":
    strategy_mode()
elif mode == "Mindset Dashboard":
    mindset_mode()
elif mode == "Trade Journal & Checklist":
    trade_journal_mode()
