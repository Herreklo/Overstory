# Shimmer

The fine change between consecutive frames (motion_measure.py), in 8-bit levels of luma: its mean per pair (median and worst over the pairs), and the share of pixels whose fine change is over 3.0 levels. Blur 1.5 px.

| Sequence | Frames | Shimmer, mean | Median | Worst pair | Flicker, mean | Worst pair |
| --- | --- | --- | --- | --- | --- | --- |
| 1600-low-sun-still | 60 | 0.4694 | 0.4733 | 0.5111 | 0.152% | 0.277% |
| 1600-low-sun-walk | 150 | 1.1701 | 1.1830 | 1.2496 | 7.153% | 7.820% |
| 1600-low-sun-pan | 180 | 1.0240 | 1.0229 | 1.0750 | 4.394% | 4.882% |
| 1600-low-sun-crane | 180 | 1.0455 | 1.1110 | 1.2597 | 4.696% | 6.010% |
| 1600-low-sun-walk-nodither | 150 | 0.8633 | 0.8845 | 0.9236 | 6.704% | 7.244% |
| 1600-low-sun-pan-nodither | 180 | 0.6809 | 0.6782 | 0.7036 | 4.074% | 4.383% |
| 1600-low-sun-crane-nodither | 180 | 0.7111 | 0.7822 | 0.9315 | 4.381% | 5.693% |
| 1600-low-sun-still-crawl | 60 | 0.4700 | 0.4741 | 0.5118 | 0.153% | 0.280% |
| 1600-low-sun-walk-crawl | 150 | 3.9691 | 3.6891 | 5.3061 | 10.687% | 11.431% |
| 1600-low-sun-still-smooth | 60 | 0.4692 | 0.4732 | 0.5110 | 0.152% | 0.277% |
| 1600-low-sun-walk-smooth | 150 | 1.1728 | 1.1863 | 1.2557 | 7.063% | 7.750% |
| 1600-low-sun-still-nodither | 60 | 0.0000 | 0.0000 | 0.0000 | 0.000% | 0.000% |
