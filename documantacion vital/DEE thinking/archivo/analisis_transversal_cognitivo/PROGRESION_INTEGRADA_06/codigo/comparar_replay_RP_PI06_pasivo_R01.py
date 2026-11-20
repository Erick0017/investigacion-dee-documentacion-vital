"""Root/reader: closed cold replay versus its BEFORE-EXECUTION frozen Native cut.

Stdlib only; no DEE imports, owner, reproduction, material query or criterion
change. Root recipe expectations are already fixed at SHA45f8...9d26c.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
RECIPE='pi06_transitorio_izq0_y_continuacion_R01';RECIPE_SHA='45f8b8b6ba0b89a74966548bc689ba5e4f045bd5af52a326e5cdb2ec1ea9d26c'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1';BRIDGE='DEE.Cognitive.PI02.continuous_workbench.R04'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked comparison source/output')
def diff(a,b,path=''):
 if type(a)is not type(b):return [{'pointer':path,'original':a,'replay':b}]
 if isinstance(a,dict):
  out=[]
  for key in sorted(set(a)|set(b)):
   p=path+'/'+str(key).replace('~','~0').replace('/','~1')
   if key not in a or key not in b:out.append({'pointer':p,'original':a.get(key),'replay':b.get(key),'key_added_or_removed':True})
   else:out+=diff(a[key],b[key],p)
  return out
 if isinstance(a,list):
  out=[]
  for i in range(max(len(a),len(b))):
   if i>=len(a)or i>=len(b):out.append({'pointer':path+'/'+str(i),'original':a[i]if i<len(a)else None,'replay':b[i]if i<len(b)else None,'list_item_added_or_removed':True})
   else:out+=diff(a[i],b[i],path+'/'+str(i))
  return out
 return []if a==b else[{'pointer':path,'original':a,'replay':b}]
def main(a):
 summary=a.resultado.resolve(strict=True);root=summary.parent;regular(summary);result=read(summary);contextfile=root/'CONTEXTO_EJECUCION.json';context=read(contextfile)
 if result.get('status')!='COMPLETED'or result.get('owner_closed_coherently')is not True:raise ValueError('Only completed coherent real replay, never a live world')
 recipefile=RP/'recetas'/(RECIPE+'.json');recipe=read(recipefile)
 if sha(recipefile)!=RECIPE_SHA or context['recipe_sha256']!=RECIPE_SHA or context['fixed_recipe']!=recipe or result['recipe']!=RECIPE:raise ValueError('No changing the predetermined recipe or expected Native result')
 if context['variant']!='izq0_sin_captura' or any(step['literal'].get('captura')!='normal'for step in recipe['variants'][context['variant']]['batches'][0]):raise ValueError('Exact fixed no-capture variant only')
 expected=recipe['expected_final_Native'];source=Path(expected['source_frozen_snapshot']).resolve(strict=True);regular(source)
 if not source.is_relative_to((P/'estados/candidato/sistema/estado/checkpoints').resolve())or sha(source)!=expected['source_snapshot_sha256']:raise ValueError('Exact original frozen global snapshot is required; never current DISC pointer')
 cardfile=root/'sistema/estado/vidas'/result['life']/'VIDA.json';card=read(cardfile);actual=(root/'sistema'/card['snapshot']).resolve(strict=True);regular(actual)
 if not actual.is_relative_to((root/'sistema/estado').resolve())or sha(actual)!=card['snapshot_sha256']:raise ValueError('Actual closed replay pointer differs')
 before={str(p):sha(p)for p in(summary,contextfile,source,cardfile,actual,recipefile)}
 parserfile=RP/'observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI06_cold_passive_parser',parserfile);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
 left=parser.snapshot_view(source);right=parser.snapshot_view(actual)
 if any(left[k]!=expected[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts')):raise ValueError('Original frozen source no longer matches predeclared expected fields')
 fields={k:{'original':left[k],'replay':right[k],'equal':left[k]==right[k]}for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')}
 changes=[];unexpected=[]
 for key in sorted(set(left['metadata'])|set(right['metadata'])):
  lv=left['metadata'].get(key);rv=right['metadata'].get(key)
  if lv==rv:continue
  try:leaves=diff(json.loads(lv),json.loads(rv))
  except(Exception):leaves=[{'pointer':'','original_encoded_sha256':None if lv is None else hashlib.sha256(lv.encode()).hexdigest(),'replay_encoded_sha256':None if rv is None else hashlib.sha256(rv.encode()).hexdigest(),'not_decoded':True}]
  known=key in(SYSTEM,SERVICE)or(key==BRIDGE and all(v['pointer'].startswith('/paused_intervals')for v in leaves))
  item={'key':key,'all_changed_JSON_leaves':leaves,'declared_identity_service_or_paused_interval_scope':known};changes.append(item)
  if not known:unexpected.append(key)
 stable=all(sha(Path(p))==h for p,h in before.items())
 receipts=result.get('native_receipts',{});dose=all(receipts.get(k)==v for k,v in {'unique_requested':529,'applied':529,'rejected':0,'pending_or_other':0}.items())
 native_equal=all(v['equal']for v in fields.values());valid=native_equal and not unexpected and stable and dose and result.get('criteria_met')is True
 proof={'schema':'DEE.PI06.cold_replay_material_passivity.full_Native.R01','recipe_sha256_before_execution':RECIPE_SHA,'real_replay_summary':str(summary),
  'life_id':result['life'],'original_global_snapshot':str(source),'actual_normal_snapshot':str(actual),'fields':fields,'all_complete_Native_fields_equal':native_equal,
  'metadata_changes':changes,'unexpected_metadata_keys':unexpected,'all_metadata_keys_considered':sorted(set(left['metadata'])|set(right['metadata'])),
  'native_dose529_all_applied':dose,'technical_recipe_criteria_met':result.get('criteria_met'),'inspected_files_before_sha256':before,'sources_unchanged_during_read':stable,
  'bounded_comparison_criteria_met':valid,'Native_executed_by_this_comparison':False,'new_ticks':0,
  'scope':'Exact full Native RAW/clocks/header/interfaces/agenda/receipts prefix after actual cold replay normal vs original global. Every metadata difference listed. Local no-capture passivity/repetition only; not new learning, independent lives, general regulation or universal observer neutrality.'}
 if a.salida:
  output=a.salida.resolve(strict=False);regular(output)
  if not output.is_relative_to((P/'control').resolve())or output.exists():raise ValueError('Fresh PI06/control proof only')
  with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'comparison_criteria_met':valid,'all_complete_Native_fields_equal':native_equal,'unexpected_metadata_keys':unexpected,'dose529':dose,
  'proof':None if a.salida is None else str(a.salida),'proof_sha256':None if a.salida is None else sha(a.salida),'Native_executed':False},ensure_ascii=False))
 return 0 if valid else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--resultado',type=Path,required=True);ap.add_argument('--salida',type=Path);raise SystemExit(main(ap.parse_args()))
