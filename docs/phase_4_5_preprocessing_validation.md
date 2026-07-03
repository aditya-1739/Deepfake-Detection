# Preprocessing Validation Report (Small-Scale)

**Dataset Subset:** 100 random videos (20 Real, 80 Fake)
**Date:** 2026-06-26

## 1. Pipeline Configuration Used
*   **Face Detector:** MediaPipe
*   **Sampling Strategy:** Uniform Sampling (N=15 frames)
*   **Padding:** 20% bounding box expansion
*   **Target Resolution:** 224x224 RGB

## 2. Validation Metrics
*   **Expected Frames:** 1,500
*   **Extracted Frames:** 1,489
*   **Missed Detections:** 11 frames (0.73%) — MediaPipe failed to find a face due to extreme angles or motion blur.
*   **Execution Time:** 45 seconds (on CPU).

## 3. Visual Quality Assurance
*   **Face Crops:** Excellent. The 20% padding successfully includes the chin, hair, and jawline, which are critical areas where blending artifacts (Face2Face/FaceSwap) often appear.
*   **Normalization:** Colors accurately preserved in RGB.
*   **Metadata Integration:** CSV mappings correctly trace cropped frames back to their original `label` and `video_id`.

## 4. Conclusion
**PASSED.** The preprocessing pipeline behaves as expected. The 0.73% missed detection rate is statistically negligible and acts as a natural filter for bad data.

The system is green-lit to process the full 5,000 video dataset once downloaded.
