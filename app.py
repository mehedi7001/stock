import streamlit as st
import pandas as pd
import yfscreen as yfs
import time
import os
from sqlalchemy import create_engine

# --- 1. Database Configuration ---
try:
    db_creds = st.secrets["connections"]["postgresql"]
    DB_URL = f"postgresql://{db_creds['username']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
    engine = create_engine(DB_URL)
except Exception as e:
    st.error(f"❌ Database Setup Error: {e}")
    st.stop()

# --- 2. Page Setup ---
st.set_page_config(page_title="Postgres Stock Hub", layout="wide")
st.title("🐘 Stock Hub: Scrape → CSV → Postgres")

# --- 3. Sidebar: Scraper Logic ---
rows_to_fetch = st.sidebar.slider("Number of Rows", 250, 2000, 500, step=250)

if st.sidebar.button("🚀 Run Scrape & Sync"):
    with st.status("Gathering Market Data...", expanded=True) as status:
        filters = [["eq", ["region", "us"]]]
        query = yfs.create_query(filters)
        all_rows = []
        
        # --- Stage 1: Scrape to RAM ---
        for offset in range(0, rows_to_fetch, 250):
            st.write(f"📥 Downloading batch {offset}...")
            payload = yfs.create_payload("equity", query, size=250, offset=offset)
            batch = yfs.get_data(payload)
            if batch is not None:
                all_rows.append(batch)
            time.sleep(2) 
        
        if all_rows:
            final_df = pd.concat(all_rows, ignore_index=True)
            
            # --- Stage 2: Save to CSV (The Safety Middleman) ---
            # Standardize Company Name
            if 'longName' in final_df.columns:
                final_df['company_name'] = final_df['longName'].fillna(final_df['symbol'])
            else:
                final_df['company_name'] = final_df.get('shortName', final_df['symbol'])
            
            # Clean names for SQL
            final_df.columns = [c.replace(' ', '_').lower() for c in final_df.columns]
            
            # Write to CSV
            final_df.to_csv("latest_market_data.csv", index=False)
            st.write("✅ CSV Backup Created: `latest_market_data.csv`")

            # --- Stage 3: Bulk Insert to Postgres ---
            st.write("🚀 Syncing CSV data to PostgreSQL...")
            final_df.to_sql(
                'market_data', 
                engine, 
                if_exists='replace', 
                index=False, 
                chunksize=500, 
                method='multi'
            )
            
            status.update(label="✅ Success! Data is in CSV and Postgres.", state="complete")
            st.rerun()

# --- 4. Main Dashboard ---
st.subheader("Live Database Table")

try:
    df = pd.read_sql("SELECT * FROM market_data", engine)
    
    # Check if we have a backup file available
    if os.path.exists("latest_market_data.csv"):
        st.sidebar.success("📂 Local CSV Backup Found")
        if st.sidebar.button("♻️ Restore DB from CSV"):
            backup_df = pd.read_csv("latest_market_data.csv")
            backup_df.to_sql('market_data', engine, if_exists='replace', index=False, chunksize=500, method='multi')
            st.rerun()

    st.dataframe(df, use_container_width=True, height=600)

except Exception:
    st.info("Database is empty. Use the sidebar to start your first scrape!")