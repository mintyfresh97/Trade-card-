import streamlit as st
import os
import pandas as pd
import random
from datetime import datetime

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(page_title="📈 Strategy Tracker", layout="wide")

# ---------------------------------------------------
# Strategy Tracker Only
# ---------------------------------------------------
def strategy_mode():
    LOG_PATH = "trade_log.csv"
    EXAMPLES_DIR = "strategy_examples"
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

    st.title("📈 Strategy Tracker")
    st.markdown("---")

    # --- Strategy Summary & Risk ---
    with st.expander("📋 Long Strategy Summary", expanded=True):
        st.markdown(
            """
**Timeframe Analysis**: 4H → 1H → 15M  
**Tools Used**: EMA, zones, structure, CHoCH, momentum

**Entry Criteria**:  
- Price returns to key zone  
- Confirm: breakout + momentum + CHoCH + EMA signal

**Risk Management**:  
- Stop Loss: 1% or below range lows  
- TP1: 3% (close 25%)  
- TP2: 5% (full exit)  
- Exit on 5m CHoCH break or momentum shift
"""
        )

    # --- Market Behavior Checklist ---
    with st.expander("📊 Market Behavior Checklist", expanded=False):
        mb1 = st.radio("Is price forming at a price level and ranging?", ["Yes","No"], key="mb1")
        mb2 = st.radio("If ranging, have highs and lows been defined?", ["Yes","No"], key="mb2")
        mb3 = st.radio("Are BTC and ETH both trading in same direction?", ["Yes","No"], key="mb3")
        mb4 = st.radio("Is there clear momentum to support the trade?", ["Yes","No"], key="mb4")
        if st.button("Save Market Behavior", key="save_mb"):
            st.success("Behavior saved!")

    st.markdown("---")

    # --- Load or init log ---
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
    else:
        df = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # --- Trade Input Form ---
    with st.form("trade_form", clear_on_submit=True):
        l, r = st.columns(2)
        with l:
            asset = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with r:
            rr = st.text_input("RR Ratio", "1:1")
            notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("Save Trade to Log")
        if submitted:
            entry = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Asset": asset.upper(),
                "Strategy": strat,
                "RR Ratio": rr,
                "Outcome": outcome,
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            df.to_csv(LOG_PATH, index=False)
            st.success("Trade saved!")

        # --- Display Log ---
    st.markdown("### 📊 Trade History")
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No trades logged yet.")

    # --- Example Upload ---
    st.markdown("---")
    st.subheader("📁 Upload Example Trades")
    uploaded = st.file_uploader(
        "Upload Example Trade Image(s)", type=["png","jpg","jpeg"], accept_multiple_files=True, key="example_upload"
    )
    if uploaded:
        for img in uploaded:
            save_path = os.path.join(EXAMPLES_DIR, img.name)
            with open(save_path, "wb") as f:
                f.write(img.getbuffer())
        st.success("Examples saved!")
        st.experimental_rerun()

    files = os.listdir(EXAMPLES_DIR)

    files = os.listdir(EXAMPLES_DIR)
    if files:
        for name in files:
            cols = st.columns([4,1])
            with cols[0]:
                st.image(os.path.join(EXAMPLES_DIR, name), caption=name, use_container_width=True)
            with cols[1]:
                if st.button(f"Delete {name}"):
                    os.remove(os.path.join(EXAMPLES_DIR, name))
                    st.experimental_rerun()
    else:
        st.info("No examples uploaded.")

# Run tracker
strategy_mode()




