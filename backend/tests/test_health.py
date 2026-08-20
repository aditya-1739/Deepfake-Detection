import sys
import unittest.mock as mock
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Mock MongoDB connections to prevent database dependency in integration testing
mock_mongo_connect = mock.patch("app.database.connection.connect_to_mongo", return_value=None)
mock_mongo_close = mock.patch("app.database.connection.close_mongo_connection", return_value=None)

mock_mongo_connect.start()
mock_mongo_close.start()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["backend"] == "running"
