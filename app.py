import streamlit as st
from PIL import Image
import os
import io
import pandas as pd
import random
from datetime import datetime
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(page_title="📈 Strategy Tracker", layout="wide")

# ---------------------------------------------------
# AWS S3 Setup
# ---------------------------------------------------
# Load your credentials & bucket from Streamlit secrets:
aws_secrets = st.secrets.get("aws", {})
AWS_ACCESS_KEY_ID     = aws_secrets.get("AWS_ACCESS_KEY_ID", "").strip()
AWS_SECRET_ACCESS_KEY = aws_secrets.get("AWS_SECRET_ACCESS_KEY", "").strip()
AWS_DEFAULT_REGION    = aws_secrets.get("AWS_DEFAULT_REGION", "").strip()
S3_BUCKET             = aws_secrets.get("S3_BUCKET", "").strip()

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET]):
    st.error(
        "🚨 S3 configuration missing. "
        "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION & S3_BUCKET in your Streamlit secrets."
    )
    st.stop()

# Build S3 client explicitly (no hidden whitespace or quotes)
s3 = boto3.client(
    "s3",
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = AWS_DEFAULT_REGION,
    config                = Config(signature_version="s3v4"),
)

# ---------------------------------------------------
# S3 Helper Functions
# ---------------------------------------------------
def list_s3_keys():
    try:
        resp = s3.list_objects_v2(Bucket=S3_BUCKET)
        return [obj["Key"] for obj in resp.get("Contents", [])]
    except ClientError as e:
        st.error(f"Could not list S3 objects: {e.response['Error']['Message']}")
        return []

def upload_to_s3(uploaded_file):
    try:
        s3.put_object(
            Bucket = S3_BUCKET,
            Key    = uploaded_file.name,
            Body   = uploaded_file.getbuffer()
        )
        return True
    except ClientError as e:
        st.error(f"Upload failed: {e.response['Error']['Message']}")
        return False

def delete_from_s3(key):
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        st.error(f"Delete failed: {e.response['Error']['Message']}")
        return False

def get_s3_image(key):
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return Image.open(io.BytesIO(obj["Body"].read()))
    except ClientError as e:
        st.error(f"Could not load image '{key}': {e.response['Error']['Message']}")
        return None

# ---------------------------------------------------
# Strategy Tracker App
# ---------------------------------------------------
def strategy_mode():
    LOG_PATH = "trade_log.csv"

    st.title("📈 Strategy Tracker")
    st.markdown("---")

    # --- Strategy Summary & Risk Management ---
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
            st.success("Market behavior saved!")

    st.markdown("---")

    # --- Load or initialize local trade log CSV ---
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
    else:
        df = pd.DataFrame(columns=["Date","Asset","Strategy","RR Ratio","Outcome","Notes"])

    # --- Trade Entry Form ---
    with st.form("trade_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            asset   = st.text_input("Asset Symbol", placeholder="e.g. BTC")
            strat   = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
            outcome = st.selectbox("Trade Outcome", ["Win","Loss","Break-even"])
        with right:
            rr    = st.text_input("RR Ratio", "1:1")
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

    # --- Trade History Display ---
    st.markdown("### 📊 Trade History")
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No trades logged yet.")

    # --- Example Trades Gallery (S3) ---
    st.markdown("---")
    with st.expander("📁 Example Trades Gallery", expanded=False):
        uploaded = st.file_uploader(
            "Upload Example Trade Images (to S3)",
            type=["png","jpg","jpeg"],
            accept_multiple_files=True,
            key="example_upload"
        )
        if uploaded:
            for img in uploaded:
                if upload_to_s3(img):
                    st.success(f"Uploaded `{img.name}` to S3")

        keys = list_s3_keys()
        if keys:
            num_cols = 3
            rows = (len(keys) + num_cols - 1) // num_cols
            for r in range(rows):
                cols = st.columns(num_cols)
                for i, col in enumerate(cols):
                    idx = r * num_cols + i
                    if idx < len(keys):
                        key = keys[idx]
                        img = get_s3_image(key)
                        if img:
                            with col:
                                st.image(img, width=200, caption=key)
                                with st.expander("View Larger", expanded=False):
                                    st.image(img, use_container_width=True)
                                    if st.button("Delete from S3", key=f"del_{idx}"):
                                        if delete_from_s3(key):
                                            st.success(f"Deleted `{key}` from S3")
        else:
            st.info("No example trades in S3 yet.")

# Run the app
strategy_mode()
