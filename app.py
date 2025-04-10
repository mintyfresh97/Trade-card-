import streamlit as st
import requests
import os
import io
import textwrap
import random
import sqlite3
from datetime import datetime, date
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

# Pre-populate coinpaprika_ids in DB if not present
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

def get_levels_from_db(asset_name):
    cursor = conn.cursor()
    cursor.execute("SELECT support, demand, resistance, supply, choch, chart_path FROM asset_levels WHERE asset = ?", (asset_name,))
    row = cursor.fetchone()
    if row:
        return {
            "support": row[0] or "",
            "demand": row[1] or "",
            "resistance": row[2] or "",
            "supply": row[3] or "",
            "choch": row[4] or "",
            "chart_path": row[5] or ""
        }
    else:
        return {"support": "", "demand": "", "resistance": "", "supply": "", "choch": "", "chart_path": ""}

def save_levels_to_db(asset_name, levels):
    cursor = conn.cursor()
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

# ---------------------------------------------------
# Shared Functions & Data
# ---------------------------------------------------
icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png",
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png",
    "FARTCOIN": "fartcoin-logo.png"
}

def get_coin_data_from_paprika(name, vs_currency="USD"):
    try:
        coin_id = coinpaprika_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinPaprika ID for coin: " + name)
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        response = requests.get(url, timeout=5)
        data = response.json()
        usd_data = data.get("quotes", {}).get(vs_currency, {})
        price = round(usd_data.get("price", 0), 2)
        daily = round(usd_data.get("percent_change_24h", 0), 2)
        weekly = round(usd_data.get("percent_change_7d", 0), 2)
        monthly = round(usd_data.get("percent_change_30d", 0), 2)
        return price, daily, weekly, monthly
    except Exception as e:
        st.error(f"CoinPaprika API Error for {name}: {e}")
        return None, None, None, None

def get_social_sentiment(coin):
    sentiment_score = random.randint(-100, 100)
    if sentiment_score > 20:
        sentiment = "Positive"
    elif sentiment_score < -20:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, sentiment_score

# ---------------------------------------------------
# Trade Journal Checklist
# ---------------------------------------------------
def show_checklist():
    st.subheader("🔍 3-Point Psychology Checklist")
    p1 = st.checkbox("✅ Do I have a clear plan (entry, SL, TP)?")
    p2 = st.checkbox("✅ Am I trading structure, not emotion?")
    p3 = st.checkbox("✅ Am I okay missing today if no setup?")
    if all([p1, p2, p3]):
        st.success("Mindset: ON POINT")
    else:
        st.warning("Mindset: Shaky. Re-check before entering.")
    st.markdown("---")
    st.subheader("Trade Setup Grading (Out of 10)")
    s1 = st.slider("Structure Break Clear?", 0, 2, 0)
    s2 = st.slider("Return to Key Zone?", 0, 2, 0)
    s3 = st.slider("Entry Signal Quality", 0, 2, 0)
    s4 = st.slider("Risk-Reward > 2:1", 0, 1, 0)
    s5 = st.slider("No Emotional Bias", 0, 1, 0)
    s6 = st.slider("Correlation Confirms Bias", 0, 1, 0)
    s7 = st.slider("Used Journal or Checklist", 0, 1, 0)
    total_score = s1 + s2 + s3 + s4 + s5 + s6 + s7
    st.write(f"**Setup Score:** {total_score} / 10")
    if total_score >= 7:
        st.success("TRADE VALID ✅")
    else:
        st.error("NO TRADE ❌ - Wait for better setup")

# ---------------------------------------------------
# Navigation
# ---------------------------------------------------
app_mode = st.sidebar.radio(
    "Select App Mode",
    ["Trade Journal & Checklist", "Asset Data", "Strategy", "Mindset Dashboard"]
)

