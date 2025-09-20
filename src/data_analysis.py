#%%
import sys
import warnings

# Handle numpy compatibility issues
try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Error importing core packages: {e}")
    print("Try: pip install --upgrade pandas numpy")
    sys.exit(1)

# Handle visualization packages with fallbacks
PLOTTING_AVAILABLE = True
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    # Set a safe backend for matplotlib
    plt.switch_backend('Agg')
except ImportError as e:
    print(f"Warning: Visualization packages not available: {e}")
    PLOTTING_AVAILABLE = False
except Exception as e:
    print(f"Warning: Matplotlib backend issue: {e}")
    PLOTTING_AVAILABLE = False

from datetime import datetime

def load_transaction_data(file_path):
    """Load transaction data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None

def perform_eda(df):
    """Perform Exploratory Data Analysis on transaction data"""
    
    print("=== TRANSACTION DATA EDA ===\n")
    
    # Basic info
    print("Dataset Shape:", df.shape)
    print("\nColumn Info:")
    print(df.info())
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nBasic Statistics:")
    print(df.describe())
    
    # Check for missing values
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    # If amount column exists, analyze it
    amount_cols = [col for col in df.columns if 'amount' in col.lower()]
    if amount_cols:
        amount_col = amount_cols[0]
        print(f"\nAmount Analysis ({amount_col}):")
        print(f"Total transactions: {len(df)}")
        print(f"Total amount: ${df[amount_col].sum():,.2f}")
        print(f"Average amount: ${df[amount_col].mean():.2f}")
        print(f"Median amount: ${df[amount_col].median():.2f}")
        
        # Plot amount distribution only if plotting is available
        if PLOTTING_AVAILABLE:
            try:
                plt.figure(figsize=(12, 4))
                
                plt.subplot(1, 2, 1)
                plt.hist(df[amount_col], bins=50, alpha=0.7)
                plt.title('Amount Distribution')
                plt.xlabel('Amount')
                plt.ylabel('Frequency')
                
                plt.subplot(1, 2, 2)
                plt.boxplot(df[amount_col])
                plt.title('Amount Box Plot')
                plt.ylabel('Amount')
                
                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"Could not generate amount plots: {e}")
        else:
            print("Visualization not available - skipping amount plots")
    
    # If category column exists, analyze it
    category_cols = [col for col in df.columns if 'category' in col.lower()]
    if category_cols:
        category_col = category_cols[0]
        print(f"\nCategory Analysis ({category_col}):")
        category_counts = df[category_col].value_counts()
        print(category_counts)
        
        # Plot category distribution only if plotting is available
        if PLOTTING_AVAILABLE:
            try:
                plt.figure(figsize=(10, 6))
                category_counts.plot(kind='bar')
                plt.title('Transaction Categories')
                plt.xlabel('Category')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"Could not generate category plot: {e}")
        else:
            print("Visualization not available - skipping category plot")
    
    # If date column exists, analyze temporal patterns
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    if date_cols:
        date_col = date_cols[0]
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            print(f"\nTemporal Analysis ({date_col}):")
            print(f"Date range: {df[date_col].min()} to {df[date_col].max()}")
            
            # Monthly transaction volume
            monthly_counts = df.set_index(date_col).resample('M').size()
            
            if PLOTTING_AVAILABLE:
                try:
                    plt.figure(figsize=(12, 4))
                    monthly_counts.plot(kind='line', marker='o')
                    plt.title('Monthly Transaction Volume')
                    plt.xlabel('Month')
                    plt.ylabel('Number of Transactions')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.show()
                except Exception as e:
                    print(f"Could not generate temporal plot: {e}")
            else:
                print("Visualization not available - showing monthly counts:")
                print(monthly_counts)
            
        except Exception as e:
            print(f"Could not parse {date_col} as datetime: {e}")

if __name__ == "__main__":
    # Example usage - adjust file path as needed
    file_path = "transactions.csv"  # Update with your actual file path
    
    df = load_transaction_data(file_path)
    if df is not None:
        perform_eda(df)
    else:
        print("Please provide a valid transaction data file")
# %%
