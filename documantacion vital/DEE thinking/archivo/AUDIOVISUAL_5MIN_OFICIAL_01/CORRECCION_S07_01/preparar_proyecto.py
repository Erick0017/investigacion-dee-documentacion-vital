"""Non-destructive snapshot and isolated working copy for one-scene correction."""
from pathlib import Path
import shutil,json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parent;source=R/'trabajo'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert source.is_dir() and (source/'producir_5min.py').is_file()
intact=H/'PROYECTO_INTACTO';candidate=H/'PROYECTO_S07';assert not intact.exists() and not candidate.exists()
intact.mkdir();candidate.mkdir()
files=list(source.rglob('*'));inputs=[p for p in files if p.is_file()]
manifest=[{'path':str(p.relative_to(source)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs]
print('Snapshot:',len(inputs),'files,',sum(x['bytes'] for x in manifest),'bytes',flush=True)
shutil.copytree(source,intact/'trabajo')
rootfiles=[p for p in R.iterdir() if p.is_file()]
for p in rootfiles:shutil.copy2(p,intact/p.name)
shutil.copytree(intact/'trabajo',candidate/'trabajo')
for p in rootfiles:shutil.copy2(p,candidate/p.name)
assert all(sha(intact/'trabajo'/x['path'])==x['sha256'] for x in manifest)
assert all(sha(candidate/'trabajo'/x['path'])==x['sha256'] for x in manifest)
plan=json.loads((candidate/'trabajo/PLAN_3D_14_ESCENAS.json').read_text('utf8'))
def find_cases(o):
 if isinstance(o,dict):
  if str(o.get('id','')).startswith('07_') and 'points' in o:return [o]
  return [p for v in o.values() for p in find_cases(v)]
 if isinstance(o,list):return [p for v in o for p in find_cases(v)]
 return []
cases={p['id']:p for p in find_cases(plan)}
assert len(cases)>=6
(candidate/'trabajo/CASOS_S07_CONGELADOS.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),'utf8')
rec={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),
 'intact_copy':str(intact),'isolated_working_copy':str(candidate),'files':manifest,
 'root_files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in rootfiles],
 'case_ids':list(cases),'verified_both_copies':True,'scope':'Only S07 graphics will be edited; no simulation, audio synthesis or replacement of the full film.'}
(H/'PRESERVACION_PROYECTO.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print('Verified both complete project copies. Cases:',list(cases),flush=True)
