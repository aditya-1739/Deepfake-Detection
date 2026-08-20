import sys
import unittest.mock as mock
import numpy as np
import cv2
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# Adjust python path to find app module
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Mock MongoDB connections to prevent database dependency in integration testing
mock_mongo_connect = mock.patch("app.database.connection.connect_to_mongo", return_value=None)
mock_mongo_close = mock.patch("app.database.connection.close_mongo_connection", return_value=None)

mock_mongo_connect.start()
mock_mongo_close.start()

from app.main import app
from app.services.inference_service import inference_service

client = TestClient(app)

def test_health_check():
    """
    Verify health endpoint returns correct status.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "ok"
    assert "device" in data
    assert "cuda_available" in data

def test_model_status():
    """
    Verify model metadata status endpoint works.
    """
    response = client.get("/api/model")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "model_loaded" in data
    assert "model_format" in data
    assert "device" in data

def test_predict_image_success():
    """
    Verify image prediction works with real image encoding.
    """
    # Create valid JPEG image bytes
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", dummy_img)
    img_bytes = encoded.tobytes()
    
    response = client.post(
        "/api/predict/image",
        files={"file": ("test_image.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prediction"] in {"REAL", "FAKE"}
    assert "confidence" in data
    assert "processing_time_ms" in data
    assert data["frames_processed"] == 1

def test_predict_image_unsupported():
    """
    Verify unsupported formats are rejected with 400.
    """
    response = client.post(
        "/api/predict/image",
        files={"file": ("test.txt", b"plain text content", "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported format" in data["detail"]

def test_predict_image_empty():
    """
    Verify empty uploads are rejected with 400.
    """
    response = client.post(
        "/api/predict/image",
        files={"file": ("test_empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Uploaded file is empty" in data["detail"]

def test_predict_image_corrupted():
    """
    Verify corrupted/undecodable images are rejected with 422.
    """
    response = client.post(
        "/api/predict/image",
        files={"file": ("corrupt.jpg", b"invalid image bytes", "image/jpeg")}
    )
    assert response.status_code == 422
    data = response.json()
    assert "Failed to decode image bytes" in data["detail"]

def test_predict_video_success():
    """
    Verify video prediction API returns valid JSON format by mocking the video prediction.
    """
    # Mock video prediction output to avoid reading dummy video bytes
    mock_result = {
        "success": True,
        "prediction": "FAKE",
        "confidence": 92.45,
        "processing_time_ms": 250,
        "frames_processed": 15,
        "device": "cpu",
        "model_version": "v1_efficientnet_b0_onnx"
    }
    
    with mock.patch.object(inference_service, "predict_video", return_value=mock_result) as mock_pred:
        response = client.post(
            "/api/predict/video",
            files={"file": ("mock_video.mp4", b"dummy video bytes", "video/mp4")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["prediction"] == "FAKE"
        assert data["confidence"] == 92.45
        assert data["frames_processed"] == 15
        mock_pred.assert_called_once()

def test_predict_video_unsupported():
    """
    Verify unsupported video format is rejected with 400.
    """
    response = client.post(
        "/api/predict/video",
        files={"file": ("test.txt", b"plain text", "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported format" in data["detail"]

def test_predict_image_oversized():
    """
    Verify images exceeding MAX_IMAGE_SIZE (10MB) are rejected with 413.
    """
    oversized_data = b"0" * (11 * 1024 * 1024) # 11MB
    response = client.post(
        "/api/predict/image",
        files={"file": ("large_image.jpg", oversized_data, "image/jpeg")}
    )
    assert response.status_code == 413
    assert "exceeds the limit" in response.json()["detail"]

def test_predict_video_oversized():
    """
    Verify videos exceeding MAX_VIDEO_SIZE (100MB) are rejected with 413.
    """
    oversized_data = b"0" * (101 * 1024 * 1024) # 101MB
    response = client.post(
        "/api/predict/video",
        files={"file": ("large_video.mp4", oversized_data, "video/mp4")}
    )
    assert response.status_code == 413
    assert "exceeds the limit" in response.json()["detail"]

def test_concurrency_stress():
    """
    Verify concurrent client requests are handled gracefully.
    """
    import threading
    results = []
    
    def worker():
        response = client.get("/api/health")
        results.append(response.status_code)
        
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert all(code == 200 for code in results)
    assert len(results) == 10
