"""Exact observer primaries, for recalculation only, never fresh native claims."""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';ROOT=RUN.parents[6]
# Locate relative to the workspace rather than requiring an old machine path.
WORK=next(p for p in RUN.parents if (p/'documantacion vital/cores').is_dir())
plans={
 '07':['HOLDOUT_LOCKS/C7H03_REPROGRAMMABLE_FUNCTIONAL_MATTER.json','RESULTS/C7H03_reprogrammable_functional_matter.json'],
 '15':['NEW_RAW_TELEMETRY/EXPANSION_FRESH_CONFIRMATION.json','NEW_FRESH_CHALLENGES/CHALLENGE_MANIFEST.json','MECHANISM_ADJUDICATION_EXPANSION.json','FINAL_REPORT.md','FINAL_FRONTIER.md']+[f'NEW_HOLDOUT_LOCKS/C15XC{i:02}.json'for i in range(1,7)],
 '16':['FINAL_HOLDOUTS/'+n+'_'+kind+'.json'for n in('OPERATOR','CAPABILITY','PROBABILITY','QUANTUM_SCALE')for kind in('CHALLENGES','HOLDOUT_RESULTS')]+['HOLDOUT_LOCKS/'+n+'.json'for n in('FUNCTIONAL_CAPABILITY_LOCK','OCCUPANCY_OPERATOR_LOCK','PROBABILITY_MEASURE_LOCK','QUANTUM_SCALE_LOCK')]+['CROSS_SCALE_INFORMATION_FLOW.json','CROSS_SCALE_MEMORY.json','FINAL_REPORT.md'],
 '17':['EXTENSION/HOLDOUT/C17E03_POLICY_REPAIR_HOLDOUT.json','EXTENSION/HOLDOUT/C17E05_R0_FACTOR_HOLDOUT.json','EXTENSION/FREEZE/C17E03_POLICY_REPAIR_LOCK.json','EXTENSION/FREEZE/C17E05_R0_FACTOR_LOCK.json','EXTENSION/CHALLENGES/C17E03_POLICY_REPAIR_CHALLENGE.json','EXTENSION/CHALLENGES/C17E05_R0_FACTOR_CHALLENGE.json','EXTENSION/CORE17_DEFINITIVE_CLOSURE.json','FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json','CORE17_FINAL_REPORT.md','CORE17_FINAL_FRONTIER.md']}
index=CORE/'documentacion/INDICE_MIEMBROS.json';idx=json.loads(index.read_text(encoding='utf8'));known={r['sha256']for r in idx['paths'].values()};pending=[];frozen={'schema':'DEE_CORE.observer_recalculation_inputs.v1','mode':'Recalculation of immutable historical primaries, NOT a new native execution','sources':[]}
for prefix,names in plans.items():
 archive=next((WORK/'documantacion vital/cores').glob(prefix+'*RESULTADOS.zip'));archive_hash=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
 with zipfile.ZipFile(archive)as z:
  if prefix in('15','16','17'):
   names=sorted(set(names)|{i.filename for i in z.infolist()if i.filename.endswith('.py')})
  for member in names:
   data=z.read(member);h=hashlib.sha256(data).hexdigest();logical='cores/CORE'+prefix+'/'+member
   if logical in idx['paths']:assert idx['paths'][logical]['sha256']==h
   else:pending.append((logical,data,h,archive.name,archive_hash,member))
   frozen['sources'].append({'logical':logical,'sha256':h,'bytes':len(data),'archive':archive.name,'archive_sha256':archive_hash,'member':member})
if pending:
 store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
 with gzip.open(store,'ab',compresslevel=9)as target:
  for logical,data,h,archive_name,archive_hash,member in pending:
   if h not in known:
    target.write(json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n');known.add(h)
   idx['paths'][logical]={'sha256':h,'bytes':len(data),'origin':{'archive':archive_name,'archive_sha256':archive_hash,'member':member,'reason':'Exact primary, lock, challenge or preserved source/helper dependency for the historical observer branches; recalculation does not claim fresh native execution.'}}
 idx['content_store_sha256']=hashlib.file_digest(store.open('rb'),'sha256').hexdigest();index.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(CORE/'configuraciones/OBSERVADORES_PRIMARIOS_CONGELADOS.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'sources':len(frozen['sources']),'added':len(pending)}))
