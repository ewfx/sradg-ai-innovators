
import pandas as pd
import pytest
from anomaly_detection.modules.data_ingestion import DataIngestion
import os

def test_load_data_valid_file(tmp_path):
    # Create sample CSV
    sample_file = tmp_path / "sample.csv"
    df = pd.DataFrame({
        "RISKDATE": ["2024-01-01", "2024-01-02"],
        "TRADEID": [1, 2],
        "VALUE": [100, 200]
    })
    df.to_csv(sample_file, index=False)

    loaded_df = DataIngestion.load_data(str(sample_file), chunksize=1)
    assert not loaded_df.empty
    assert len(loaded_df) == 2
    assert "RISKDATE" in loaded_df.columns

def test_load_data_file_not_found():
    df = DataIngestion.load_data("non_existent_file.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.empty

def test_load_data_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")
    df = DataIngestion.load_data(str(empty_file))
    assert isinstance(df, pd.DataFrame)
    assert df.empty
