"""Exact physical and native-receipt checks of both executed app profiles."""
import argparse,gc,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.initiative_use_e1 import InitiativeUseE1Session
from integracion.relational_pair import physical

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def collect(path,cls):
 s=cls.load(path);r={'physical':physical(s.world),'native_receipts':{x['id']:x['receipt']for x in s.receipts()},'view':s.view()};del s;gc.collect();return r
def run(out,basica='resultados/app/DEMO_BASICA_V2R1',integrada='resultados/app/DEMO_INTEGRADA_V2R1'):
 rows=[]
 for profile,cls,app,ref in(
  ('basica',LongitudinalE1Session,str(Path(basica)/'E1_T549.deetsnap.gz'),'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/T549.deetsnap.gz'),
  ('integrada',InitiativeUseE1Session,str(Path(integrada)/'E1_T549.deetsnap.gz'),'resultados/integracion/IUE_P01_RETURN_USED_PLUS/T549.deetsnap.gz'),
  ('integrada_consulta_nueva',InitiativeUseE1Session,str(Path(integrada)/'E1_T616.deetsnap.gz'),'resultados/integracion/IUE_T11_RESTORE_PLUS_NEW_QUERY/T616.deetsnap.gz')):
  a=collect(ROOT/app,cls);b=collect(ROOT/ref,cls);rows.append({'profile':profile,'app':app,'reference':ref,'exact_RAW_clocks_tick':a['physical']==b['physical'],'exact_native_receipts':a['native_receipts']==b['native_receipts'],'app_physical':a['physical'],'reference_physical':b['physical'],'view_current':a['view'],'same_current_view':a['view']==b['view']})
 views=[]
 for name in(basica,integrada):
  events=[json.loads(line)for line in(ROOT/name/'OBSERVACIONES.jsonl').read_text(encoding='utf-8').splitlines()]
  frames=[x['contenido']for x in events if x['origen']=='ENTE'];views.append({'app':name,'number_of_current_passive_frames':len(frames),'all_passive':all(x['observacion_pasiva_comprobada']for x in frames),'errors':[x for x in events if x['contenido'].get('estado')in('ERROR_EXPLICITO','RECHAZO_EXPLICITO')]})
 result={'schema':'CPC8R.actual_app.v2.audit','comparisons':rows,'passive_views':views,'instrumentation_failure_preserved':'resultados/app/DEMO_INTEGRADA_V2:missing prepared_vs_acquired before curriculum; app fallback corrected display metadata only.','source_hashes':{x.relative_to(ROOT).as_posix():hashlib.sha256(x.read_bytes()).hexdigest()for x in(ROOT/'app/experimento.py',ROOT/'ejecutar.py',ROOT/'configuraciones/demo_integrada.jsonl',ROOT/'configuraciones/demo_e1.jsonl')},'scope':'Executed native trajectories, not transcripts. Basica and integrada have different initial preparations; their scores are not added as one lifetime.'}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'profile':x['profile'],'physical':x['exact_RAW_clocks_tick'],'receipts':x['exact_native_receipts'],'view':x['same_current_view']}for x in rows]))
 if not all(x['exact_RAW_clocks_tick']and x['exact_native_receipts']for x in rows):raise RuntimeError('Actual app mismatch')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--basica',default='resultados/app/DEMO_BASICA_V2R1');p.add_argument('--integrada',default='resultados/app/DEMO_INTEGRADA_V2R1');a=p.parse_args();run(a.out,a.basica,a.integrada)
