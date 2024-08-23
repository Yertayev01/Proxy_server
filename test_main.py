from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_historical_data():
    response = client.get("/historical-data/", params={
        "ticker": "AAPL",
        "multiplier": 1,
        "timespan": "day",
        "start_date": "2022-01-01",
        "end_date": "2022-12-31"
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
