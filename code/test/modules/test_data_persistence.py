
import pandas as pd
import os
from anomaly_detection.modules.data_persistence import DataPersistence

def test_save_anomalies(tmp_path):
    # Prepare dummy anomalies DataFrame
    df = pd.DataFrame({
        "TRADEID": [1, 2],
        "Anomaly": ["Yes", "Yes"],
        "COMMENT": ["Test 1", "Test 2"]
    })

    output_file = tmp_path / "anomalies.csv"
    DataPersistence.save_anomalies(df, str(output_file))

    # Check if file is created and content is not empty
    assert output_file.exists()
    saved_df = pd.read_csv(output_file)
    assert not saved_df.empty
    assert list(saved_df.columns) == list(df.columns)
