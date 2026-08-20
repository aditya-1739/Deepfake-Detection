import os
from app.services.inference_service import inference_service

class DeepfakePredictor:
    """
    Backward-compatible wrapper for DeepfakePredictor pointing to the optimized InferenceService.
    """
    def __init__(self, model_path: str = None, model_name=None):
        # Singleton InferenceService is loaded once at startup
        pass

    def predict_image(self, image_bytes: bytes) -> dict:
        res = inference_service.predict_image(image_bytes)
        return {
            "prediction": "Deepfake" if res["prediction"] == "FAKE" else "Real",
            "confidence": res["confidence"],
            "processing_time": res["processing_time_ms"] / 1000.0,
            "model_version": res["model_version"],
            "backbone": "EfficientNet-B0"
        }

    def predict_video(self, video_path: str, num_frames=15) -> dict:
        if not os.path.exists(video_path):
            return {"error": "Invalid video file"}
            
        with open(video_path, "rb") as f:
            content = f.read()
            
        res = inference_service.predict_video(content, max_frames=num_frames)
        if not res.get("success", False):
            return {"error": res.get("error", "Unknown prediction error")}
            
        return {
            "prediction": "Deepfake" if res["prediction"] == "FAKE" else "Real",
            "confidence": res["confidence"],
            "processing_time": res["processing_time_ms"] / 1000.0,
            "frames_processed": res["frames_processed"],
            "positive_frames": int(res["frames_processed"] * res.get("fake_votes_ratio", 0.5)),
            "model_version": res["model_version"],
            "backbone": "EfficientNet-B0"
        }
