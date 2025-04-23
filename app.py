import streamlit as st
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

import requests, os, textwrap, random, io
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# =============================================================================
# PERSISTENT DATA FOLDERS & FILES
# =============================================================================
DATA_DIR = "/mnt/data"
JOURNAL_CHART_DIR = os.path.join(DATA_DIR, "journal_charts")
CHARTS_DIR = os.path.join(DATA_DIR, "charts")
LOG_CSV = os.path.join(DATA_DIR, "trade_log.csv")
MINDSET_CSV = os.path.join(DATA_DIR, "mindset_log.csv")

for d in (DATA_DIR, JOURNAL_CHART_DIR, CHARTS_DIR):
    if not os.path.exists(d):
        os.makedirs(d)

# =============================================================================
# QUERY-PARAMETER SUB-PAGES
# =============================================================================
params = st.query_params
if "page" in params:
    page = params["page"][0]
    if page == "orderbook":
        st.title("Order Book Dashboard")
        st.write("Fetching KuCoin Level-2 order book data…")
        def fetch_orderbook(symbol: str):
            api = f"https://api.kucoin.com/api/v1/market/orderbook/level2?symbol={symbol}-USDT"
            try:
                r = requests.get(api, timeout=5); r.raise_for_status()
                return r.json()
            except Exception as e:
                return {"error": str(e), "symbol": symbol}
        ASSETS = ["BTC","ETH","ADA","SOL","LINK","XRP","ONDO","SUI","CVX","CRV","FARTCOIN"]
        st.json({a: fetch_orderbook(a) for a in ASSETS})
        st.stop()
    elif page == "buy":
        st.title("Where and How to Buy"); st.write("Coming soon!"); st.stop()
    elif page == "sell":
        st.title("Where to Sell"); st.write("Coming soon!"); st.stop()
    elif page == "market_sell":
        st.title("Selling the Market"); st.write("Coming soon!"); st.stop()

# =============================================================================
# MAIN APP MODES
# =============================================================================
def trade_journal_mode():
    st.title("🧾 Trade Journal & Checklist")
    st.caption("Daily pre-trade mindset and structure check")
    col1, col2 = st.columns(2)

    # — Checklist & grading —
    with col1:
        st.subheader("🔍 3-Point Psychology Checklist")
        p1 = st.checkbox("✅ Clear plan (entry, SL, TP)?")
        p2 = st.checkbox("✅ Trading structure, not emotion?")
        p3 = st.checkbox("✅ Okay missing today if no setup?")
        if all([p1,p2,p3]):
            st.success("Mindset: ON POINT")
        else:
            st.warning("Mindset: Shaky. Re-check before entering.")

        st.markdown("---")
        st.subheader("Trade Setup Grading (Out of 10)")
        labels = [
            ("Structure Break Clear?",2),
            ("Return to Key Zone?",2),
            ("Entry Signal Quality",2),
            ("Risk-Reward > 2:1",1),
            ("No Emotional Bias",1),
            ("Correlation Confirms Bias",1),
            ("Used Journal or Checklist",1),
        ]
        score = sum(st.slider(lbl, 0, mx, 0) for lbl,mx in labels)
        st.write(f"**Setup Score:** {score}/10")
        if score >= 7:
            st.success("TRADE VALID ✅")
        else:
            st.error("NO TRADE ❌ — Wait for better setup")

    # — Replay & upload —
    with col2:
        st.subheader("📅 Replay Journal Viewer")
        day = st.date_input("Select Day to Review", date.today())
        if os.path.exists(LOG_CSV):
            df = pd.read_csv(LOG_CSV, parse_dates=["Date"])
            df_day = df[df["Date"] == pd.to_datetime(day)]
            if not df_day.empty:
                for _,r in df_day.iterrows():
                    label = f"{r.Date.date()} – {r.Asset} ({r.Outcome})"
                    with st.expander(label):
                        st.markdown(f"**Strategy:** {r.Strategy}")
                        st.markdown(f"**RR Ratio:** {r['RR Ratio']}")
                        st.markdown(f"**Notes:** {r.Notes}")
                        img = os.path.join(JOURNAL_CHART_DIR,
                                           f"{r.Asset.split()[0].upper()}_{r.Date.date()}.png")
                        if os.path.exists(img):
                            st.image(img, caption="Chart")
            else:
                st.info("No trades found on that date.")
        else:
            st.info("No trade log found.")

        st.subheader("📥 Upload Chart to Log Entry")
        asset_name = st.text_input("Asset (e.g. BTC)", key="upl_asset")
        upl_date   = st.date_input("Date of Trade", date.today(), key="upl_date")
        upl_file   = st.file_uploader("Chart (PNG/JPG)", type=["png","jpg","jpeg"], key="upl_chart")
        if upl_file and asset_name:
            path = os.path.join(JOURNAL_CHART_DIR,
                                f"{asset_name.strip().upper()}_{upl_date}.png")
            with open(path,"wb") as f:
                f.write(upl_file.read())
            st.success("Chart saved.")

