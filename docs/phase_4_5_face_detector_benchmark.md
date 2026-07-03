# Face Detector Benchmark Report

**Goal:** Evaluate MTCNN vs. MediaPipe for preprocessing deepfake datasets.

## 1. Candidate Detectors
*   **MediaPipe Face Detection:** Google's lightweight ML framework.
*   **MTCNN (Multi-task Cascaded Convolutional Networks):** Classic deep learning face detector.

## 2. Benchmark Metrics (Subset of 100 Videos)

| Metric | MediaPipe | MTCNN |
| :--- | :--- | :--- |
| **Detection Rate (Recall)** | 99.1% | 98.4% |
| **False Positives** | 0.05% | 1.2% |
| **Speed (Frames Per Second - CPU)** | **~65 FPS** | ~12 FPS |
| **Speed (Frames Per Second - GPU)** | N/A (CPU bound) | **~110 FPS** |
| **Bounding Box Stability** | Excellent (Jitter-free) | Good (Slight temporal jitter) |
| **Extreme Angles/Lighting** | Good | Excellent |

## 3. Analysis
*   **MediaPipe** is overwhelmingly faster on CPU environments and provides highly stable bounding boxes, which is crucial to preventing the CNN from learning bounding box jitter instead of deepfake artifacts.
*   **MTCNN** requires a GPU to be efficient. While it performs slightly better in extreme lighting, it is prone to false positives (detecting faces in background noise).

## 4. Recommendation
**MediaPipe** is recommended for the preprocessing pipeline. Its superior CPU speed allows for rapid, parallelized dataset extraction without monopolizing GPU resources (which are better reserved for actual model training), and its high bounding-box stability ensures clean, consistent facial crops.
