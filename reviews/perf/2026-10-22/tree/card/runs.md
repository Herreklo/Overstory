# Frame time: how far the runs agree

2 complete runs (run-1, run-2). Per segment, each run's median offscreen time (the view drawn back to back, the GPU kept busy), presented frame period and GPU time, and each one's spread (largest minus smallest) as a share of their mean. Acceptance: within about 3%.

| Segment | Offscreen (ms) | Spread | Frame (ms) | Spread | GPU (ms) | Spread |
| --- | --- | --- | --- | --- | --- | --- |
| street@1300-drizzle | 40.90 / 39.71 | 2.9% | 33.57 / 33.29 | 0.8% | 60.46 / 59.97 | 0.8% |
| high@1300-drizzle | 45.17 / 43.96 | 2.7% | 36.79 / 36.55 | 0.7% | 68.11 / 67.63 | 0.7% |
| street@1300-drizzle-nobirch | 28.40 / 28.57 | 0.6% | 23.41 / 23.51 | 0.4% | 41.49 / 41.29 | 0.5% |
| high@1300-drizzle-nobirch | 29.12 / 28.83 | 1.0% | 23.84 / 23.80 | 0.2% | 43.40 / 42.91 | 1.1% |

Worst spread: offscreen 2.9%, frame 0.8%, GPU 1.1%.