def strategy_mode():
    st.title("Strategy")
    st.markdown("---")
    st.header("Strategy Tracker")
    c1,c2 = st.columns(2)
    with c1:
        a = st.text_input("Asset Symbol", placeholder="e.g. BTC")
        strat = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
        outc = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
    with c2:
        rr = st.text_input("RR Ratio", value="1:1")
        notes = st.text_area("Additional Notes")

    if st.button("Save Trade to Log"):
        row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Asset": a.upper(),
            "Strategy": strat,
            "RR Ratio": rr,
            "Outcome": outc,
            "Notes": notes
        }
        df_new = pd.DataFrame([row])
        if os.path.exists(LOG_CSV):
            df_all = pd.concat([pd.read_csv(LOG_CSV), df_new], ignore_index=True)
        else:
            df_all = df_new
        df_all.to_csv(LOG_CSV, index=False)
        st.success("Trade saved.")

    if os.path.exists(LOG_CSV):
        df = pd.read_csv(LOG_CSV, parse_dates=["Date"])
        st.markdown("### Trade History")
        st.dataframe(df)

        st.markdown("### Performance Summary")
        total = len(df)
        wins  = len(df[df.Outcome=="Win"])
        rate  = round(wins/total*100,1) if total else 0
        st.write(f"Total Trades: {total}")
        st.write(f"Win Rate: {rate}%")

        st.markdown("### Trade Analytics")
        st.subheader("Outcomes")
        st.bar_chart(df.Outcome.value_counts())
        try:
            df["RR_num"] = df["RR Ratio"].str.extract(r"([\d\.]+)").astype(float)
            st.subheader("RR Over Time")
            st.line_chart(df.set_index("Date")["RR_num"])
        except:
            pass

        st.download_button("Download CSV",
                           data=df.to_csv(index=False),
                           file_name="trade_log.csv",
                           mime="text/csv")
    else:
        st.info("No trade log yet.")

def asset_data_mode():
    st.markdown("""
    <div class="asset-data-banner">
      <h1>Asset Data</h1>
      <p>Monitor real-time market info and manage key levels</p>
    </div>
    """, unsafe_allow_html=True)
    st_autorefresh(interval=30000, limit=100, key="autorefresh")
    col1,col2 = st.columns([1,2])

    # Left panel – market data, sentiment, levels
    with col1:
        coins = {
          'Bitcoin (BTC)': 'btc-bitcoin', 'Ethereum (ETH)': 'eth-ethereum', 
          # … etc …
        }
        sel = st.selectbox("Select Asset", list(coins.keys()))
        sym = sel.split("(")[-1].strip(")")
        # price fetch …
        try:
            resp = requests.get(f"https://api.coinpaprika.com/v1/tickers/{coins[sel]}", timeout=5).json()
            q = resp.get("quotes",{}).get("USD",{})
            st.markdown(f"**Live Price:** ${q.get('price'):.2f}")
            st.markdown(f"**Daily:** {q.get('percent_change_24h'):.2f}%  \n"
                        f"**Weekly:** {q.get('percent_change_7d'):.2f}%  \n"
                        f"**Monthly:** {q.get('percent_change_30d'):.2f}%")
        except:
            st.warning("No market data.")

        sentiment = random.randint(-100,100)
        st.markdown(f"**Social Sentiment:** "
                    + ("Positive" if sentiment>20 else "Negative" if sentiment<-20 else "Neutral")
                    + f" (Score: {sentiment})")

        # levels & volume (you can keep your existing code here)…

        st.markdown("---")
        st.markdown(
            "[Where and How to Buy](?page=buy)  |  "
            "[Where to Sell](?page=sell)  |  "
            "[Selling the Market](?page=market_sell)",
            unsafe_allow_html=True
        )

    # Right panel – edit levels/upload chart & grading
    with col2:
        # … your existing chart‐upload & grading code …

        pass  # (paste in your full right‐column logic here)

def mindset_mode():
    st.markdown("""
    <style>
      .main { background-color: #111; color: #fff; }
      .sidebar-content { background-color: #222; color: #fff; }
    </style>
    """, unsafe_allow_html=True)
    st.title("🧠 Mindset Dashboard")
    st.caption("Inspired by *Trading in the Zone*…")
    c1, c2 = st.columns(2)

    # Pre‐trade logging
    with c1:
        es = st.slider("Emotional State",0,10,5)
        fl = st.slider("Focus Level",0,10,5)
        cf = st.slider("Confidence",0,10,5)
        st.markdown("### ✅ Pre-Trade Checklist")
        checks = []
        for label in ["Accepted risk","Setup fits my plan","Not attached to outcome","Clear entry/SL/TP","Execute without fear"]:
            if st.checkbox(label): checks.append(label)
        if st.button("📌 Log Mindset"):
            row = {
                "Timestamp": datetime.now(),
                "Emotional State": es,
                "Focus Level": fl,
                "Confidence": cf,
                "Checklist": ", ".join(checks),
                "Followed Plan": "",
                "Impact": "",
                "Reflection": ""
            }
            df = pd.DataFrame([row])
            if os.path.exists(MINDSET_CSV):
                df = pd.concat([pd.read_csv(MINDSET_CSV), df], ignore_index=True)
            df.to_csv(MINDSET_CSV, index=False)
            st.success("Mindset logged!")

    # Post‐trade reflection & display
    with c2:
        # … your existing reflection code …
        pass

    st.markdown("---")
    if os.path.exists(MINDSET_CSV):
        st.dataframe(pd.read_csv(MINDSET_CSV))
    else:
        st.info("No logs yet.")

# ──────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────
mode = st.sidebar.radio(
    "Select App Mode",
    ["Asset Data","Strategy","Mindset Dashboard","Trade Journal & Checklist"]
)

if mode == "Asset Data":
    asset_data_mode()
elif mode == "Strategy":
    strategy_mode()
elif mode == "Mindset Dashboard":
    mindset_mode()
elif mode == "Trade Journal & Checklist":
    trade_journal_mode()
