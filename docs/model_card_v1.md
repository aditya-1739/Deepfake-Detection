# Model Card: Deepfake Detection Model V1.0

## Model Details
- **Model Name:** Deepfake Detection Model
- **Version:** v1.0
- **Architecture:** EfficientNet-B0 (backbone from `timm` library)
- **Training Date:** 2026-07-28
- **Evaluation Date:** 2026-07-28
- **Intended Use:** Detection of face manipulations in images and video streams.
- **Out-of-Scope Use:** Anything other than facial deepfake detection.

## Dataset & Split Configuration
- **Dataset Source:** FaceForensics++ C23
- **Total Training Split:** 2,040 frames (136 videos, 70% split)
- **Total Validation Split:** 435 frames (29 videos, 15% split)
- **Total Holdout Test Split:** 450 frames (30 videos, 15% split)
- **Video Overlap:** Exactly 0 (Strict video-level split)

## Performance Metrics (Holdout Test Set)
- **Accuracy:** 45.56%
- **Precision:** 0.4490
- **Recall (Sensitivity):** 0.3911
- **Specificity:** 0.5200
- **F1 Score:** 0.4181
- **ROC-AUC:** 0.4479
- **PR-AUC:** 0.4731

## Ethical Considerations
- Deepfake detection models can exhibit bias if the training demographics are skewed. FaceForensics++ contains a specific set of actors, and performance on the general public should be evaluated prior to critical deployment.
- This model is intended as a helper utility and should not be used as the sole source of truth in legal or investigative actions.

## Hardware & Software Configuration
- **Hardware Used:** NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)
- **Software Stack:** PyTorch, PyTorch Lightning, Albumentations, timm

## Future Improvements
- Incorporate temporal face consistency checking.
- Perform training on larger datasets (e.g. Celeb-DF, DFDC) for enhanced generalization.
