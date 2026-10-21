"""A crown's value, measured on rendered frames: its pixels (saturated against the grey clay), their luminance spread from
the tenth to the ninetieth percentile ("raw"), and the same after a blur within the crown so leaf-scale speckle averages
out ("form": what a lobe's lit cap against its shaded sides gives). Judged beside the eye, never instead of it.

    python blender/tools/crown_value.py <frame.png> [<frame.png> ...]     (needs numpy and Pillow)
"""
import sys, numpy as np
from PIL import Image
def box_blur(x, r):
    # separable box blur, three passes (about Gaussian)
    for _ in range(3):
        c=np.cumsum(np.pad(x,((r+1,r),(0,0)),mode='edge'),axis=0); x=(c[2*r+1:]-c[:-2*r-1])/(2*r+1)
        c=np.cumsum(np.pad(x,((0,0),(r+1,r)),mode='edge'),axis=1); x=(c[:,2*r+1:]-c[:,:-2*r-1])/(2*r+1)
    return x
def spread(path, box=(240,0,1680,1080), sat=22, r=6):
    a=np.asarray(Image.open(path).convert('RGB').crop(box)).astype(float)
    m=((a.max(axis=2)-a.min(axis=2))>sat).astype(float)
    lum=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
    Lb=box_blur(lum*m,r); Mb=box_blur(m,r)
    sel=(m>0)&(Mb>0.6)
    form=(Lb/np.maximum(Mb,1e-3))[sel]
    v=lum[m>0]; p=np.percentile(v,[10,90]); q=np.percentile(form,[10,90])
    return "raw %.0f  form %.0f  (median %.0f)"%(p[1]-p[0], q[1]-q[0], np.median(v))
for f in sys.argv[1:]:
    print("%-55s %s"%(f.split('/')[-1], spread(f)))
