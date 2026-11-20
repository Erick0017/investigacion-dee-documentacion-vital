"""Offline auditor: recalculate observations without importing DEE or a model."""
import hashlib,json,sys,zipfile
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def lines(path):
 with path.open(encoding='utf-8') as f:
  for line in f:
   if line.strip():yield json.loads(line)
def recalculate():
 result={'schema':'CPC8.offline.recalculation.v1','participant_imported':False,'errors':[],'formulas':{
  'coverage':'responses with covered=true / all requested responses; missing and wrong are distinct',
  'correct':'covered response.value == current reference in auditor-only observation row',
  'retention':'correct covered answers for previously acquired, still-valid relations / such queries',
  'reg_delivery':'state>0, semantic!=5, load3, direction(1,0,0), exact tick15, fixed requested delivery class',
  'uncertainty':'No coverage is not converted to numeric zero; a valid opposite direction is an error, not silence.'}}
 wheel=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
 result['wheel_sha256']=sha(wheel)
 if result['wheel_sha256']!='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c':result['errors'].append('WHL identity differs')
 with zipfile.ZipFile(wheel) as z:
  names=[n for n in z.namelist() if n.endswith('.pyd')]
  result['native_sha256_in_wheel']=hashlib.sha256(z.read(names[0])).hexdigest()
 if result['native_sha256_in_wheel']!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d':result['errors'].append('PYD identity differs')
 tests=list(lines(ROOT/'resultados/regresion_producto45/TESTS.jsonl'))
 result['product_tests']={'count':len(tests),'statuses':dict(Counter(r['status'] for r in tests))}
 if len(tests)!=82 or any(r['status']!='SUCCESS' for r in tests):result['errors'].append('Product test count/status discrepancy')
 scores=defaultdict(lambda:Counter(queries=0,covered=0,correct=0,wrong=0,missing=0))
 for r in lines(ROOT/'comparadores/OBSERVACIONES.jsonl'):
  response=r['response'];covered=bool(response.get('covered',response.get('coverage',response.get('value') is not None)))
  value=response.get('value');correct=covered and value==r['expected'];s=scores[r['method']]
  s['queries']+=1;s['covered']+=int(covered);s['correct']+=int(correct);s['wrong']+=int(covered and not correct);s['missing']+=int(not covered)
  if bool(r['correct'])!=correct:result['errors'].append('Comparator auditor row differs from primary response')
 result['comparison']={k:dict(v) for k,v in scores.items()}
 reg=[]
 for folder in sorted((ROOT/'resultados/regulacion').iterdir()):
  if not (folder/'RESULT.json').exists():continue
  reported=load(folder/'RESULT.json');config=load(folder/'CONFIG.json');frames=load(folder/'OBSERVACIONES.json')
  frame=next(f['panel'] for f in frames if f['tick']==15);context=config['evaluation_context_not_given_to_participant'];count=0;other=0
  for p in config['geometry']['regulators']:
   r=frame['delivery.'+p['id']];valid=r['state']>0 and r['semantic']!=5 and r['s_reg']==3 and r['direction']==[1,0,0]
   count+=int(valid and p['source']==context);other+=int(valid and p['source']!=context)
  if(count,other)!=(reported['requested_deliveries'],reported['other_deliveries']):result['errors'].append('Regulatory metric differs: '+folder.name)
  reg.append({'case_id':folder.name,'requested':count,'other':other})
 result['regulation']=reg
 matrix=load(ROOT/'revision/NSM65_EVIDENCIAS.json')
 result['catalogue_count']=matrix['count'];result['semantic_level_counts']=matrix.get('local_prime_levels',{})
 result['semantic_count_scope']='Counts are read from individually argued evidence cards, not automatically inferred from directional responses.'
 parity=load(ROOT/'resultados/sem01_reproduccion/HISTORICAL_PARITY.json')
 result['SEM01_physical_parity']={k:parity[k] for k in('initial_physical_equal','final_physical_equal')}
 if not all(result['SEM01_physical_parity'].values()):result['errors'].append('Historical SEM01 physical parity differs')
 manifest=ROOT/'MANIFEST.json'
 if manifest.exists():
  m=load(manifest);mismatches=[]
  for row in m['files']:
   path=ROOT/row['path']
   if not path.is_file() or path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:mismatches.append(row['path'])
  result['payload_manifest']={'files':len(m['files']),'mismatches':mismatches}
  result['errors']+=['Manifest mismatch: '+n for n in mismatches]
 else:result['payload_manifest']={'state':'Not yet sealed; manifest supplied in final ZIP'}
 result['technical_recalculation_ok']=not result['errors']
 result['scope']='Technical data/maths checks only. Does not issue a global scientific verdict, infer65meanings, or replace physical clean reproduction.'
 return result
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 data=recalculate();print(json.dumps(data,ensure_ascii=False,indent=2));raise SystemExit(0 if data['technical_recalculation_ok'] else 1)
