# import streamlit as st
# import pandas as pd
# import os
# import yfscreen as yfs
# import time
# import yfinance as yf

# # Page Configuration
# st.set_page_config(page_title="Stock Screener Pro", layout="wide")
# st.title("📈 2026 Live Market Screener")

# DATA_PATH = "data/tables/full_market_2000.csv"
# os.makedirs('data/tables', exist_ok=True)

# # --- Helper to Fix Names ---
# def clean_and_verify_data(df):
#     """Ensures names and prices are mapped correctly."""
#     # Yahoo columns often change; we standardize them here
#     rename_map = {
#         'shortName': 'Name',
#         'longName': 'Name',
#         'regularMarketPrice': 'Price',
#         'symbol': 'Ticker',
#         'marketCap': 'Market Cap'
#     }
#     df = df.rename(columns=rename_map)
    
#     # If 'Name' is still missing or NaN, use Ticker as the Name
#     if 'Name' not in df.columns:
#         df['Name'] = df['Ticker']
#     df['Name'] = df['Name'].fillna(df['Ticker'])
    
#     return df

# # --- Sidebar Controls ---
# st.sidebar.header("Scraper Controls")
# rows_to_fetch = st.sidebar.slider("Rows to fetch", 250, 2000, 500, step=250)

# if st.sidebar.button("🚀 Run Live Scrape"):
#     with st.status("Fetching data from Yahoo...", expanded=True) as status:
#         filters = [["eq", ["region", "us"]]]
#         query = yfs.create_query(filters)
#         all_rows = []
        
#         for offset in range(0, rows_to_fetch, 250):
#             st.write(f"Downloading batch starting at {offset}...")
#             payload = yfs.create_payload("equity", query, size=250, offset=offset)
#             batch = yfs.get_data(payload)
#             if batch is not None:
#                 all_rows.append(batch)
#             time.sleep(2)
        
#         if all_rows:
#             final_df = pd.concat(all_rows, ignore_index=True)
#             # Apply our cleaning function
#             final_df = clean_and_verify_data(final_df)
#             final_df.to_csv(DATA_PATH, index=False)
#             status.update(label="✅ Scrape Complete!", state="complete")
#             st.rerun()
#         else:
#             status.update(label="❌ Scrape Failed", state="error")

# # --- Main Dashboard ---
# if os.path.exists(DATA_PATH):
#     df = pd.read_csv(DATA_PATH)
    
#     # Simple formatting for the UI
#     st.subheader(f"Displaying {len(df)} Companies")
    
#     # Search functionality
#     search = st.text_input("🔍 Search by Ticker or Name")
#     if search:
#         df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

#     # Display the table
#     # We filter to show the most important columns first
#     important_cols = ['Ticker', 'Name', 'Price', 'Market Cap']
#     existing_important = [c for c in important_cols if c in df.columns]
#     other_cols = [c for c in df.columns if c not in existing_important]
    
#     st.dataframe(df[existing_important + other_cols], use_container_width=True, height=600)
# else:
#     st.info("No data found. Click 'Run Live Scrape' to fetch 2026 market data.")
