import streamlit as st
st.set_page_config(page_title="Trade Journal & PnL Dashboard", layout="wide")

import requests
import os
import random
import sqlite3
from datetime import datetime, date
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
    cursor.execute("SELECT support, demand, resistance, supply, choch, chart_path FROM asset_levels WHERE asset = ?", (asset_name,))
    row = cursor.fetchone()
    if row:
        return dict(zip(["support","demand","resistance","supply","choch","chart_path"], [val or "" for val in row]))
    return {k: "" for k in ["support","demand","resistance","supply","choch","chart_path"]}

def save_levels_to_db(asset_name, levels):
    cursor.execute(
        "INSERT INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path) VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(asset) DO UPDATE SET support=excluded.support, demand=excluded.demand, resistance=excluded.resistance, "
        "supply=excluded.supply, choch=excluded.choch, chart_path=excluded.chart_path",
        (asset_name, levels.get('support',''), levels.get('demand',''), levels.get('resistance',''), levels.get('supply',''), levels.get('choch',''), levels.get('chart_path',''))
    )
    conn.commit()

def get_levels_for_asset(asset_name):
    levels = get_levels_from_db(asset_name)
    st.session_state.setdefault('levels_data', {})[asset_name] = levels
    return levels

def save_levels_for_asset(asset_name, levels):
    st.session_state.setdefault('levels_data', {})[asset_name] = levels
    save_levels_to_db(asset_name, levels)

icon_map = {"BTC":"bitcoin-btc-logo.png","ETH":"ethereum-eth-logo.png","ADA":"cardano-ada-logo.png",
            "SOL":"solana-sol-logo.png","LINK":"chainlink-link-logo.png","XRP":"xrp-xrp-logo.png",
            "ONDO":"ondo-finance-ondo-logo.png","SUI":"sui-sui-logo.png","CRV":"curve-dao-token-crv-logo.png",
            "CVX":"convex-finance-cvx-logo.png","FARTCOIN":"fartcoin-logo.png"}

# =============================================================================
# MODE DEFINITIONS
# =============================================================================
def trade_journal_mode():
    st.title("🧾 Trade Journal & Checklist")
    st.caption("Daily pre-trade mindset and structure check")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 3-Point Psychology Checklist")
        p1 = st.checkbox("✅ Do I have a clear plan (entry, SL, TP)?")
        p2 = st.checkbox("✅ Am I trading structure, not emotion?")
        p3 = st.checkbox("✅ Am I okay missing today if no setup?")
        if all([p1, p2, p3]): st.success("Mindset: ON POINT")
        else: st.warning("Mindset: Shaky. Re-check before entering.")
        st.markdown("---")
        st.subheader("Trade Setup Grading (Out of 10)")
        scores = [st.slider(label, 0, max_val, 0)
                  for label, max_val in [
                      ("Structure Break Clear?",2),("Return to Key Zone?",2),
                      ("Entry Signal Quality",2),("Risk-Reward > 2:1",1),
                      ("No Emotional Bias",1),("Correlation Confirms Bias",1),
                      ("Used Journal or Checklist",1)
                  ]]
        total_score = sum(scores)
        st.write(f"**Setup Score:** {total_score} / 10")
        st.success("TRADE VALID ✅") if total_score>=7 else st.error("NO TRADE ❌ - Wait for better setup")
    with col2:
        st.subheader("📅 Replay Journal Viewer")
        selected_day = st.date_input("Select Day to Review", value=date.today())
        log_path = "trade_log.csv"
        if os.path.exists(log_path):
            df_log = pd.read_csv(log_path); df_log['Date']=pd.to_datetime(df_log['Date'],errors='coerce')
            df_day = df_log[df_log['Date']==pd.to_datetime(selected_day)]
            if not df_day.empty:
                for _,row in df_day.iterrows():
                    with st.expander(f"{row['Date'].date()} - {row['Asset']} ({row['Outcome']})"):
                        st.markdown(f"**Strategy:** {row['Strategy']}")
                        st.markdown(f"**RR Ratio:** {row['RR Ratio']}")
                        st.markdown(f"**Notes:** {row['Notes']}")
                        chart = os.path.join("journal_charts", f"{row['Asset'].split()[0].upper()}_{row['Date'].date()}.png")
                        if os.path.exists(chart): st.image(chart, caption="Attached Chart Screenshot")
            else: st.info("No trades found on that date.")
        else: st.info("No trade log found.")
        st.subheader("📥 Upload Chart to Log Entry")
        asset_for_upload = st.text_input("Asset Name (e.g. BTC)", key="upload_asset_journal")
        upload_date = st.date_input("Date of Trade", value=date.today(), key="upload_date_journal")
        chart_file = st.file_uploader("Chart Image (PNG or JPG)", type=["png","jpg","jpeg"], key="journal_chart")
        if chart_file and asset_for_upload:
            path = os.path.join("journal_charts", f"{asset_for_upload.strip().upper()}_{upload_date}.png")
            with open(path,"wb") as f: f.write(chart_file.read())
            st.success("Chart uploaded and auto-linked to journal entry.")


