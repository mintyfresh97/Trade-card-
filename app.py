import streamlit as st
import os
import random
import pandas as pd
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

    st.title("📈 Strategy Tracker")
    st.markdown("---")

    # --- Example Trades (Persistent) ---
    EXAMPLES_DIR = "strategy_examples"
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

    st.subheader("📁 Example Trades")
    uploaded_examples = st.file_uploader(
        "Upload Example Trade Image(s)", type=["png","jpg","jpeg"], accept_multiple_files=True
    )
    if uploaded_examples:
        for ex in uploaded_examples:
            save_path = os.path.join(EXAMPLES_DIR, ex.name)
            with open(save_path, "wb") as f:
                f.write(ex.getbuffer())
        st.success("Example(s) saved!")

    example_files = os.listdir(EXAMPLES_DIR)
    if example_files:
        cols = st.columns(min(3, len(example_files)))
        for idx, fname in enumerate(example_files):
            with cols[idx % len(cols)]:
                st.image(os.path.join(EXAMPLES_DIR, fname), caption=fname, use_container_width=True)
    else:
        st.info("No example trades uploaded yet.")

    st.markdown("---")

    # --- Long Strategy Summary + Risk Management ---
    with st.expander("📋 Long Strategy Summary", expanded=True):
        st.markdown("""
**Timeframe Analysis**: 4H → 1H → 15M  
**Tools Used**: EMA Long Strategy, manually drawn zones, market structure, CHoCH, momentum

**Entry Criteria**:  
- Price returns to key structure level (zone)  
- Confirmation: breakout + momentum + CHoCH + EMA signal

**Risk Management**:  
- Stop Loss: 1% or below range lows  
- TP1: 3% → close 25%  
- TP2: 5% → full exit  
- Exit on 5m CHoCH break or momentum shift
""")

    # --- Market Behavior Checklist ---
    with st.expander("📊 Market Behavior Checklist", expanded=False):
        mb1 = st.radio("Is price forming at a price level and ranging?", ["Yes","No"], key="mb1")
        mb2 = st.radio("If ranging, have highs and lows been defined?", ["Yes","No"], key="mb2")
        mb3 = st.radio("Are BTC and ETH both trading in same direction?", ["Yes","No"], key="mb3")
        mb4 = st.radio("Is there clear momentum to support the trade?", ["Yes","No"], key="mb4")
        if st.button("Save Market Behavior", key="save_mb"):
            st.success("Market behavior saved!")

    st.markdown("---")

    # --- Load or Initialize Trade Log ---
    if os.path.exists(LOG_PATH):
        df_log = pd.read_csv(LOG_PATH)
    else:
        df_log = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # --- Input Form ---
    with st.form("strategy_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            asset = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strategy = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with right:
            rr = st.text_input("RR Ratio", "1:1")
            notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("Save Trade to Log")
        if submitted:
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Asset": asset.upper(),
                "Strategy": strategy,
                "RR Ratio": rr,
                "Outcome": outcome,
                "Notes": notes
            }
            df_log = pd.concat([df_log, pd.DataFrame([new_entry])], ignore_index=True)
            df_log.to_csv(LOG_PATH, index=False)
            st.success("Trade saved to log!")

    # --- Display Trade History ---
    st.markdown("### 📊 Trade History")
    if not df_log.empty:
        st.dataframe(df_log)
    else:
        st.info("No trades logged yet.")

# ---------------------------------------------------
# Launch Strategy Tracker directly
# ---------------------------------------------------
strategy_mode()
