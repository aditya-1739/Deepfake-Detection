import os
import argparse
import hashlib
from pathlib import Path
import cv2

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def validate_dataset(raw_dir):
    print("=========================================")
    print("       REAL DATASET VALIDATION REPORT    ")
    print("=========================================\n")
    
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        print(f"[ERROR] Directory {raw_dir} does not exist. Please follow the Acquisition Guide.")
        return False

    real_videos = []
    fake_videos = []
    
    # Map for FaceForensics++
    if (raw_path / 'original').exists():
        real_dirs = ['original', 'real', 'Celeb-real']
        fake_dirs = ['Deepfakes', 'Face2Face', 'FaceSwap', 'NeuralTextures', 'FaceShifter', 'fake', 'Celeb-synthesis']
        
        for r_dir in real_dirs:
            if (raw_path / r_dir).exists():
                real_videos.extend(list((raw_path / r_dir).glob('**/*.mp4')))
                
        for f_dir in fake_dirs:
            if (raw_path / f_dir).exists():
                fake_videos.extend(list((raw_path / f_dir).glob('**/*.mp4')))
    else:
        # Default real/fake
        real_dir = raw_path / 'real'
        fake_dir = raw_path / 'fake'
        if not real_dir.exists() and not fake_dir.exists():
            print(f"[ERROR] Expected dataset subdirectories inside {raw_dir}.")
            return False
        real_videos = list(real_dir.glob('**/*.mp4'))
        fake_videos = list(fake_dir.glob('**/*.mp4'))

    all_videos = real_videos + fake_videos

    print(f"Total Videos Found: {len(all_videos)}")
    print(f" -> Real Videos: {len(real_videos)}")
    print(f" -> Fake Videos: {len(fake_videos)}\n")

    if len(all_videos) == 0:
        print("[WARNING] No .mp4 files found. Validation aborted.")
        return False

    # Check Class Balance
    real_pct = len(real_videos) / len(all_videos) * 100
    fake_pct = len(fake_videos) / len(all_videos) * 100
    print(f"Class Balance: {real_pct:.1f}% Real / {fake_pct:.1f}% Fake")

    # Check Corrupted Files
    corrupted = []
    # Limit corruption check for massive datasets to prevent hours of processing for validation report
    check_limit = min(len(all_videos), 200) 
    print(f"\nChecking {check_limit} videos for corruption...")
    import random
    random.seed(42)
    sample_videos = random.sample(all_videos, check_limit)
    
    for video in sample_videos:
        cap = cv2.VideoCapture(str(video))
        if not cap.isOpened():
            corrupted.append(video.name)
        else:
            # Read first frame to ensure it's valid
            ret, _ = cap.read()
            if not ret:
                corrupted.append(video.name)
        cap.release()

    print(f"Corrupted Files Found in sample: {len(corrupted)}")
    for c in corrupted:
        print(f" - {c}")
        
    print("\n=========================================")
    if len(corrupted) == 0 and len(all_videos) > 0:
        print("[SUCCESS] Dataset passes integrity verification!")
        return True
    else:
        print("[WARNING] Dataset requires manual cleanup before preprocessing.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate physical deepfake dataset.")
    parser.add_argument("--raw_dir", type=str, default="../../datasets/raw", help="Path to raw dataset")
    args = parser.parse_args()
    
    validate_dataset(args.raw_dir)
