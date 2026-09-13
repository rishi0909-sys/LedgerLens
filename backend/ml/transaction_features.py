import pandas as pd
import numpy as np

def construct_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct causal transaction features without future leakage.
    Ensures that for transaction t, only transactions < t are used.
    """
    if df.empty:
        return df

    # 1. Sort strictly chronologically
    # If timestamps are identical, preserve stable sorting by transaction_id
    df = df.sort_values(['timestamp', 'transaction_id']).reset_index(drop=True)
    
    # 2. Base temporal features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    
    # 3. Categorical encodings
    # For baseline, we can one-hot encode or use numerical mapping for transaction_type
    tx_types = ['SALARY', 'INVOICE_PAYMENT', 'TRANSFER', 'REIMBURSEMENT']
    for tx_type in tx_types:
        df[f'is_{tx_type.lower()}'] = (df['transaction_type'] == tx_type).astype(int)

    # 4. Causal historical features by source_account
    # We use shift(1) to exclude the current transaction from its own historical baseline
    
    # Time since previous transaction (in seconds)
    df['prev_timestamp'] = df.groupby('source_account')['timestamp'].shift(1)
    df['time_since_previous'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds()
    df['time_since_previous'] = df['time_since_previous'].fillna(0) # Default for first txn
    
    # Cumulative stats (shifted to be strictly < t)
    df['rolling_amount_sum'] = df.groupby('source_account')['amount'].transform(lambda x: x.cumsum().shift(1)).fillna(0)
    df['rolling_txn_count'] = df.groupby('source_account')['amount'].transform(lambda x: (~x.isna()).cumsum().shift(1)).fillna(0)
    
    # Historical average amount
    # Add a small epsilon to avoid division by zero
    df['rolling_avg_amount'] = np.where(
        df['rolling_txn_count'] > 0, 
        df['rolling_amount_sum'] / df['rolling_txn_count'], 
        0
    )
    
    # Amount deviation from historical average
    df['amount_deviation'] = df['amount'] - df['rolling_avg_amount']
    df['amount_deviation_ratio'] = np.where(
        df['rolling_avg_amount'] > 0,
        df['amount'] / df['rolling_avg_amount'],
        1.0
    )
    
    # 5. Counterparty features
    # Count unique counterparties < t
    def unique_counterparties_prior(group):
        seen = set()
        res = []
        for dst in group:
            res.append(len(seen))
            seen.add(dst)
        return pd.Series(res, index=group.index)
        
    df['unique_counterparty_count'] = df.groupby('source_account')['destination_account'].transform(unique_counterparties_prior)
    
    # Clean up intermediate columns if desired
    df = df.drop(columns=['prev_timestamp', 'rolling_amount_sum'])
    
    return df
