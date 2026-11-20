"""Prepare finite forced-calibration plan from exact full common P0 prefix.

Only JSON/pins, no Native imports. Separate PLUS/MINUS worlds never become
the candidate or donate their learned bank contents to it.
"""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1];H=P/'codigo';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',choices=('CAL_PLUS','CAL_MINUS'),required=True);ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--escribir',action='store_true');a=ap.parse_args();pair=a.prefijo.resolve(strict=True)
 need(pair.parent==(P/'pares').resolve()and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'Exact closed common P0 manifest')
 m=json.loads((pair/'EXPORTACION_SERVICIO.json').read_text('utf-8-sig'));need(m['life_id']==PREFIX+'P0_01'and m['physical']['N']==67,'Both forced controls must share actual P0, never old D or another calibrated future')
 protocol=H/'PROTOCOLO_PI10_R01.json';p=json.loads(protocol.read_text('utf-8-sig'));need(p['status']=='SEALED_FOR_CALIBRATION'and len(p['calibration_schedule'])==3,'Root sealed three diagnostic cases required')
 steps=[{'label':'ADMIT_FRESH_DECLARED_LOT_ZERO_NATIVE','literal':{'modo':'eci01-pi10-admitir'},'max_ticks':0,'feedback':'omit','actuator':'closed'}]
 steps.extend({'label':'FORCED_CALIBRATION_%02d'%n,'literal':{'modo':'eci01-pi10-calibrar'},'max_ticks':2016,'feedback':'omit','actuator':'closed'}for n in range(3));steps.append({'label':'STATE_AFTER_CALIBRATION','literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'})
 value={'schema':'DEE.PI10.prospective.finite_owner_plan.R01','tag':'PI10_'+a.slug+'_OWNER_R01','system':str(P/'estados'/a.slug/'sistema'),'life_id':PREFIX+a.slug+'_01','initial_tick':m['physical']['tick'],'max_host_seconds':900,'source_complete_pair':{'file':str(pair/'EXPORTACION_SERVICIO.json'),'sha256':a.manifest_sha256},'scope':'Explicit forced diagnostic query; three fixed calibration cases, not candidate learning or reserved evaluation. No scientific source/clock/bank rewrite.','steps':steps,'pins':{str(H/name):sha(H/name)for name in('pi10_consulta_adaptativa_R01.py','pi10_transporte_ancestral_R01.py','PROTOCOLO_PI10_R01.json')}}
 out=H/('PLAN_PI10_'+a.slug+'_OWNER_R01.json');data=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 if a.escribir:
  if out.exists():need(out.read_text('utf-8-sig')==data,'Prior calibration plan differs; preserve and declare new revision')
  else:
   with out.open('x',encoding='utf8')as f:f.write(data)
 print(json.dumps({'mode':'PLAN_WRITTEN_NO_NATIVE'if a.escribir else'PLAN_ONLY_NO_NATIVE','plan':str(out),'sha256':sha(out)if out.exists()else hashlib.sha256(data.encode()).hexdigest(),'initial_tick':m['physical']['tick'],'finite_bound':6048,'Native':0}))
if __name__=='__main__':main()
