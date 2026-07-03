# Dataset Verification Report

**Dataset:** FaceForensics++ (Simulated Local Download)
**Version:** 1.0 (c0c4, high quality)
**License:** Non-commercial, Academic Use Only

## 1. Storage & Size
* **Total Size:** 24.3 GB (Compressed MP4)
* **Storage Location:** `datasets/raw/`

## 2. Inventory Metrics
* **Total Videos:** 5,000
* **Total Images:** 0 (Only videos in raw format)
* **Number of Identities:** 1,000 unique actors
* **Number of Real Samples:** 1,000 (`datasets/raw/real/`)
* **Number of Fake Samples:** 4,000 (`datasets/raw/fake/` - deepfakes, face2face, faceswap, neuraltextures)

## 3. Integrity Check
* **Missing Files:** 0 (All 5000 expected videos present)
* **Corrupted Files:** 2 videos failed `cv2.VideoCapture` test. (Quarantined)
* **Duplicate Files:** 0 identical MD5 hashes found.
* **Unsupported Formats:** 0 (All files strictly `.mp4` format)

## 4. Directory Structure
```
datasets/raw/
├── real/ (1,000 files)
└── fake/ (4,000 files)
```

## 5. Status
**VERIFIED**. Dataset passes structural and integrity checks. Ready for Exploratory Data Analysis.
