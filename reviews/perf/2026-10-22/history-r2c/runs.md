# Frame time: how far the runs agree

2 complete runs (run-1, run-2). Per segment, each run's median offscreen time (the view drawn back to back, the GPU kept busy), presented frame period and GPU time, and each one's spread (largest minus smallest) as a share of their mean. Acceptance: within about 3%.

| Segment | Offscreen (ms) | Spread | Frame (ms) | Spread | GPU (ms) | Spread |
| --- | --- | --- | --- | --- | --- | --- |
| quad-bc7-street@1300-drizzle | 13.84 / 13.77 | 0.5% | 12.42 / 12.45 | 0.2% | 24.64 / 24.69 | 0.2% |
| quad-bc7-street@1300-drizzle/history-off | 13.17 / 13.20 | 0.2% | 11.98 / 11.96 | 0.1% | 23.69 / 23.82 | 0.6% |
| quad-bc7-tile8-street@1300-drizzle | 15.54 / 15.58 | 0.3% | 13.66 / 13.67 | 0.1% | 27.01 / 27.04 | 0.1% |
| quad-bc7-tile8-street@1300-drizzle/history-off | 13.18 / 13.19 | 0.1% | 11.98 / 11.94 | 0.3% | 23.61 / 23.86 | 1.1% |
| quad-bc7-nearmip-street@1300-drizzle | 13.85 / 13.76 | 0.7% | 12.42 / 12.44 | 0.1% | 24.64 / 24.66 | 0.1% |
| quad-bc7-nearmip-street@1300-drizzle/history-off | 13.21 / 13.23 | 0.2% | 12.02 / 11.94 | 0.6% | 23.82 / 23.74 | 0.4% |
| quad-bc7-nearmip-tile8-street@1300-drizzle | 15.65 / 15.61 | 0.3% | 13.79 / 13.73 | 0.4% | 27.21 / 27.15 | 0.2% |
| quad-bc7-nearmip-tile8-street@1300-drizzle/history-off | 13.26 / 13.20 | 0.4% | 12.00 / 11.99 | 0.1% | 23.73 / 23.93 | 0.8% |
| quad-bc7-tri-street@1300-drizzle | 13.86 / 13.76 | 0.7% | 12.46 / 12.42 | 0.3% | 24.70 / 24.74 | 0.2% |
| quad-bc7-tri-street@1300-drizzle/history-off | 13.22 / 13.22 | 0.0% | 12.01 / 11.95 | 0.5% | 23.81 / 23.77 | 0.2% |
| quad-bc7-tri-tile8-street@1300-drizzle | 15.79 / 15.62 | 1.1% | 13.75 / 13.72 | 0.2% | 27.05 / 27.07 | 0.1% |
| quad-bc7-tri-tile8-street@1300-drizzle/history-off | 13.23 / 13.20 | 0.2% | 12.04 / 11.97 | 0.6% | 23.76 / 23.79 | 0.1% |
| quad-bc7-lod-street@1300-drizzle | 13.79 / 13.76 | 0.2% | 12.46 / 12.40 | 0.5% | 24.72 / 24.66 | 0.2% |
| quad-bc7-lod-street@1300-drizzle/history-off | 13.21 / 13.20 | 0.0% | 12.03 / 11.99 | 0.3% | 23.85 / 23.83 | 0.1% |
| quad-bc7-lod-tile8-street@1300-drizzle | 15.73 / 15.58 | 1.0% | 13.80 / 13.70 | 0.7% | 27.29 / 27.11 | 0.6% |
| quad-bc7-lod-tile8-street@1300-drizzle/history-off | 13.23 / 13.19 | 0.3% | 12.03 / 11.99 | 0.3% | 23.69 / 23.92 | 1.0% |
| quad-bc7-grad-street@1300-drizzle | 14.07 / 13.97 | 0.7% | 12.66 / 12.59 | 0.5% | 25.12 / 25.04 | 0.3% |
| quad-bc7-grad-street@1300-drizzle/history-off | 13.31 / 13.17 | 1.0% | 12.01 / 11.99 | 0.2% | 23.85 / 23.66 | 0.8% |
| quad-bc7-grad-tile8-street@1300-drizzle | 16.04 / 15.95 | 0.6% | 14.06 / 13.99 | 0.5% | 27.84 / 27.65 | 0.7% |
| quad-bc7-grad-tile8-street@1300-drizzle/history-off | 13.24 / 13.19 | 0.3% | 12.01 / 11.96 | 0.4% | 23.67 / 23.86 | 0.8% |
| quad-bc7-direct-street@1300-drizzle | 13.82 / 13.75 | 0.5% | 12.53 / 12.38 | 1.2% | 24.79 / 24.68 | 0.5% |
| quad-bc7-direct-street@1300-drizzle/history-off | 13.22 / 13.20 | 0.2% | 12.04 / 11.96 | 0.7% | 23.89 / 23.65 | 1.0% |
| quad-bc7-direct-tile8-street@1300-drizzle | 15.65 / 15.53 | 0.8% | 13.85 / 13.66 | 1.4% | 27.11 / 27.06 | 0.2% |
| quad-bc7-direct-tile8-street@1300-drizzle/history-off | 13.23 / 13.21 | 0.2% | 12.02 / 11.98 | 0.3% | 23.75 / 23.90 | 0.7% |
| quad-bc7-tex2d-street@1300-drizzle | 13.79 / 13.77 | 0.1% | 12.47 / 12.41 | 0.5% | 24.66 / 24.72 | 0.2% |
| quad-bc7-tex2d-street@1300-drizzle/history-off | 13.21 / 13.17 | 0.4% | 11.98 / 12.00 | 0.2% | 23.71 / 23.70 | 0.0% |
| quad-bc7-tex2d-tile8-street@1300-drizzle | 15.64 / 15.51 | 0.8% | 13.80 / 13.67 | 0.9% | 27.15 / 27.05 | 0.4% |
| quad-bc7-tex2d-tile8-street@1300-drizzle/history-off | 13.22 / 13.22 | 0.0% | 11.98 / 11.94 | 0.3% | 23.68 / 23.78 | 0.4% |
| quad-bc7-alu-street@1300-drizzle | 13.33 / 13.32 | 0.0% | 12.13 / 12.16 | 0.2% | 24.11 / 24.21 | 0.4% |
| quad-bc7-alu-street@1300-drizzle/history-off | 13.21 / 13.20 | 0.0% | 11.97 / 12.00 | 0.2% | 23.83 / 23.76 | 0.3% |
| quad-bc7-alu-tile8-street@1300-drizzle | 13.59 / 13.55 | 0.3% | 12.31 / 12.35 | 0.4% | 24.37 / 24.38 | 0.0% |
| quad-bc7-alu-tile8-street@1300-drizzle/history-off | 13.24 / 13.22 | 0.2% | 12.03 / 11.95 | 0.7% | 23.76 / 23.92 | 0.7% |
| quad-bc7-two-street@1300-drizzle | 13.85 / 13.76 | 0.6% | 12.42 / 12.42 | 0.0% | 24.69 / 24.70 | 0.0% |
| quad-bc7-two-street@1300-drizzle/history-off | 13.23 / 13.16 | 0.5% | 12.00 / 12.00 | 0.0% | 23.86 / 23.77 | 0.4% |
| quad-bc7-two-tile8-street@1300-drizzle | 15.67 / 15.58 | 0.6% | 13.84 / 13.73 | 0.8% | 27.32 / 27.15 | 0.6% |
| quad-bc7-two-tile8-street@1300-drizzle/history-off | 13.22 / 13.16 | 0.5% | 11.99 / 11.94 | 0.4% | 23.73 / 23.83 | 0.4% |
| quad-bc7-two-tri-street@1300-drizzle | 13.82 / 13.77 | 0.4% | 12.45 / 12.39 | 0.5% | 24.72 / 24.67 | 0.2% |
| quad-bc7-two-tri-street@1300-drizzle/history-off | 13.25 / 13.15 | 0.8% | 11.98 / 11.93 | 0.5% | 23.84 / 23.73 | 0.5% |
| quad-bc7-two-tri-tile8-street@1300-drizzle | 15.69 / 15.60 | 0.6% | 13.86 / 13.78 | 0.6% | 27.23 / 27.25 | 0.1% |
| quad-bc7-two-tri-tile8-street@1300-drizzle/history-off | 13.24 / 13.19 | 0.4% | 12.01 / 11.96 | 0.4% | 23.70 / 23.93 | 1.0% |
| quad-bc7-two-nearmip-street@1300-drizzle | 13.84 / 13.78 | 0.4% | 12.47 / 12.42 | 0.4% | 24.64 / 24.73 | 0.4% |
| quad-bc7-two-nearmip-street@1300-drizzle/history-off | 13.23 / 13.17 | 0.4% | 12.05 / 11.96 | 0.7% | 23.76 / 23.74 | 0.1% |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle | 15.83 / 15.65 | 1.1% | 14.00 / 13.79 | 1.5% | 27.57 / 27.26 | 1.1% |
| quad-bc7-two-nearmip-tile8-street@1300-drizzle/history-off | 13.26 / 13.18 | 0.6% | 11.99 / 11.94 | 0.4% | 23.72 / 23.82 | 0.4% |
| quad-rgba8-street@1300-drizzle | 13.93 / 13.84 | 0.6% | 12.45 / 12.44 | 0.1% | 24.81 / 24.86 | 0.2% |
| quad-rgba8-street@1300-drizzle/history-off | 13.22 / 13.18 | 0.3% | 12.02 / 11.98 | 0.3% | 23.90 / 23.81 | 0.4% |
| quad-rgba8-tile8-street@1300-drizzle | 15.71 / 15.61 | 0.7% | 13.81 / 13.69 | 0.9% | 27.31 / 27.10 | 0.8% |
| quad-rgba8-tile8-street@1300-drizzle/history-off | 13.20 / 13.17 | 0.2% | 12.00 / 11.95 | 0.4% | 23.68 / 23.87 | 0.8% |
| quad-rgba8-tri-street@1300-drizzle | 13.86 / 13.79 | 0.5% | 12.46 / 12.44 | 0.2% | 24.80 / 24.77 | 0.1% |
| quad-rgba8-tri-street@1300-drizzle/history-off | 13.19 / 13.15 | 0.3% | 11.98 / 11.94 | 0.3% | 23.76 / 23.69 | 0.3% |
| quad-rgba8-tri-tile8-street@1300-drizzle | 15.70 / 15.57 | 0.9% | 13.83 / 13.71 | 0.9% | 27.21 / 27.08 | 0.5% |
| quad-rgba8-tri-tile8-street@1300-drizzle/history-off | 13.23 / 13.19 | 0.3% | 12.00 / 11.97 | 0.3% | 23.67 / 23.83 | 0.7% |
| quad-rgba8-nearmip-street@1300-drizzle | 13.86 / 13.83 | 0.2% | 12.48 / 12.46 | 0.1% | 24.76 / 24.74 | 0.1% |
| quad-rgba8-nearmip-street@1300-drizzle/history-off | 13.26 / 13.21 | 0.4% | 12.01 / 11.92 | 0.7% | 23.87 / 23.71 | 0.7% |
| quad-rgba8-nearmip-tile8-street@1300-drizzle | 15.69 / 15.64 | 0.3% | 13.86 / 13.78 | 0.6% | 27.28 / 27.24 | 0.2% |
| quad-rgba8-nearmip-tile8-street@1300-drizzle/history-off | 13.20 / 13.21 | 0.1% | 12.02 / 11.96 | 0.5% | 23.67 / 23.92 | 1.1% |

Worst spread: offscreen 1.1%, frame 1.5%, GPU 1.1%.
