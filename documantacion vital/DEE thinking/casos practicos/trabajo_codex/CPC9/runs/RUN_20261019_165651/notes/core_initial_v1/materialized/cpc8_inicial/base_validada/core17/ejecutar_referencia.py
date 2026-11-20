"""Finite CORE17 reference adapter/validator. Targets are evaluator-only."""
import argparse
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CONFIG=HERE/'FROZEN_CONFIG.json'
REFERENCE=ROOT/'genealogia/fuentes/a2c7e52c523365ae6a9c.json'
ORIGINAL=ROOT/'genealogia/fuentes/4049a7f9dd846e6a65fb.py'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def freeze():
 if CONFIG.exists():raise FileExistsError(CONFIG)
 original=json.loads(REFERENCE.read_text(encoding='utf-8-sig'))
 cases=[]
 for idx in list(range(7))+[7]:
  row=original['rows'][idx]
  for arm in ['exact_diagnostic']+(['standard_channels'] if idx in (0,3,4,7) else []):
   cfg={'case_id':f'C17R_{idx:02d}_{arm}','reference_row':idx,'n':row['n'],'seed':row['seed'],
        'permutation':row['frame']['permutation'],'signs':row['frame']['signs'],
        'mode':row['mode'],'input_mode':arm,'cohort':'FROZEN_ADAPTER_RESERVE' if idx==7 else 'HISTORICAL_REFERENCE_CONTRAST',
        **{k:row['geometry'][k] for k in ('receiver','source1','source2','d1','d2')}}
   cases.append(cfg)
 data={'schema':'CPC8.CORE17.adapter.frozen.v1','source_sha256':sha(ORIGINAL),'reference_sha256':sha(REFERENCE),
       'participant_sha256':sha(HERE/'repair45.py'),'runner_sha256':sha(__file__),
       'instrument_version':'4.5.0','kernel':'v27','wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c',
       'native_sha256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d',
       'criteria':'Compare actual local RAW/state/sreg/direction/semantic and query aggregate to frozen source rows after trajectory; source has no full-world clock arrays, so no claim of full-array historical identity.',
       'reserve_scope':'Second historical holdout geometry reserved for this adapter before execution; known historical result, not a new blind scientific holdout.',
       'cases':cases}
 put(CONFIG,data)
 (HERE/'ADAPTATION.diff').write_text(''.join(difflib.unified_diff(ORIGINAL.read_text(encoding='utf-8-sig').splitlines(True),(HERE/'repair45.py').read_text(encoding='utf-8').splitlines(True),fromfile='preserved_CORE17/run_e02_redundant_policy_repair.py',tofile='CPC8/repair45.py')),encoding='utf-8')
 print(json.dumps({'frozen_cases':len(cases),'config_sha256':sha(CONFIG)}))

def equivalent(actual,expected):
 if actual is None or expected is None:return actual is expected
 return all((str(actual[k])==str(expected[k])) if k=='raw' else actual[k]==expected[k]
            for k in ('raw','state','sreg','direction','semantic'))

def run(phase):
 spec=importlib.util.spec_from_file_location('cpc8_core17_repair45',HERE/'repair45.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 import dee_thinking as d
 import dee_thinking._native as native
 cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
 assert sha(HERE/'repair45.py')==cfg['participant_sha256']
 assert sha(__file__)==cfg['runner_sha256']
 assert d.__version__=='4.5.0' and sha(native.__file__)==cfg['native_sha256']
 reference=json.loads(REFERENCE.read_text(encoding='utf-8-sig'))
 assert sha(REFERENCE)==cfg['reference_sha256']
 root=ROOT/'resultados/core17_repair'
 outputs=[];failures=[]
 for c in cfg['cases']:
  if phase=='pilot' and c['reference_row']!=0:continue
  dest=root/c['case_id']
  existing=dest/'MEASUREMENTS.json'
  was_resumed=existing.exists()
  start=time.monotonic()
  try:
   result=json.loads(existing.read_text(encoding='utf-8')) if existing.exists() else module.run_case(c,dest)
   expected=reference['rows'][c['reference_row']]
   checks={key:equivalent(result[key],expected[key]) for key in ['backup_after_learning','first_arrival','second_arrival','query']}
   checks.update({key:result[key]==expected[key] for key in ['fresh_function_after_reconstruction','reconstructed_policy_at_arrival','source1_depleted','source2_depleted']})
   checks['final_summary_at_query']=all(result['final_at_query'][k]==expected['final'][k] for k in ('support','sreg_total','state_xor'))
   checks['save_load_continuation_equal']=result['continuation_same_after_save_load']
   receipt_applied=all(row['status'].lower()=='applied' for row in result['final_receipts'])
   if c['input_mode']=='standard_channels':checks['all_native_inputs_applied']=receipt_applied
   row={'case_id':c['case_id'],'mode':c['mode'],'input_mode':c['input_mode'],'cohort':c['cohort'],
        'checks':checks,'technical_status':'PASS' if all(checks.values()) else 'DIFFERENCE_RETAINED',
        'functional_reconstruction':result['fresh_function_after_reconstruction'],'query':result['query'],
        'diagnostic_forks':result['diagnostic_forks'],'receipts':len(result['final_receipts']),
        'config_sha256':sha(CONFIG),'source_sha256':cfg['source_sha256'],'reference_sha256':cfg['reference_sha256'],
        'participant_sha256':cfg['participant_sha256'],'measurements':str(existing.relative_to(ROOT)).replace('\\','/'),
        'measurements_sha256':sha(existing),'elapsed_seconds':time.monotonic()-start,'resumed_complete_case':was_resumed}
   put(dest/'COMPARISON.json',row);outputs.append(row)
  except BaseException as error:
   error_record={'case_id':c['case_id'],'error':repr(error),'traceback':traceback.format_exc(),'elapsed_seconds':time.monotonic()-start}
   put(dest/'TECHNICAL_ERROR.json',error_record);failures.append(error_record)
 result={'schema':'CPC8.CORE17.adapter.summary.v1','phase':phase,'config_sha256':sha(CONFIG),
         'version':d.__version__,'imported_module':d.__file__,'native_sha256':sha(native.__file__),
         'records':outputs,'errors':failures,'counting':'12 configured trajectories at most:8 exact-clock diagnostic replays and4 standard-channel adaptations, not twelve independent new learners.',
         'scope':'No E1 MAIN changed. Exact legacy clock replay requires diagnostic input forks. Standard channels change input-clock contract to0. Every historical edit is explicit; repair itself follows v27.',
         'status':'PASS' if not failures and outputs and all(r['technical_status']=='PASS' for r in outputs) else 'PARTIAL_OR_DIFFERENCES'}
 put(root/('SUMMARY_'+phase+'.json'),result)
 print(json.dumps({'phase':phase,'status':result['status'],'records':len(outputs),'errors':len(failures),'queries':[(r['case_id'],r['query']) for r in outputs]},ensure_ascii=False))
 return bool(failures)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--phase',choices=['pilot','all'],default='all');a=p.parse_args()
 if a.freeze:freeze()
 else:raise SystemExit(1 if run(a.phase) else 0)
