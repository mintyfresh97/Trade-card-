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
        icon_path = f"assets/{icon_map.get(sym, '')}"
        if os.path.exists(icon_path):
            st.image(icon_path, width=32)
        # Fetch price data
        price, daily, weekly, monthly = None, None, None, None
        try:
            data = requests.get(
                f"https://api.coinpaprika.com/v1/tickers/{coinpaprika_ids[asset_display]}",
                timeout=5
            ).json()
            q = data.get("quotes", {}).get("USD", {})
            price = round(q.get("price", 0), 2)
            daily = round(q.get("percent_change_24h", 0), 2)
            weekly = round(q.get("percent_change_7d", 0), 2)
            monthly = round(q.get("percent_change_30d", 0), 2)
        except Exception:
            pass
        if price is not None:
            st.markdown(f"**Live Price:** ${price}")
        if daily is not None:
            st.markdown(
                f"""**Daily (24h):** {daily}%  
**Weekly (7d):** {weekly}%  
**Monthly (30d):** {monthly}%"""
            )
        # Social sentiment
        sentiment_score = random.randint(-100, 100)
        sentiment = (
            "Positive" if sentiment_score > 20 else
            "Negative" if sentiment_score < -20 else
            "Neutral"
        )
        st.markdown(f"**Social Sentiment:** {sentiment} (Score: {sentiment_score})")
        # Key levels
        levels = get_levels_for_asset(asset_display)
        st.markdown("### Key Levels & Volume Strength")
        for level in ["support", "demand", "resistance", "supply", "choch"]:
            st.markdown(f"**{level.capitalize()}:** {levels[level] or 'N/A'}")
        # Volume strength
        vol_df = pd.DataFrame({
            "Date": pd.date_range(date.today() - pd.Timedelta(days=29), periods=30),
            "Volume": np.random.randint(1000, 5000, 30)
        }).sort_values("Date")
        vol_df["MA"] = vol_df["Volume"].rolling(window=14).mean()
        last_vol = vol_df.iloc[-1]["Volume"]
        last_ma = vol_df.iloc[-1]["MA"] or 1
        ratio = last_vol / last_ma
        if ratio < 0.5:
            vol_score = 0.0
        elif ratio > 2.0:
            vol_score = 10.0
        else:
            vol_score = (ratio - 0.5) / (1.5) * 10.0
        st.markdown(f"**Volume Strength Score:** {vol_score:.1f} / 10")
        st.markdown("---")
        st.markdown(
            "[Where and How to Buy](?page=buy)  |  [Where to Sell](?page=sell)  |  [Selling the Market](?page=market_sell)",
            unsafe_allow_html=True
        )
    with col2:
        st.subheader("Edit Key Levels / Upload Chart")
        with st.expander("Modify Levels & Chart", expanded=True):
            k1, k2 = st.columns(2)
            sup = k1.text_input("Support", value=levels["support"])
            dem = k1.text_input("Demand", value=levels["demand"])
            res = k2.text_input("Resistance", value=levels["resistance"])
            sup2 = k2.text_input("Supply", value=levels["supply"])
            cho = k2.text_input("CHoCH", value=levels["choch"])
            st.markdown("---")
            upload_file = st.file_uploader("Attach Chart", type=["png","jpg","jpeg"], key="dash_chart")
            if st.button("Save Levels & Chart"):
                new_levels = {"support": sup, "demand": dem, "resistance": res, "supply": sup2, "choch": cho}
                if upload_file is not None:
                    chart_fname = f"{sym}.png"
                    chart_path = os.path.join("charts", chart_fname)
                    with open(chart_path, "wb") as f:
                        f.write(upload_file.getvalue())
                    new_levels["chart_path"] = chart_fname
                save_levels_for_asset(asset_display, new_levels)
                st.success("Levels and chart updated!")
        st.subheader("Trade Setup Grading (Out of 10)")
        t_scores = [
            st.slider(label, 0, max_val, 0)
            for label, max_val in [
                ("Structure Break Clear?", 2), ("Return to Key Zone?", 2),
                ("Entry Signal Quality", 2), ("Risk-Reward > 2:1", 1),
                ("No Emotional Bias", 1), ("Correlation Confirms Bias", 1),
                ("Used Journal or Checklist", 1)
            ]
        ]
        total = sum(t_scores)
        st.write(f"**Setup Score:** {total} / 10")
        total >= 7 and st.success("✅ TRADE VALID") or st.error("❌ NO TRADE")
        st.subheader(f"{sym} Daily Analysis")
        chart_file = levels.get("chart_path", "")
        if chart_file and os.path.exists(os.path.join("charts", chart_file)):
            st.image(os.path.join("charts", chart_file), use_container_width=True)
        else:
            st.info("No chart uploaded yet.")


