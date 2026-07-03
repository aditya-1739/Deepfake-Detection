# Dataset Acquisition Guide

This guide details how to legally obtain the **Celeb-DF-v2** dataset and inject it into the pipeline for validation.

## Step 1: Legal Acquisition
1. Go to the official Celeb-DF GitHub repository: `https://github.com/yuezunli/celeb-deepfakeforensics`
2. Scroll to the **Download** section and click the Google Form link to request access.
3. Fill out the academic/research usage form.
4. An automated email will be sent containing the Google Drive / Baidu download links.

## Step 2: Downloading a Representative Subset
You do not need to download the full 5.5GB immediately if you just want to pass the Phase 5 Validation.
1. Access the provided Google Drive link.
2. Download **10 videos from the `Celeb-real`** folder.
3. Download **10 videos from the `Celeb-synthesis`** folder.

## Step 3: Directory Placement
Place the downloaded files into the local repository exactly as follows:

```text
Deepfake-Detection-main/
└── datasets/
    └── raw/
        ├── real/
        │   ├── id0_0000.mp4
        │   └── ... (9 more videos)
        └── fake/
            ├── id0_id1_0000.mp4
            └── ... (9 more videos)
```

## Step 4: Run Validation
Once the files are correctly placed, the AI Pipeline can dynamically read them.
Run the validation script to generate your actual statistics:
```bash
python ai_training/utils/validate_dataset.py --raw_dir datasets/raw
```

## Step 5: Run Small-Scale Preprocessing
To verify frame extraction and face detection:
```bash
python ai_training/data/preprocess.py --raw_dir datasets/raw --processed_dir datasets/processed
```

Once these steps succeed without throwing errors, notify the system to freeze configurations and proceed to Phase 6.
