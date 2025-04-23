import streamlit as st
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

import requests
import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, date
from streamlit_autorefresh import st_autorefresh

# =============================================================================
# PERSISTENT DATA PATHS
# =============================================================================
DATA_DIR = "/mnt/data"
LOG_CSV = os.path.join(DATA_DIR, "trade_log.csv")
JOURNAL_CHART_DIR = os.path.join(DATA_DIR, "journal_charts")
MINDSET_CSV = os.path.join(DATA_DIR, "mindset_log.csv")
for d in [DATA_DIR, JOURNAL_CHART_DIR]:
    os.makedirs(d, exist_ok=True)

# =============================================================================
# SUB-PAGES VIA QUERY PARAMS
# =============================================================================
params = st.query_params
if "page" in params:
    page = params["page"][0]
    if page == "orderbook":
        st.title("Order Book Dashboard")
        st.write("Fetching KuCoin Level‑2 order book data...")
        def fetch_orderbook(sym):
            url = f"https://api.kucoin.com/api/v1/market/orderbook/level2?symbol={sym}-USDT"
            try:
                r = requests.get(url, timeout=5); r.raise_for_status()
                return r.json()
            except:
                return {"error":"failed", "symbol":sym}
        assets = ["BTC","ETH","ADA","SOL","LINK","XRP","ONDO","SUI","CVX","CRV","FARTCOIN"]
        data = {a:fetch_orderbook(a) for a in assets}
        st.json(data)
        st.stop()
    elif page == "buy": st.title("Where and How to Buy"); st.write("Coming soon!"); st.stop()
    elif page == "sell": st.title("Where to Sell"); st.write("Coming soon!"); st.stop()
    elif page == "market_sell": st.title("Selling the Market"); st.write("Coming soon!"); st.stop()

# =============================================================================
# MAIN MODES
# =============================================================================
def trade_journal_mode():
    st.title("🧾 Trade Journal & Checklist")
    col1,col2 = st.columns(2)
    with col1:
        # psychology checklist & grading
        p1=st.checkbox("Clear plan?"); p2=st.checkbox("Trading structure?"); p3=st.checkbox("Okay missing?")
        if all([p1,p2,p3]): st.success("Mindset ON POINT")
        else: st.warning("Mindset shaky")
        st.markdown("---")
        labels=[("Structure Break Clear?",2),("Return to Key Zone?",2),("Entry Signal Quality",2),("RR>2:1",1),("No Emotional Bias",1),("Correlation Confirms",1),("Used Checklist",1)]
        score=sum(st.slider(lbl,0,m,0) for lbl,m in labels)
        st.write(f"**Score:** {score}/10"); st.success("✅") if score>=7 else st.error("❌")
    with col2:
        st.subheader("Replay Trades")
        d=st.date_input("Select date",date.today())
        if os.path.exists(LOG_CSV):
            df=pd.read_csv(LOG_CSV,parse_dates=["Date"])
            df_day=df[df.Date==pd.to_datetime(d)]
            if df_day.empty: st.info("No trades")
            else:
                for _,r in df_day.iterrows():
                    with st.expander(f"{r.Date.date()} - {r.Asset} ({r.Outcome})"):
                        st.write(f"Strategy: {r.Strategy}")
                        st.write(f"RR Ratio: {r['RR Ratio']}")
                        st.write(f"Notes: {r.Notes}")
                        img=os.path.join(JOURNAL_CHART_DIR,f"{r.Asset}_{r.Date.date()}.png")
                        if os.path.exists(img): st.image(img)
        else: st.info("No trade log")
        st.subheader("Upload Chart")
        asset=st.text_input("Asset e.g. BTC",key="aj"); date_u=st.date_input("Date",date.today(),key="dj"); f=st.file_uploader("Chart png/jpg",type=["png","jpg"])
        if f and asset:
            path=os.path.join(JOURNAL_CHART_DIR,f"{asset.upper()}_{date_u}.png")
            open(path,"wb").write(f.read()); st.success("Chart saved")


def strategy_mode():
    st.title("Strategy Tracker")
    c1,c2=st.columns(2)
    with c1:
        a=st.text_input("Asset Symbol"); s=st.text_input("Strategy"); o=st.selectbox("Outcome",["Win","Loss","Break-even"])
    with c2:
        rr=st.text_input("RR Ratio","1:1"); n=st.text_area("Notes")
    if st.button("Save Trade"):
        row={"Date":datetime.now().strftime("%Y-%m-%d"),"Asset":a.upper(),"Strategy":s,"RR Ratio":rr,"Outcome":o,"Notes":n}
        df_new=pd.DataFrame([row])
        if os.path.exists(LOG_CSV): df=pd.read_csv(LOG_CSV);
        else: df=pd.DataFrame()
        df_all=pd.concat([df,df_new],ignore_index=True)
        df_all.to_csv(LOG_CSV,index=False)
        st.success("Saved")
    if os.path.exists(LOG_CSV):
        df=pd.read_csv(LOG_CSV,parse_dates=["Date"])
        st.dataframe(df)
        st.bar_chart(df.Outcome.value_counts())
        try:
            df['RR_num']=df['RR Ratio'].str.extract(r'([\d.]+)').astype(float)
            st.line_chart(df.set_index('Date')['RR_num'])
        except: pass
    else: st.info("No trades yet")


def asset_data_mode():
    st.title("Asset Data")
    st_autorefresh(30000,limit=100)
    assets={'BTC':'btc-bitcoin','ETH':'eth-ethereum','ADA':'ada-cardano'}
    sel=st.selectbox("Asset",list(assets.keys()))
    try:
        q=requests.get(f"https://api.coinpaprika.com/v1/tickers/{assets[sel]}",timeout=5).json()['quotes']['USD']
        st.write(f"Price: ${q['price']:.2f}")
        st.write(f"24h: {q['percent_change_24h']:.2f}%")
    except: st.warning("No data")


def mindset_mode():
    st.title("Mindset Dashboard")
    c1,c2=st.columns(2)
    with c1:
        es=st.slider("Emotional State",0,10,5); fl=st.slider("Focus",0,10,5); cf=st.slider("Confidence",0,10,5)
        if st.button("Log Mindset"):
            row={"Timestamp":datetime.now(),"Emotional":es,"Focus":fl,"Confidence":cf}
            df=pd.DataFrame([row])
            if os.path.exists(MINDSET_CSV): df_old=pd.read_csv(MINDSET_CSV);
            else: df_old=pd.DataFrame()
            pd.concat([df_old,df]).to_csv(MINDSET_CSV,index=False)
            st.success("Logged")
    if os.path.exists(MINDSET_CSV): st.dataframe(pd.read_csv(MINDSET_CSV))
    else: st.info("No logs")

mode=st.sidebar.radio("Mode",["Trade Journal","Strategy","Asset Data","Mindset"])
if mode=="Trade Journal": trade_journal_mode()
elif mode=="Strategy": strategy_mode()
elif mode=="Asset Data": asset_data_mode()
else: mindset_mode()
