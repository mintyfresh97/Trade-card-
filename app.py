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

import cv2

def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    return Image.fromarray(thresh)

def chart_analysis_mode():
    st.title("🧠 Chart Image Analyzer")
    uploaded_img = st.file_uploader("Upload Coinalyze/TV Chart", type=["png","jpg"])

    if uploaded_img:
        raw_img = Image.open(uploaded_img)
        img = preprocess_image(raw_img)
        st.image(raw_img, caption="Original Uploaded Chart", use_column_width=True)
        st.image(img, caption="Preprocessed for OCR", use_column_width=True)

        text = pytesseract.image_to_string(img)
        st.markdown("---")
        st.markdown("**🧾 OCR Text Extracted:**")
        st.text(text[:1000])

        analysis = []
        oi_vals = [float(x.replace("M","")) for x in re.findall(r'(\d+\.\d+)M', text)]
        funding_match = re.search(r"Funding Rate.*?([+-]?\d+\.\d+)", text)
        cvd_match = re.search(r"CVD.*?([+-]?\d+\.\d+)", text)

        if len(oi_vals) >= 2:
            if oi_vals[-1] > oi_vals[0]:
                analysis.append("📈 Open Interest is increasing – new positions entering.")
            elif oi_vals[-1] < oi_vals[0]:
                analysis.append("📉 Open Interest is declining – positions are closing.")
            else:
                analysis.append("➖ Open Interest is flat – indecision.")

        if funding_match:
            funding = float(funding_match.group(1))
            if funding > 0.01:
                analysis.append(f"💡 Funding Rate: {funding:.4f} (High, long bias)")
            elif funding < -0.01:
                analysis.append(f"🔻 Funding Rate: {funding:.4f} (Shorts aggressive)")
            else:
                analysis.append(f"🟰 Funding Rate: {funding:.4f} (Neutral)")

        if cvd_match:
            cvd = float(cvd_match.group(1))
            if cvd < 0:
                analysis.append(f"📉 CVD: {cvd} (Net selling pressure)")
            else:
                analysis.append(f"📈 CVD: {cvd} (Net buying pressure)")

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
            "Short Bias" if 'Shorts aggressive' in ' '.join(analysis) else "Neutral",
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
                "❌" if 'Shorts aggressive' in ' '.join(analysis) else "✅",
                "✅"  # compression can go both ways
            ]
        }
        st.dataframe(pd.DataFrame(readiness_data))

# Existing app modes retained...
def asset_data_mode():
    ...

# -----------------------------------------------------------------------------
mode = st.sidebar.radio("Mode", ["Asset Data","Strategy","Mindset Dashboard","Trade Journal","Chart Analyzer"])
if mode=="Asset Data":      asset_data_mode()
elif mode=="Strategy":      strategy_mode()
elif mode=="Mindset Dashboard": mindset_mode()
elif mode=="Chart Analyzer": chart_analysis_mode()
else:                       trade_journal_mode()
