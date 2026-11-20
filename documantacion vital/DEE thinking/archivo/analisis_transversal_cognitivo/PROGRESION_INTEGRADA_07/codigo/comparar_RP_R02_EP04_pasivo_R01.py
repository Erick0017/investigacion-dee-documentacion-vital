"""Passive fixed EP04/EP08 Native comparisons after the one cold R02 replay.

No DEE, world loading or material query. Expectations were frozen in the RP
recipe before its Native run. Recording-pattern swap, not absence of observer.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
RECIPE='pi07_r02_8_ep04';RECIPE_SHA='4c1f8ba423a3a357783ca4af3e226649bb491a8acffbdc56e71c4d636051775b'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1';BRIDGE='DEE.Cognitive.PI02.continuous_workbench.R04';ENV='DEE.Cognitive.PI07.regulation.environment.R02'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked comparison source/output')
def diff(a,b,path=''):
 if type(a)is not type(b):return[{'pointer':path,'original':a,'replay':b}]
 if isinstance(a,dict):
  out=[]
  for key in sorted(set(a)|set(b)):
   pointer=path+'/'+str(key).replace('~','~0').replace('/','~1')
   if key not in a or key not in b:out.append({'pointer':pointer,'original':a.get(key),'replay':b.get(key),'key_added_or_removed':True})
   else:out+=diff(a[key],b[key],pointer)
  return out
 if isinstance(a,list):
  out=[]
  for i in range(max(len(a),len(b))):
   if i>=len(a)or i>=len(b):out.append({'pointer':path+'/'+str(i),'original':a[i]if i<len(a)else None,'replay':b[i]if i<len(b)else None,'list_item_added_or_removed':True})
   else:out+=diff(a[i],b[i],path+'/'+str(i))
  return out
 return[]if a==b else[{'pointer':path,'original':a,'replay':b}]
def compare(parser,source,actual,expected):
 if sha(source)!=expected['source_snapshot_sha256']:raise ValueError('Original frozen source changed')
 left=parser.snapshot_view(source);right=parser.snapshot_view(actual)
 names=('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')
 if any(left[k]!=expected[k]for k in names):raise ValueError('Frozen source does not match before-execution expected fields')
 fields={k:{'original':left[k],'replay':right[k],'equal':left[k]==right[k]}for k in names};changes=[];unexpected=[]
 for key in sorted(set(left['metadata'])|set(right['metadata'])):
  lv=left['metadata'].get(key);rv=right['metadata'].get(key)
  if lv==rv:continue
  try:leaves=diff(json.loads(lv),json.loads(rv))
  except Exception:leaves=[{'pointer':'','original_encoded_sha256':None if lv is None else hashlib.sha256(lv.encode()).hexdigest(),'replay_encoded_sha256':None if rv is None else hashlib.sha256(rv.encode()).hexdigest(),'not_decoded':True}]
  allowed=key in(SYSTEM,SERVICE)or(key==BRIDGE and all(v['pointer'].startswith('/paused_intervals')for v in leaves))or(key==ENV and all(v['pointer']in('/life_id','/instrumentation/global_enabled','/log_chain_sha256')for v in leaves))
  changes.append({'KEY':key,'changed_JSON_leaves':leaves,'declared_transport_recording_or_journal_scope':allowed})
  if not allowed:unexpected.append(key)
 return{'original':str(source),'replay':str(actual),'original_encoded_sha256':sha(source),'replay_encoded_sha256':sha(actual),'fields':fields,'all_complete_Native_fields_equal':all(v['equal']for v in fields.values()),'metadata_changes':changes,'unexpected_metadata_keys':unexpected,'all_metadata_keys_considered':sorted(set(left['metadata'])|set(right['metadata']))}
def main(a):
 summary=a.resultado.resolve(strict=True);root=summary.parent;contextfile=root/'CONTEXTO_EJECUCION.json';result=read(summary);context=read(contextfile)
 if result.get('status')!='COMPLETED'or result.get('owner_closed_coherently')is not True:raise ValueError('Only actually closed completed replay, never an open world')
 recipefile=RP/'recetas'/(RECIPE+'.json');recipe=read(recipefile)
 if sha(recipefile)!=RECIPE_SHA or context['recipe_sha256']!=RECIPE_SHA or context['fixed_recipe']!=recipe or result['recipe']!=RECIPE or context['variant']!='swap_global_ep04':raise ValueError('Exact before-run frozen recipe/recording swap required')
 ep04=next(r for r in result['rows']if r['step']=='EP04');primary=(root/ep04['primary']).resolve(strict=True);saved=read(primary);owner_result=json.loads(saved['result']);wrapped=owner_result['result']['rows'][0]
 if wrapped['observed_ordinal']!=4 or wrapped['original_result']['ordinal']!=4:raise ValueError('Fixed EP04 primary expected')
 ep04snapshot=Path(wrapped['native_after_EP04']['path']).resolve(strict=True)
 if not ep04snapshot.is_relative_to((root/'sistema/estado/observacion_pasiva').resolve())or sha(ep04snapshot)!=wrapped['native_after_EP04']['sha256']:raise ValueError('Actual EP04 diagnostic snapshot differs')
 cardfile=root/'sistema/estado/vidas'/result['life']/'VIDA.json';card=read(cardfile);finalsnapshot=(root/'sistema'/card['snapshot']).resolve(strict=True)
 if not finalsnapshot.is_relative_to((root/'sistema/estado').resolve())or sha(finalsnapshot)!=card['snapshot_sha256']:raise ValueError('Actual closed final pointer differs')
 originals=[Path(recipe[k]['source_frozen_snapshot']).resolve(strict=True)for k in('expected_EP04_Native','expected_final_Native')]
 files=[summary,contextfile,recipefile,primary,cardfile,ep04snapshot,finalsnapshot,*originals]
 for file in files:regular(file)
 before={str(file):sha(file)for file in files};parserfile=RP/'observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI07_cold_passive_snapshot_parser',parserfile);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
 cuts={'EP04':compare(parser,originals[0],ep04snapshot,recipe['expected_EP04_Native']),'EP08':compare(parser,originals[1],finalsnapshot,recipe['expected_final_Native'])}
 stable=all(sha(Path(file))==h for file,h in before.items());dose=all(result.get('native_receipts',{}).get(k)==v for k,v in{'unique_requested':1464,'applied':1464,'rejected':0,'pending_or_other':0}.items())
 valid=stable and dose and result.get('criteria_met')is True and all(v['all_complete_Native_fields_equal']and not v['unexpected_metadata_keys']for v in cuts.values())
 proof={'schema':'DEE.PI07.R02.RP_recording_swap.complete_Native.comparison.R01','recipe_sha256_before_execution':RECIPE_SHA,'replay_summary':str(summary),'life_id':result['life'],'cuts':cuts,'Native_dose1464_all_applied':dose,'technical_recipe_criteria_met':result.get('criteria_met'),'inspected_files_before_sha256':before,'sources_unchanged_during_passive_read':stable,'bounded_comparison_criteria_met':valid,'Native_executed_by_comparison':False,'new_ticks':0,'scope':'EP04 and EP08 full Native RAW/clocks/header/interfaces/agenda/receipts prefix, every metadata difference listed. Inner R02 recording disabled; independent external EP04 recorder enabled. Recording-pattern swap, not absence of all global observation. Technical reproduction of positive AND negative uses, not learned protection or universal observation passivity.'}
 if a.salida:
  output=a.salida.resolve(strict=False);regular(output)
  if output.exists()or not output.is_relative_to((P/'control').resolve()):raise ValueError('Fresh P7/control proof only')
  with output.open('x',encoding='utf8')as out:json.dump(proof,out,ensure_ascii=False,indent=2);out.write('\n')
 print(json.dumps({'comparison_criteria_met':valid,'cuts':{key:{'Native_equal':value['all_complete_Native_fields_equal'],'unexpected_metadata_keys':value['unexpected_metadata_keys']}for key,value in cuts.items()},'dose1464':dose,'proof':None if a.salida is None else str(a.salida),'proof_sha256':None if a.salida is None else sha(a.salida),'Native_executed':False},ensure_ascii=False));return 0 if valid else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--resultado',type=Path,required=True);ap.add_argument('--salida',type=Path);raise SystemExit(main(ap.parse_args()))
