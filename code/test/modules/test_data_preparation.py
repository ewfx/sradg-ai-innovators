
import pandas as pd
import pytest
import os
from anomaly_detection.modules.data_preparation import DataPreparation

def test_preprocess_data(tmp_path):
    # Create a minimal DataFrame
    df = pd.DataFrame({
        "RISKDATE": pd.date_range(start="2024-01-01", periods=10),
        "DESKNAME": ["DeskA"] * 10,
        "QUANTITYDIFFERENCE": [10, 20, 15, 5, 30, 25, 20, 10, 5, 0],
        "IMPACT_PRICE": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "IMPACT_QUANTITY": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
    })

    # Ensure encoder directory exists
    os.makedirs("models", exist_ok=True)
    
    features = DataPreparation.preprocess_data(df)
    
    # Check expected columns
    expected_cols = [
        'QUANTITYDIFFERENCE', 'IMPACT_PRICE', 'IMPACT_QUANTITY', 'day_of_week', 'month',
        'deskname_encoded', 'quantity_mean_7d', 'price_std_7d', 'quantity_diff_lag1'
    ]
    assert all(col in features.columns for col in expected_cols)
    assert not features.empty
