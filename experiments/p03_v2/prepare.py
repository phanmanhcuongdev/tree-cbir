from pathlib import Path
import csv, json, re, hashlib, shutil, zipfile
from PIL import Image, ImageDraw
D=Path('data/standardized')
O=Path(__file__).resolve().parent
OLD=O.parent/'p03_2_auto'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p):
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
        for pattern in ['src/**/*.py','tests/**/*.py','scripts/*.py','docs/**/*.md','*.toml','*.md','requirements*.txt','sql/*.sql','outputs/trunk/p03_2_v2/*.py']:
            for f in Path('.').glob(pattern): z.write(f)
def sheet(names,label):
    for j in range(0,len(names),4):
        s=Image.new('RGB',(4*212,282),'white')
        d=ImageDraw.Draw(s)
        for i,n in enumerate(names[j:j+4]):
            t=Image.open(D/n).resize((192,256))
            x=i*212+16
            s.paste(t,(x,20))
            d.text((x,0),n,fill='black')
            for k in range(0,256,16):
                d.text((x-16,k+16),str(k),fill='black',font_size=9)
                for a in range(0,192,16): d.point((x+a,k+20),fill='magenta')
            for a in range(32,192,32): d.text((x+a-5,10),str(a),fill='black',font_size=9)
        s.save(O/'references'/f'{label}{j//4}.png')
if __name__=='__main__':
    for d in ['baseline','references','splits','root_cause_analysis','final','independent_validation']: (O/d).mkdir(exist_ok=True)
    snapshot(O/'baseline/source_snapshot.zip')
    shutil.copy(OLD/'references/annotations.json',O/'references/A.json')
    A=list(json.loads((O/'references/A.json').read_text())['rows'])
    B=[r['filename'] for r in csv.DictReader((OLD/'independent_visual_review.csv').open())]
    used=set(A+B)
    for f in O.parent.glob('*/*'):
        if f.is_relative_to(O): continue
        for p in ([f] if f.is_file() else f.rglob('*')):
            if p.suffix.lower() in ['.csv','.md','.json','.txt']: used.update(re.findall(r'(?<![\w])\d+\.jpg',p.read_text(encoding='utf-8-sig',errors='ignore')))
            m=re.match(r'(\d+)_',p.name)
            if m: used.add(m[1]+'.jpg')
    names=sorted(Path('outputs/preprocessing/standardization/valid_candidates.txt').read_text().splitlines())
    pool=sorted(set(names)-used)
    C=[pool[(2*i+1)*len(pool)//48] for i in range(24)]
    with (O/'splits/manifest.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['filename','set','sha256'])
        for n in names: w.writerow([n,'A' if n in A else 'B' if n in B else 'C' if n in C else 'excluded' if n in used else 'unused',digest(D/n)])
    (O/'splits/design.txt').write_text(f'Lexicographic manifest, exclude prior trunk evidence names then midpoint of 24 equal index strata. Pool {len(pool)}. A/B development only. C sealed until final freeze.')
    sheet(B,'B')

