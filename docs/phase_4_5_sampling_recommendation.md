# Frame Sampling Strategy Recommendation

**Goal:** Determine the optimal frame sampling frequency for extracting images from the dataset's raw videos.

## 1. Evaluated Strategies

1.  **Extract All Frames (30 FPS):** ~2.3 million frames. Extreme redundancy (adjacent frames are near-identical). Massively inflates storage (100+ GB) and slows down epochs without proportional accuracy gains.
2.  **1 FPS (1 frame per second):** ~75,000 frames. Extremely fast training, but throws away useful temporal variations and subtle deepfake artifacts.
3.  **5 FPS:** ~375,000 frames. Good balance, but still contains significant redundancy for static talking-head videos.
4.  **Uniform Sampling (Fixed N frames per video):** Extracts exactly N evenly spaced frames across the video duration (e.g., N=15).

## 2. Analysis of Uniform Sampling (N=15)
*   **Dataset Size:** 5,000 videos * 15 frames = 75,000 images.
*   **Storage Requirements:** ~3.5 GB of cropped faces.
*   **Training Time:** ~2-3 minutes per epoch on modern GPUs.
*   **Artifact Capture:** By spreading the 15 frames uniformly across the video, we capture different head poses, lighting conditions, and potential temporal artifacts (glitches) without saturating the dataset with duplicate frames.

## 3. Recommendation
**Uniform Sampling (N=15 frames per video).**
This strategy normalizes the dataset (every video contributes equally to the loss function regardless of its duration), minimizes storage/compute overhead, and safely removes temporal redundancy. If the model underfits, this parameter can be increased to N=30 in subsequent dataset versions.
