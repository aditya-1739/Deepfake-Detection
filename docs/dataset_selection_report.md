# Dataset Selection Report

**Goal:** Recommend the optimal Deepfake dataset for Version 1 of this academic/student project.

## Candidate Datasets Evaluated

### 1. Deepfake Detection Challenge (DFDC)
* **Source:** Facebook/Meta via Kaggle.
* **Size:** ~470 GB.
* **Licensing:** Restricted to non-commercial research; requires Kaggle account verification.
* **Pros:** Massive diversity, extreme variations in lighting and compression.
* **Cons:** Far too large for a student project starting out. High barrier to entry for storage and compute.

### 2. FaceForensics++
* **Source:** TUM.
* **Size:** ~100 GB.
* **Licensing:** Academic usage; requires signing a legal form and submitting it to the authors.
* **Pros:** Highly structured, covers 4 distinct manipulation methods.
* **Cons:** Manual verification process by authors can delay acquisition.

### 3. Celeb-DF (v2)
* **Source:** University at Albany, SUNY.
* **Size:** ~5.5 GB (MP4 format).
* **Licensing:** Free for academic research. Requires filling out a Google Form to receive an automated download link.
* **Pros:** Small storage footprint (5.5 GB), exceptionally high visual quality making it a harder challenge than older datasets, no wait time for manual approval.
* **Cons:** Less variation in demographics compared to DFDC.

## Final Recommendation: Celeb-DF-v2
**Celeb-DF-v2** is strongly recommended as the Version 1 dataset. 
* **Storage Feasibility:** At ~5.5 GB, it fits easily on a local drive and won't overwhelm local RAM/VRAM during processing.
* **High Quality:** The deepfakes in this dataset contain fewer obvious visual artifacts (like color mismatch) compared to earlier datasets, forcing the model to learn meaningful deepfake indicators.
* **Immediate Access:** The automated form approval means you can download it today and immediately continue the pipeline.
