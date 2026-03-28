import yfscreen as yfs
import pandas as pd
import os
import time

# 1. Setup Folders
os.makedirs('data/tables', exist_ok=True)

def collect_2000_rows():
    print("🚀 Starting Full Market Scrape (2000 Rows)...")
    
    # Define filters (e.g., US stocks only)
    # You can change 'us' to 'gb' for UK, 'ca' for Canada, etc.
    filters = [["eq", ["region", "us"]]]
    
    # Build the protocol
    query = yfs.create_query(filters)
    
    all_rows = []
    total_to_fetch = 2000
    batch_size = 250  # Max rows per request
    
    for offset in range(0, total_to_fetch, batch_size):
        print(f"📥 Fetching Batch: {offset} to {offset + batch_size}...")
        
        try:
            # Create a unique payload for each page (offset)
            payload = yfs.create_payload(
                sec_type="equity", 
                query=query, 
                size=batch_size, 
                offset=offset
            )
            
            # Request data
            data = yfs.get_data(payload)
            
            if data is not None and not data.empty:
                all_rows.append(data)
                print(f"✅ Successfully added {len(data)} rows.")
            else:
                print("⚠️ No more data returned or reached the limit.")
                break
            
            # CRITICAL: Sleep to avoid being flagged on your live server
            print("💤 Cooling down for 3 seconds...")
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error at offset {offset}: {e}")
            break

    # 2. Combine and Clean
    if all_rows:
        final_table = pd.concat(all_rows, ignore_index=True)
        
        # Save to your stock folder
        output_path = "data/tables/full_market_2000.csv"
        final_table.to_csv(output_path, index=False)
        
        print("\n" + "="*30)
        print(f"🎉 FINISHED! Total Rows Collected: {len(final_table)}")
        print(f"📂 Saved to: {output_path}")
        print("="*30)
    else:
        print("❌ Failed to collect any data.")

if __name__ == "__main__":
    collect_2000_rows()