def asset_data_mode():
    st.markdown(
        '<div class="asset-data-banner">'
        '<h1>Asset Data</h1>'
        '<p>Monitor real-time market info and manage key levels</p>'
        '</div>', unsafe_allow_html=True
    )
    st_autorefresh(interval=30000, limit=100, key="autorefresh")
    col1,col2=st.columns([1,2])
    with col1:
        asset_display=st.selectbox("Select Asset", list(coinpaprika_ids.keys()))
        sym=asset_display.split("(")[-1].strip(")")
        icon=f"assets/{icon_map.get(sym,"")}"; os.path.exists(icon) and st.image(icon,width=32)
        price,daily,weekly,monthly=None,None,None,None
        try:
            data=requests.get(f"https://api.coinpaprika.com/v1/tickers/{coinpaprika_ids[asset_display]}",timeout=5).json()
            q=data.get("quotes",{}).get("USD",{})
            price,daily,weekly,monthly=round(q.get("price",0),2),round(q.get("percent_change_24h",0),2),round(q.get("percent_change_7d",0),2),round(q.get("percent_change_30d",0),2)
        except: pass
        price and st.markdown(f"**Live Price:** ${price}")
        daily is not None and st.markdown(f"**Daily (24h):** {daily}%  
**Weekly (7d):** {weekly}%  
**Monthly (30d):** {monthly}%")
        sent,score= ("Neutral",0)
        s=random.randint(-100,100); sent="Positive" if s>20 else("Negative" if s<-20 else"Neutral"); score=s
        st.markdown(f"**Social Sentiment:** {sent} (Score: {score})")
        levels=get_levels_for_asset(asset_display)
        st.markdown("### Key Levels & Volume Strength")
        for k in["support","demand","resistance","supply","choch"]: st.markdown(f"**{k.title()}:** {levels[k] or 'N/A'}")
        dfv=pd.DataFrame({"Date":pd.date_range(date.today()-pd.Timedelta(days=29),periods=30),"Volume":np.random.randint(1000,5000,30)}).sort_values("Date")
        dfv["MA"]=dfv["Volume"].rolling(14).mean()
        ratio=dfv.iloc[-1,1]/(dfv.iloc[-1,2] or 1)
        score_vol=0 if ratio<0.5 else(10 if ratio>2 else (ratio-0.5)/1.5*10)
        st.markdown(f"**Volume Strength Score:** {score_vol:.1f} / 10")
        st.markdown("---")
        st.markdown("[Where and How to Buy](?page=buy)  |  [Where to Sell](?page=sell)  |  [Selling the Market](?page=market_sell)",unsafe_allow_html=True)
    with col2:
        st.subheader("Edit Key Levels / Upload Chart")
        with st.expander("Modify Levels & Chart",True):
            kl1,kl2=st.columns(2)
            sup=kl1.text_input("Support",value=levels["support"]); dem=kl1.text_input("Demand",value=levels["demand"])
            res=kl2.text_input("Resistance",value=levels["resistance"]); sup2=kl2.text_input("Supply",value=levels["supply"]); cho=kl2.text_input("CHoCH",value=levels["choch"])
            st.markdown("---")
            up=st.file_uploader("Attach Chart",type=["png","jpg","jpeg"],key="dash_chart")
            if st.button("Save Levels & Chart"):
                new={"support":sup,"demand":dem,"resistance":res,"supply":sup2,"choch":cho,"chart_path":levels.get("chart_path","")}
                if up: open(os.path.join("charts",f"{sym}.png"),"wb").write(up.getvalue()); new["chart_path"]=f"{sym}.png"
                save_levels_for_asset(asset_display,new); st.success("Levels and chart updated!")
        st.subheader("Trade Setup Grading (Out of 10)")
        t_scores=[st.slider(l,0,m,0) for l,m in [("Structure Break Clear?",2),("Return to Key Zone?",2),("Entry Signal Quality",2),("Risk-Reward > 2:1",1),("No Emotional Bias",1),("Correlation Confirms Bias",1),("Used Journal or Checklist",1)]]
        tot=sum(t_scores); st.write(f"**Setup Score:** {tot}/10"); st.success("✅") if tot>=7 else st.error("❌")
        st.subheader(f"{sym} Daily Analysis")
        cp=levels.get("chart_path","")
        if cp and os.path.exists(os.path.join("charts",cp)): st.image(os.path.join("charts",cp),use_container_width=True)
        else: st.info("No chart uploaded yet.")


def mindset_mode():
    st.markdown("""
    <style>.main {background:#111;color:#fff;} .sidebar-content{background:#222;color:#fff;}</style>
    """,unsafe_allow_html=True)
    st.title("🧠 Mindset Dashboard")
    st.caption("Inspired by Trading in the Zone...")
    c1,c2=st.columns(2)
    with c1:
        es=st.slider("Emotional State",0,10,5)
        fl=st.slider("Focus Level",0,10,5)
        cf=st.slider("Confidence",0,10,5)
        st.markdown("### ✅ Pre-Trade Checklist")
        cl=[]
        for label in ["Accepted risk","Setup fits my plan","Not attached to outcome","Clear entry/SL/TP","Execute without fear"]:
            if st.checkbox(label): cl.append(label)
        if st.button("📌 Log Mindset"):
            df=pd.read_csv("mindset_log.csv") if os.path.exists("mindset_log.csv") else pd.DataFrame(columns=["Timestamp","Emotional State","Focus Level","Confidence","Checklist","Followed Plan","Impact","Reflection"])
            df2=pd.DataFrame([{"Timestamp":datetime.now(),"Emotional State":es,"Focus Level":fl,"Confidence":cf,"Checklist":", ".join(cl),"Followed Plan":"","Impact":"","Reflection":""}])
            df=pd.concat([df,df2],ignore_index=True); df.to_csv("mindset_log.csv",index=False); st.success("Mindset logged!")
    with c2:
        affirm=["Anything can happen.","You don’t need to know...","Trading is not about being right...","I am the casino...","My edge plays out...","Accepting risk is power..."]
        if "aff" not in st.session_state: st.session_state.aff=random.choice(affirm)
        st.markdown(f"> *{st.session_state.aff}*")
        if st.button("🔁 Shuffle"): st.session_state.aff=random.choice(affirm)
        st.markdown("### 🧾 Post-Trade Reflection")
        fp=st.radio("Did you follow your plan?",["Yes","No"])
        imp=st.selectbox("What affected your decision?",["None","Fear","Overconfidence","FOMO","Impatience","External Distraction"])
        refl=st.text_area("Notes or lessons learned")
        if st.button("📝 Save Reflection"):
            df=pd.read_csv("mindset_log.csv")
            df.at[len(df)-1,"Followed Plan"]=fp; df.at[len(df)-1,"Impact"]=imp; df.at[len(df)-1,"Reflection"]=refl; df.to_csv("mindset_log.csv",index=False); st.success("Reflection saved.")
    st.markdown("---")
    if os.path.exists("mindset_log.csv"): st.dataframe(pd.read_csv("mindset_log.csv"))
    else: st.info("No logs found yet.")


def strategy_mode():
    st.title("Strategy")
    st.header("Strategy Tracker")
    col1,col2=st.columns(2)
    with col1:
        a=st.text_input("Asset Symbol")
        s=st.text_input("Strategy Name")
        o=st.selectbox("Trade Outcome",["Win","Loss","Break-even"])
    with col2:
        r=st.text_input("RR Ratio","1:1")
        n=st.text_area("Additional Notes")
    if st.button("Save Trade to Log"):
        cursor.execute("INSERT INTO trade_log (date,asset,strategy,rr_ratio,outcome,notes) VALUES (?,?,?,?,?,?)",(datetime.now().strftime("%Y-%m-%d"),a.upper(),s,r,o,n));conn.commit();st.success("Trade saved!")
    df=pd.read_sql("SELECT date AS Date, asset AS Asset, strategy AS Strategy, rr_ratio AS 'RR Ratio', outcome AS Outcome, notes AS Notes FROM trade_log ORDER BY date",conn)
    if not df.empty:
        st.markdown("### Trade History"); st.dataframe(df)
        st.markdown("### Performance Summary"); total=len(df);wins=len(df[df.Outcome=="Win"]);wr=round(wins/total*100,1) if total>0 else 0; st.write(f"Total Trades: {total}");st.write(f"Win Rate: {wr}%"); st.write(f"Most Used Strategy: {df.Strategy.mode()[0] if total>0 else 'N/A'}")
        st.bar_chart(df.Outcome.value_counts())
        try: df['RR Numeric']=df['RR Ratio'].str.extract(r'([0-9\.]+)').astype(float); st.line_chart(df.set_index('Date')[['RR Numeric']])
        except: pass
        st.download_button("Download CSV",data=df.to_csv(index=False),file_name="trade_log.csv",mime="text/csv")
    else: st.info("No trade log found yet.")

# =============================================================================
# NAVIGATION
# =============================================================================
mode=st.sidebar.radio("Select App Mode",["Asset Data","Strategy","Mindset Dashboard","Trade Journal & Checklist"])
if mode=="Asset Data": asset_data_mode()
elif mode=="Strategy": strategy_mode()
elif mode=="Mindset Dashboard": mindset_mode()
elif mode=="Trade Journal & Checklist": trade_journal_mode()
