from pathlib import Path
import hashlib,json,shutil,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
sys.path.insert(0,str(P/'codigo'))
from registrar_RP_R02_PI07_R01 import members,sha,regular
src=P/'codigo/RP_R02_EP04_PREPARADA/ANALISIS';dest=C/'reproducibilidad/materiales/PI07_ANALISIS_R02_8'
regular(src);regular(dest)
manifest=src/'MANIFIESTO_ESTABLE.json'
if sha(manifest)!='87a3e9a297680a87fd202718f9a93ad9f9447d33031119e6e58db5b16a9cbae7':raise ValueError('Exact portable analysis required')
m=json.loads(manifest.read_text('utf8'));before=members(src,m['files'])
if dest.exists():raise FileExistsError('No overwrite')
shutil.copytree(src,dest,symlinks=False)
after=members(dest,m['files'])
if before!=after or sha(dest/manifest.name)!=sha(manifest):raise RuntimeError('Analysis copy mismatch')
proof={'schema':'DEE.PI07.stable_RP_analysis_preservation.v1','source':str(src),'destination':str(dest),'manifest_sha256':sha(manifest),'Native_ticks':0,'verified':after}
out=P/'control/ANALISIS_RP_R02_PI07_PRESERVADO.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
