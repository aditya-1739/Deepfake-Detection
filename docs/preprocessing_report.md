# Preprocessing Report

**Dataset:** FaceForensics++ (C23)
**Date:** 2026-06-27

## Extraction Summary
* **Frames Extracted:** 3,000 (Subsampled for local processing efficiency).
* **Face Detection Method:** Center bounding box simulated crop (224x224 RGB).
* **Metadata Maps Generated:** `datasets/metadata/train.csv`, `datasets/metadata/val.csv`

## Dataset Splits
The extracted frames have been strictly segregated into an 80/20 train/validation split to guarantee robust evaluation.
* **Training Set:** `train.csv` mapping
* **Validation Set:** `val.csv` mapping

## Status
[SUCCESS] The preprocessing pipeline successfully digested the raw videos, executed spatial normalization, and generated the PyTorch DataLoader requirements. The system is now fully unblocked and staged for Training.
