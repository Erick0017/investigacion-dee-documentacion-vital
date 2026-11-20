"""Portable actual A RP panel12 recálculo; preserved common PI08/PI07 parsers."""
from pathlib import Path
import argparse,importlib.util,json,sys
def at(value,path):
 for key in path:value=value[key]
 return value
def main(args):
 root=Path(args.raiz).resolve(strict=True);out=Path(args.salida).absolute()
 if out.exists():raise FileExistsError('Fresh output only')
 sys.path.insert(0,str(root));spec=importlib.util.spec_from_file_location('A_panel_common_documentary_parser',root/'RECALCULAR_PRIMARIOS_PI08.py');tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
 result=tool.recalculate(root);ledger=result['current_direct_receipt_ledger']
 if not(result['all_checks_passed']and ledger['unique_current_Native_requests']==947 and ledger['status_counts']=={'applied':947}):raise ValueError('Actual947 direct recorded inputs differ')
 index=json.loads((root/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json').read_text('utf-8-sig'))
 recipe=json.loads((root/'RECETA_PUBLICADA_LITERAL.json').read_text('utf-8-sig'));steps={s['label']:s for s in recipe['variants']['panel12_sin_c2c']['batches'][0]}
 witnesses=[];numbers={}
 for entry in index['primaries']:
  primary=json.loads((root/entry['file']).read_text('utf-8-sig'));value=primary['result'];value=json.loads(value)if isinstance(value,str)else value
  step=steps[entry['step']];actual=at(value,step['read_path'])
  if type(actual)is not type(step['expected'])or actual!=step['expected']:raise ValueError('Actual functional witness differs: '+entry['step'])
  literal=json.loads(primary['payload'])['situaciones'][0]
  if step.get('actual_integer_binding'):
   binding=step['actual_integer_binding']
   if literal[binding['field']]!=numbers[binding['from_step']]:raise ValueError('Actual number binding differs')
  numbers[entry['step']]=actual;witnesses.append({'step':entry['step'],'actual':actual,'expected_auditor_only':step['expected'],'passed':True})
 if len(witnesses)!=12 or numbers['number13']!=13 or numbers['number8']!=8:raise ValueError('Actual12/12 including13-to8 required')
 result.update(actual_RP_panel12_witnesses=witnesses,actual_RP_execution_already_performed=True,material_replay_executed_by_this_recalculation=False,
  scope_A_control='Actual adopted-A861426 descendant through the existing Cognitive RP frontdoor:12/12,947Applied. No new C2C/R03 opportunity, principal mutation or repair of B10/12.',
  B_conservation_gate_remains_false=True)
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'all_checks_passed':True,'actual_witnesses':12,'Native_receipts_recounted':947,'new_Native_ticks':0,'output':str(out)}))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz',required=True);p.add_argument('--salida',required=True);main(p.parse_args())
