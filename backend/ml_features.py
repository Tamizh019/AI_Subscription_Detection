import pandas as pd
import numpy as np
from datetime import datetime

def extract_ml_features(group_df):
    """
    Extract ML features from a transaction group for subscription detection
    """
    if len(group_df) < 2:
        return None
    
    # Sort by date
    group_df = group_df.sort_values('date').copy()
    
    # Time-based features
    date_diffs = group_df['date'].diff().dt.days.dropna()
    
    if len(date_diffs) == 0:
        return None
    
    features = {
        # Frequency Features
        'transaction_count': len(group_df),
        'avg_interval_days': float(date_diffs.mean()),
        'interval_std': float(date_diffs.std()) if len(date_diffs) > 1 else 0.0,
        'interval_cv': float(date_diffs.std() / date_diffs.mean()) if len(date_diffs) > 0 and date_diffs.mean() > 0 else 0.0,
        
        # Amount Features
        'avg_amount': float(group_df['amount'].mean()),
        'amount_std': float(group_df['amount'].std()),
        'amount_consistency': float(1 - (group_df['amount'].std() / group_df['amount'].mean())) if group_df['amount'].mean() > 0 else 0.0,
        'total_spent': float(group_df['amount'].sum()),
        'max_amount': float(group_df['amount'].max()),
        'min_amount': float(group_df['amount'].min()),
        
        # Date Pattern Features
        'day_of_month_std': float(group_df['date'].dt.day.std()),
        'days_since_last': int((pd.Timestamp.now() - group_df['date'].iloc[-1]).days),
        
        # Regularity Score (custom metric)
        'is_monthly_pattern': 1 if 25 <= date_diffs.mean() <= 35 else 0,
        'is_yearly_pattern': 1 if 360 <= date_diffs.mean() <= 375 else 0,
        'is_weekly_pattern': 1 if 6 <= date_diffs.mean() <= 8 else 0,
    }
    
    # Handle edge cases
    if np.isnan(features['interval_cv']) or np.isinf(features['interval_cv']):
        features['interval_cv'] = 0.0
    
    if np.isnan(features['amount_consistency']) or np.isinf(features['amount_consistency']):
        features['amount_consistency'] = 0.0
    
    return features


def features_to_array(features_dict):
    """Convert feature dict to numpy array for ML model"""
    if features_dict is None:
        return None
    
    feature_order = [
        'transaction_count', 'avg_interval_days', 'interval_std', 'interval_cv',
        'avg_amount', 'amount_std', 'amount_consistency', 'total_spent',
        'max_amount', 'min_amount', 'day_of_month_std', 'days_since_last',
        'is_monthly_pattern', 'is_yearly_pattern', 'is_weekly_pattern'
    ]
    
    try:
        array = np.array([features_dict[k] for k in feature_order], dtype=float).reshape(1, -1)
        
        # Replace any NaN or Inf values
        array = np.nan_to_num(array, nan=0.0, posinf=1.0, neginf=0.0)
        
        return array
    except Exception as e:
        print(f"Error converting features to array: {e}")
        return None
