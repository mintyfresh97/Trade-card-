# init_db.py
import sqlite3

# The SQLite database file that will be created in the repo root.
DB_FILE = "levels_data.db"

# Connect to (or create) the SQLite database.
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Create the asset_levels table if it doesn't already exist.
cursor.execute("""
CREATE TABLE IF NOT EXISTS asset_levels (
    asset TEXT PRIMARY KEY,
    support TEXT,
    demand TEXT,
    resistance TEXT,
    supply TEXT,
    choch TEXT,
    chart_path TEXT
)
""")
conn.commit()

# Define your assets (from your coinpaprika_ids dictionary)
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

# Seed the table with default values (empty strings) for each asset.
# This uses INSERT OR IGNORE so if the asset is already in the table it won't be reinserted.
for asset in coinpaprika_ids.keys():
    cursor.execute("""
        INSERT OR IGNORE INTO asset_levels (asset, support, demand, resistance, supply, choch, chart_path)
        VALUES (?, '', '', '', '', '', '')
    """, (asset,))
conn.commit()

print("Database initialized and seeded successfully.")

conn.close()
