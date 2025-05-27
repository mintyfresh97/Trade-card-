import streamlit as st
import requests
import os
import random
import sqlite3
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
import re
import pytesseract

# ---------------------------------------------------
# Directory Setup
# ---------------------------------------------------
JOURNAL_CHART_DIR = "journal_charts"
os.makedirs(JOURNAL_CHART_DIR, exist_ok=True)
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# ---------------------------------------------------
# SQLite Persistence Setup
# ---------------------------------------------------
conn = sqlite3.connect("levels_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS asset_levels (
    asset TEXT PRIMARY KEY,
    support TEXT, demand TEXT,
    resistance TEXT, supply TEXT,
    choch TEXT, chart_path TEXT
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
    cursor.execute(
        "INSERT OR IGNORE INTO asset_levels (asset,support,demand,resistance,supply,choch,chart_path) VALUES (?,?,?,?,?,?,?)",
        (asset, "", "", "", "", "", "")
    )
conn.commit()

def get_levels(asset):
    cursor.execute("SELECT support,demand,resistance,supply,choch,chart_path FROM asset_levels WHERE asset=?", (asset,))
    row = cursor.fetchone() or [""]*6
    return dict(zip(["support","demand","resistance","supply","choch","chart_path"], row))

def save_levels(asset, levels):
    cursor.execute("""
        INSERT INTO asset_levels (asset,support,demand,resistance,supply,choch,chart_path)
        VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(asset) DO UPDATE SET
            support=excluded.support,
            demand=excluded.demand,
            resistance=excluded.resistance,
            supply=excluded.supply,
            choch=excluded.choch,
            chart_path=excluded.chart_path
    """, (asset,levels["support"],levels["demand"],levels["resistance"],
          levels["supply"],levels["choch"],levels["chart_path"]))
    conn.commit()



