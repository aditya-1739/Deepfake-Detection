# Production Inference Benchmark Report

**Date:** 2026-07-28  
**Model Backbone:** EfficientNet-B0  
**Model File Size:** 15.58 MB (PyTorch state dictionary)  
**Lightning Checkpoint Size:** 46.35 MB  

## 1. Single Image Inference Latencies
Measurements are averaged over 100 runs after 20 warmup cycles.

| Hardware / Device | Mean Latency (ms) | Median Latency (ms) | 95th Percentile (ms) | Frames Per Second (FPS) |
| :--- | :--- | :--- | :--- | :--- |
| **CPU (Intel/AMD)** | 80.67 ms | 80.69 ms | 84.94 ms | 12.4 FPS |
| **GPU (RTX 4060)** | 14.06 ms | 14.0 ms | 15.96 ms | 71.1 FPS |

---

## 2. Video Inference Latencies (15 Frames)
Simulates video processing pipeline: loads 15 frames, crops face boundaries, and runs batch/sequential inference.

| Hardware / Device | Mean Latency (s) | Median Latency (s) | 95th Percentile (s) | Frames Per Second (FPS) |
| :--- | :--- | :--- | :--- | :--- |
| **CPU (Intel/AMD)** | 1.187 s | 1.187 s | 1.198 s | 12.63 FPS |
| **GPU (RTX 4060)** | 0.215 s | 0.212 s | 0.25 s | 69.77 FPS |

---

## 3. Resource Utilization Summary
- **Torch Loading Time (Model loading):** 1.0664 seconds
- **CPU Memory Usage (Process RAM):** 120.0 MB
- **Max VRAM Allocated (GPU Memory):** 101.58 MB
