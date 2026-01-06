import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Database Connection Configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construct the connection string
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def load_data():
    """Reads CSV, cleans headers, and loads into PostgreSQL"""
    
    csv_path = os.path.join("data", "raw", "orders.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    print("Loading data from CSV...")
    df = pd.read_csv(csv_path)

    # basic check
    print(f"Data Loaded. Shape: {df.shape}")

    # 3. Clean Column Names
    # SQL prefers snake_case (e.g., 'Order Date' -> 'order_date')
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Specific fix: 'profit' often comes as string with '$' in this dataset, let's ensure it is numeric
    # (Depending on the specific CSV version, sometimes it is clean, but safe to check)
    # df['profit'] = df['profit'].replace('[$,]', '', regex=True).astype(float) 

    print("Columns cleaned:", list(df.columns))

    # 4. Load to Database
    print("Uploading to PostgreSQL...")
    engine = create_engine(connection_string)
    
    try:
        df.to_sql(name='retail_orders', con=engine, if_exists='replace', index=False)
        print("Success! Data loaded into table 'retail_orders'.")
    except Exception as e:
        print(f"Error loading data to DB: {e}")

if __name__ == "__main__":
    load_data()