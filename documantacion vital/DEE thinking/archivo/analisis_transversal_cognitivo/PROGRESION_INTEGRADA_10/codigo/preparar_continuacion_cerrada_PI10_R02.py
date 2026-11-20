"""Pure finite plan from a coherent CLOSED existing PI10 diagnostic world.

No full export/copy, Native import, query, input, tick, config rewrite or reset.
The complete local operational state stays where it was; its exact closure,
card/snapshot/code/proof/scope hashes are pinned for the new finite phase.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,re
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',required=True);ap.add_argument('--fase',required=True);ap.add_argument('--comprobante',type=Path,required=True);group=ap.add_mutually_exclusive_group(required=True);group.add_argument('--episodios',type=int);group.add_argument('--pasos',type=Path);ap.add_argument('--escribir',action='store_true');a=ap.parse_args()
 need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch('[A-Z][A-Z0-9_]{0,14}',a.fase),'Exact unique phase/clone slug');system=P/'estados'/a.slug/'sistema';contextfile=system.parent/'CONTEXTO_EJECUCION.json';context=read(contextfile);life=context['life'];need(not(system/'estado/ACTIVO.json').exists()and life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'),'Existing unselected PI10 diagnostic continuation only')
 proof=a.comprobante.resolve(strict=True);need(proof.is_relative_to((P/'control').resolve()),'Actual local closed owner proof required');closed=read(proof);need(closed.get('schema')=='DEE.PI10.actual.finite_owner_plan.R01'and closed.get('life_id')==life and closed.get('closed')is True and closed.get('error')is None and closed.get('protected_before')==closed.get('protected_after'),'No partial/failed/foreign phase may be silently continued')
 guard=H/'comprobar_proceso_PI10_R02.py';need(sha(guard)=='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb','Reviewed exact process/queue guard changed');state=load('PI10_closed_plan_process_guard',guard).inspect('PI10_closed_existing_plan_source',system,life);need(state['no_live_affected_writer'],'Affected world has live/uncertain owner, queue or lock')
 cardfile=system/'estado/vidas'/life/'VIDA.json';card=read(cardfile);snapshot=system/card['snapshot'];need(card['physical']['tick']==closed['final_tick']and sha(snapshot)==card['snapshot_sha256']==closed['final_saved_Native']['encoded_sha256'],'Closed proof is not this exact current saved cut')
 parserpath=C/'reproducibilidad/observador_pasivo.py';need(sha(parserpath)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Exact passive parser changed');v=load('PI10_closed_existing_snapshot',parserpath).snapshot_view(snapshot);need(v['physical']==closed['final_saved_Native']['physical']and v['causal_prefix_sha256']==closed['final_saved_Native']['causal_prefix_sha256'],'Saved Native identity differs from actual closed proof')
 progress=json.loads(v['metadata'][KEY]);need(progress.get('ready')and progress.get('admitted')and not progress.get('pending')and not progress.get('uncertain')and progress['ordinal']==len(progress['rows']),'Closed admitted PI10 history; no readmission/reset/repair')
 scopefile=system/'capacidades/PI10_EXPERIMENTO_R02.json';scope=read(scopefile);protocol=system/'capacidades/PROTOCOLO_PI10_R02.json';need(scope['life_id']==life and scope['protocol_sha256']==sha(protocol)==progress['protocol_sha256']and scope['role']=='evaluation'and scope['force_query']is None,'Installed frozen evaluation scope/protocol; no switching calibration or control after experience')
 codefile=system.parent/'SISTEMA_CODIGO_PI10.json';need(context['source_code_manifest_sha256']==sha(codefile),'Actual frozen code closure differs')
 for row in read(codefile)['files']:need(sha(system/row['file'])==row['sha256'],'Installed source changed: '+row['file'])
 start=progress['ordinal'];pins={str(p):sha(p)for p in(proof,scopefile,protocol,contextfile,codefile)}
 if a.episodios is not None:
  limit=18 if scope['arm']=='real'and scope['trace_control']=='none'else 12;need(0<a.episodios<=18 and start+a.episodios<=limit,'Current actual finite stock only')
  steps=[{'label':'PI10_EP_%02d'%n,'literal':{'modo':'eci01-pi10-episodio'},'max_ticks':2016,'feedback':'omit','actuator':'closed'}for n in range(start,start+a.episodios)];steps.append({'label':'STATE_AFTER_'+str(start+a.episodios),'literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'});target=start+a.episodios
 else:
  prepared=a.pasos.resolve(strict=True);need(prepared.is_relative_to(H.resolve()),'Exact reviewed finite existing step source under campaign code');value=read(prepared);steps=copy.deepcopy(value['steps']if isinstance(value,dict)else value);need(isinstance(steps,list)and steps,'Nonempty declared finite panel/reopening steps');pins[str(prepared)]=sha(prepared);target=None
  for step in steps:need(isinstance(step.get('literal'),dict)and step['literal'].get('modo')not in('eci01-pi10-preparar','eci01-pi10-admitir','eci01-pi10-calibrar')and type(step.get('max_ticks'))is int and 0<=step['max_ticks']<=5000,'No P0/re-admission/calibration or unbounded step on continuation')
 tag='PI10_'+a.slug+'_'+a.fase+'_OWNER_R01';plan={'schema':'DEE.PI10.prospective.finite_owner_plan.R01','tag':tag,'system':str(system),'life_id':life,'initial_tick':card['physical']['tick'],'max_host_seconds':1800,'initial_ordinal':start,'final_ordinal_planned':target,'admission_required':False,'source_closed_operational_state':{'system':str(system),'card':str(cardfile),'card_sha256':sha(cardfile),'snapshot':str(snapshot),'snapshot_sha256':sha(snapshot),'closed_proof':str(proof),'closed_proof_sha256':sha(proof),'scope_sha256':sha(scopefile),'no_export_or_snapshot_restore':True},'steps':steps,'pins':pins}
 out=H/('PLAN_'+tag+'.json');data=json.dumps(plan,ensure_ascii=False,indent=2)+'\n'
 if a.escribir:
  if out.exists():need(out.read_text('utf-8-sig')==data,'Prior phase plan differs; preserve and choose a new phase tag')
  else:
   with out.open('x',encoding='utf8')as f:f.write(data)
 print(json.dumps({'mode':'CLOSED_CONTINUATION_PLAN_WRITTEN_NO_NATIVE'if a.escribir else'PLAN_ONLY_NO_NATIVE','plan':str(out),'sha256':sha(out)if out.exists()else hashlib.sha256(data.encode()).hexdigest(),'initial_tick':card['physical']['tick'],'actual_ordinal':start,'admission_now':False,'finite_bound':sum(s['max_ticks']for s in steps),'Native':0,'full_pair_duplicated':False,'installed_scope_or_code_modified':False}))
if __name__=='__main__':main()
