# Dataset Statistics Report

**Dataset:** FaceForensics++ (C23)
**Date:** 2026-06-27

## Class Distribution (Raw Videos)
* **Real Videos:** 1,000 (16.7%)
* **Fake Videos:** 5,000 (83.3%)
* **Total Videos:** 6,000

*Observation: The extreme 1:5 class imbalance mandates class weighting in the PyTorch `CrossEntropyLoss` module (or focal loss). The updated `dataset.yaml` config reflects a 5:1 real-to-fake weight ratio.*

## Video Types (Fake Distributions)
Each manipulation technique contributes equally to the fake class:
* **Deepfakes (Autoencoder):** 20% of fakes
* **Face2Face (Graphics):** 20% of fakes
* **FaceSwap (Graphics):** 20% of fakes
* **NeuralTextures (GAN):** 20% of fakes
* **FaceShifter (GAN):** 20% of fakes

## Expected Extracted Dimensions
* **Target Frame Output:** 224x224 RGB
* **Frames Per Video Target:** 15
* **Total Anticipated Frames (Full Extraction):** 90,000 frames.

*(Note: For iterative local execution, preprocessing may operate on a subsample of this total to prevent memory/storage overload).*
