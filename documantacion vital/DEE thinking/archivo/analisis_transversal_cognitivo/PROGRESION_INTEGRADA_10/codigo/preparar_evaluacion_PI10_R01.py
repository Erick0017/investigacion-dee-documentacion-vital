"""Pure prospective evaluation/fork/continuation scopes and finite plans.

Reads complete frozen pairs, not the live Native world. No DEE imports,
engine calls, trials, promotion or installed-world code changes. Yoke values
can only come from an actual complete closed Real18 export, never a target.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01';VERSION='DEE.PI10.adaptive_query.two_native_traces.R01'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bytes_json(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def put_exact(p,v):
 data=bytes_json(v)
 if p.exists():need(p.read_bytes()==data,'Prior exact scope/plan differs; preserve and choose a new phase/revision')
 else:
  with p.open('xb')as f:f.write(data)
 return sha(p)
def pair(path,digest):
 path=path.resolve(strict=True);need(path.parent==(P/'pares').resolve()and sha(path/'EXPORTACION_SERVICIO.json')==digest,'Actual frozen complete local pair/hash required');m=read(path/'EXPORTACION_SERVICIO.json')
 need(m['physical']['N']==67 and m['physical']['tick']>=922374,'Actual post-P0 current N67 continuation required')
 parser_path=C/'reproducibilidad/observador_pasivo.py';need(sha(parser_path)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Reviewed passive snapshot parser changed');sp=importlib.util.spec_from_file_location('PI10_frozen_eval_prefix_reader',parser_path);parser=importlib.util.module_from_spec(sp);sp.loader.exec_module(parser);v=parser.snapshot_view(path/'VIDA.deetsnap.gz')
 need(v['encoded_sha256']==m['snapshot_sha256']and all(v['physical'][k]==m['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Frozen physical/card mismatch')
 progress=json.loads(v['metadata'][KEY]);need(progress.get('version')==VERSION and progress.get('ready')is True and not progress.get('pending')and not progress.get('uncertain')and progress['ordinal']==len(progress['rows']),'Actual coherent ready PI10 prefix, no reset or repair')
 return path,m,progress
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',required=True);ap.add_argument('--fase',default='F0');ap.add_argument('--vida',required=True);ap.add_argument('--brazo',choices=('real','nonfailure','yoked'),default='real');ap.add_argument('--traza',choices=('none','cut','sham'),default='none');ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--episodios',type=int,required=True);ap.add_argument('--continuar',action='store_true');ap.add_argument('--yoke-source',type=Path);ap.add_argument('--yoke-manifest-sha256');ap.add_argument('--escribir',action='store_true');a=ap.parse_args()
 need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch('[A-Z][A-Z0-9_]{0,14}',a.fase)and re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9_]{1,25}',a.vida),'Exact current/new diagnostic identity and unique phase')
 protocol=H/'PROTOCOLO_PI10_R01.json';p=read(protocol);ph=sha(protocol);need(p.get('status')=='SEALED_FOR_EVALUATION','Root must seal evaluation protocol after actual calibration')
 for name,digest in p['sources_sha256'].items():need(Path(name).name==name and sha(H/name)==digest,'Frozen scientific source changed: '+name)
 prefix,m,progress=pair(a.prefijo,a.manifest_sha256);start=progress['ordinal'];admit=not progress.get('admitted');need(not admit or(start==0 and not progress['rows']),'An unadmitted lot cannot contain acquired episodes')
 stop=start+a.episodios;limit=24 if a.brazo=='real'and a.traza=='none'else 18;need(type(a.episodios)is int and 0<a.episodios<=24 and stop<=limit,'Finite real/control stock only, no reset/readmission')
 scope={'schema':'DEE.PI10.fixed_experiment_scope.R01','life_id':a.vida,'role':'evaluation','arm':a.brazo,'trace_control':a.traza,'force_query':None,'protocol_sha256':ph,'source_physical':{k:m['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'source_full_pair_manifest_sha256':a.manifest_sha256,'calibration_authorized':False,'evaluation_authorized':True,'environment_and_instrumentation_not_Native_policy':True}
 if a.brazo=='yoked':
  need(a.yoke_source is not None and a.yoke_manifest_sha256 is not None,'Actual Real18 source required before any yoked scope')
  yp,ym,real=pair(a.yoke_source,a.yoke_manifest_sha256);need(real.get('admitted')and real['ordinal']==18 and len(real['rows'])==18 and real.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Actual continuous unforced Real18, not calibration/control/prompt')
  need(real['protocol_sha256']==ph,'Real18 protocol must match this prospective fixed yoke')
  failed=[r['actual_failed']for r in real['rows']];need(all(type(v)is bool for v in failed)and p['yoke_permutation']==[(i+5)%18 for i in range(18)],'Actual failures and fixed +5permutation, no optimization')
  scope.update(yoked_values=[failed[i]for i in p['yoke_permutation']],yoked_source_failed=failed,yoked_source_vector_sha256=hashlib.sha256(json.dumps(failed,separators=(',',':')).encode()).hexdigest(),yoked_source={'life_id':ym['life_id'],'tick':ym['physical']['tick'],'snapshot_sha256':ym['snapshot_sha256'],'manifest':str(yp/'EXPORTACION_SERVICIO.json'),'manifest_sha256':a.yoke_manifest_sha256,'permutation':p['yoke_permutation']})
 system=P/'estados'/a.slug/'sistema';tag='PI10_'+a.slug+'_'+a.fase+'_OWNER_R01';need(len(tag)<=75,'Finite transport tag')
 if a.continuar:
  need(m['life_id']==a.vida and system.is_dir(),'A continuation uses its own actual reached export, not another branch')
  card=read(system/'estado/vidas'/a.vida/'VIDA.json');need(card['snapshot_sha256']==m['snapshot_sha256']and card['physical']==m['physical'],'Current continuation advanced; reconcile rather than restore')
  installed=system/'capacidades/PI10_EXPERIMENTO_R01.json';old=read(installed);need(all(old[k]==scope[k]for k in('life_id','role','arm','trace_control','force_query','protocol_sha256')),'Existing evaluation control/config cannot change silently');scope=old
  need(progress.get('admitted')and progress['protocol_sha256']==ph,'Continuation requires the actual prior admitted history');admit=False
 else:need(not(system/'estado/vidas'/a.vida).exists(),'New clone only; never overwrite or reconfigure an existing world')
 steps=[]
 if admit:steps.append({'label':'EXPLICIT_FINITE_LOT_ADMISSION_ZERO_NATIVE','literal':{'modo':'eci01-pi10-admitir'},'max_ticks':0,'feedback':'omit','actuator':'closed'})
 steps.extend({'label':'PI10_EP_%02d'%n,'literal':{'modo':'eci01-pi10-episodio'},'max_ticks':2016,'feedback':'omit','actuator':'closed'}for n in range(start,stop));steps.append({'label':'STATE_AFTER_'+str(stop),'literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'})
 plan={'schema':'DEE.PI10.prospective.finite_owner_plan.R01','tag':tag,'system':str(system),'life_id':a.vida,'initial_tick':m['physical']['tick'],'max_host_seconds':1800,'source_complete_pair':{'file':str(prefix/'EXPORTACION_SERVICIO.json'),'sha256':a.manifest_sha256},'initial_ordinal':start,'final_ordinal_planned':stop,'admission_required':admit,'historical_preparation_header_unchanged':True,'steps':steps,'pins':{str(H/name):sha(H/name)for name in('pi10_consulta_adaptativa_R01.py','pi10_transporte_ancestral_R01.py','PROTOCOLO_PI10_R01.json')}}
 scopefile=H/('PI10_EXPERIMENTO_'+a.slug+'_'+a.fase+'_R01.json');planfile=H/('PLAN_'+tag+'.json')
 if a.escribir:
  put_exact(scopefile,scope);put_exact(planfile,plan)
  if not a.continuar:
   canonical=H/'PI10_EXPERIMENTO_R01.json';temporary=canonical.with_name(canonical.name+'.WRITING');need(not temporary.exists(),'Prior canonical scope write unresolved');temporary.write_bytes(bytes_json(scope));temporary.replace(canonical)
 print(json.dumps({'mode':'EVALUATION_SCOPE_PLAN_WRITTEN_NO_NATIVE'if a.escribir else'PLAN_ONLY_NO_NATIVE','life_id':a.vida,'scope':str(scopefile),'scope_sha256':sha(scopefile)if scopefile.exists()else hashlib.sha256(bytes_json(scope)).hexdigest(),'plan':str(planfile),'plan_sha256':sha(planfile)if planfile.exists()else hashlib.sha256(bytes_json(plan)).hexdigest(),'initial_tick':m['physical']['tick'],'initial_ordinal':start,'admit_now':admit,'planned_final_ordinal':stop,'finite_bound':a.episodios*2016,'Native':0}))
if __name__=='__main__':main()
