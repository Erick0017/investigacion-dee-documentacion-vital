"""Correct only the outer-only receipt checker, using the three frozen groups."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 source=P/'control/PI07_C2C_CONSERVACION_28_29_R02.json'
 out=P/'control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json'
 if out.exists():raise FileExistsError(out)
 old=read(source)
 if not old['closed']or old['correct']!=old['tested']!=2:
  raise ValueError('Two actual functional uses and coherent close required')
 if old['error']is not None or old['scientific_stop']is not None:raise ValueError('Do not override a real material or transport error')
 spec=importlib.util.spec_from_file_location('documentary_decoder',P/'codigo/RECALCULAR_PRIMARIOS_PI07.py')
 dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
 checks=[];rows=[];ids=set();status={};sources=[]
 for item in old['rows']:
  p=P/'ensayos'/Path(item['primary']).name
  if sha(p)!=item['primary_sha256']:raise ValueError('Published primary differs')
  envelope,records=dec.decoded_result(read(p));r=records[0]
  life=envelope['committed_snapshot']['life_id'];product=r['actual_effect']['product']
  productpath=P/'estados/candidato/sistema/estado/servicios_locales'/life/'PI04_C2C_COORDINACION_R01/dispositivo'/product['path']
  data=productpath.read_bytes()
  if len(data)!=64 or hashlib.sha256(data).hexdigest()!=product['sha256']:raise ValueError('Actual useful product changed')
  record=dec.inspect_C2C(r,p.name,{product['sha256']:data},checks);rows.append(record)
  groups={'outer':r['requests'],'FI':r['native_arithmetic']['native_operation']['native_trial']['requests'],
          'MU':r['second_native_use']['requests']}
  direct,aliases=dec.receipts([q for group in groups.values()for q in group])
  if ids.intersection(direct):raise ValueError('Material ID reused between opportunities')
  ids.update(direct)
  for receipt in direct.values():status[receipt['status']]=status.get(receipt['status'],0)+1
  record['actual_group_counts']={k:len(v)for k,v in groups.items()}
  sources.append({'file':str(p),'sha256':sha(p),'product_file':str(productpath),'product_sha256':product['sha256']})
 if [r['ordinal']for r in rows]!=[28,29]or len(ids)!=372or status!={'applied':372}:
  raise ValueError('Original372receipt criterion not met by actual outer/FI/MU groups')
 result={'schema':'DEE.PI07.C2C.corrected_three_group_verification.R03','new_Native_ticks':0,
  'original_checker_proof':{'file':str(source),'sha256':sha(source),'status':old['status'],'criteria_met':old['criteria_met']},
  'correction':'The R02 runner counted only each outer6 while the unchanged scientific _native_input_summary counts outer6+FI176+MU4. No denominator, metric, Native input or result was changed. Original false gate is preserved.',
  'source_code':{'file':'capacidades/pi04_coordinacion_central_C2C.py','sha256':sha(P/'estados/candidato/sistema/capacidades/pi04_coordinacion_central_C2C.py'),'function':'_native_input_summary'},
  'closed':True,'material_success':True,'opportunities':2,'products':2,'Native_inputs':{'unique_requested':372,'applied':372,'rejected_or_other':0},
  'initial_tick':old['before_tick'],'final_tick':old['after_tick'],'actual_Native_ticks':old['new_Native_ticks'],
  'rows':rows,'checks':checks,'sources':sources,'no_retry_or_reteaching':True}
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'material_success':True,'Native_inputs':result['Native_inputs'],'final_tick':old['after_tick']}))
if __name__=='__main__':main()
