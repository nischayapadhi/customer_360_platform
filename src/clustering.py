import pandas as pd
import os
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def run_clustering():
    print("--- Starting Clustering Pipeline ---")
    
    # 2. Connect to Database
    engine = create_engine(connection_string)
    
    # 3. Read the SQL Query
    # IMPORTANT: Ensure this filename matches where you saved your SQL code
    # You mentioned earlier you might have put it in schema.sql, so check the name!
    sql_file_path = os.path.join("sql", "rfm_analysis.sql") 
    
    # Fallback: if schema.sql doesn't exist, try rfm_analysis.sql
    if not os.path.exists(sql_file_path):
         sql_file_path = os.path.join("sql", "rfm_analysis.sql")
         
    print(f"Reading SQL from: {sql_file_path}")

    with open(sql_file_path, "r") as file:
        query = file.read()
    
    # --- THE FIX IS HERE ---
    # We replace single '%' with double '%%' so Python doesn't treat it as a variable placeholder
    query = query.replace('%', '%%') 
    # -----------------------

    print("Executing RFM Analysis SQL...")
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"SQL Execution Failed: {e}")
        return

    print(f"Data Loaded: {df.shape[0]} customers found.")
    
    if df.empty:
        print("Error: No data returned from SQL.")
        return

    # 4. Preprocessing
    features = ['recency_days', 'frequency_orders', 'monetary_profit']
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 5. K-Means Clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster_id'] = kmeans.fit_predict(X_scaled)
    
    print("Clustering Complete. Sample:")
    print(df.head())
    
    # 6. Save Results to Database
    output_table = 'customer_segments'
    print(f"Saving results to table '{output_table}'...")
    df.to_sql(output_table, engine, if_exists='replace', index=False)
    print("Success! Segmentation saved to Database.")

    # Save a copy for the web dashboard to use without DB
    df.to_csv("data/processed/customer_segments.csv", index=False)
    print("Portable CSV created in data/ folder.")

if __name__ == "__main__":
    run_clustering()

