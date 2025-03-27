
import pytest
from fastapi.testclient import TestClient
from anomaly_detection.api.anomalydetection import app

client = TestClient(app)

@pytest.fixture
def sample_batch_data():
    return [
        {
            "TRADEID": 123,
            "RISKDATE": "2023-10-26T10:00:00",
            "DESKNAME": "DeskA",
            "QUANTITYDIFFERENCE": 15.0,
            "IMPACT_PRICE": 100.0,
            "IMPACT_QUANTITY": 5.0,
            "COMMENT": "Data entry error"
        },
        {
            "TRADEID": 456,
            "RISKDATE": "2023-10-27T11:00:00",
            "DESKNAME": "DeskB",
            "QUANTITYDIFFERENCE": 2.0,
            "IMPACT_PRICE": 50.0,
            "IMPACT_QUANTITY": 1.0,
            "COMMENT": "Rounding error"
        },
        {
            "TRADEID": 789,
            "RISKDATE": "2024-03-20T14:30:00",
            "DESKNAME": "DeskC",
            "QUANTITYDIFFERENCE": 50.0,
            "IMPACT_PRICE": 200.0,
            "IMPACT_QUANTITY": 10.0,
            "COMMENT": "Large quantity difference, potential manual error"
        }
    ]

def test_batch_anomaly_processing(sample_batch_data):
    response = client.post("/batch_anomaly/", json=sample_batch_data)
    assert response.status_code == 200
    assert "message" in response.json()
