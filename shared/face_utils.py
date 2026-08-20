import cv2
import numpy as np
from facenet_pytorch import MTCNN
from PIL import Image

class FaceDetector:
    def __init__(self, device='cpu', margin=0.2, image_size=224):
        """
        Initializes the MTCNN face detector.
        margin: Fraction of face size to add as margin (e.g., 0.2 means 20% margin).
        """
        self.device = device
        self.margin = margin
        self.image_size = image_size
        
        # Initialize MTCNN
        # keep_all=True allows finding multiple faces, we will filter for the largest
        # post_process=False because we handle normalization in our own pipeline
        self.mtcnn = MTCNN(
            keep_all=True, 
            device=self.device, 
            post_process=False,
            margin=0 # We will calculate margin manually to ensure precise bounds
        )
        
    def detect_and_crop(self, frame_bgr):
        """
        Detects the largest face in a BGR frame, applies margin, crops, and resizes.
        Returns:
            rgb_cropped_resized (np.ndarray): The processed face frame in RGB format, shape (224, 224, 3)
            error (str): None if successful, or error message if failed.
        """
        if frame_bgr is None or not isinstance(frame_bgr, np.ndarray):
            return None, "Invalid frame"
            
        if len(frame_bgr.shape) != 3 or frame_bgr.shape[2] != 3:
            return None, "Frame must be 3-channel BGR"

        # Convert to RGB for MTCNN (which expects PIL Image or np.ndarray in RGB)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        
        # Detect faces
        import torch
        with torch.no_grad():
            boxes, probs = self.mtcnn.detect(img_pil)
        
        if boxes is None or len(boxes) == 0:
            return None, "No face detected"
            
        # Select largest face
        largest_box = None
        max_area = 0
        
        for box, prob in zip(boxes, probs):
            if prob < 0.90:  # Confidence threshold
                continue
                
            x1, y1, x2, y2 = box
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                largest_box = box
                
        if largest_box is None:
            return None, "No face met confidence threshold"
            
        # Apply margin and crop
        x1, y1, x2, y2 = [int(b) for b in largest_box]
        w = x2 - x1
        h = y2 - y1
        
        margin_x = int(w * self.margin)
        margin_y = int(h * self.margin)
        
        # Calculate new bounds, constrained to image dimensions
        img_h, img_w, _ = frame_rgb.shape
        x1_m = max(0, x1 - margin_x)
        y1_m = max(0, y1 - margin_y)
        x2_m = min(img_w, x2 + margin_x)
        y2_m = min(img_h, y2 + margin_y)
        
        # Crop
        cropped = frame_rgb[y1_m:y2_m, x1_m:x2_m]
        
        if cropped.size == 0:
            return None, "Crop resulted in empty image"
            
        # Resize to 224x224
        resized = cv2.resize(cropped, (self.image_size, self.image_size), interpolation=cv2.INTER_LINEAR)
        
        return resized, None

def normalize_face(face_rgb):
    """
    Applies standard ImageNet normalization to an RGB face crop.
    Returns tensor shape (3, 224, 224)
    """
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    normalized = face_rgb.astype(np.float32) / 255.0
    normalized = (normalized - mean) / std
    return normalized.transpose(2, 0, 1)
