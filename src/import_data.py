#%%
import pandas as pd
import sqlite3
import json

# Read Excel file
df = pd.read_excel('/Users/alessiogandelli/dev/starthacktoursept25/moneybuddy-backend/data/transactions.xlsx', sheet_name='TRX Data')

# Connect to SQLite database
conn = sqlite3.connect('/Users/alessiogandelli/dev/starthacktoursept25/moneybuddy-backend/instance/transactions.db')

# Map Excel columns to database columns
column_mapping = {
    'TRX_ID': 'trx_id',
    'MONEY_ACCOUNT_NAME': 'account_name',
    'KUNDEN_NAME': 'customer_name',
    'PRODUKT': 'product',
    'TRX_TYPE_SHORT': 'trx_type',
    'BUCHUNGS_ART_NAME': 'booking_type',
    'VAL_DATE': 'value_date',
    'TRX_DATE': 'booking_date',
    'TRX_CURRY_NAME': 'currency',
    'POINT_OF_SALE_AND_LOCATION': 'merchant_name',
    'TEXT_CREDITOR': 'merchant_full_text',
    'CRED_ADDR_TEXT': 'merchant_address',
    'CRED_IBAN': 'merchant_iban',
    'CARD_ID': 'card_id_masked',
    'ACQUIRER_COUNTRY_NAME': 'acquirer_country',
    'CRED_REF_NR': 'reference_nr'
}

# Rename columns based on mapping
df_mapped = df.rename(columns=column_mapping)

# Add missing columns with default values
df_mapped['account_iban'] = df_mapped['account_name'].str.extract(r'([A-Z]{2}\d{2}[A-Z\d]+)')  # Extract IBAN if present
df_mapped['account_currency'] = 'CHF'  # Default currency
df_mapped['direction'] = df_mapped['trx_type'].apply(lambda x: 'debit' if 'debit' in str(x).lower() else 'credit')

# Find amount column - look for numeric columns or common amount column names
amount_cols = [col for col in df.columns if any(x in col.upper() for x in ['AMOUNT', 'BETRAG', 'SUM', 'TOTAL'])]
if amount_cols:
    df_mapped['amount'] = pd.to_numeric(df[amount_cols[0]], errors='coerce').fillna(0)
else:
    # Try the last numeric column
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        df_mapped['amount'] = pd.to_numeric(df[numeric_cols[-1]], errors='coerce').fillna(0)
    else:
        df_mapped['amount'] = 0  # Default fallback

# Ensure currency is not null
df_mapped['currency'] = df_mapped['currency'].fillna('CHF')

# Ensure direction is not null
df_mapped['direction'] = df_mapped['direction'].fillna('credit')

# Ensure trx_id is not null
df_mapped['trx_id'] = df_mapped['trx_id'].fillna('').astype(str)

df_mapped['raw_payload'] = df.apply(lambda row: json.dumps(row.to_dict(), default=str), axis=1)

# Select only the columns we need for the database
final_columns = [
    'trx_id', 'account_iban', 'account_name', 'account_currency', 'customer_name', 
    'product', 'trx_type', 'booking_type', 'value_date', 'booking_date', 
    'direction', 'amount', 'currency', 'merchant_name', 'merchant_full_text',
    'merchant_address', 'merchant_iban', 'card_id_masked', 'acquirer_country',
    'reference_nr', 'raw_payload'
]

# Create final dataframe with only existing columns
df_final = df_mapped[final_columns].copy()

# Convert dates
df_final['value_date'] = pd.to_datetime(df_final['value_date'], errors='coerce')
df_final['booking_date'] = pd.to_datetime(df_final['booking_date'], errors='coerce')

# Add timestamps for database tracking
from datetime import datetime
current_time = datetime.now()
df_final['created_at'] = current_time
df_final['updated_at'] = current_time

# Insert into database
df_final.to_sql('transactions', conn, if_exists='append', index=False)

print(f"Imported {len(df_final)} transactions to database")
conn.close()
# %%
