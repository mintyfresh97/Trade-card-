import streamlit as st
import os
import random
import pandas as pd
from datetime import datetime

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(page_title="Strategy Tracker", layout="wide")

# ---------------------------------------------------
# Strategy Mode (only)
# ---------------------------------------------------
def strategy_mode():
    LOG_PATH = "trade_log.csv"

    st.title("📈 Strategy Tracker")
    st.markdown("---")

    # Long Strategy Summary
    with st.expander("📋 Long Strategy Summary", expanded=True):
        st.markdown("""
**Timeframe Analysis**: 4H → 1H → 15M  
**Tools Used**: EMA, zones, structure, CHoCH, momentum  

**Entry Criteria**:  
- Price returns to a key zone  
- Confirmation: breakout + momentum + CHoCH + EMA signal  

**Risk Management**:  
- Stop Loss: 1% or range lows  
- TP1: 3% (close 25%)  
- TP2: 5% (full exit)  
- Exit early on 5m CHoCH break or momentum shift  
""")

    # Market Behavior Checklist
    with st.expander("📊 Market Behavior Checklist", expanded=False):
        mb1 = st.radio("Is price forming at a price level and ranging?", ["Yes","No"], key="mb1")
        mb2 = st.radio("If ranging, have highs and lows been defined?", ["Yes","No"], key="mb2")
        mb3 = st.radio("Are BTC and ETH both trading in the same direction?", ["Yes","No"], key="mb3")
        mb4 = st.radio("Is there clear momentum to support the trade?", ["Yes","No"], key="mb4")
        if st.button("Save Market Behavior", key="save_mb"):
            st.success("Market behavior saved!")

    st.markdown("---")

    # Load or initialize trade log
    if os.path.exists(LOG_PATH):
        df_log = pd.read_csv(LOG_PATH)
    else:
        df_log = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # Input Form
    with st.form("strategy_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            asset_sym = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat_name = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with right:
            rr = st.text_input("RR Ratio", "1:1")
            notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("Save Trade to Log")
        if submitted:
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Asset": asset_sym.upper(),
                "Strategy": strat_name,
                "RR Ratio": rr,
                "Outcome": outcome,
                "Notes": notes
            }
            df_log = pd.concat([df_log, pd.DataFrame([new_row])], ignore_index=True)
            df_log.to_csv(LOG_PATH, index=False)
            st.success("Trade saved to log!")

    # Display the log
    st.markdown("### 📊 Trade History")
    if not df_log.empty:
        st.dataframe(df_log)
    else:
        st.info("No trades logged yet.")

# ---------------------------------------------------
# Launch the Strategy page directly
# ---------------------------------------------------
strategy_mode()


