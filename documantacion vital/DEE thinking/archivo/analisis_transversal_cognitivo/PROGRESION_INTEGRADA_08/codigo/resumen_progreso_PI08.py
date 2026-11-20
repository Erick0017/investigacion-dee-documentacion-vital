"""Read only compact PI08 primaries for progress, not an actor/evaluator."""
from pathlib import Path
import argparse,json
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--prefijo',default='');args=parser.parse_args()
for p in sorted((P/'ensayos').glob(args.prefijo+'*.json')):
 d=json.loads(p.read_text(encoding='utf8'));v=json.loads(d['result'])if isinstance(d.get('result'),str)else d.get('result')
 if not isinstance(v,dict):
  error=json.loads(d['error'])if isinstance(d.get('error'),str)else d.get('error')or{}
  print(json.dumps({'file':p.name,'status':d['status'],'error_type':error.get('type'),'error_detail':error.get('detail'),'checkpoint_error':error.get('checkpoint_error')},ensure_ascii=False));continue
 rows=v.get('result',{}).get('rows',[])
 if not rows:continue
 r=rows[0];out={'file':p.name,'ticks':[v['before_tick'],v['after_tick']]}
 for k in('ordinal','actual_numeric_result','useful_product','actual_failed','returned_failed','pulse_applied','early_physical_choice','prepared','committed','already_committed','new_native_ticks'):
  if k in r:out[k]=r[k]
 if 'formed_native_command'in r.get('reader',{}):out['command']=r['reader']['formed_native_command']
 if 'FI'in r:out['FI_q4']=r['FI'].get('early_physical_choice')
 if 'message'in r:out['message']=r['message'].get('delivered_exact')
 if 'sensor'in r:out['sensor']=r['sensor'].get('actual_state_datum');out['Native_choice']=r.get('reader',{}).get('choice')
 if 'environment_spec'in r:out['nominal_cue']=r['environment_spec'].get('cue')
 print(json.dumps(out,ensure_ascii=False))
