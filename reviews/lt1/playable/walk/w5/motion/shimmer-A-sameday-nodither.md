# Shimmer

The fine change between consecutive frames (motion_measure.py), in 8-bit levels of luma: its mean per pair (median and worst over the pairs), and the share of pixels whose fine change is over 3.0 levels. Blur 1.5 px.

| Sequence | Frames | Shimmer, mean | Median | Worst pair | Flicker, mean | Worst pair |
| --- | --- | --- | --- | --- | --- | --- |
| 1600-low-sun-walk | 150 | 1.1858 | 1.2008 | 1.2756 | 7.255% | 7.972% |
| 1600-low-sun-still | 60 | 0.4719 | 0.4758 | 0.5140 | 0.156% | 0.285% |
| 1600-low-sun-still-nodither | 60 | 0.0000 | 0.0000 | 0.0000 | 0.000% | 0.000% |
| 1600-low-sun-walk-nodither | 150 | 0.8852 | 0.9101 | 0.9584 | 6.773% | 7.352% |
