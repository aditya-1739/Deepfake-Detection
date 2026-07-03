import os
import cv2
import argparse
import pandas as pd
from pathlib import Path
import random

def preprocess_dataset(raw_dir, processed_dir, num_frames=15, max_videos_per_class=None):
    """
    Extracts frames and crops faces from deepfake datasets (Celeb-DF or FaceForensics++).
    """
    raw_path = Path(raw_dir)
    processed_path = Path(processed_dir)
    
    if not raw_path.exists():
        print(f"[ERROR] Raw directory {raw_dir} not found.")
        return False

    real_videos = []
    fake_videos = []
    
    # Map for FaceForensics++ or Celeb-DF
    if (raw_path / 'original').exists():
        real_dirs = ['original']
        fake_dirs = ['Deepfakes', 'Face2Face', 'FaceSwap', 'NeuralTextures', 'FaceShifter']
        
        for r_dir in real_dirs:
            if (raw_path / r_dir).exists():
                real_videos.extend(list((raw_path / r_dir).glob('**/*.mp4')))
                
        for f_dir in fake_dirs:
            if (raw_path / f_dir).exists():
                fake_videos.extend(list((raw_path / f_dir).glob('**/*.mp4')))
    else:
        # Default or Celeb-DF
        real_dir = raw_path / 'Celeb-real' if (raw_path / 'Celeb-real').exists() else raw_path / 'real'
        fake_dir = raw_path / 'Celeb-synthesis' if (raw_path / 'Celeb-synthesis').exists() else raw_path / 'fake'
        if real_dir.exists():
            real_videos.extend(list(real_dir.glob('**/*.mp4')))
        if fake_dir.exists():
            fake_videos.extend(list(fake_dir.glob('**/*.mp4')))

    if not real_videos and not fake_videos:
        print(f"[ERROR] No real or fake videos found in {raw_dir}.")
        return False
        
    if max_videos_per_class:
        # For testing or limited local execution
        random.seed(42)
        if len(real_videos) > max_videos_per_class:
            real_videos = random.sample(real_videos, max_videos_per_class)
        if len(fake_videos) > max_videos_per_class:
            fake_videos = random.sample(fake_videos, max_videos_per_class)

    metadata = []
    
    for class_name, videos, label in [("real", real_videos, 0), ("fake", fake_videos, 1)]:
        if not videos: continue
        
        out_class_dir = processed_path / class_name
        os.makedirs(out_class_dir, exist_ok=True)
        
        print(f"Processing {len(videos)} videos in class '{class_name}'...")
        
        for i, vid_path in enumerate(videos):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(videos)} videos in {class_name}...")
            cap = cv2.VideoCapture(str(vid_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                continue
            
            frame_indices = [int(j * total_frames / num_frames) for j in range(num_frames)]
            
            vid_out_dir = out_class_dir / vid_path.stem
            os.makedirs(vid_out_dir, exist_ok=True)
            
            for idx, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # Bounding box simulated by center crop
                    h, w, _ = frame.shape
                    size = min(h, w)
                    cy, cx = h//2, w//2
                    cropped = frame[cy-size//2:cy+size//2, cx-size//2:cx+size//2]
                    resized = cv2.resize(cropped, (224, 224))
                    
                    frame_name = f"frame_{idx:03d}.jpg"
                    frame_path = vid_out_dir / frame_name
                    cv2.imwrite(str(frame_path), resized)
                    
                    metadata.append({
                        "video": vid_path.name,
                        "frame": frame_name,
                        "path": f"{class_name}/{vid_path.stem}/{frame_name}",
                        "label": label
                    })
            cap.release()
            
    if metadata:
        df = pd.DataFrame(metadata)
        # 80/20 train/val split
        train_df = df.sample(frac=0.8, random_state=42)
        val_df = df.drop(train_df.index)
        
        metadata_dir = Path("datasets/metadata") if Path("datasets").exists() else Path("../../datasets/metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        train_df.to_csv(metadata_dir / "train.csv", index=False)
        val_df.to_csv(metadata_dir / "val.csv", index=False)
        print(f"Preprocessing complete. Extracted {len(metadata)} frames.")
        print("Metadata saved.")
        return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", default="datasets/raw/FaceForensics++_C23")
    parser.add_argument("--processed_dir", default="datasets/processed")
    parser.add_argument("--limit", type=int, default=100, help="Max videos per class to process for local execution")
    args = parser.parse_args()
    
    # Adjust paths if run from ai_training dir
    if not os.path.exists(args.raw_dir) and os.path.exists("../../" + args.raw_dir):
        args.raw_dir = "../../" + args.raw_dir
        args.processed_dir = "../../" + args.processed_dir
        
    preprocess_dataset(args.raw_dir, args.processed_dir, max_videos_per_class=args.limit)
