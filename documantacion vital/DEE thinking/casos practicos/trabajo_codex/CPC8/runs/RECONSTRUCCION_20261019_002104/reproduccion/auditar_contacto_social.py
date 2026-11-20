"""Post-trajectory comparison of the real public CTS app with frozen primaries.

This auditor opens historical results only after all requested native app
trajectories have finished. It never supplies targets or response choices to
participants, and does not equate snapshot metadata/identifiers with physics.
"""
import argparse,gc,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reproduccion.worker_limpio import collect,sha
CASES=(('DEMO_CONTACTO_SOCIAL_P11','CTS_R1_P11_NEW_CONTACT'),('DEMO_CONTACTO_SOCIAL_P12','CTS_R1_P12_NEW_FREE'),('DEMO_CONTACTO_SOCIAL_R31','CTS_R1_R31_NEW_HISTORY_CONTACT'),('DEMO_CONTACTO_SOCIAL_C11','CTS_R1_C11_NO_FORM'),('DEMO_CONTACTO_SOCIAL_C15','CTS_R1_C15_REG_OFFPATH_CONTACT'))
def audit(apps,restore=None):
 rows=[]
 for directory,case in CASES:
  path=ROOT/'resultados/semantica'/case/'MEASUREMENTS.json';m=json.loads(path.read_text(encoding='utf8'));app=apps/directory;observations=[json.loads(x)for x in(app/'OBSERVACIONES.jsonl').read_text(encoding='utf8').splitlines()];frames=[x['contenido']for x in observations if x['origen']=='ENTE'];comparisons=[];final=None
  for tick in(549,616):
   result=collect(app/f'E1_CONTACTO_T{tick}.deetsnap.gz');expected=next(x['physical']for x in m['snapshots']if x['tick']==tick)
   comparisons.append({'tick':tick,'actual':result['physical'],'expected':expected,'full_RAW_clocks_tick_equal':result['physical']==expected})
   if tick==616:final=result
  historical=collect(path.parent/'T616.deetsnap.gz');comparisons[-1].update(native_receipts_equal=final['operative']['native_receipts']==[r['receipt']for r in sorted(m['requests'],key=lambda r:r['id'])],whole_operative_equal=final['operative']==historical['operative'])
  b554=next(x for x in frames if x['tick']==554);probe=m['case'].get('communication_probe_load',7);records=[]
  for item in b554['comunicacion_contacto_actual']:
   q=next(x for x in m['geometry']['contact_social']['receivers']if x['id']==item['receiver']);receipt=next(x for x in final['operative']['native_receipts']if x['channels']==[q['query_port']]and x['requested_tick']==551);physical=item['memory'];qualified=receipt['status']=='applied'and physical['active']and physical['semantic']==1 and physical['direction'][:2]==[0,1]and physical['direction'][2]in(-1,0)and physical['s_reg']>probe
   records.append({'receiver':item['receiver'],'physical':physical,'receipt':receipt,'qualified':bool(qualified)})
  primary_records=[x for x in m['contact_social_observations']if x['phase']=='QUERY'];metric={'formula':'At554: applied fixed read, active semantic1, X0/Y+1/Zin{-1,0}, native load greater than actual probe dose. Not a count of names or general semantic primitives.','probe_dose':probe,'actual_qualified_count':sum(x['qualified']for x in records),'primary_qualified_count':sum(bool(x['covered'])for x in primary_records),'actual_records':records};metric['equal']=metric['actual_qualified_count']==metric['primary_qualified_count']
  errors=[x for x in observations if x['contenido'].get('estado')in('ERROR_EXPLICITO','RECHAZO_EXPLICITO')];row={'case_id':case,'app':str(app),'primary':str(path.relative_to(ROOT)),'primary_sha256':sha(path),'comparisons':comparisons,'metric':metric,'passive_current_views':all(x['observacion_pasiva_comprobada']for x in frames),'explicit_errors':errors};row['passed']=all(x['full_RAW_clocks_tick_equal']and x.get('native_receipts_equal',True)and x.get('whole_operative_equal',True)for x in comparisons)and metric['equal']and row['passive_current_views']and not errors;rows.append(row);del final,historical;gc.collect()
 result={'schema':'CPC8R.public_CTS.actual_audit.v1','cases':rows,'source_hashes':{str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'app/experimento.py',ROOT/'ejecutar.py',*(ROOT/'configuraciones'/name for name in('demo_contacto_social.jsonl','demo_contacto_social_libre.jsonl','demo_contacto_social_reserva.jsonl','demo_contacto_social_control.jsonl','demo_contacto_social_contraflujo_fuera_ruta.jsonl')))},'scope':'Real native app trajectories on frozen CTS preparations; complementary recording/read roles and external programmed counterflow remain explicit. Histories are not pooled as one life. No new discovery, native law or arbitrary linguistic map is added.'}
 if restore:
  before=collect(apps/'DEMO_CONTACTO_SOCIAL_P11/E1_CONTACTO_T549.deetsnap.gz');same=collect(restore/'RESTORED_CONTACTO_T549.deetsnap.gz');after=collect(apps/'DEMO_CONTACTO_SOCIAL_P11/E1_CONTACTO_T616.deetsnap.gz');continued=collect(restore/'RESTORED_CONTACTO_T616.deetsnap.gz');result['separate_process_restoration']=[{'tick':549,'physical_equal':before['physical']==same['physical'],'operative_equal':before['operative']==same['operative']},{'tick':616,'physical_equal':after['physical']==continued['physical'],'operative_equal':after['operative']==continued['operative']}]
 result['passed']=all(x['passed']for x in rows)and all(x['physical_equal']and x['operative_equal']for x in result.get('separate_process_restoration',[]));return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--apps',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--restore',type=Path);a=p.parse_args()
 if a.report.exists():raise FileExistsError('Existing audit report protected')
 result=audit(a.apps.resolve(),a.restore.resolve()if a.restore else None);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':result['passed'],'cases':[(x['case_id'],x['passed'],x['metric']['actual_qualified_count'])for x in result['cases']]}),flush=True)
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
