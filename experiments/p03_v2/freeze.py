from prepare import *
from oracle import records
F=O/'final'
snapshot(F/'source_snapshot.zip')
config=dict(version=10,entry="segment_trunk(rgb, method='v2')",prior="hybrid",default="hybrid",source={str(p):digest(p) for p in sorted(Path('src/tree_cbir/segmentation').glob('trunk*.py'))},archive_sha256=digest(F/'source_snapshot.zip'),selection="maximum joint development usable count among zero incorrect reliable, preserved four A cases")
(F/'best_configuration.json').write_text(json.dumps(config,indent=2))
(F/'freeze.sha256').write_text(digest(F/'best_configuration.json')+' best_configuration.json')
sheet([r['filename'] for r in records() if r['set']=='C'],'C')

