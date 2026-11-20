"""Audit completed public MCTS trajectories against frozen native primaries.

No historical target, measurement, or expected value is passed to a native
participant. This separate process opens them only after the app has finished.
"""
import argparse,gc,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reproduccion.worker_limpio import collect,sha
CASES=(('DEMO_MAGNITUD_SOCIAL_P31','MCTS_P01_SOURCE31'),('DEMO_MAGNITUD_SOCIAL_H11','MCTS_H01_SOURCE11'),('DEMO_MAGNITUD_SOCIAL_R17','MCTS_R101_VALUE17_NEW_HISTORY'),('DEMO_MAGNITUD_SOCIAL_C01','MCTS_C01_SOURCE_OMITTED'))
EVENTS=('demo_magnitud_social.jsonl','demo_magnitud_social_historia11.jsonl','demo_magnitud_social_reserva17.jsonl','demo_magnitud_social_control.jsonl')

def audit(apps,restore=None):
 rows=[]
 for directory,case in CASES:
  path=ROOT/'resultados/transferencia_magnitud'/case/'MEASUREMENTS.json';m=json.loads(path.read_text(encoding='utf8'));app=apps/directory
  observations=[json.loads(x)for x in(app/'OBSERVACIONES.jsonl').read_text(encoding='utf8').splitlines()];frames=[x['contenido']for x in observations if x['origen']=='ENTE'];comparisons=[];final=None
  for tick in(73,549,616):
   actual=collect(app/f'E1_MAGNITUD_T{tick}.deetsnap.gz');expected=next(x['physical']for x in m['snapshots']if x['physical']['tick']==tick)
   comparisons.append({'tick':tick,'actual':actual['physical'],'expected':expected,'full_RAW_clocks_tick_equal':actual['physical']==expected})
   if tick==616:final=actual
  historical=collect(path.parent/'T616.deetsnap.gz');comparisons[-1].update(native_receipts_equal=final['operative']['native_receipts']==[r['receipt']for r in sorted(m['requests'],key=lambda r:r['id'])],whole_operative_equal=final['operative']==historical['operative'])
  readings=[]
  for primary in m['magnitude_readings']:
   tick=primary['tick'];before=next(x['magnitud_recibida_actual']for x in frames if x['tick']==tick-1);after=next(x['magnitud_recibida_actual']for x in frames if x['tick']==tick)
   reference,current,output=before['reference_site'],before['object_site'],after['center'];direction=[(reference['s_reg']>current['s_reg'])-(reference['s_reg']<current['s_reg']),0,0]
   operands=reference['active']and current['active'];qualified=operands and output['active']and output['direction']==direction
   equal=reference==primary['reference']and current==primary['object']and output==primary['output']
   readings.append({'tick':tick,'reference':reference,'object':current,'output':output,'posttrajectory_direction_from_actual_operands':direction,'operands_present':bool(operands),'actual_qualified':bool(qualified),'frozen_primary_qualified':primary['qualified'],'exact_observations_equal':equal,'qualification_equal':bool(qualified)==primary['qualified']})
  errors=[x for x in observations if x['contenido'].get('estado')in('ERROR_EXPLICITO','RECHAZO_EXPLICITO')]
  row={'case_id':case,'app':str(app),'primary':str(path.relative_to(ROOT)),'primary_sha256':sha(path),'comparisons':comparisons,'metric':{'formula':'Three post-trajectory comparisons of actual B reference and actual new object loads. Qualification requires both operands active, native output active, and native X direction=sign(reference_load-object_load); active zero differs from an absent output. No score is fed back.','readings':readings,'qualified_count':sum(x['actual_qualified']for x in readings),'denominator':3},'passive_current_views':all(x['observacion_pasiva_comprobada']for x in frames),'explicit_errors':errors}
  row['passed']=all(x['full_RAW_clocks_tick_equal']and x.get('native_receipts_equal',True)and x.get('whole_operative_equal',True)for x in comparisons)and all(x['exact_observations_equal']and x['qualification_equal']for x in readings)and row['passive_current_views']and not errors;rows.append(row);del final,historical;gc.collect()
 result={'schema':'CPC8R.public_MCTS.actual_audit.v1','cases':rows,'source_hashes':{str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'app/experimento.py',ROOT/'ejecutar.py',ROOT/'reproduccion/worker_limpio.py',ROOT/'reproduccion/auditar_magnitud_social.py',*(ROOT/'configuraciones'/name for name in EVENTS))},'scope':'Native shared-Runtime MCTS app. Separately post-T0-taught backup emits a magnitude that reaches B; B receives no host reference experience. Additional exposure and seven supports are not free copying. Existing CTS/IUE/basica lives remain distinct. No arbitrary semantic dictionary or general learned comparator is claimed.'}
 if restore:
  checks=[]
  for tick in(73,549,616):
   original=collect(apps/f'DEMO_MAGNITUD_SOCIAL_P31/E1_MAGNITUD_T{tick}.deetsnap.gz');continued=collect(restore/f'RESTORED_MAGNITUD_T{tick}.deetsnap.gz')
   checks.append({'tick':tick,'physical_equal':original['physical']==continued['physical'],'operative_equal':original['operative']==continued['operative']})
  result['separate_process_restoration']=checks
 result['passed']=all(x['passed']for x in rows)and all(x['physical_equal']and x['operative_equal']for x in result.get('separate_process_restoration',[]));return result

def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--apps',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--restore',type=Path);a=p.parse_args()
 if a.report.exists():raise FileExistsError('Existing audit report protected')
 result=audit(a.apps.resolve(),a.restore.resolve()if a.restore else None);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':result['passed'],'cases':[(x['case_id'],x['passed'],x['metric']['qualified_count'])for x in result['cases']]}),flush=True)
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
