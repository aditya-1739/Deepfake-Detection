# Model Card: Deepfake Detection Version 1

## Model Description
* **Architecture:** EfficientNet-B0 (Timm)
* **Task:** Binary Image Classification (0 = Real, 1 = Fake)
* **Intended Use:** Detection of synthesized/manipulated faces in video frames.
* **Release Date:** TBD
* **Model Size:** TBD MB

## Dataset Used
* **Primary Dataset:** Celeb-DF-v2
* **Training Splits:** 80% Train, 10% Validation, 10% Holdout Test
* **Face Detector:** MediaPipe
* **Frame Sampling:** Uniform 15 frames per video

## Training Configuration
* **Optimizer:** AdamW
* **Learning Rate:** TBD (Cosine Annealing)
* **Batch Size:** TBD
* **Epochs:** TBD
* **Hardware:** TBD

## Evaluation Metrics (Holdout Test Set)
* **Accuracy:** TBD%
* **Precision:** TBD%
* **Recall:** TBD%
* **F1-Score:** TBD%
* **ROC-AUC:** TBD

## Benchmark Results
* **Average Image Inference Latency:** TBD ms
* **Average Video Processing Time (15 frames):** TBD s

## Limitations
* Evaluated strictly on Celeb-DF-v2 data distribution. Performance on wild/unseen deepfake generators (e.g., modern diffusion models) is unverified.
* Highly compressed social media videos may degrade accuracy.
