"""
run_analytics.py - Execute all SQL analytical queries against the loaded PostgreSQL database
"""

import os
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(BASE_DIR, 'sql')

engine = create_engine("postgresql://postgres:@bhinav123@localhost:5432/postgres")

# SQL files to run (in order)
sql_files = [
    'customer_analysis.sql',
    'credit_risk.sql',
    'churn_analysis.sql',
    'distribution_analysis.sql',
]

with engine.connect() as conn:
    for sql_file in sql_files:
        filepath = os.path.join(SQL_DIR, sql_file)
        print("\n" + "=" * 70)
        print(f"  RUNNING: {sql_file}")
        print("=" * 70)
        
        with open(filepath, 'r') as f:
            sql_content = f.read()
        
        queries = sql_content.split(';')
        for query in queries:
            stripped = query.strip()
            if not stripped:
                continue
            
            # Extract the comment header as a label
            lines = stripped.split('\n')
            label_lines = [l for l in lines if l.strip().startswith('--')]
            label = label_lines[0].strip() if label_lines else "Query"
            print(f"\n{label}")
            
            try:
                result = conn.execute(text(stripped))
                rows = result.fetchall()
                if rows:
                    # Print column headers
                    cols = result.keys()
                    print("  " + " | ".join(str(c) for c in cols))
                    print("  " + "-" * 60)
                    for row in rows[:20]:  # Limit output to 20 rows per query
                        print("  " + " | ".join(str(v) for v in row))
                    if len(rows) > 20:
                        print(f"  ... ({len(rows)} total rows, showing first 20)")
                else:
                    print("  (no results)")
            except Exception as e:
                conn.rollback()
                err_msg = str(e)
                # Truncate very long error messages
                if len(err_msg) > 200:
                    err_msg = err_msg[:200] + "..."
                print(f"  [SKIPPED] {err_msg}")

print("\n" + "=" * 70)
print("  ALL ANALYTICAL QUERIES COMPLETE")
print("=" * 70)
