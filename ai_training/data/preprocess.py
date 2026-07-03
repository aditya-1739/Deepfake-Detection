import os
import cv2
import argparse
from pathlib import Path

def extract_frames(video_path: str, output_dir: str, num_frames: int = 10):
    """
    Extracts a fixed number of frames evenly spaced from a video.
    In a full pipeline, this would also include face detection (e.g., using MTCNN or dlib)
    to crop only the face before saving.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        return

    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, frame_idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            # TODO: Add Face Detection Cropping here
            out_path = os.path.join(output_dir, f"frame_{idx:03d}.jpg")
            cv2.imwrite(out_path, frame)
    
    cap.release()

def process_dataset(raw_dir: str, processed_dir: str):
    """
    Iterate over raw dataset directory (assumes folders 'real' and 'fake')
    and extracts frames/faces to the processed directory.
    """
    raw_path = Path(raw_dir)
    for class_name in ['real', 'fake']:
        class_dir = raw_path / class_name
        if not class_dir.exists():
            continue
            
        for video_file in class_dir.glob("*.mp4"):
            out_subdir = Path(processed_dir) / class_name / video_file.stem
            extract_frames(str(video_file), str(out_subdir))
            print(f"Processed {video_file.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deepfake Dataset Preprocessing")
    parser.add_argument("--raw_dir", type=str, default="../../datasets/raw", help="Path to raw dataset")
    parser.add_argument("--processed_dir", type=str, default="../../datasets/processed", help="Path to save processed faces")
    args = parser.parse_args()
    
    process_dataset(args.raw_dir, args.processed_dir)
