"""Recálculo pasivo del primario R05c: cinco recibos de tarea + uno de guarda.

No Native, propietario, consulta, ajuste de lector ni modificación de receta.
La igualdad física se comprueba por separado con comprobar_fisica_final.py.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,sys
sys.dont_write_bytecode=True
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--resultado',required=True,type=Path);ap.add_argument('--salida',type=Path);a=ap.parse_args()
 summary=a.resultado.resolve(strict=True);initial_sha=sha(summary);r=read(summary);root=summary.parent
 if r.get('recipe')!='pi03_guardia_cola_R05c'or r.get('variant')!='guard'or r.get('status')!='COMPLETED'or r.get('owner_closed_coherently')is not True:
  raise ValueError('Only the actual completed/closed R05c guard reproduction')
 context=read(root/'CONTEXTO_EJECUCION.json')
 if context['life']!=r['life']or not r['life'].startswith('ECI02_PI03_REPRO_'):raise ValueError('Explicit diagnostic identity required')
 rows=[x for x in r['rows']if x['step']=='guard']
 if len(rows)!=1:raise ValueError('Exactly one complete fixed guard operation expected')
 primary=(root/rows[0]['primary']).resolve(strict=True)
 if not primary.is_relative_to(root):raise ValueError('Primary escaped diagnostic root')
 primary_sha=sha(primary);raw=read(primary)
 if raw.get('status')!='completed':raise ValueError('Primary operation did not complete')
 native=json.loads(raw['result'])if isinstance(raw['result'],str)else raw['result']
 value=native['result']['rows'][0];task=value['actual_task_result'];guard=value['guard_preparation']['receipt']
 task_unique={};aliases=0
 for item in task['requests']:
  receipt=item['receipt'];rid=receipt['id']
  if type(rid)is not int or rid!=item['id']:raise ValueError('Task/receipt identity differs')
  if rid in task_unique:
   aliases+=1
   if receipt!=task_unique[rid]:raise ValueError('Conflicting task receipt alias')
  task_unique[rid]=receipt
 all_ids=dict(task_unique);gid=guard['id']
 if type(gid)is not int:raise ValueError('Guard receipt has no Native ID')
 guard_alias=gid in all_ids
 if guard_alias and all_ids[gid]!=guard:raise ValueError('Guard aliases a different Native input')
 all_ids[gid]=guard
 choice=task['reader']['choice']
 if type(task['opportunity'])is not int or task['opportunity']<0:raise ValueError('Actual finite opportunity index required')
 product_name='%04d.bin'%task['opportunity']
 product=root/'sistema/estado/servicios_locales'/r['life']/'PI03_TAREA_DIFERIDA_R02/dispositivo/products'/product_name
 prefix_product=Path(context['prefix'])/'artefactos_trabajador/PI03_TAREA_DIFERIDA_R02/dispositivo/products'/product_name
 product_bytes=product.stat().st_size if product.is_file()else None
 product_sha=sha(product)if product.is_file()else None
 effect=task['actual_effect']
 checks={'fixed_material_zero':type(choice)is int and choice==0,
   'useful_product':task['useful_product']is True,
   'original_q6_read_tick':task['reader']['tick']==771955,
   'fixed_query_tick':value['calendar']['query_tick']==771949,
   'final_tick':value['final_tick']==772227,
   'new_native_ticks_in_actual_reproduction':value['new_native_ticks']==3910,
   'six_distinct_inputs':len(task_unique)==5 and len(all_ids)==6 and not guard_alias,
   'all_six_applied':all(x['status']=='applied'for x in all_ids.values()),
   'guard_offset':[0,3,0]==value['guard_preparation']['offset'],
   'actual_new_64byte_product':product_bytes==64 and product_bytes==effect['actual_product_bytes']and product_sha==effect['actual_product_sha256']and not prefix_product.exists()}
 if primary_sha!=sha(primary)or initial_sha!=sha(summary):raise ValueError('Source changed during passive recalculation')
 result={'schema':'DEE.PI03.R05c.full_native_receipt_recalculation.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'life':r['life'],'summary':str(summary),'summary_sha256':initial_sha,'primary':str(primary),'primary_sha256':primary_sha,
  'fixed_reader_choice':choice,'useful_product':task['useful_product'],
  'task_receipts':{'unique':len(task_unique),'applied':sum(x['status']=='applied'for x in task_unique.values()),'ids':sorted(task_unique)},
  'guard_receipt':guard,'all_native_receipts':{'unique_requested':len(all_ids),'applied':sum(x['status']=='applied'for x in all_ids.values()),
     'rejected':sum(x['status'].startswith('rejected')for x in all_ids.values()),'ids':sorted(all_ids),'aliases_excluded':aliases+int(guard_alias)},
  'actual_product':{'path':str(product),'bytes':product_bytes,'sha256':product_sha,'same_path_absent_in_source_prefix':not prefix_product.exists()},
  'checks':checks,'all_frozen_local_checks_met':all(checks.values()),'new_native_ticks_by_this_recalculation':0,'DEE_imports':0,
  'scope':'Task-only runner denominator5 and separate guard1 are consolidated here by actual Native IDs. This is documentary recalculation, not a new execution, independent history, acquired protection or general cognitive approval.'}
 if a.salida:
  if a.salida.exists():raise FileExistsError('Preserve previous proof; new output only')
  with a.salida.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if all(checks.values())else 2
if __name__=='__main__':raise SystemExit(main())
