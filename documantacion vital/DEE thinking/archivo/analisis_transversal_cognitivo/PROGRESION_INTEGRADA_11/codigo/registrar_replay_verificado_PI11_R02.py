"""Record a closed exact experimental replay in the existing public RP index.

Only a documentary verification annex is added. Recipe/capsule/engine and
all six operational selectors remain literal. No principal acquisition or
adoption is asserted. No Native import, state load, tick or queue write.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';S=C/'sistema'
RID='pi11_habitat16_familia_desde_REAL2_R02';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_RP_R01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p).resolve(strict=True);return{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--comparison',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();comparison=a.comparison.resolve(strict=True);need(comparison.is_relative_to(P.resolve()),'Local actual comparison only');v=read(comparison);dest=P/'estados/REPLAYRP01';result=read(dest/'RESULTADO_REPRODUCCION.json');driver=read(dest/'GUARDIA_DRIVER_FAMILIA_PI11_R02.json')
    need(v.get('overall')is True and v.get('Native_strict_equal')is True and v.get('binary_causal_prefix_equal')is True and v.get('Native_normalization_performed')is False and v.get('replay_life')==LIFE,'Actual strict exact replay, no normalized Native claim')
    need(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('criteria_met')is True and driver.get('status')=='COMPLETED_DRIVER'and driver.get('completed_steps')==19 and driver.get('new_Native_ticks')==25024,'Actual complete finite Native16 replay and closure')
    need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'No active Native owner/guard')
    recipe=RP/'recetas'/(RID+'.json');publication=P/'control/PUBLICACION_REPRODUCCION_READONLY_PI11_R02/REGISTRO_COMPLETADO.json';pub=read(publication);need(sha(recipe)==pub['files_after']['recipe_R02'],'Exact original registered recipe bytes')
    active=read(S/'estado/ACTIVO.json');cardfile=S/'estado/vidas'/PARENT/'VIDA.json';card=read(cardfile);need(active['life_id']==PARENT and card['physical']['tick']==947395 and card['snapshot_sha256']=='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc','Original PI10 remains selected')
    protected=[*(C/n for n in SELECTORS),recipe,RP/'RECURSOS.json',RP/'reproducir.py',cardfile,S/card['snapshot']];before={str(p):sha(p)for p in protected}
    target=RP/'verificaciones'/RID/'VERIFICACION_NATIVE16_PI11_R02_R01.json';proof=P/'control/REGISTRO_REPLAY_VERIFICADO_PI11_R02_R01.json';need(not target.exists()and not proof.exists(),'Preserve prior registry outcome')
    record={'schema':'DEE.reproduction.actual_native_verification.v1','recipe':RID,'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'VERIFIED_EXACT_EXPERIMENTAL_NATIVE16_NOT_ADOPTED','actual_native_execution_completed':True,'actual_diagnostic_life':LIFE,'variant':'real16','new_native_ticks':25024,'complete_opportunities':16,'complete_driver_steps':19,'source_neutral_prefix_tick':947395,'source_acquisition_cut_tick':972419,'strict_Native_prefix_equal':True,'Native_normalization_performed':False,'result':ref(dest/'RESULTADO_REPRODUCCION.json'),'driver_guard':ref(dest/'GUARDIA_DRIVER_FAMILIA_PI11_R02.json'),'exact_comparison':ref(comparison),'registered_recipe':ref(recipe),'registered_capsule_manifest_sha256':pub['new_capsule_manifest_sha256'],'experimental_mechanism_reproducible':True,'acquired_in_current_operational_principal':False,'adopted':False,'principal_selected':PARENT,'principal_tick':947395,'principal_snapshot_sha256':card['snapshot_sha256'],'principal_modified':False,'adverse_MAIN_future_repaired_or_replaced':False,'scope':'Exact acquisition replay16, including original errors. A mechanism available through the RP manager; not a new capability acquired by the selected principal, generalization, autonomous recovery or independent organism.','public_command':[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(RP/'reproducir.py'),'reproducir',RID,'--variante','real16','--vida',LIFE,'--destino',str(dest),'--material'],'reuse_rule':'This exact ID/destination is now used. Use a new diagnostic ID matching the registered family and a new empty destination; the family rejects principal/used IDs/nonempty destinations before effects.','no_PI11_public_operational_use_deployed':True}
    if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY','target':str(target),'record':record,'Native':0},ensure_ascii=False,indent=2));return
    target.parent.mkdir(parents=True,exist_ok=True);write(target,record);need(before=={p:sha(Path(p))for p in before},'A protected recipe/selector/Native file changed')
    receipt={'schema':'DEE.PI11.experimental_replay_public_registry_append.R02','Native_ticks':0,'Native_imported':False,'verification_annex':ref(target),'visible_through':'reproducir.py verificar RID and listar: actual_registered_verifications','recipe_capsule_and_six_selectors_literal_unchanged':True,'protected_hashes':before,'principal_adopted':False};write(proof,receipt);print(json.dumps({'proof':str(proof),'annex':str(target),'annex_sha256':sha(target),'Native':0,'principal_adopted':False},ensure_ascii=False))
if __name__=='__main__':main()
