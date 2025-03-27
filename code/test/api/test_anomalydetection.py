
import pytest
from fastapi.testclient import TestClient
from anomaly_detection.api.anomalydetection import app
from anomaly_detection.api.models import RealtimeData

client = TestClient(app)

# Sample payload for testing
sample_data = {
    "TRADEID": 101,
    "RISKDATE": "2025-03-27",
    "DESKNAME": "Fixed Income",
    "QUANTITYDIFFERENCE": 150.0,
    "IMPACT_PRICE": 230.5,
    "IMPACT_QUANTITY": 145.0,
    "COMMENT": "Late trade booking caused quantity mismatch"
}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_realtime_anomaly_endpoint():
    response = client.post("/realtime_anomaly/", json=sample_data)
    assert response.status_code == 200
    assert "message" in response.json()

def test_batch_anomaly_endpoint():
    response = client.post("/batch_anomaly/", json=[sample_data])
    assert response.status_code == 200
    assert "message" in response.json()
