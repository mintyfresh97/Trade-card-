import streamlit as st
from PIL import Image
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
        left, right = st.columns(2)
        with left:
            asset = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with right:
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

        # --- Example Trades Grid (Compact) ---
    st.markdown("---")
    with st.expander("📁 Example Trades Gallery", expanded=False):
        # Upload section
        uploaded = st.file_uploader(
            "Upload Example Trade Images", type=["png","jpg","jpeg"], accept_multiple_files=True, key="example_upload"
        )
        if uploaded:
            for img in uploaded:
                save_path = os.path.join(EXAMPLES_DIR, img.name)
                with open(save_path, "wb") as f:
                    f.write(img.getbuffer())
            st.success("Examples saved!")
            

                # Display grid
        files = sorted(os.listdir(EXAMPLES_DIR))
        if files:
            num_cols = 3  # fewer columns for larger images
            rows = (len(files) + num_cols - 1) // num_cols
            for row in range(rows):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    idx = row * num_cols + col_idx
                    if idx < len(files):
                        fname = files[idx]
                        img_path = os.path.join(EXAMPLES_DIR, fname)
                        try:
                            img = Image.open(img_path)
                            img.thumbnail((300, 300))  # increase thumbnail size
                            with cols[col_idx]:
                                st.image(img, caption=fname, width=300)
                                if st.button("Delete", key=f"del_{idx}"):
                                    os.remove(img_path)
                        except Exception:
                            cols[col_idx].markdown(f"Error loading {fname}")
        else:
            st.info("No example trades uploaded yet.")
            st.info("No example trades uploaded yet.")

# Run the Strategy Tracker
strategy_mode()




