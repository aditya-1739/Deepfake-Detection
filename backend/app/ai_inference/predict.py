import cv2
import torch
import numpy as np
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
import time
# In production, import the actual model architecture used in training
# Here we simulate loading the timm EfficientNet-B0 model
import timm

class DeepfakePredictor:
    def __init__(self, model_path: str, model_name="efficientnet_b0"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Load backbone
        self.model = timm.create_model(model_name, pretrained=False, num_classes=2)
        
        # Load weights if available
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        self.model.to(self.device)
        self.model.eval()
        
        self.transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2()
        ])

    def predict_image(self, image_bytes):
        start_time = time.time()
        
        # 1. Decode Image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 2. Face Detection Placeholder (Assuming image is already a face crop or we crop center)
        h, w, _ = img.shape
        size = min(h, w)
        cy, cx = h//2, w//2
        cropped = img[cy-size//2:cy+size//2, cx-size//2:cx+size//2]
        
        # 3. Preprocess
        tensor = self.transform(image=cropped)['image'].unsqueeze(0).to(self.device)
        
        # 4. Inference
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1)
            fake_prob = probs[0][1].item() * 100
            
        processing_time = time.time() - start_time
        
        return {
            "prediction": "Deepfake" if fake_prob > 50 else "Real",
            "confidence": round(fake_prob if fake_prob > 50 else 100 - fake_prob, 2),
            "processing_time": round(processing_time, 2),
            "model_version": "v1.0",
            "backbone": "EfficientNet-B0"
        }

    def predict_video(self, video_path, num_frames=10):
        start_time = time.time()
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            return {"error": "Invalid video file"}
            
        frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
        
        frames_processed = 0
        positive_frames = 0
        fake_probs = []
        
        # We can do batch inference, but for simplicity we iterate
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret: continue
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            size = min(h, w)
            cy, cx = h//2, w//2
            cropped = frame[cy-size//2:cy+size//2, cx-size//2:cx+size//2]
            
            tensor = self.transform(image=cropped)['image'].unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(tensor)
                probs = torch.softmax(outputs, dim=1)
                fake_prob = probs[0][1].item()
                fake_probs.append(fake_prob)
                
                if fake_prob > 0.5:
                    positive_frames += 1
            frames_processed += 1
            
        cap.release()
        
        avg_fake_prob = sum(fake_probs) / len(fake_probs) if fake_probs else 0
        processing_time = time.time() - start_time
        
        return {
            "prediction": "Deepfake" if avg_fake_prob > 0.5 else "Real",
            "confidence": round(avg_fake_prob * 100 if avg_fake_prob > 0.5 else (1 - avg_fake_prob) * 100, 2),
            "processing_time": round(processing_time, 2),
            "frames_processed": frames_processed,
            "positive_frames": positive_frames,
            "model_version": "v1.0",
            "backbone": "EfficientNet-B0"
        }

import os
