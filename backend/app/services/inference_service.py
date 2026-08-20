import os
import sys
import time
import torch
import cv2
import tempfile
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from app.config.settings import settings

# Dynamically resolve project root (which is 3 levels up from this file)
workspace_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(workspace_dir))
from shared.face_utils import FaceDetector, normalize_face

class InferenceService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InferenceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_format="onnx", model_path=None, device=None, max_workers=4):
        """
        Singleton Inference Service for backend integration.
        """
        if self._initialized:
            return
            
        self.model_format = model_format.lower()
        self.device_str = device
        self.max_workers = max_workers
        self.model = None
        self.ort_session = None
        
        if self.device_str is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.device_str)
            
        # Initialize Face Detector
        print(f"Initializing FaceDetector on {self.device}...")
        self.face_detector = FaceDetector(device='cuda' if self.device.type == 'cuda' else 'cpu')
            
        possible_paths = []
        if model_path:
            possible_paths.append(Path(model_path))
        if settings.MODEL_PATH:
            possible_paths.append(Path(settings.MODEL_PATH))
            possible_paths.append(workspace_dir / settings.MODEL_PATH)
        
        possible_paths.extend([
            workspace_dir / "model_registry/exports/model.onnx",
            workspace_dir / "model_registry/exports/model.torchscript.pt",
            workspace_dir / "model_registry/exports/model_optimized.pt",
            Path("../model_registry/exports/model.onnx"),
            Path("../model_registry/exports/model.torchscript.pt")
        ])
        
        self.resolved_model_path = None
        for p in possible_paths:
            if p.exists() and p.is_file():
                self.resolved_model_path = p
                ext = p.suffix.lower()
                if ext == ".onnx":
                    self.model_format = "onnx"
                elif ext == ".pt" or ext == ".pth":
                    if "torchscript" in p.name:
                        self.model_format = "torchscript"
                    else:
                        self.model_format = "pytorch"
                break
                
        if self.resolved_model_path is None:
            print(f"[WARNING] Inference model files not found in resolved paths. Staging directory...")
            self.resolved_model_path = workspace_dir / "model_registry/exports/model.onnx"
            
        print(f"[INFO] Inference service resolved model path: {self.resolved_model_path} (Format: {self.model_format})")
        self._initialized = True
        
    def load_model(self):
        if self.model is not None or self.ort_session is not None:
            return
            
        if not self.resolved_model_path.exists():
            raise FileNotFoundError(f"[ERROR] Production model file not found at: {self.resolved_model_path}")
            
        t0 = time.time()
        print(f"[INFO] Loading production model from {self.resolved_model_path}...")
        
        if self.model_format == "onnx":
            import onnxruntime as ort
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = self.max_workers
            opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            
            providers = ['CPUExecutionProvider']
            if self.device.type == 'cuda':
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                
            try:
                self.ort_session = ort.InferenceSession(str(self.resolved_model_path), sess_options=opts, providers=providers)
            except Exception as e:
                print(f"[WARNING] Failed to load ONNX on GPU: {e}. Falling back to CPU.")
                providers = ['CPUExecutionProvider']
                self.ort_session = ort.InferenceSession(str(self.resolved_model_path), sess_options=opts, providers=providers)
                self.device = torch.device("cpu")
                
        elif self.model_format == "torchscript":
            try:
                self.model = torch.jit.load(str(self.resolved_model_path), map_location=self.device)
                self.model.eval()
            except Exception:
                self.device = torch.device("cpu")
                self.model = torch.jit.load(str(self.resolved_model_path), map_location=self.device)
                self.model.eval()
                
        elif self.model_format == "pytorch":
            import timm
            try:
                backbone = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
                backbone.load_state_dict(torch.load(str(self.resolved_model_path), map_location=self.device))
                self.model = backbone.to(self.device)
                self.model.eval()
            except Exception:
                self.device = torch.device("cpu")
                backbone = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
                backbone.load_state_dict(torch.load(str(self.resolved_model_path), map_location=self.device))
                self.model = backbone.to(self.device)
                self.model.eval()
                
        load_time = time.time() - t0
        print(f"[INFO] Production model loaded successfully in {load_time:.3f} seconds.")
        
    def warmup(self):
        self.load_model()
        dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
        for _ in range(5):
            if self.ort_session is not None:
                _ = self.ort_session.run(None, {self.ort_session.get_inputs()[0].name: dummy_input})
            else:
                dummy_tensor = torch.tensor(dummy_input).to(self.device)
                with torch.no_grad():
                    with torch.amp.autocast(device_type=self.device.type, enabled=(self.device.type == 'cuda')):
                        _ = self.model(dummy_tensor)
        
    def _preprocess_single_frame(self, frame):
        """
        Applies MTCNN face detection. If no face is found, returns None.
        """
        cropped_rgb, err = self.face_detector.detect_and_crop(frame)
        if cropped_rgb is None:
            return None
        return normalize_face(cropped_rgb)
        
    def predict_images_batch(self, images, batch_size=16):
        """
        Runs inference on a list of images. Returns an array of probabilities.
        """
        self.load_model()
        if not images:
            return np.array([], dtype=np.float32)
            
        num_samples = len(images)
        fake_probabilities = []
        
        for i in range(0, num_samples, batch_size):
            chunk = images[i:i+batch_size]
            batch_data = np.stack(chunk)
            
            if self.ort_session is not None:
                ort_inputs = {self.ort_session.get_inputs()[0].name: batch_data}
                logits = self.ort_session.run(None, ort_inputs)[0]
                exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
                probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
                fake_probs = probs[:, 1]
                fake_probabilities.extend(fake_probs.tolist())
            else:
                batch_tensor = torch.tensor(batch_data).to(self.device)
                with torch.no_grad():
                    with torch.amp.autocast(device_type=self.device.type, enabled=(self.device.type == 'cuda')):
                        logits = self.model(batch_tensor)
                        probs = torch.softmax(logits, dim=1)
                        fake_probs = probs[:, 1].cpu().numpy()
                        fake_probabilities.extend(fake_probs.tolist())
                        
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
            
        return np.array(fake_probabilities, dtype=np.float32)
        
    def predict_image(self, image_bytes: bytes) -> dict:
        t0 = time.time()
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image bytes. File may be corrupted.")
            
        processed = self._preprocess_single_frame(img)
        if processed is None:
            raise ValueError("No recognizable face detected in the image.")
            
        probs = self.predict_images_batch([processed], batch_size=1)
        if len(probs) == 0:
            raise RuntimeError("Inference did not return predictions.")
            
        fake_prob = float(probs[0])
        decision = "FAKE" if fake_prob > 0.5 else "REAL"
        
        processing_time_ms = int((time.time() - t0) * 1000)
        
        return {
            "success": True,
            "prediction": decision,
            "confidence": round(fake_prob * 100, 2) if decision == "FAKE" else round((1.0 - fake_prob) * 100, 2),
            "processing_time_ms": processing_time_ms,
            "frames_processed": 1,
            "device": str(self.device),
            "model_version": f"v1_efficientnet_b0_{self.model_format}"
        }
        
    def predict_video(self, video_bytes: bytes, max_frames=15) -> dict:
        import psutil
        import gc
        process = psutil.Process(os.getpid())
        def get_ram_mb():
            return process.memory_info().rss / 1024 / 1024

        DEBUG_MEMORY = False
        if DEBUG_MEMORY:
            print(f"[DEBUG_MEMORY] RAM before inference: {get_ram_mb():.2f} MB")

        t0 = time.time()
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
            
        try:
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise ValueError("Failed to open video file. Format may be unsupported or corrupted.")
                
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                raise ValueError("Video file contains zero or invalid frames.")
                
            if total_frames <= max_frames:
                frame_indices = list(range(total_frames))
            else:
                frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int).tolist()
                
            processed_frames = []
            failed_frames = 0
            frames_sampled = 0

            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames_sampled += 1
                    pf = self._preprocess_single_frame(frame)
                    if pf is not None:
                        processed_frames.append(pf)
                    else:
                        failed_frames += 1
            cap.release()
            gc.collect()
            
            if DEBUG_MEMORY:
                print(f"[DEBUG_MEMORY] RAM after video decoding/frame preprocessing: {get_ram_mb():.2f} MB")

            if frames_sampled == 0:
                raise ValueError("No valid frames could be decoded from the video.")
                    
            if not processed_frames:
                raise ValueError(f"No recognizable faces detected in any of the {frames_sampled} sampled frames.")
                
            if DEBUG_MEMORY:
                print(f"[DEBUG_MEMORY] RAM immediately before ONNX inference: {get_ram_mb():.2f} MB")

            probs = self.predict_images_batch(processed_frames, batch_size=16)

            if DEBUG_MEMORY:
                print(f"[DEBUG_MEMORY] RAM after ONNX inference: {get_ram_mb():.2f} MB")

            if len(probs) == 0:
                raise RuntimeError("Inference did not return predictions for video frames.")
                
            mean_fake_prob = float(np.mean(probs))
            decision = "FAKE" if mean_fake_prob > 0.5 else "REAL"
            confidence = mean_fake_prob if decision == "FAKE" else (1.0 - mean_fake_prob)
            
            processing_time_ms = int((time.time() - t0) * 1000)
            
            result = {
                "success": True,
                "prediction": decision,
                "confidence": round(confidence * 100, 2),
                "mean_fake_probability": mean_fake_prob,
                "processing_time_ms": processing_time_ms,
                "frames_processed": len(processed_frames),
                "frames_sampled": frames_sampled,
                "faces_failed": failed_frames,
                "device": str(self.device),
                "model_version": f"v1_efficientnet_b0_{self.model_format}"
            }
            
            del processed_frames
            del probs
            gc.collect()
            if DEBUG_MEMORY:
                print(f"[DEBUG_MEMORY] RAM after cleanup: {get_ram_mb():.2f} MB")

            return result

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    def get_status(self) -> dict:
        return {
            "model_loaded": self.model is not None or self.ort_session is not None,
            "model_format": self.model_format,
            "device": str(self.device),
            "cuda_available": torch.cuda.is_available(),
            "model_path": str(self.resolved_model_path) if self.resolved_model_path else "Not resolved",
            "model_version": "v1_efficientnet_b0"
        }

inference_service = InferenceService()
