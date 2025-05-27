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

icon_map = { sym: f"{sym.lower()}-logo.png" for sym in 
    ["BTC","ETH","XRP","ADA","SOL","LINK","ONDO","CRV","CVX","SUI","FARTCOIN"] }

def fetch_price(name):
    try:
        data = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coinpaprika_ids[name]}", timeout=5).json()
        q = data["quotes"]["USD"]
        return round(q["price"],2), round(q["percent_change_24h"],2), round(q["percent_change_7d"],2), round(q["percent_change_30d"],2)
    except:
        return None, None, None, None

def random_sentiment():
    s = random.randint(-100,100)
    return ("Positive" if s>20 else "Negative" if s< -20 else "Neutral"), s

# -----------------------------------------------------------------------------
# Modes
# -----------------------------------------------------------------------------

def asset_data_mode():
    st.markdown("<div style='background:linear-gradient(to right,#2c2c2c,#3d3d3d);padding:1rem;border-radius:.5rem'>"
                "<h1 style='color:#FFD700;text-align:center'>Asset Data</h1></div>",
                unsafe_allow_html=True)
    st_autorefresh(30000, key="ref1")
    col1, col2 = st.columns([1,2])
    with col1:
        name = st.selectbox("Asset", list(coinpaprika_ids))
        sym = name.split("(")[-1].strip(")")
        price,daily,weekly,monthly = fetch_price(name)
        if price:
            st.write(f"**Price**: ${price}")
            st.write(f"24h: {daily}%, 7d: {weekly}%, 30d: {monthly}%")
        else:
            st.write("Data unavailable.")
        sent,sc = random_sentiment()
        st.write(f"**Sentiment**: {sent} (Score {sc})")
        levels = get_levels(name)
        st.write("### Key Levels")
        for k in ["support","demand","resistance","supply","choch"]:
            st.write(f"**{k.title()}**: {levels[k] or 'N/A'}")
        st.write("**Volume Strength**:", round(random.uniform(0,10),1), "/10")
    with col2:
        st.subheader("Modify Levels / Upload Chart")
        lv = get_levels(name)
        s1 = st.text_input("Support", lv["support"])
        s2 = st.text_input("Demand", lv["demand"])
        s3 = st.text_input("Resistance", lv["resistance"])
        s4 = st.text_input("Supply", lv["supply"])
        s5 = st.text_input("CHoCH", lv["choch"])
        up = st.file_uploader("Chart", type=["png","jpg"])
        if st.button("Save"):
            path = lv["chart_path"]
            if up:
                fn = f"{sym}.png"
                with open(os.path.join(CHARTS_DIR,fn),"wb") as f: f.write(up.getvalue())
                path = fn
            save_levels(name, {"support":s1,"demand":s2,"resistance":s3,"supply":s4,"choch":s5,"chart_path":path})
            st.success("Saved!")
        if lv["chart_path"]:
            st.image(os.path.join(CHARTS_DIR,lv["chart_path"]), use_container_width=True)

def strategy_mode():
    st.title("Strategy Tracker")
    a = st.text_input("Asset Symbol","BTC")
    strat = st.text_input("Strategy","EMA Bounce")
    outcome = st.selectbox("Outcome",["Win","Loss","Break-even"])
    rr = st.text_input("RR","1:1")
    notes = st.text_area("Notes")
    if st.button("Save Trade"):
        df = pd.DataFrame([{ "Date":datetime.now().strftime("%Y-%m-%d"),
                             "Asset":a,"Strategy":strat,"Outcome":outcome,
                             "RR":rr,"Notes":notes }])
        lp="trade_log.csv"
        old = pd.read_csv(lp) if os.path.exists(lp) else pd.DataFrame()
        pd.concat([old,df]).to_csv(lp,index=False)
        st.success("Logged")
    if os.path.exists("trade_log.csv"):
        df = pd.read_csv("trade_log.csv")
        st.dataframe(df)
        st.write("Win rate:",round(len(df[df.Outcome=="Win"])/len(df)*100,1),"%")

def mindset_mode():
    st.title("Mindset Dashboard")
    e = st.slider("Emotional State",0,10,5)
    f = st.slider("Focus",0,10,5)
    c = st.slider("Confidence",0,10,5)
    checklist = []
    for label in ["Accepted risk","Plan fits","Detached","Setup clear","Execute fearlessly"]:
        if st.checkbox(label): checklist.append(label)
    if st.button("Log Mindset"):
        df = pd.DataFrame([{ "Time":datetime.now(), "E":e,"F":f,"C":c, "Checklist":",".join(checklist) }])
        lp="mindset_log.csv"
        old = pd.read_csv(lp) if os.path.exists(lp) else pd.DataFrame()
        pd.concat([old,df]).to_csv(lp,index=False)
        st.success("Saved")
    if os.path.exists("mindset_log.csv"):
        st.dataframe(pd.read_csv("mindset_log.csv").tail(5))

def trade_journal_mode():
    st.title("📓 Trade Journal & Checklist")
    if os.path.exists("trade_log.csv"):
        df = pd.read_csv("trade_log.csv")
        day = st.date_input("Review Date", datetime.now().date())
        sub = df[df.Date==day.strftime("%Y-%m-%d")]
        if sub.empty: st.write("No entries")
        else:
            for _,r in sub.iterrows():
                with st.expander(f"{r.Date} {r.Asset} {r.Outcome}"):
                    st.write(r.to_dict())

# -----------------------------------------------------------------------------
mode = st.sidebar.radio("Mode", ["Asset Data","Strategy","Mindset Dashboard","Trade Journal"])
if mode=="Asset Data":      asset_data_mode()
elif mode=="Strategy":      strategy_mode()
elif mode=="Mindset Dashboard": mindset_mode()
else:                       trade_journal_mode()
