# Frame time: how far the runs agree

2 complete runs (run-1, run-2). Per segment, each run's median offscreen time (the view drawn back to back, the GPU kept busy), presented frame period and GPU time, and each one's spread (largest minus smallest) as a share of their mean. Acceptance: within about 3%.

| Segment | Offscreen (ms) | Spread | Frame (ms) | Spread | GPU (ms) | Spread |
| --- | --- | --- | --- | --- | --- | --- |
| eye-foot@1600-low-sun | 34.44 / 39.90 | 14.7% | 28.85 / 32.44 | 11.7% | 51.25 / 46.32 | 10.1% |
| street@1600-low-sun | 29.44 / 32.87 | 11.0% | 24.65 / 29.37 | 17.5% | 42.74 / 42.43 | 0.7% |
| high@1600-low-sun | 28.91 / 31.28 | 7.9% | 27.27 / 27.64 | 1.4% | 32.19 / 43.46 | 29.8% |
| steps@1600-low-sun | 30.93 / 33.66 | 8.5% | 27.00 / 29.28 | 8.1% | 38.37 / 51.66 | 29.5% |
| eye-foot@1600-low-sun/beams-copy | 34.60 / 37.94 | 9.2% | 29.80 / 31.64 | 6.0% | 50.79 / 52.85 | 4.0% |
| street@1600-low-sun/beams-copy | 29.95 / 32.81 | 9.1% | 24.83 / 26.76 | 7.5% | 42.63 / 44.51 | 4.3% |
| high@1600-low-sun/beams-copy | 29.05 / 32.13 | 10.1% | 24.66 / 26.83 | 8.4% | 43.12 / 44.92 | 4.1% |
| steps@1600-low-sun/beams-copy | 31.28 / 35.03 | 11.3% | 26.47 / 28.95 | 8.9% | 45.47 / 47.83 | 5.1% |
| eye-foot@1600-low-sun/beams-nocomposite | 34.64 / 37.10 | 6.9% | 28.36 / 30.95 | 8.7% | 49.54 / 51.88 | 4.6% |
| street@1600-low-sun/beams-nocomposite | 30.09 / 32.03 | 6.3% | 24.43 / 26.10 | 6.6% | 41.79 / 44.57 | 6.4% |
| high@1600-low-sun/beams-nocomposite | 29.54 / 30.81 | 4.2% | 24.04 / 26.11 | 8.3% | 41.83 / 44.87 | 7.0% |
| steps@1600-low-sun/beams-nocomposite | 31.20 / 32.82 | 5.1% | 25.92 / 27.19 | 4.8% | 44.29 / 47.16 | 6.3% |
| eye-foot@1600-low-sun/-beams | 33.29 / 35.74 | 7.1% | 27.48 / 29.38 | 6.7% | 49.13 / 52.53 | 6.7% |
| street@1600-low-sun/-beams | 27.77 / 29.54 | 6.2% | 23.00 / 24.77 | 7.4% | 40.47 / 43.11 | 6.3% |
| high@1600-low-sun/-beams | 27.36 / 30.67 | 11.4% | 22.53 / 24.19 | 7.1% | 40.28 / 43.60 | 7.9% |
| steps@1600-low-sun/-beams | 29.60 / 33.26 | 11.7% | 24.29 / 27.27 | 11.5% | 43.56 / 47.97 | 9.6% |

Worst spread: offscreen 14.7%, frame 17.5%, GPU 29.8%.
