#%%
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np
import re
import json
import requests
from typing import Dict, List, Tuple, Optional
from collections import Counter
import uuid

# Connect to the transaction database
conn = sqlite3.connect('/Users/alessiogandelli/dev/starthacktoursept25/moneybuddy-backend/instance/transactions.db')


df = pd.read_sql('SELECT * FROM transactions', conn)



# Close the connection
conn.close()
# %%

# %%
def generate_synthetic_user_id():
    """Generate a random user ID"""
    return str(uuid.uuid4())

def generate_synthetic_transactions(original_df: pd.DataFrame, num_users: int = 10, total_transactions: int = 1200) -> pd.DataFrame:
    """
    Generate synthetic transactions based on existing data patterns
    """
    synthetic_data = []
    user_ids = [generate_synthetic_user_id() for _ in range(num_users)]
    customer_names = ["franco", "peppe", "gianni", "luigi", "mario", "pino", "spongebob", "skuz", "dema", "gandi"]
    
    # Create user mapping
    user_customer_mapping = dict(zip(user_ids, customer_names))
    
    # Calculate transactions per month (should be 100)
    transactions_per_month = total_transactions // 12
    
    for month_offset in range(12):  # Last 12 months
        for _ in range(transactions_per_month):
            # Select a random row from original data as template
            template_row = original_df.sample(n=1).iloc[0]
            
            # Generate random date within the month
            base_date = datetime.now() - timedelta(days=30 * (11 - month_offset))
            random_day = random.randint(1, 28)  # Safe day range for all months
            transaction_date = base_date.replace(day=random_day)
            
            # Create new transaction with random user
            new_transaction = template_row.copy()
            selected_user_id = random.choice(user_ids)
            new_transaction['user_id'] = selected_user_id
            
            # Set customer_name based on user_id
            if 'customer_name' in original_df.columns:
                new_transaction['customer_name'] = user_customer_mapping[selected_user_id]
            
            # Update date fields if they exist
            if 'date' in original_df.columns:
                new_transaction['date'] = transaction_date.strftime('%Y-%m-%d')
            if 'timestamp' in original_df.columns:
                new_transaction['timestamp'] = transaction_date.isoformat()
            
            # Add some variance to amount if it exists
            if 'amount' in original_df.columns:
                variance = random.uniform(0.8, 1.2)  # ±20% variance
                new_transaction['amount'] = float(template_row['amount']) * variance
            
            synthetic_data.append(new_transaction)
    
    return pd.DataFrame(synthetic_data)

# Generate synthetic data
print("Generating synthetic transactions...")
synthetic_df = generate_synthetic_transactions(df, num_users=10, total_transactions=1200)

# Create new database with synthetic data
synthetic_conn = sqlite3.connect('/Users/alessiogandelli/dev/starthacktoursept25/moneybuddy-backend/instance/synthetic_transactions.db')

# Write synthetic data to new database
synthetic_df.to_sql('transactions', synthetic_conn, if_exists='replace', index=False)

print(f"Created synthetic database with {len(synthetic_df)} transactions")
print(f"Number of unique users: {synthetic_df['user_id'].nunique()}")
print(f"Date range: {synthetic_df.get('date', pd.Series()).min()} to {synthetic_df.get('date', pd.Series()).max()}")

# Close the connection
synthetic_conn.close()
# Update dates to be from Sept 21, 2024 to Sept 21, 2025
def update_dates_in_synthetic_db():
    """Update dates in synthetic database to range from Sept 21, 2024 to Sept 21, 2025"""
    conn = sqlite3.connect('/Users/alessiogandelli/dev/starthacktoursept25/moneybuddy-backend/instance/synthetic_transactions.db')
    
    # Read the synthetic data
    df = pd.read_sql('SELECT * FROM transactions', conn)
    
    # Generate new dates within the specified range
    start_date = datetime(2024, 9, 21)
    end_date = datetime(2025, 9, 21)
    date_range = (end_date - start_date).days
    
    for idx in range(len(df)):
        # Generate random date within range
        random_days = random.randint(0, date_range)
        new_date = start_date + timedelta(days=random_days)
        
        # Update date fields
        if 'date' in df.columns:
            df.loc[idx, 'date'] = new_date.strftime('%Y-%m-%d')
        if 'timestamp' in df.columns:
            df.loc[idx, 'timestamp'] = new_date.isoformat()
    
    # Write updated data back to database
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    
    print(f"Updated dates to range from {df.get('date', pd.Series()).min()} to {df.get('date', pd.Series()).max()}")
    
    conn.close()

# Update the dates
update_dates_in_synthetic_db()

# %%
