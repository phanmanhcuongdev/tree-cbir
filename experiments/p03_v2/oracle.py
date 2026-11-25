from prepare import *
import cv2,numpy as np
from tree_cbir.segmentation.trunk_localization import track_boundaries
from tree_cbir.segmentation.trunk import _grabcut_corridor
def ref(n):
    a=json.loads((O/'references/A.json').read_text())['rows']
    if n in a: strips=[a[n]]; scale=2
    else:
        p=O/'references/B.json'
        if n not in json.loads(p.read_text())['rows']: p=O/'references/C.json'
        strips=json.loads(p.read_text())['rows'][n]; scale=4
    mask=np.zeros((1024,768),np.uint8)
    for rows in strips:
        poly=[(l,y) for y,l,r in rows]+[(r,y) for y,l,r in rows[::-1]]
        if poly: cv2.fillPoly(mask,[np.array(poly,np.int32)*scale],1)
    return mask.astype(bool)
def metrics(m,r):
    t=np.sum(m&r)
    return dict(iou=float(t/max(1,(m|r).sum())),precision=float(t/max(1,m.sum())),recall=float(t/max(1,r.sum())),dice=float(2*t/max(1,m.sum()+r.sum())))
def writecsv(p,rows):
    with p.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def records():return list(csv.DictReader((O/'splits/manifest.csv').open()))
if __name__=='__main__':
    out=[]
    for rec in records():
        n=rec['filename']
        if rec['set'] not in ['A','B']: continue
        rgb=np.asarray(Image.open(D/n))
        r=ref(n); y=int(np.quantile(np.where(r)[0],.67)); xs=np.where(r[y])[0]
        lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB).astype(np.float32)
        seed=(y,int(xs[0]),int(xs[-1])+1)
        axis=track_boundaries(lab,seed); obs=np.zeros_like(r)
        for yy,l,h in axis:
            pix=lab[yy,l:h]; obs[yy,l:h]=np.linalg.norm(pix-np.median(pix,axis=0),axis=1)<=24
        m=_grabcut_corridor(rgb,lab,axis,obs) if axis else obs
        folder='iteration_03' if rec['set']=='A' else 'independent_validation_contact_sheets'
        old=np.array(Image.open(OLD/folder/'samples'/f'{Path(n).stem}_mask.png'))>0
        out.append(dict(filename=n,seed=seed,baseline_iou=metrics(old,r)['iou'],**metrics(m,r)))
    writecsv(O/'root_cause_analysis/oracle.csv',out)
    print([(x['filename'],round(x['baseline_iou'],2),round(x['iou'],2)) for x in out])

