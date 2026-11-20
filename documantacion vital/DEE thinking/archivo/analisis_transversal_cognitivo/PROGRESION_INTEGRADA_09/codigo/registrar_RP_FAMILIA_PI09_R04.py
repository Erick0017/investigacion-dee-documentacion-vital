"""Root-only additive verification through existing registrar, no Native.

Default is a plan. Requires actual coherent supervisor result AND full passive
canonical comparison. Does not change literal recipe/capsule or select a life.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';DEST=P/'estados/RP_FAMILIA_R04_R01'
RID='pi09_consulta_native12_familia_desde_C_R04';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_20261111A';RESULT=DEST/'RESULTADO_REPRODUCCION.json';SUPERVISION=P/'control/SUPERVISION_RP_FAMILIA_PI09_R04.json';OUTPUT=P/'control/RP_FAMILIA_REGISTRADA_PI09_R04.json'
RECIPE_SHA='8054297bdd57e1203a0e2f5b8e89261ba43f5c6f0e15e38ec65cafc8e088f052'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def ref(p):return {'path':str(p),'sha256':sha(p)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--registrar',action='store_true');ap.add_argument('--comparacion',type=Path);a=ap.parse_args()
 command=[str(PY),'-I','-B','-X','utf8',str(RP/'registrar_verificacion.py'),'--resultado',str(RESULT)]
 if not a.registrar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','registrar_command':command+['--nota','PI09 cold12 actual; add exact closed/full passive comparison hash after run.'],'requires':['SUPERVISION closedtrue','RESULTADO COMPLETED/criteria_mettrue','full Native canonical comparison overalltrue','--comparacion ACTUAL_JSON'],'Native_executed':False,'recipe_literal_remains_prepared_and_actual_verification_is_additive':True},ensure_ascii=False));return
 need(a.comparacion is not None and not OUTPUT.exists(),'Exact new comparison and fresh registration proof required')
 comparison_file=a.comparacion.resolve(strict=True);need(comparison_file.is_relative_to((P/'control').resolve()),'Actual comparison under PI09 control')
 supervision=read(SUPERVISION);result=read(RESULT);comparison=read(comparison_file);context=read(DEST/'CONTEXTO_EJECUCION.json')
 need(supervision.get('closed')is True and supervision.get('protected_principal_unchanged')is True and supervision.get('life_id')==LIFE and supervision.get('actual',{}).get('summary_sha256')==sha(RESULT),'Actual coherent bounded supervisor proof required')
 need(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('criteria_met')is True and result.get('life')==LIFE and result.get('recipe')==RID and result.get('variant')=='native12'and result.get('last_tick')==903603,'Actual fixed cold12 result required')
 need(result['native_receipts']=={'unique_requested':2280,'applied':2280,'rejected':0,'pending_or_other':0,'scope':'Only explicit receipt_paths frozen in recipe; aliases deduplicated by Native ID.'},'Actual2280/2280 direct receipts required')
 need(context['recipe_sha256']==RECIPE_SHA and sha(RP/'recetas'/(RID+'.json'))==RECIPE_SHA and context['prefix_manifest_sha256']=='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','Frozen recipe/prefix binding differs')
 need(comparison.get('overall')is True and comparison.get('physical_equal')is True and comparison.get('causal_prefix_equal')is True and comparison.get('unexpected_metadata_changes')==[] and comparison.get('replay_result',{}).get('sha256')==sha(RESULT),'Actual narrow full Native passive comparison required; preserve failures without relaxation')
 need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'No registration while writer/uncertain material guard remains')
 record=RP/'verificaciones'/RID/(LIFE+'.json');need(not record.exists(),'Already registered: inspect actual record, never repeat material')
 note='PI09 cold12 by actual gestionar reproducibilidad frontdoor. Coherent supervisor '+sha(SUPERVISION)+'; canonical full Native comparison '+sha(comparison_file)+'. Native18768,2280/2280Applied,12/12local usefulness,8questions. Metadata identity/log differences explicitly audited. No promotion or first-query specific credit claim.'
 stdout=P/'control/RP_FAMILIA_REGISTRO_PI09_R04.stdout.json';stderr=stdout.with_name(stdout.stem+'.stderr.txt')
 with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:process=subprocess.run(command+['--nota',note],cwd=P,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=120)
 need(process.returncode==0 and record.is_file(),'Existing registrar failed; preserve output, no material repeat')
 registered=read(record);need(registered['actual_native_execution_completed']is True and registered['owner_closed_coherently']is True and registered['fixed_local_criteria_met']is True and registered['recipe_sha256_at_run']==RECIPE_SHA,'Registered evidence does not match actual cold12')
 proof={'schema':'DEE.PI09.RP.family_actual_cold12.additive_registration.R04','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registered':True,'recipe':RID,'life_id':LIFE,'registered_verification':ref(record),'supervision':ref(SUPERVISION),'full_passive_comparison':ref(comparison_file),'actual_result':ref(RESULT),'registrar':ref(RP/'registrar_verificacion.py'),'registrar_stdout':ref(stdout),'registrar_stderr':ref(stderr),'new_native_ticks_in_registration':0,'actual_prior_native_replay_ticks':18768,'recipe_and_capsule_literal_unchanged':True,'Native_executed_by_registration':False}
 with OUTPUT.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'registered_verification':str(record),'Native_executed':False}))
if __name__=='__main__':main()
