# Shimmer

The fine change between consecutive frames (motion_measure.py), in 8-bit levels of luma: its mean per pair (median and worst over the pairs), and the share of pixels whose fine change is over 3.0 levels. Blur 1.5 px.

| Sequence | Frames | Shimmer, mean | Median | Worst pair | Flicker, mean | Worst pair |
| --- | --- | --- | --- | --- | --- | --- |
| 1600-low-sun-walk | 150 | 1.1858 | 1.2009 | 1.2755 | 7.255% | 7.971% |
| 1600-low-sun-still | 60 | 0.4721 | 0.4760 | 0.5143 | 0.160% | 0.290% |
| 1600-low-sun-walk-nodither | 150 | 0.8847 | 0.9093 | 0.9578 | 6.772% | 7.353% |