# ====================================================
# 1) Trade Journal & Checklist (Dark Mode, 2-Column)
# ====================================================
if app_mode == "Trade Journal & Checklist":
    # Dark mode for consistency
    st.markdown(
        """
        <style>
        .reportview-container, .main, .block-container {
            background-color: #111;
            color: #fff;
        }
        .sidebar .sidebar-content {
            background-color: #222;
            color: #fff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("🧾 Trade Journal & Checklist")
    st.caption("Daily pre-trade mindset and structure check")

    col1, col2 = st.columns(2)

    # --- Column 1: Checklist & Grading ---
    with col1:
        show_checklist()

    # --- Column 2: Journal Replay & Chart Upload ---
    with col2:
        st.subheader("📅 Replay Journal Viewer")
        selected_day = st.date_input("Select Day to Review", value=datetime.now().date())
        log_path = "trade_log.csv"
        if os.path.exists(log_path):
            df_log = pd.read_csv(log_path)
            df_log['Date'] = pd.to_datetime(df_log['Date'], errors='coerce')
            df_day = df_log[df_log['Date'] == pd.to_datetime(selected_day)]
            if not df_day.empty:
                for idx, row in df_day.iterrows():
                    expander_label = f"{row['Date'].date()} - {row['Asset']} ({row['Outcome']})"
                    with st.expander(expander_label):
                        st.markdown(f"**Strategy:** {row['Strategy']}")
                        st.markdown(f"**RR Ratio:** {row['RR Ratio']}")
                        st.markdown(f"**Notes:** {row['Notes']}")
                        base_asset = row['Asset'].split()[0].upper()
                        chart_name = f"{base_asset}_{row['Date'].date()}.png"
                        image_path = os.path.join(JOURNAL_CHART_DIR, chart_name)
                        if os.path.exists(image_path):
                            st.image(image_path, caption="Attached Chart Screenshot")
            else:
                st.info("No trades found on that date.")
        else:
            st.info("No trade log found.")

        st.subheader("📥 Upload Chart to Log Entry")
        asset_for_upload = st.text_input("Asset Name (e.g. BTC)", key="upload_asset_journal")
        upload_date = st.date_input("Date of Trade", value=datetime.now().date(), key="upload_date_journal")
        chart_file = st.file_uploader("Chart Image (PNG or JPG)", type=["png", "jpg", "jpeg"], key="journal_chart")
        if chart_file and asset_for_upload:
            asset_clean = asset_for_upload.strip().upper()
            chart_path = os.path.join(JOURNAL_CHART_DIR, f"{asset_clean}_{upload_date}.png")
            with open(chart_path, "wb") as f:
                f.write(chart_file.read())
            st.success("Chart uploaded and auto-linked to journal entry.")

# ====================================================
# 2) Asset Data (formerly PnL & Risk Dashboard) 
#    We remove 'Show Trade Card Preview' block
# ====================================================
elif app_mode == "Asset Data":
    # Optionally, you can add dark mode CSS if you want it dark too.
    st.title("Asset Data")
    
    # Auto-refresh if desired
    st_autorefresh(interval=30000, limit=100, key="autorefresh")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        # Asset Selection and Data
        display_names = list(coinpaprika_ids.keys())
        asset_display = st.selectbox("Select Asset", display_names)
        asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()

        # Asset Icon
        icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
        if os.path.exists(icon_path):
            st.image(icon_path, width=32)
        else:
            st.warning("Icon not found")

        # Live price data
        price, daily_change, weekly_change, monthly_change = get_coin_data_from_paprika(asset_display)
        if price is not None:
            st.markdown(f"**Live Price:** ${price}")
            st.markdown(
                f"**Daily (24h):** {daily_change}%  \n"
                f"**Weekly (7d):** {weekly_change}%  \n"
                f"**Monthly (30d):** {monthly_change}%"
            )
        else:
            st.markdown("No market data available.")

        # Sentiment
        sentiment, sentiment_score = get_social_sentiment(asset_display)
        st.markdown(f"**Social Sentiment:** {sentiment} (Score: {sentiment_score})")

        # Key Levels
        levels = get_levels_for_asset(asset_display)
        st.markdown("### Key Levels & Volume Strength")
        st.markdown(f"**Support:** {levels['support'] or 'N/A'}")
        st.markdown(f"**Demand:** {levels['demand'] or 'N/A'}")
        st.markdown(f"**Resistance:** {levels['resistance'] or 'N/A'}")
        st.markdown(f"**Supply:** {levels['supply'] or 'N/A'}")
        st.markdown(f"**CHoCH:** {levels['choch'] or 'N/A'}")

        # Volume Strength
        vol_df = pd.DataFrame({
            "Date": pd.date_range("2023-01-01", periods=30, freq="D"),
            "Volume": np.random.randint(1000, 5000, 30)
        })
        vol_df.sort_values("Date", inplace=True)
        vol_score = 0.0
        if len(vol_df) >= 14:
            vol_df["VolumeMA"] = vol_df["Volume"].rolling(window=14).mean()
            last_vol = vol_df["Volume"].iloc[-1]
            last_ma = vol_df["VolumeMA"].iloc[-1]
            if pd.notna(last_ma):
                ratio = last_vol / last_ma
                if ratio < 0.5:
                    vol_score = 0.0
                elif ratio > 2.0:
                    vol_score = 10.0
                else:
                    vol_score = (ratio - 0.5) / (2.0 - 0.5) * 10.0
        st.markdown(f"**Volume Strength Score:** {vol_score:.1f} / 10")

    with col2:
        st.subheader("Edit Key Levels / Upload Chart")
        with st.expander("Modify Levels & Chart", expanded=False):
            new_support = st.text_input("Support", value=levels["support"])
            new_demand = st.text_input("Demand", value=levels["demand"])
            new_resistance = st.text_input("Resistance", value=levels["resistance"])
            new_supply = st.text_input("Supply", value=levels["supply"])
            new_choch = st.text_input("CHoCH", value=levels["choch"])
            st.markdown("#### Upload Chart Analysis")
            uploaded_file = st.file_uploader("Drag and drop your chart image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="dashboard_chart")

            if st.button("Save Levels & Chart"):
                updated_levels = {
                    "support": new_support,
                    "demand": new_demand,
                    "resistance": new_resistance,
                    "supply": new_supply,
                    "choch": new_choch,
                    "chart_path": levels.get("chart_path", "")
                }
                if uploaded_file is not None:
                    file_ext = os.path.splitext(uploaded_file.name)[1]
                    filename = f"{asset_symbol}.png"
                    file_path = os.path.join(CHARTS_DIR, filename)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    updated_levels["chart_path"] = filename

                save_levels_for_asset(asset_display, updated_levels)
                st.success("Levels and chart updated!")
                st.experimental_rerun()

        st.subheader(f"{asset_symbol} Daily Analysis")
        # Display the chart if uploaded
        chart_filename = levels.get("chart_path", "")
        if chart_filename:
            chart_path = os.path.join(CHARTS_DIR, chart_filename)
            if os.path.exists(chart_path):
                st.image(chart_path, caption=f"{asset_symbol} Chart Analysis", use_container_width=True)
            else:
                st.info("Chart file not found. Please upload again.")
        else:
            st.info("No chart uploaded yet for this asset.")

        # [REMOVED] The entire "Show Trade Card Preview" block

# ====================================================
# 3) Strategy (moved from the old "PnL & Risk Dashboard" bottom section)
# ====================================================
elif app_mode == "Strategy":
    st.title("Strategy")
    
    # Strategy Tracking & Performance Summaries
    st.markdown("---")
    st.header("Strategy Tracker")
    track_col1, track_col2 = st.columns(2)

    with track_col1:
        # Let user pick an asset for logging, if needed
        asset_for_strategy = st.text_input("Asset Symbol", placeholder="e.g. BTC")
        strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
        trade_result = st.selectbox("Trade Outcome", ["Win", "Loss", "Break-even"])

    with track_col2:
        rr_logged = st.text_input("RR Ratio", value="1:1")
        notes = st.text_area("Additional Notes")

    if st.button("Save Trade to Log"):
        trade_data = {
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Asset": [asset_for_strategy.upper()],
            "Strategy": [strategy_used],
            "RR Ratio": [rr_logged],
            "Outcome": [trade_result],
            "Notes": [notes],
        }
        df_new = pd.DataFrame(trade_data)
        log_path = "trade_log.csv"
        if os.path.exists(log_path):
            df_existing = pd.read_csv(log_path)
            df_all = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_all = df_new
        df_all.to_csv(log_path, index=False)
        st.success("Trade saved to log!")

    # Show trade history
    log_path = "trade_log.csv"
    if os.path.exists(log_path):
        st.markdown("### Trade History")
        df_hist = pd.read_csv(log_path)
        st.dataframe(df_hist)

        # Filtering
        st.sidebar.header("Filter Trade History")
        date_filter = st.sidebar.date_input("Select Date Range", [])
        if date_filter and len(date_filter) == 2:
            start_date, end_date = date_filter
            df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
            df_filtered = df_hist[(df_hist['Date'] >= pd.to_datetime(start_date)) & (df_hist['Date'] <= pd.to_datetime(end_date))]
            st.write("Filtered Trade History:")
            st.dataframe(df_filtered)

        # Performance Summary
        st.markdown("### Performance Summary")
        total = len(df_hist)
        wins = len(df_hist[df_hist["Outcome"] == "Win"])
        losses = len(df_hist[df_hist["Outcome"] == "Loss"])
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0
        st.write(f"Total Trades: {total}")
        st.write(f"Win Rate: {win_rate}%")
        if total > 0:
            st.write(f"Most Used Strategy: {df_hist['Strategy'].mode()[0]}")
        else:
            st.write("No trades logged yet.")

        # Trade Analytics
        st.markdown("### Trade Analytics")
        df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
        st.subheader("Trade Outcomes")
        outcome_counts = df_hist['Outcome'].value_counts()
        st.bar_chart(outcome_counts)
        try:
            df_hist['RR Numeric'] = df_hist['RR Ratio'].str.extract('([0-9\.]+)').astype(float)
            df_hist_sorted = df_hist.sort_values("Date")
            rr_data = df_hist_sorted.set_index("Date")[["RR Numeric"]]
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

# ====================================================
# 4) Mindset Dashboard
# ====================================================
elif app_mode == "Mindset Dashboard":
    st.markdown(
        """
        <style>
        .reportview-container, .main, .block-container {
            background-color: #111;
            color: #fff;
        }
        .sidebar .sidebar-content {
            background-color: #222;
            color: #fff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("🧠 Mindset Dashboard")
    st.caption("Inspired by *Trading in the Zone* — build discipline and self-awareness before and after every trade.")
    
    col1, col2 = st.columns(2)
    
    # --- Column 1: Mindset Check-in ---
    with col1:
        st.subheader("🔍 Current Mental State")
        emotional_state = st.slider("Emotional State", 0, 10, 5, help="0 = Calm, 10 = Anxious")
        focus_level = st.slider("Focus Level", 0, 10, 5, help="0 = Distracted, 10 = Fully Focused")
        confidence = st.slider("Confidence", 0, 10, 5, help="0 = Doubtful, 10 = Highly Confident")
        
        st.markdown("### ✅ Pre-Trade Checklist")
        checklist = []
        if st.checkbox("I’ve accepted the risk"):
            checklist.append("Accepted risk")
        if st.checkbox("Setup fits my plan"):
            checklist.append("Setup valid")
        if st.checkbox("I am not attached to the outcome"):
            checklist.append("Detached")
        if st.checkbox("Clear entry/SL/TP defined"):
            checklist.append("Defined setup")
        if st.checkbox("I will execute without fear"):
            checklist.append("Execute confidently")
        
        if st.button("📌 Log Mindset"):
            new_row = {
                "Timestamp": datetime.now(),
                "Emotional State": emotional_state,
                "Focus Level": focus_level,
                "Confidence Level": confidence,
                "Checklist": ", ".join(checklist),
                "Followed Plan": "",
                "Impact": "",
                "Reflection": ""
            }
            csv_file = "mindset_log.csv"
            if not os.path.exists(csv_file):
                pd.DataFrame(columns=[
                    "Timestamp", "Emotional State", "Focus Level", "Confidence Level",
                    "Checklist", "Followed Plan", "Impact", "Reflection"
                ]).to_csv(csv_file, index=False)
            df = pd.read_csv(csv_file)
            df = df.append(new_row, ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.success("Mindset logged!")
    
    # --- Column 2: Affirmations & Reflection ---
    with col2:
        st.subheader("💬 Daily Affirmation")
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
        if st.button("🔁 Shuffle"):
            st.session_state.affirmation = random.choice(affirmations)
        
        st.markdown("### 🧾 Post-Trade Reflection")
        followed_plan = st.radio("Did you follow your plan?", ["Yes", "No"])
        impact = st.selectbox("What affected your decision?", [
            "None", "Fear", "Overconfidence", "FOMO", "Impatience", "External Distraction"
        ])
        reflection = st.text_area("Notes or lessons learned")
        
        if st.button("📝 Save Reflection"):
            csv_file = "mindset_log.csv"
            if not os.path.exists(csv_file):
                st.warning("Please log your mindset first.")
            else:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    df.at[len(df)-1, "Followed Plan"] = followed_plan
                    df.at[len(df)-1, "Impact"] = impact
                    df.at[len(df)-1, "Reflection"] = reflection
                    df.to_csv(csv_file, index=False)
                    st.success("Reflection saved to last log.")
                else:
                    st.warning("Please log your mindset first.")
    
    st.markdown("---")
    st.markdown("### 🗂️ Recent Logs")
    csv_file = "mindset_log.csv"
    if os.path.exists(csv_file):
        log_df = pd.read_csv(csv_file)
        st.dataframe(log_df.tail(5))
    else:
        st.info("No logs found yet.")
