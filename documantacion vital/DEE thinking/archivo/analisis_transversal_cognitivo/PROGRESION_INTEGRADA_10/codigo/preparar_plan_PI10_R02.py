"""Pure finite R02 preparation/calibration plans, no Native execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',default='P02');ap.add_argument('--fase',required=True);ap.add_argument('--etapa',choices=('preparar','calibrar'),required=True);ap.add_argument('--prefijo',type=Path);ap.add_argument('--manifest-sha256');ap.add_argument('--comprobante',type=Path);ap.add_argument('--escribir',action='store_true');a=ap.parse_args();need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch('[A-Z][A-Z0-9_]{0,14}',a.fase),'Unique exact clone/phase');system=P/'estados'/a.slug/'sistema';life=PREFIX+a.slug+'_01';proto=H/'PROTOCOLO_PI10_R02.json';p=read(proto);need(p['status']=='SEALED_FOR_CALIBRATION'and len(p['calibration_schedule'])==5,'Root sealed five-case R02 calibration protocol')
 pins={str(H/name):sha(H/name)for name in('pi10_consulta_adaptativa_R02.py','pi10_transporte_ancestral_R01.py','PROTOCOLO_PI10_R02.json')}
 if a.etapa=='preparar':
  need(a.prefijo is not None and a.manifest_sha256 is not None,'Actual complete unlearned R01-P0 source');mf=a.prefijo.resolve(strict=True)/'EXPORTACION_SERVICIO.json';need(sha(mf)==a.manifest_sha256,'Full neutral source manifest');m=read(mf);tick=m['physical']['tick'];need(m['life_id']==PREFIX+'P0_01'and tick==922374,'Never use R01 adverse/acquired future as neutral P02')
  steps=[{'label':'TWO_LEGAL_POSTREAD_STOPS_P02','literal':{'modo':'eci01-pi10-preparar'},'max_ticks':3,'feedback':'omit','actuator':'closed'},{'label':'P02_NEUTRAL_READY_NOT_ADMITTED','literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'}];source={'pair':str(mf),'manifest_sha256':a.manifest_sha256}
 else:
  need(a.comprobante is not None,'Actual closed P02 PREP proof required');proof=a.comprobante.resolve(strict=True);closed=read(proof);context=read(system.parent/'CONTEXTO_EJECUCION.json');life=context['life'];card=read(system/'estado/vidas'/life/'VIDA.json');tick=card['physical']['tick'];need(closed.get('closed')is True and closed.get('error')is None and closed['life_id']==life and closed['final_tick']==tick and card['snapshot_sha256']==closed['final_saved_Native']['encoded_sha256'],'Actual same-world closed neutral source')
  guard=H/'comprobar_proceso_PI10_R02.py';need(sha(guard)=='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb','Reviewed scoped guard');need(load('R02_same_P02_cal_closed_guard',guard).inspect('same_P02_before_CAL5',system,life)['no_live_affected_writer'],'Close owner before admitting metrology')
  parser=C/'reproducibilidad/observador_pasivo.py';v=load('R02_same_P02_neutral_reader',parser).snapshot_view(system/card['snapshot']);own=json.loads(v['metadata'][KEY]);need(own.get('ready')and not own.get('admitted')and own['ordinal']==0 and not own['rows']and not own.get('pending')and not own.get('uncertain'),'Neutral before-learning state, no reset of learned metrology')
  scope=read(system/'capacidades/PI10_EXPERIMENTO_R02.json');need(scope['life_id']==life and scope['role']=='calibration'and scope['force_query']is True and scope['arm']=='real'and scope['protocol_sha256']==sha(proto),'Same fixed all-query scope from P02 preparation, no role/code switch')
  steps=[{'label':'P02_SAME_WORLD_ADMIT_CAL5_ZERO_NATIVE','literal':{'modo':'eci01-pi10-admitir'},'max_ticks':0,'feedback':'omit','actuator':'closed'}]+[{'label':'P02_FORCED_CAL_%02d'%i,'literal':{'modo':'eci01-pi10-calibrar'},'max_ticks':2016,'feedback':'omit','actuator':'closed'}for i in range(5)]+[{'label':'STATE_AFTER_CAL5','literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'}];pins[str(proof)]=sha(proof);source={'closed_proof':str(proof),'sha256':sha(proof),'no_reimport_or_restore':True}
 tag='PI10_'+a.slug+'_'+a.fase+'_OWNER_R01';value={'schema':'DEE.PI10.prospective.finite_owner_plan.R01','tag':tag,'system':str(system),'life_id':life,'initial_tick':tick,'max_host_seconds':1800,'scientific_revision':'R02 separate KEY/protocol/scope, original R01 retained','stage':a.etapa,'source':source,'steps':steps,'pins':pins};out=H/('PLAN_'+tag+'.json');data=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 if a.escribir:
  if out.exists():need(out.read_text('utf8')==data,'Prior plan differs; preserve and use a new phase')
  else:
   with out.open('x',encoding='utf8')as f:f.write(data)
 print(json.dumps({'mode':'WRITTEN_NO_NATIVE'if a.escribir else'PLAN_ONLY_NO_NATIVE','plan':str(out),'sha256':sha(out)if out.exists()else hashlib.sha256(data.encode()).hexdigest(),'initial_tick':tick,'finite_bound':sum(s['max_ticks']for s in steps),'Native':0}))
if __name__=='__main__':main()
