
from anomaly_detection.api.models import RealtimeData
from pydantic import ValidationError
import pytest

def test_realtime_data_model_valid():
    data = {
        "TRADEID": 101,
        "RISKDATE": "2025-03-27",
        "DESKNAME": "Commodities",
        "QUANTITYDIFFERENCE": 200.0,
        "IMPACT_PRICE": 102.5,
        "IMPACT_QUANTITY": 190.0,
        "COMMENT": "Typo in quantity entry"
    }
    model = RealtimeData(**data)
    assert model.TRADEID == 101
    assert model.DESKNAME == "Commodities"

def test_realtime_data_model_invalid_type():
    invalid_data = {
        "TRADEID": "invalid",  # Should be int
        "RISKDATE": "2025-03-27",
        "DESKNAME": "FX",
        "QUANTITYDIFFERENCE": 100.0,
        "IMPACT_PRICE": 101.0,
        "IMPACT_QUANTITY": 98.0,
        "COMMENT": "Non-integer TRADEID"
    }
    with pytest.raises(ValidationError):
        RealtimeData(**invalid_data)
