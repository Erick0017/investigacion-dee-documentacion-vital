"""Seal the already reached operational cut. No DEE import or evolution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    dest=ROOT/'CONTINUIDAD_ENTE_DEE_EVOLUCION_02.json'
    if dest.exists():raise FileExistsError('Operational cut already sealed')
    verified=json.loads((EV/'recalculo/IDENTIDAD_ESTADOS_FINALES.json').read_bytes())
    if verified['issues']or not verified['active_pointer_unchanged']:raise ValueError('Final identity check failed')
    lives=[]
    expected={'EO02_MAIN':169383,'EO02_SENSORIAL_R10_T0':40353}
    for life,tick in expected.items():
        record=json.loads((ROOT/'sistema/estado/vidas'/life/'VIDA.json').read_bytes())
        if record['physical']['tick']!=tick:raise ValueError('Actual life advanced beyond approved cut')
        p=ROOT/'sistema'/record['snapshot']
        if sha(p)!=record['snapshot_sha256']:raise ValueError('Current complete snapshot identity mismatch')
        lives.append({k:record.get(k)for k in ['life_id','world_id','profile','branch','parent','snapshot','snapshot_sha256','physical','interfaces','protocols','availability']})
        lives[-1]['snapshot_bytes']=p.stat().st_size
        lives[-1]['pending_inputs']=0
        lives[-1]['operational_history_record']={'path':(ROOT/'sistema/estado/vidas'/life/'VIDA.json').relative_to(ROOT).as_posix(),'bytes':(ROOT/'sistema/estado/vidas'/life/'VIDA.json').stat().st_size,'sha256':sha(ROOT/'sistema/estado/vidas'/life/'VIDA.json')}
    manual=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_ENTE02_SIN_VALIDACION_VISUAL.docx'
    if sha(manual)!='4213141eeef8740a6acb4be0ed4214dab7eadca6022243d19258eec5d8e07851':raise ValueError('Approved actual Word required')
    cut={'campaign':'ENTE_DEE_EVOLUCION_02','status':'CLOSED_NATIVE_RESEARCH_OPERATIVE_CUT_READY_FOR_DISTRIBUTION','closed_native_utc':datetime.now(timezone.utc).isoformat(),'no_automatic_new_simulations':True,'lives':lives,'protected_default':verified['active'],'protected_parent_records_unchanged':True,'final_identity_receipt':{'path':'evidencia/campanas/ENTE_DEE_EVOLUCION_02/recalculo/IDENTIDAD_ESTADOS_FINALES.json','sha256':sha(EV/'recalculo/IDENTIDAD_ESTADOS_FINALES.json')},'main_current_knowledge':{'own':[420,410],'context':[7,5],'private_B':[61,19],'effective_criterion':14,'old_context_reacquired_not_retained':True},'alternative_current_knowledge':{'own':[114,107],'context':[0,5],'private_B':[61,19],'effective_criterion':4,'new_T0_not_EO01_knowledge':True},'promotion':'No global promotion. Both exact states are selectable bounded options; default protected E1_SOCIAL_11 unchanged.','use':'Fork the selected life, present raw observations through the existing manager, save and continue the same fork. Never replace the learned state with a recipe or merge branches.','commands':['bifurcar EO02_MAIN MI_EVOLUCION','evolucion-servicio --vida MI_EVOLUCION --dominio trabajadores --observaciones "[[8,22,4,4]]" --referencia-entorno 14 --reiniciar-entorno','bifurcar EO02_SENSORIAL_R10_T0 MI_SENSORIAL','evolucion-sensorial --vida MI_SENSORIAL --dominio trabajadores --observaciones "[[2,4,3,5,4,4,5,5]]" --referencia-entorno 4 --reiniciar-entorno','guardar --vida MI_EVOLUCION'],'manual':{'path':manual.name,'bytes':manual.stat().st_size,'sha256':sha(manual),'actual_Word_updated':True,'structural_check':True,'visual_check':False,'render_failure':'Authorized bundle did not include soffice.exe; no page image produced.'},'analysis_package_not_operational_backup':True,'native_research_completed_but_distribution_receipt_external':True}
    put(dest,cut);put(EV/'CONTINUIDAD_ENTE_DEE_EVOLUCION_02.json',cut)
    previous=ROOT/'REANUDACION.json'
    if previous.exists():
        backup=EV/'REANUDACION_PREVIA_CONSERVADA.json'
        if backup.exists():raise FileExistsError('Preserved previous resumption record exists')
        shutil.copyfile(previous,backup)
    resume={'campaign':cut['campaign'],'state':'NATIVE_RESEARCH_CLOSED_DELIVERY_IN_PROGRESS','active_protected':'E1_SOCIAL_11','continuity':dest.name,'current_lives':[{k:r[k]for k in ['life_id','snapshot','snapshot_sha256','physical']}for r in lives],'latest_operations':'MAIN new boundary use then prepare/verify across processes; R10 actual8-input services then return to gates; explicit saves completed.','known_limits':['Two context policies not retained','R10 separate newT0','No P2/R2 or newNSM65','No joint16/32','Word visual QA unavailable'],'next_task':'Finish existing distribution update and exact-final-ZIP checks, then close; no automatic new experiment or budget restart.','fixed_budget':'laboratorio/campanas/ENTE_DEE_EVOLUCION_02/PRESUPUESTO.json'}
    put(previous,resume);put(ROOT/'REANUDACION_ENTE_DEE_EVOLUCION_02.json',resume)
    budget=json.loads((HERE/'PRESUPUESTO.json').read_bytes())
    resources={'recorded_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-budget['start_monotonic'],'maximum_seconds':budget['maximum_seconds'],'deadline_not_restarted':True,'native_research_closed':True,'distribution_and_analysis_still_count_in_budget':True,'disk_free_bytes':shutil.disk_usage(ROOT).free,'memory_measurement_scope':'Recorded per-process resource observations during the pilot; no global cognition/energy interpretation.','histories_are_not_native_memory_volume':True,'main_record_bytes':lives[0]['operational_history_record']['bytes'],'R10_record_bytes':lives[1]['operational_history_record']['bytes'],'native_snapshot_bytes':[r['snapshot_bytes']for r in lives],'no_other_processes_terminated':True}
    put(EV/'RECURSOS_CORTE_OPERATIVO.json',resources)
    print(json.dumps({'continuity':str(dest),'lives':[(r['life_id'],r['physical']['tick'],r['snapshot_sha256'])for r in lives],'elapsed_seconds':resources['elapsed_seconds']},ensure_ascii=False))
if __name__=='__main__':main()
