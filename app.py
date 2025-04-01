import streamlit as st
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import os

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide") st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

Asset data

assets = { "BTC": {"name": "Bitcoin", "logo": "bitcoin-btc-logo.png"}, "ETH": {"name": "Ethereum", "logo": "ethereum-eth-logo.png"}, "XRP": {"name": "XRP", "logo": "xrp-xrp-logo.png"}, "ADA": {"name": "Cardano", "logo": "cardano-ada-logo.png"}, "SOL": {"name": "Solana", "logo": "solana-sol-logo.png"}, "LINK": {"name": "Chainlink", "logo": "chainlink-link-logo.png"}, "CRV": {"name": "Curve", "logo": "curve-dao-token-crv-logo.png"}, "CVX": {"name": "Convex", "logo": "convex-finance-cvx-logo.png"}, "SUI": {"name": "SUI", "logo": "sui-sui-logo.png"}, "ONDO": {"name": "Ondo", "logo": "ondo-finance-ondo-logo.png"} }

asset = st.selectbox("Select Asset", options=assets.keys()) icon_path = os.path.join("assets", assets[asset]["logo"])

Display asset logo

if os.path.exists(icon_path): st.image(icon_path, width=32) else: st.warning("Icon not found")

Fetch live price

live_price = None try: url = f"https://api.coingecko.com/api/v3/simple/price?ids={assets[asset]['name'].lower()}&vs_currencies=gbp" response = requests.get(url) if response.status_code == 200: live_price = response.json().get(assets[asset]['name'].lower(), {}).get("gbp") except: pass

Trade input

st.subheader("Trade Setup") position = st.number_input("Position Size (£)", value=500) leverage = st.number_input("Leverage", value=20) entry = st.number_input("Entry Price", value=live_price if live_price else 0.0, format="%.5f") stop_loss = st.number_input("Stop Loss", value=0.0, format="%.5f") take_profit = st.number_input("Take Profit", value=0.0, format="%.5f") date = st.date_input("Trade Date", value=datetime.now().date())

Calculations

try: total_exposure = position * leverage risk = abs(entry - stop_loss) * total_exposure / entry reward = abs(take_profit - entry) * total_exposure / entry breakeven = round((entry + stop_loss) / 2, 5) rr_ratio = round(reward / risk, 2) if risk != 0 else 0

st.subheader("Results")
st.write(f"Live Price: {'£{:.2f}'.format(live_price) if live_price else 'Not available'}")
st.write(f"Total Exposure: £{total_exposure:.2f}")
st.write(f"Risk: £{risk:.2f}")
st.write(f"Reward: £{reward:.2f}")
st.write(f"RR Ratio: {rr_ratio}:1")
st.write(f"Breakeven Price: £{breakeven}")

# Create downloadable trade card
if st.button("Download Trade Card"):
    card_width, card_height = 800, 400
    card = Image.new("RGB", (card_width, card_height), color=(20, 20, 20))
    draw = ImageDraw.Draw(card)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
        heading_font = ImageFont.truetype("arial.ttf", 26)
    except:
        font = ImageFont.load_default()
        heading_font = font

    draw.text((30, 20), "PnL Trade Card", fill=(255, 255, 255), font=heading_font)

    y = 80
    spacing = 30
    details = [
        f"Date: {date}",
        f"Asset: {asset}",
        f"Live Price: £{live_price if live_price else 'N/A'}",
        f"Position Size: £{position}",
        f"Leverage: {leverage}x",
        f"Entry: £{entry}",
        f"Stop Loss: £{stop_loss}",
        f"Take Profit: £{take_profit}",
        f"Risk: £{risk:.2f}",
        f"Reward: £{reward:.2f}",
        f"RR Ratio: {rr_ratio}:1"
    ]

    for line in details:
        draw.text((30, y), line, fill=(255, 255, 255), font=font)
        y += spacing

    buffer = io.BytesIO()
    card.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="Download Card",
        data=buffer,
        file_name="trade_card.png",
        mime="image/png"
    )

except Exception as e: st.error(f"Error calculating trade: {e}")

