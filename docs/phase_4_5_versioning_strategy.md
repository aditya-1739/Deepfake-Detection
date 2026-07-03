# Dataset Versioning Strategy

**Goal:** Ensure 100% reproducibility of the training data over time.

## 1. Directory Structure

Processed datasets will not overwrite each other. They will be strictly versioned within `datasets/processed/` and `datasets/metadata/`.

```
datasets/
├── raw/
├── processed/
│   ├── v1.0_uniform15_mediapipe_224/
│   └── v1.1_uniform30_mtcnn_256/
└── metadata/
    ├── v1.0_train.csv
    ├── v1.0_val.csv
    └── v1.0_test.csv
```

## 2. Naming Convention
`v[MAJOR].[MINOR]_[SAMPLING]_[DETECTOR]_[RESOLUTION]`
*   **MAJOR:** Changes in the underlying raw dataset (e.g., adding a new deepfake corpus).
*   **MINOR:** Changes to preprocessing (bounding box padding, normalization).
*   **SAMPLING:** The frame extraction logic (e.g., `uniform15`).
*   **DETECTOR:** The face extraction model (e.g., `mediapipe`).
*   **RESOLUTION:** Final crop size (e.g., `224`).

## 3. Metadata Generation
Every version will programmatically generate a JSON file alongside the CSVs containing:
* Timestamp of generation.
* Total frames extracted.
* Albumentation configurations (if any offline augmentations are applied, though online is preferred).
* Script commit hash used during extraction.

## 4. Usage
The active dataset version is specified in `ai_training/config/dataset.yaml`. Model registries will trace their exact dataset version origin.