def mindset_mode():
    st.markdown(
        """
        <style>
            .main { background-color: #111; color: #fff; }
            .sidebar-content { background-color: #222; color: #fff; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("🧠 Mindset Dashboard")
    st.caption("Inspired by Trading in the Zone — build discipline and self-awareness before and after every trade.")
    col1, col2 = st.columns(2)
    with col1:
        emotional_state = st.slider("Emotional State", 0, 10, 5)
        focus_level = st.slider("Focus Level", 0, 10, 5)
        confidence = st.slider("Confidence", 0, 10, 5)
        st.markdown("### ✅ Pre-Trade Checklist")
        checklist = []
        if st.checkbox("I’ve accepted the risk"): checklist.append("Accepted risk")
        if st.checkbox("Setup fits my plan"): checklist.append("Setup valid")
        if st.checkbox("I am not attached to the outcome"): checklist.append("Detached")
        if st.checkbox("Clear entry/SL/TP defined"): checklist.append("Defined setup")
        if st.checkbox("I will execute without fear"): checklist.append("Execute confidently")
        if st.button("📌 Log Mindset"):
            csv_file = "mindset_log.csv"
            if not os.path.exists(csv_file):
                pd.DataFrame(columns=[
                    "Timestamp", "Emotional State", "Focus Level", "Confidence",
                    "Checklist", "Followed Plan", "Impact", "Reflection"
                ]).to_csv(csv_file, index=False)
            df = pd.read_csv(csv_file)
            new_row = {
                "Timestamp": datetime.now(),
                "Emotional State": emotional_state,
                "Focus Level": focus_level,
                "Confidence": confidence,
                "Checklist": ", ".join(checklist),
                "Followed Plan": "",
                "Impact": "",
                "Reflection": ""
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.success("Mindset logged!")
    with col2:
        affirmations = [
            "Anything can happen.",
            "You don’t need to know what’s going to happen next to make money.",
            "Trading is not about being right, it’s about managing risk.",
            "I am the casino, not the gambler.",
            "My edge plays out over time, not every trade.",
            "Accepting risk is power. I control my response."
        ]
        if "affirmation" not in st.session_state:
            st.session_state.affirmation = random.choice(affirmations)
        st.markdown(f"> *{st.session_state.affirmation}*")
        if st.button("🔁 Shuffle"): st.session_state.affirmation = random.choice(affirmations)
        st.markdown("### 🧾 Post-Trade Reflection")
        followed_plan = st.radio("Did you follow your plan?", ["Yes", "No"])
        impact = st.selectbox("What affected your decision?", [
            "None", "Fear", "Overconfidence", "FOMO", "Impatience", "External Distraction"
        ])
        reflection = st.text_area("Notes or lessons learned")
        if st.button("📝 Save Reflection"):
            csv_file = "mindset_log.csv"
            df = pd.read_csv(csv_file)
            df.at[len(df)-1, "Followed Plan"] = followed_plan
            df.at[len(df)-1, "Impact"] = impact
            df.at[len(df)-1, "Reflection"] = reflection
            df.to_csv(csv_file, index=False)
            st.success("Reflection saved to last log.")
    st.markdown("---")
    st.markdown("### 🗂️ Recent Logs")
    csv_file = "mindset_log.csv"
    if os.path.exists(csv_file):
        st.dataframe(pd.read_csv(csv_file))
    else:
        st.info("No logs found yet.")


def strategy_mode():
    st.title("Strategy")
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
        cursor.execute(
            "INSERT INTO trade_log (date, asset, strategy, rr_ratio, outcome, notes) VALUES (?, ?, ?, ?, ?, ?)"  ,
            (datetime.now().strftime("%Y-%m-%d"), asset_for_strategy.upper(), strategy_used, rr_logged, trade_result, notes)
        )
        conn.commit()
        st.success("Trade saved!")
    df_hist = pd.read_sql("SELECT date AS Date, asset AS Asset, strategy AS Strategy, rr_ratio AS 'RR Ratio', outcome AS Outcome, notes AS Notes FROM trade_log ORDER BY date", conn)
    if not df_hist.empty:
        st.markdown("### Trade History")
        st.dataframe(df_hist)
        st.markdown("### Performance Summary")
        total = len(df_hist)
        wins = len(df_hist[df_hist.Outcome == "Win"]```
