"""Root-only additive verification through existing registrar, no Native.

Default is a plan. Requires actual coherent supervisor result AND full passive
canonical comparison. Does not change literal recipe/capsule or select a life.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';DEST=P/'estados/RP_D_FAMILIA_R01'
RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_20261111A';RESULT=DEST/'RESULTADO_REPRODUCCION.json';SUPERVISION=P/'control/SUPERVISION_RP_D6_FAMILIA_PI09_R01.json';OUTPUT=P/'control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json'
RECIPE_SHA='25ac34885918f7da9a43577dfaedcf4128d6297d6ef15633fba121fcb5785ac4'
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
 need(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('criteria_met')is True and result.get('life')==LIFE and result.get('recipe')==RID and result.get('variant')=='real6'and result.get('last_tick')==917679,'Actual fixed cold12 result required')
 need(result['native_receipts']=={'unique_requested': 1139, 'applied': 1137, 'rejected': 2, 'pending_or_other': 0, 'scope': 'Only explicit receipt_paths frozen in recipe; aliases deduplicated by Native ID.'},'Actual frozen D6 guard+whole two-stage receipt dose required')
 need(context['recipe_sha256']==RECIPE_SHA and sha(RP/'recetas'/(RID+'.json'))==RECIPE_SHA and context['prefix_manifest_sha256']=='8500dafda573afb48ca631b1a7cd3f2cdb1131769485f49811f4f1cfac5fe067','Frozen recipe/prefix binding differs')
 need(comparison.get('overall')is True and comparison.get('physical_equal')is True and comparison.get('causal_prefix_equal')is True and comparison.get('unexpected_metadata_changes')==[] and comparison.get('replay_result',{}).get('sha256')==sha(RESULT),'Actual narrow full Native passive comparison required; preserve failures without relaxation')
 need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'No registration while writer/uncertain material guard remains')
 record=RP/'verificaciones'/RID/(LIFE+'.json');need(not record.exists(),'Already registered: inspect actual record, never repeat material')
 note='PI09 D6 actual generic-family gestionar/RP frontdoor. Full source6 Native comparison '+sha(comparison_file)+'. Frozen actual errors, NULL and terminal conflicts are preserved; equality is separate from all-six usefulness. No first-query credit or learned guard claim.'
 stdout=P/'control/RP_D6_FAMILIA_REGISTRO_PI09_R01.stdout.json';stderr=stdout.with_name(stdout.stem+'.stderr.txt')
 with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:process=subprocess.run(command+['--nota',note],cwd=P,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=120)
 need(process.returncode==0 and record.is_file(),'Existing registrar failed; preserve output, no material repeat')
 registered=read(record);need(registered['actual_native_execution_completed']is True and registered['owner_closed_coherently']is True and registered['fixed_local_criteria_met']is True and registered['recipe_sha256_at_run']==RECIPE_SHA,'Registered evidence does not match actual cold12')
 proof={'schema':'DEE.PI09.D.RP.family6.additive_registration.R01','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registered':True,'recipe':RID,'life_id':LIFE,'registered_verification':ref(record),'supervision':ref(SUPERVISION),'full_passive_comparison':ref(comparison_file),'actual_result':ref(RESULT),'registrar':ref(RP/'registrar_verificacion.py'),'registrar_stdout':ref(stdout),'registrar_stderr':ref(stderr),'new_native_ticks_in_registration':0,'actual_prior_native_replay_ticks':10136,'recipe_and_capsule_literal_unchanged':True,'Native_executed_by_registration':False}
 with OUTPUT.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'registered_verification':str(record),'Native_executed':False}))
if __name__=='__main__':main()
