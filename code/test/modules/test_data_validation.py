
import pandas as pd
from anomaly_detection.modules.data_validation import DataValidation

def test_validate_data_consistency():
    df = pd.DataFrame({
        "TRADEID": [1, 2, 3],
        "QUANTITYDIFFERENCE": [5, 20, 8]
    })

    filtered_df = DataValidation.validate_data_consistency(df, quantity_threshold=10)
    
    assert not filtered_df.empty
    assert len(filtered_df) == 2
    assert all(filtered_df["QUANTITYDIFFERENCE"].abs() < 10)
