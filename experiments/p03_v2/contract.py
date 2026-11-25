from evaluate import *
from tree_cbir.segmentation.trunk_measurements import measurements
from tree_cbir.features.trunk import extract_trunk_features
from dataclasses import asdict
report=[]
for folder in [O/'iteration_10',O/'independent_validation/iteration_10']:
    for row in csv.DictReader((folder/'results.csv').open()):
        n=row['filename'];rgb=np.array(Image.open(D/n));prior,_=pickle.loads((O/'baseline/cache'/(n+'.pkl')).read_bytes())
        p=refine(rgb,prior,10); i=measurements(p)
        assert p.mask.shape==rgb.shape[:2] and p.mask.dtype==bool and int(p.mask.sum())==int(row['area']) and p.expected_height==.6*rgb.shape[0]
        g=metrics(p.mask,ref(n));assert abs(g['iou']-float(row['iou']))<1e-12
        values,valid,_=extract_trunk_features(rgb,p.mask,p.expected_height)
        assert len(values)==len(valid)==9
        assert all(i.quality[k]!='measured' for k in ('base','upper','width') if row['status']!='RELIABLE_DETECTION')
        # Independent image evidence measured on the final boundary and its interior.
        lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)
        gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        edges=cv2.dilate(cv2.Canny(gray,35,90),np.ones((5,5),np.uint8))>0
        border=p.mask & (cv2.erode(p.mask.astype(np.uint8),np.ones((3,3),np.uint8))==0)
        report.append(dict(filename=n,split=row['set'],status=row['status'],computable=valid.tolist(),area=int(p.mask.sum()),expected_height=p.expected_height,mask_boundary_edge_support=float(edges[border].mean()) if border.any() else None,mask_green_fraction=float((lab[:,:,1][p.mask]<110).mean()) if p.mask.any() else None,**asdict(i)))
(O/'final/downstream_contract_validation.json').write_text(json.dumps(report,indent=1))

