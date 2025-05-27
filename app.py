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

def get_slope_of_region(img_array, region):
    x1, y1, x2, y2 = region
    crop = img_array[y1:y2, x1:x2]
    if crop.ndim == 3:
        crop_gray = np.mean(crop, axis=2)  # Convert RGB to grayscale
    else:
        crop_gray = crop
    vertical_profile = np.mean(crop_gray, axis=1)
    slope = vertical_profile[-1] - vertical_profile[0]
    return slope

def chart_analysis_mode():
    st.title("🧠 Chart Image Analyzer")
    uploaded_img = st.file_uploader("Upload Coinalyze/TV Chart", type=["png","jpg"])

    if uploaded_img:
        raw_img = Image.open(uploaded_img)
        img = raw_img

        img_array = np.array(img)
        h, w = img_array.shape[:2]

        cvd_slope = get_slope_of_region(img_array, (0, int(h*0.83), w, int(h*0.98)))
        funding_slope = get_slope_of_region(img_array, (0, int(h*0.66), w, int(h*0.83)))
        oi_slope = get_slope_of_region(img_array, (0, int(h*0.5), w, int(h*0.66)))

        analysis = []
        if oi_slope > 10:
            analysis.append("📈 Open Interest is increasing – new positions entering.")
        elif oi_slope < -10:
            analysis.append("📉 Open Interest is declining – positions are closing.")
        else:
            analysis.append("➖ Open Interest is flat – indecision.")

        if funding_slope > 10:
            analysis.append("💡 Funding Rate rising (potential long bias)")
        elif funding_slope < -10:
            analysis.append("🔻 Funding Rate falling (potential short pressure)")
        else:
            analysis.append("🟰 Funding Rate flat")

        if cvd_slope < -10:
            analysis.append("📉 CVD: Net selling pressure")
        elif cvd_slope > 10:
            analysis.append("📈 CVD: Net buying pressure")
        else:
            analysis.append("➖ CVD: Sideways / Neutral")

        st.markdown("---")
        st.markdown("### 📊 Analysis Summary")
        for line in analysis:
            st.write(line)

        st.markdown("---")
        st.markdown("## 🧠 Top-Level Summary")
        st.markdown("""
- **Price**: (Needs manual interpretation)
- **Open Interest (OI)**: {} 
- **Funding Rate**: {} 
- **CVD**: {}
        """.format(
            "Increasing" if 'Open Interest is increasing' in ' '.join(analysis) else
            "Decreasing" if 'Open Interest is declining' in ' '.join(analysis) else "Flat",
            "Long Bias" if 'long bias' in ' '.join(analysis) else
            "Short Bias" if 'short pressure' in ' '.join(analysis) else "Neutral",
            "Selling Pressure" if 'Net selling pressure' in ' '.join(analysis) else
            "Buying Pressure" if 'Net buying pressure' in ' '.join(analysis) else "Unknown"
        ))

        st.markdown("## ✅ Trade Readiness Checklist")
        readiness_data = {
            "Signal": ["OI increasing", "CVD rising", "Price holding range", "Funding overheating", "Volatility compression"],
            "Bullish": [
                "✅" if 'Open Interest is increasing' in ' '.join(analysis) else "❌",
                "✅" if 'Net buying pressure' in ' '.join(analysis) else "❌",
                "✅",  # placeholder for manual confirmation
                "❌" if 'long bias' in ' '.join(analysis) else "✅",
                "✅"  # placeholder for manual compression detection
            ],
            "Bearish": [
                "❌" if 'Open Interest is increasing' in ' '.join(analysis) else "✅",
                "✅" if 'Net selling pressure' in ' '.join(analysis) else "❌",
                "⚠️",  # weak structure
                "❌" if 'short pressure' in ' '.join(analysis) else "✅",
                "✅"  # compression can go both ways
            ]
        }
        st.dataframe(pd.DataFrame(readiness_data))

        st.markdown("---")
        st.markdown("### 🧠 GPT-style Interpretation")
        st.write("Based on the current analysis:")

        st.markdown("---")
        st.markdown("### 🧾 Full ChatGPT-style Breakdown")
        cvd_note = ""
        if 'Net selling pressure' in ' '.join(analysis):
            cvd_note = "Sharp rebound, but still net negative → suggests passive buying, active sellers still exiting."
        elif 'Net buying pressure' in ' '.join(analysis):
            cvd_note = "Net buying stepping in — active demand returning."
        else:
            cvd_note = "Sideways CVD — market indecisive or passive."

        price_comment = "Price: (Needs manual context — e.g., breakout, range, or deviation.)"
        oi_comment = "Open Interest: Increasing (shows fresh participation)." if 'Open Interest is increasing' in ' '.join(analysis) else (
            "Open Interest: Decreasing (positions closing, caution needed)." if 'Open Interest is declining' in ' '.join(analysis) else "Open Interest: Flat")
        funding_comment = "Funding: Positive, climbing — long bias building." if 'long bias' in ' '.join(analysis) else (
            "Funding: Dropping — shorts pressing." if 'short pressure' in ' '.join(analysis) else "Funding: Neutral")

        st.markdown(f"""
- **{price_comment}**  
- **{oi_comment}**  
- **{funding_comment}**  
- **CVD**: {cvd_note}  
        """)

        if 'Open Interest is increasing' in ' '.join(analysis) and 'Net buying pressure' in ' '.join(analysis) and 'long bias' in ' '.join(analysis):
            st.success("**Bias**: Bullish continuation likely — strong alignment.")
        elif 'Net selling pressure' in ' '.join(analysis):
            st.warning("**Bias**: Bearish exhaustion or distribution — wait for confirmation.")
        else:
            st.info("**Bias**: Mixed — stay patient or zoom in to lower timeframe.")
        if 'Open Interest is increasing' in ' '.join(analysis):
            st.write("- **OI is increasing**, confirming participation. Could support continuation if price structure is bullish.")
        elif 'Open Interest is declining' in ' '.join(analysis):
            st.write("- **OI is declining**, suggesting position unwinding or lack of conviction.")

        if 'Funding Rate rising' in ' '.join(analysis):
            st.write("- **Funding rate is rising**, showing long bias building. Be cautious of potential long crowding.")
        elif 'Funding Rate falling' in ' '.join(analysis):
            st.write("- **Funding rate is dropping**, indicating short interest increasing. May hint at bearish setups.")

        if 'Net buying pressure' in ' '.join(analysis):
            st.write("- **CVD shows net buying**, suggesting active buyers stepping in. Good if matched with bullish structure.")
        elif 'Net selling pressure' in ' '.join(analysis):
            st.write("- **CVD shows net selling**, suggesting passive buyers absorbing sell pressure or distribution occurring.")
