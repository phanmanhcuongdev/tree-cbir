"""V2 evaluation, run from repository root. Local cache stores independently timed baseline."""
from oracle import *
import argparse,pickle,time,statistics,sys,subprocess
from tree_cbir.segmentation.trunk import segment_trunk
from tree_cbir.segmentation.trunk_v2 import refine
from PIL import ImageFont
def shape(m):
    ys=np.flatnonzero(m.any(axis=1))
    samples=ys[::max(1,len(ys)//30)]
    axis=[(int(np.median(np.where(m[y])[0])),int(y)) for y in samples]
    return axis,float(np.median(m.sum(axis=1)[ys])) if len(ys) else None
def summary(rows):
    nums=lambda k:np.array([r[k] for r in rows])
    return dict(images=len(rows),usable=sum(r['grade']=='usable' for r in rows),partial=sum(r['grade']=='partial' for r in rows),failed=sum(r['grade']=='failed' for r in rows),reliable=sum(r['status']=='RELIABLE_DETECTION' for r in rows),incorrect_reliable=sum(r['status']=='RELIABLE_DETECTION' and r['grade']!='usable' for r in rows),mean_iou=nums('iou').mean(),median_iou=np.median(nums('iou')),mean_precision=nums('precision').mean(),mean_recall=nums('recall').mean(),median_seconds=np.median(nums('seconds')),max_seconds=max(nums('seconds')),mean_seconds=nums('seconds').mean())
def run(v,hold=False):
    folder=O/('independent_validation' if hold else '')/('baseline' if not v else f'iteration_{v:02}')
    folder.mkdir(parents=True,exist_ok=True); sheets=folder/'contact_sheets';sheets.mkdir(exist_ok=True)
    cache=O/'baseline/cache';cache.mkdir(exist_ok=True)
    rows=[]
    for rec in records():
        n=rec['filename']; split=rec['set']
        if split not in (['C'] if hold else ['A','B']):continue
        rgb=np.array(Image.open(D/n)); r=ref(n); path=cache/(n+'.pkl')
        if not path.exists():
            t=time.perf_counter();prior=segment_trunk(rgb,method='hybrid');sec=time.perf_counter()-t
            path.write_bytes(pickle.dumps((prior,sec)))
        else:prior,sec=pickle.loads(path.read_bytes())
        t=time.perf_counter();p=refine(rgb,prior,v) if v else prior
        sec+=time.perf_counter()-t
        m=p.mask;metrics_row=metrics(m,r); g=metrics_row
        grade='usable' if g['iou']>=.5 and g['precision']>=.7 and g['recall']>=.6 else 'partial' if g['iou']>=.2 else 'failed'
        axis,width=shape(m); truth,_=shape(r); by=np.flatnonzero(r.any(axis=1))
        error=np.linalg.norm((np.array(p.base)-[np.median(np.where(r[by[-1]])[0]),by[-1]])/[768,1024]) if len(by) and p.base else None
        cen=np.mean([min(np.linalg.norm((np.array(q)-a)/[768,1024]) for a in axis) for q in truth]) if truth and axis else None
        diag=p.diagnostics
        row=dict(filename=n,set=split,grade=grade,**g,seconds=sec,area=int(m.sum()),bbox=p.bbox,base=p.base,upper=p.upper,centerline=axis,median_width=width,components=cv2.connectedComponents(m.astype(np.uint8))[0]-1,base_error=error,centerline_error=cen,boundary_support=diag.get('paired_boundary_support',diag.get('ground_support')),green_fraction=diag.get('strong_green_fraction'),confidence=p.confidence,status=diag['status'],reason=diag.get('reason'),backend=diag.get('backend','paired')); rows.append(row)
        panel=Image.new('RGB',(1152,300),'white');draw=ImageDraw.Draw(panel)
        draw.text((5,1),f"{n}   {row['status']} {p.confidence:.2f}    IoU {g['iou']:.2f}    P {g['precision']:.2f}    R {g['recall']:.2f}",fill='black',font_size=16)
        over=rgb.copy();over[m]=rgb[m]*.52+np.array([255,45,15])*.48
        cand=rgb.copy()
        for point in axis:cv2.circle(cand,point,5,(255,0,255),-1)
        region=diag.get('selected_roi')
        if region:
            l,t,w,h=region;cv2.rectangle(cand,(l,t),(l+w,t+h),(255,230,0),3)
        for j,(label,img) in enumerate(zip(['Original','Whole tree: unavailable','Proposal / axis','Mask','Overlay','Approx. reference'],[rgb,None,cand,m,over,r])):
            draw.text((192*j+3,22),label,fill='black')
            if img is not None:panel.paste(Image.fromarray(img).convert('RGB').resize((192,256)),(192*j,42))
        idx=sum(k['set']==split for k in rows)-1
        sp=sheets/f'{split}_{idx//4+1}.jpg'
        if idx%4:sheet=Image.open(sp).convert('RGB')
        else:sheet=Image.new('RGB',(1152,1200),'white')
        sheet.paste(panel,(0,300*(idx%4)));sheet.save(sp,quality=94)
    writecsv(folder/'results.csv',rows)
    stats={s:summary([r for r in rows if r['set']==s]) for s in sorted({r['set'] for r in rows})}
    (folder/'summary.json').write_text(json.dumps(stats,indent=2));print(v,[(s,a['usable'],round(a['mean_iou'],3),a['incorrect_reliable']) for s,a in stats.items()],flush=True)
    if v and not hold:
        snapshot(folder/'source_snapshot.zip')
        (folder/'config.json').write_text(json.dumps(dict(version=v,prior='hybrid',source_sha256=digest(folder/'source_snapshot.zip'))))
        test=subprocess.run([sys.executable,'-m','pytest','tests/unit','-q'],capture_output=True,text=True)
        (folder/'pytest_results.txt').write_text(test.stdout+test.stderr)
        if test.returncode:raise RuntimeError('unit regression')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('versions',nargs='+',type=int);parser.add_argument('--hold',action='store_true');args=parser.parse_args()
    for v in args.versions:run(v,args.hold)

