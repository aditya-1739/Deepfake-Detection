# Dataset Report - FaceForensics++ (Proposed)

**Date generated:** 2026-06-26

## 1. Overview
* **Dataset Name:** FaceForensics++
* **Source:** Technical University of Munich (TUM)
* **License:** Non-commercial, Academic Use Only

## 2. Statistics
* **Number of Videos:** 1,000 original videos, 4,000 manipulated videos (Deepfakes, Face2Face, FaceSwap, NeuralTextures)
* **Total Videos:** 5,000
* **Expected Images (Frames):** ~1,500,000 frames (at 10 frames sampled per video)
* **Number of Classes:** 2 (Real, Fake)
* **Distribution:** 
  * Real: 20% (1,000 videos)
  * Fake: 80% (4,000 videos) - *Note: Imbalance will be handled during DataLoaders by class weighting.*

## 3. Split Configuration
* **Train Split:** 70% (3,500 videos)
* **Validation Split:** 15% (750 videos)
* **Test Split:** 15% (750 videos)

## 4. Integrity and Storage
* **Missing or Corrupt Files:** 0 known
* **Expected Storage Requirements:** ~30 GB (compressed videos), ~150 GB (extracted uncompressed frames)
* **Expected Preprocessing Pipeline:**
  1. Extract frames from raw mp4 files using OpenCV.
  2. Detect faces using MTCNN.
  3. Crop and align faces with 20% padding.
  4. Resize to 224x224 and save to `datasets/processed/`.
