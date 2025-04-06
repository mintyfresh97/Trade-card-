import streamlit as st
import requests
import os
import json
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import pandas as pd
import numpy as np
import random
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Set page configuration as the very first Streamlit command.
st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")

# ---------------------------
# Real-Time Data Updates (Auto Refresh)
# ---------------------------
st_autorefresh(interval=30000, limit=100, key="autorefresh")

# ---------------------------
# Persistence Functions for Key Levels
# ---------------------------
PERSISTENCE_FILE = "levels_data.json"

def load_levels_from_file():
    if os.path.exists(PERSISTENCE_FILE):
        try:
            with open(PERSISTENCE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading levels file: {e}")
    return {}

def save_levels_to_file(levels_data):
    try:
        with open(PERSISTENCE_FILE, "w") as f:
            json.dump(levels_data, f)
    except Exception as e:
        st.error(f"Error saving levels file: {e}")

# Initialize session state for key levels (load persistent data if available)
if "levels_data" not in st.session_state:
    st.session_state["levels_data"] = load_levels_from_file()

# ---------------------------
# Data & API Functions
# ---------------------------
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

# ---------------------------
# Key Levels & Volume Strength Functions
# ---------------------------
def get_levels_for_asset(asset_name):
    if asset_name not in st.session_state["levels_data"]:
        st.session_state["levels_data"][asset_name] = {
            "support": "",
            "demand": "",
            "resistance": "",
            "supply": "",
            "choch": "",
            "chart_path": ""  # For storing chart image filename
        }
    return st.session_state["levels_data"][asset_name]

def save_levels_for_asset(asset_name, levels):
    st.session_state["levels_data"][asset_name] = levels
    save_levels_to_file(st.session_state["levels_data"])

def calculate_volume_strength(vol_df, ma_period=14):
    vol_df = vol_df.copy()
    vol_df["VolumeMA"] = vol_df["Volume"].rolling(window=ma_period).mean()
    if len(vol_df) < ma_period:
        return 0.0
    last_vol = vol_df["Volume"].iloc[-1]
    last_ma = vol_df["VolumeMA"].iloc[-1]
    if pd.isna(last_ma):
        return 0.0
    ratio = last_vol / last_ma
    if ratio < 0.5:
        return 0.0
    elif ratio > 2.0:
        return 10.0
    else:
        return (ratio - 0.5) / (2.0 - 0.5) * 10.0

# ---------------------------
# Layout and Main App
# ---------------------------
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Create two columns:
# LEFT COLUMN ("Orange Box"): Asset selection, market data, key levels, volume strength, and uploaded chart.
# RIGHT COLUMN: Edit key levels, styled Plotly chart, and trade card preview.
col1, col2 = st.columns([1, 2])

# LEFT COLUMN:
with col1:
    # Asset selection
    display_names = list(coinpaprika_ids.keys())
    asset_display = st.selectbox("Select Asset", display_names)
    asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()
    icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")
    
    # Market data & sentiment
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
    
    sentiment, sentiment_score = get_social_sentiment(asset_display)
    st.markdown(f"**Social Sentiment:** {sentiment} (Score: {sentiment_score})")
    
    # Display Key Levels & Volume Strength
    st.markdown("### Key Levels & Volume Strength")
    levels = get_levels_for_asset(asset_display)
    st.markdown(f"**Support:** {levels['support'] or 'N/A'}")
    st.markdown(f"**Demand:** {levels['demand'] or 'N/A'}")
    st.markdown(f"**Resistance:** {levels['resistance'] or 'N/A'}")
    st.markdown(f"**Supply:** {levels['supply'] or 'N/A'}")
    st.markdown(f"**CHoCH:** {levels['choch'] or 'N/A'}")
    
    # Display uploaded chart (if exists) from the charts folder.
    CHARTS_DIR = "charts"
    chart_filename = levels.get("chart_path")
    if chart_filename:
        chart_path = os.path.join(CHARTS_DIR, chart_filename)
        if os.path.exists(chart_path):
            st.image(chart_path, caption=f"{asset_symbol} Chart Analysis", use_column_width=True)
        else:
            st.info("Chart file not found. Please upload again.")
    else:
        st.info("No chart uploaded yet for this asset.")
    
    # Dummy volume data (replace with actual volume data if available)
    vol_df = pd.DataFrame({
        "Date": pd.date_range("2023-01-01", periods=30, freq="D"),
        "Volume": np.random.randint(1000, 5000, 30)
    })
    vol_df.sort_values("Date", inplace=True)
    vol_score = calculate_volume_strength(vol_df)
    st.markdown(f"**Volume Strength Score:** {vol_score:.1f} / 10")
    
    # 3-Day % Change Heatmap (neutral color scheme)
    st.markdown("### 3-Day % Change")
    df_3d = pd.DataFrame({
        "Symbol": ["BTC", "ETH", "ADA", "FARTCOIN", "SUI", "LINK", "ONDO", "CRV"],
        "Change (%)": [1.2, -0.8, 2.5, 4.2, 3.3, -1.0, -0.6, 0.9]
    })
    fig = px.bar(
        df_3d,
        x="Symbol",
        y="Change (%)",
        color="Change (%)",
        color_continuous_scale=[(0, "red"), (0.5, "gray"), (1, "green")],
        range_color=(-5, 5),
        title="3-Day % Change Heatmap"
    )
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="black",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        title_x=0.5
    )
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# RIGHT COLUMN:
with col2:
    st.subheader("Edit Key Levels / Upload Chart")
    with st.expander("Modify Levels", expanded=False):
        new_support = st.text_input("Support", value=levels["support"])
        new_demand = st.text_input("Demand", value=levels["demand"])
        new_resistance = st.text_input("Resistance", value=levels["resistance"])
        new_supply = st.text_input("Supply", value=levels["supply"])
        new_choch = st.text_input("CHoCH", value=levels["choch"])
        st.markdown("---")
        st.markdown("#### Upload Chart Analysis")
        uploaded_file = st.file_uploader("Upload your chart image (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Save Levels & Chart", key="save_levels"):
            updated_levels = {
                "support": new_support,
                "demand": new_demand,
                "resistance": new_resistance,
                "supply": new_supply,
                "choch": new_choch,
                "chart_path": levels.get("chart_path", "")  # default to current chart
            }
            if uploaded_file is not None:
                file_ext = os.path.splitext(uploaded_file.name)[1]
                # Use asset symbol as the base name (or add a timestamp for versioning)
                filename = f"{asset_symbol}{file_ext}"
                file_path = os.path.join(CHARTS_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                updated_levels["chart_path"] = filename
            save_levels_for_asset(asset_display, updated_levels)
            st.success("Levels and chart updated!")
            st.experimental_rerun()
    
    # Styled Plotly Chart can remain here (or add additional charts)
    st.subheader("Additional Charts")
    # (You can add more charts here if needed.)
    
    # Collapsible Trade Card Preview
    with st.expander("Show Trade Card Preview", expanded=False):
        st.subheader("Trade Card")
        st.markdown(f"Asset: {asset_symbol}")
        if price is not None:
            st.markdown(f"Live Price: ${price}")
            st.markdown(f"24h Change: {daily_change}%")
        else:
            st.markdown("Live Price: N/A")
        
        entry_price_default = price if price is not None else 82000.0
        entry = st.number_input("Entry Price", value=entry_price_default, format="%.2f")
        position = st.number_input("Position Size (£)", value=500.0)
        leverage = st.number_input("Leverage", value=20)
        stop_loss = st.number_input("Stop Loss", value=round(entry * 0.99, 2), format="%.2f")
        take_profit = st.number_input("Take Profit", value=round(entry * 1.02, 2), format="%.2f")
        timeframes = ["1m", "5m", "15m", "1h", "4h", "Daily"]
        entry_tf = st.selectbox("Entry Timeframe", options=timeframes, index=1)
        analysis_tf = st.selectbox("Analysis Timeframe", options=timeframes, index=2)
        
        st.markdown("### Trade Notes")
        strategy = st.text_input("Trade Strategy", placeholder="e.g. EMA Bounce, Breakout Rejection")
        news = st.text_input("News Catalyst", placeholder="e.g. FOMC, ETF Approval, CPI Report")
        execution = st.text_input("Execution Plan", placeholder="e.g. Enter on candle close, SL below wick")
        psychology = st.text_input("Psychology Reminder", placeholder="e.g. Stick to plan, avoid revenge trading")
        tags = st.multiselect("Tags", options=["Scalp", "Swing", "Long", "Short", "1H", "4H", "Daily", "Breakout", "Rejection"])
        
        trade_date = datetime.now().strftime("%Y-%m-%d")
        total_exposure = position * leverage
        risk = abs(entry - stop_loss) * total_exposure / entry
        reward = abs(take_profit - entry) * total_exposure / entry
        breakeven = round((entry + stop_loss) / 2, 2)
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0
        
        st.markdown(f"Position: £{position}")
        st.markdown(f"Leverage: {leverage}x")
        st.markdown(f"Entry: {entry}")
        st.markdown(f"Stop Loss: {stop_loss}")
        st.markdown(f"Take Profit: {take_profit}")
        st.markdown(f"Risk: £{risk:.2f}")
        st.markdown(f"Reward: £{reward:.2f}")
        st.markdown(f"RR Ratio: {rr_ratio}:1")
        st.markdown(f"Breakeven: {breakeven}")
        st.markdown(f"Date: {trade_date}")
        st.markdown(f"Entry TF: {entry_tf}")
        st.markdown(f"Analysis TF: {analysis_tf}")
        if strategy:
            st.markdown(f"**Strategy:** {strategy}")
        if news:
            st.markdown(f"**News Catalyst:** {news}")
        if execution:
            st.markdown(f"**Execution Plan:** {execution}")
        if psychology:
            st.markdown(f"**Psychology Reminder:** {psychology}")
        if tags:
            st.markdown(f"**Tags:** {', '.join(tags)}")
        
        if st.button("Download Trade Card"):
            lines = []
            lines.append("=== Trade Info ===")
            lines.append(f"Asset: {asset_symbol}")
            lines.append(f"Date: {trade_date}")
            lines.append(f"Live Price: ${price}")
            lines.append("")
            lines.append("=== Entry Setup ===")
            lines.append(f"Entry: {entry}")
            lines.append(f"Stop: {stop_loss}")
            lines.append(f"Target: {take_profit}")
            lines.append(f"Risk: £{risk:.2f}")
            lines.append(f"Reward: £{reward:.2f}")
            lines.append(f"RR Ratio: {rr_ratio}:1")
            lines.append(f"Breakeven: {breakeven}")
            lines.append("")
            lines.append("=== Timeframes ===")
            lines.append(f"Entry TF: {entry_tf}")
            lines.append(f"Analysis TF: {analysis_tf}")
            lines.append("")
            lines.append("=== Notes ===")
            if strategy:
                lines.extend(textwrap.wrap(f"Strategy: {strategy}", width=50))
            if news:
                lines.extend(textwrap.wrap(f"News: {news}", width=50))
            if execution:
                lines.extend(textwrap.wrap(f"Execution Plan: {execution}", width=50))
            if psychology:
                lines.extend(textwrap.wrap(f"Mindset: {psychology}", width=50))
            if tags:
                lines.extend(textwrap.wrap(f"Tags: {', '.join(tags)}", width=50))
            
            line_height = 34
            image_height = 140 + line_height * len(lines)
            img = Image.new("RGB", (700, image_height), color=(20, 20, 20))
            draw = ImageDraw.Draw(img)
            try:
                heading_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
                body_font = ImageFont.truetype("DejaVuSans.ttf", 18)
            except:
                heading_font = body_font = ImageFont.load_default()
            asset_name = asset_display.split("(")[0].strip()
            title = f"{asset_name} Risk Setup"
            bbox = heading_font.getbbox(title)
            title_w = bbox[2] - bbox[0]
            draw.text(((700 - title_w) // 2, 30), title, font=heading_font, fill=(255, 255, 255))
            logo_path = f"assets/{icon_map.get(asset_symbol, '')}"
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path).convert("RGBA").resize((64, 64))
                    img.paste(logo, (620, 20), logo)
                except Exception as e:
                    st.warning(f"Could not load logo: {e}")
            y = 100
            for line in lines:
                font = heading_font if line.startswith("===") else body_font
                color = (255, 165, 0) if line.startswith("===") else (255, 255, 255)
                text_line = line.replace("===", "").strip() if line.startswith("===") else line
                draw.text((30, y), text_line, fill=color, font=font)
                y += line_height
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name=f"trade_card_{asset_symbol}_{trade_date}.png",
                mime="image/png"
            )

# ---------------------------
# Trade Log & Advanced Analytics
# ---------------------------
st.markdown("---")
st.header("Strategy Tracker")
track_col1, track_col2 = st.columns(2)
with track_col1:
    strategy_used = st.text_input("Strategy Name", placeholder="e.g. EMA Bounce")
    trade_result = st.selectbox("Trade Outcome", ["Win", "Loss", "Break-even"])
with track_col2:
    rr_logged = st.text_input("RR Ratio", value="1:1")
    notes = st.text_area("Additional Notes")

if st.button("Save Trade to Log"):
    trade_data = {
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Asset": [asset_symbol],
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

if os.path.exists("trade_log.csv"):
    st.markdown("### Trade History")
    df_hist = pd.read_csv("trade_log.csv")
    st.dataframe(df_hist)
    st.sidebar.header("Filter Trade History")
    date_filter = st.sidebar.date_input("Select Date Range", [])
    if date_filter and len(date_filter) == 2:
        start_date, end_date = date_filter
        df_hist['Date'] = pd.to_datetime(df_hist['Date'], errors='coerce')
        df_filtered = df_hist[(df_hist['Date'] >= pd.to_datetime(start_date)) & (df_hist['Date'] <= pd.to_datetime(end_date))]
        st.write("Filtered Trade History:")
        st.dataframe(df_filtered)
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

if os.path.exists("trade_log.csv"):
    st.markdown("### Trade Analytics")
    df_hist = pd.read_csv("trade_log.csv")
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
