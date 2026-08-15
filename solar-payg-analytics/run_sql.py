import os
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(BASE_DIR, 'sql')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Connect to postgres
print("Connecting to PostgreSQL...")
try:
    engine = create_engine("postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres")
    
    with engine.connect() as conn:
        print("Connected successfully!")
        
        # 1. Run schema.sql
        print("Running schema.sql to create tables...")
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        with open(os.path.join(SQL_DIR, 'schema.sql'), 'r') as f:
            schema_sql = f.read()
        
        # Split by statements and execute
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
        print("Schema created successfully!")

        # 2. Load data from processed CSVs
        print("Loading data into tables (this may take a minute)...")
        tables = [
            ('products', 'products_clean.csv'),
            ('customers', 'customers_clean.csv'),
            ('loans', 'loans_clean.csv'),
            ('payments', 'payments_clean.csv'),
            ('distribution', 'distribution_clean.csv'),
            ('monthly_customer_metrics', 'monthly_metrics_clean.csv')
        ]
        
        for table_name, csv_file in tables:
            print(f"Loading {table_name}...")
            df = pd.read_csv(os.path.join(DATA_DIR, csv_file))
            # Some dates might need parsing or letting to_sql handle it
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Loaded {len(df)} rows into {table_name}.")

        # 3. Run data quality checks as a test
        print("\nRunning Data Quality Checks:")
        with open(os.path.join(SQL_DIR, 'data_quality.sql'), 'r') as f:
            dq_sql = f.read()
            
        queries = dq_sql.split(';')
        for query in queries:
            if query.strip():
                # Extract a short name for the query from comments
                lines = query.strip().split('\n')
                name = lines[0] if lines[0].startswith('--') else "Query"
                print(f"\n{name}")
                try:
                    result = conn.execute(text(query))
                    for row in result.fetchall():
                        print(row)
                except Exception as e:
                    print(f"Error running query: {e}")

    print("\nDatabase setup and loading complete!")

except Exception as e:
    print(f"Database Error: {e}")
    print("\nIf authentication failed, you may need to provide a password. Update the connection string in this script.")
