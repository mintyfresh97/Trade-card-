
import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

coingecko_ids = {
    'Bitcoin (BTC)': 'bitcoin',
    'Ethereum (ETH)': 'ethereum',
    'XRP (XRP)': 'ripple',
    'Solana (SOL)': 'solana',
    'Cardano (ADA)': 'cardano',
    'Chainlink (LINK)': 'chainlink',
    'Curve (CRV)': 'curve-dao-token',
    'Convex (CVX)': 'convex-finance',
    'Sui (SUI)': 'sui',
    'Fartcoin (FARTCOIN)': 'fartcoin',
    'Ondo (ONDO)': 'ondo-finance'
}

icon_map = {
    "BTC": "bitcoin-btc-logo.png", "ETH": "ethereum-eth-logo.png",
    "XRP": "xrp-xrp-logo.png", "ADA": "cardano-ada-logo.png",
    "SOL": "solana-sol-logo.png", "LINK": "chainlink-link-logo.png",
    "ONDO": "ondo-finance-ondo-logo.png", "CRV": "curve-dao-token-crv-logo.png",
    "CVX": "convex-finance-cvx-logo.png", "SUI": "sui-sui-logo.png",
    "FARTCOIN": "fartcoin-logo.png"
}

def get_crypto_price_from_coingecko(name):
    try:
        coin_id = coingecko_ids.get(name)
        if not coin_id:
            raise ValueError("Unknown CoinGecko ID")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return round(data[coin_id]['usd'], 2)
    except Exception as e:
        st.error(f"CoinGecko API Error for {name}: {e}")
        return None

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    display_names = list(coingecko_ids.keys())
    asset_display = st.selectbox("Select Asset", display_names)
    asset_symbol = asset_display.split("(")[-1].replace(")", "").strip()
    icon_path = f"assets/{icon_map.get(asset_symbol, '')}"
    if os.path.exists(icon_path):
        st.image(icon_path, width=32)
    else:
        st.warning("Icon not found")

position = st.number_input("Position Size (Â£)", value=500.0)
leverage = st.number_input("Leverage", value=20)

try:
    live_price = get_crypto_price_from_coingecko(asset_display)
    if live_price:
        entry = st.number_input("Entry Price", value=live_price, format="%.2f")
    else:
        entry = st.number_input("Entry Price", value=82000.0, format="%.2f")
except:
    entry = st.number_input("Entry Price", value=82000.0, format="%.2f")
    live_price = "Not available"

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

with col2:
    st.subheader("Trade Card")
    st.markdown(f"Asset: {asset_symbol}")
    st.markdown(f"Live Price: {live_price if live_price else 'N/A'}")
    st.markdown(f"Position: Â£{position}")
    st.markdown(f"Leverage: {leverage}x")
    st.markdown(f"Entry: {entry}")
    st.markdown(f"Stop Loss: {stop_loss}")
    st.markdown(f"Take Profit: {take_profit}")
    st.markdown(f"Risk: Â£{risk:.2f}")
    st.markdown(f"Reward: Â£{reward:.2f}")
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

with st.expander("Export Trade Card", expanded=False):
    if st.button("Download PNG"):
            lines = []
            lines.append("=== Trade Info ===")
            lines.append(f"Asset: {asset_symbol}")
            lines.append(f"Date: {trade_date}")
            lines.append(f"Live Price: {live_price}")
        
            lines.append("")
            lines.append("=== Entry Setup ===")
            lines.append(f"Entry: {entry}")
            lines.append(f"Stop: {stop_loss}")
            lines.append(f"Target: {take_profit}")
            lines.append(f"Risk: Â£{risk:.2f}")
            lines.append(f"Reward: Â£{reward:.2f}")
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
        
            # Centered heading
            # Centered heading
            asset_name = asset_display.split("(")[0].strip()
            title = f"{asset_name} Risk Setup"
            bbox = heading_font.getbbox(title)
            title_w = bbox[2] - bbox[0]
            title_h = bbox[3] - bbox[1]
            draw.text(((700 - title_w) // 2, 30), title, font=heading_font, fill=(255, 255, 255))
        
            # Logo
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
                text = line.replace("===", "").strip() if line.startswith("===") else line
                draw.text((30, y), text, fill=color, font=font)
                y += line_height
        
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="Download Image",
                data=buf.getvalue(),
                file_name=f"trade_card_{asset_symbol}_{trade_date}.png",
                mime="image/png"
            )
