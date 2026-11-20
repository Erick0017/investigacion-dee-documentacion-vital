"""Collect reached, closed PI11 facts; no Native import, write or repair.

The original selected PI10 and the saved adverse MAIN future are distinct.
No adoption/IF is fabricated. Run only after the public replay is closed.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,sqlite3
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';REPLAY='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_RP_R01'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01';FI='DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01';PI10='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p).resolve(strict=True);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def state(system,life,parser):
    cardfile=system/'estado/vidas'/life/'VIDA.json';card=read(cardfile);need(sha(system/card['snapshot'])==card['snapshot_sha256'],'Saved Native/card mismatch');v=parser.snapshot_view(system/card['snapshot']);meta={};stocks={}
    for k,x in v['metadata'].items():
        try:meta[k]=json.loads(x)
        except json.JSONDecodeError:meta[k]=x
    for label,key,total in (('PI10',PI10,18),('FI8_PI09','DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),('FI_PI07','DEE.Cognitive.PI07.regulated_FI_access.R01',8),('C2C','DEE.Cognitive.PI04.C2C.coordination.R01',32),('FI8_PI11_new',FI,8),('habitat_PI11',KEY,24)):
        if key in meta:
            m=meta[key];stocks[label]={'ordinal':m.get('ordinal'),'total':total,'remaining':None if type(m.get('ordinal'))is not int else total-m['ordinal'],'pending_present':bool(m.get('pending')),'uncertain':m.get('uncertain',False),'metadata_sha256':hashlib.sha256(v['metadata'][key].encode('utf8')).hexdigest()}
            if key==KEY:
                stocks[label]['counter_scope']='Native protocol opportunities, not material resource stock or usable availability after a safety stop'
        else:stocks[label]={'present':False}
    info={'life_id':life,'profile':card['profile'],'physical':card['physical'],'parent':card.get('parent'),'card':ref(cardfile),'snapshot':ref(system/card['snapshot']),'stocks':stocks,'system':str(system),'raw_state_scope':'Saved Native and administrative metadata, no new material request'}
    envfile=system/'estado/servicios_locales'/life/'PI11_HABITAT_ADAPTATIVO_R01/PI11_HABITAT_R01/ESTADO.json'
    if envfile.exists():
        env=read(envfile);info['external_habitat']={'state':ref(envfile),'tick':env['tick'],'completed_external_offers':env.get('completed'),'open_offer':env.get('open_offer'),'resource_slots_remaining':sum(not r['delivered']for r in env['slots']),'permissions':env['permissions'],'certificate':env.get('certificate'),'scope':'External law/accounting/resources; these are not Native learned memory or energy'}
    return card,v,meta,info
def queue(system,life):
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    for suffix in ('-wal','-journal'):
        aux=Path(str(db)+suffix);need(not aux.exists()or aux.stat().st_size==0,'Nonempty SQLite auxiliary file must be preserved/reconciled, never ignored by immutable read: '+str(aux))
    con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0];owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
    finally:con.close()
    need(integrity=='ok'and not pending and owner.get('running')is False,'Actual queue must be closed before final facts')
    return {'SQLite':ref(db),'integrity_check':integrity,'unresolved_requests':pending,'cached_owner':{k:owner.get(k)for k in('pid','running','paused','tick','last_saved_tick','uncertain_external_result','wall_utc')},'WAL_bytes':Path(str(db)+'-wal').stat().st_size if Path(str(db)+'-wal').exists()else 0,'SHM_bytes':Path(str(db)+'-shm').stat().st_size if Path(str(db)+'-shm').exists()else 0}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--comparison',type=Path,required=True);ap.add_argument('--RP-verification',type=Path,required=True);ap.add_argument('--output',type=Path,default=P/'fuentes/HECHOS_CIERRE_NATIVE_PI11_R01.json');a=ap.parse_args()
    need(not a.output.exists(),'Preserve prior final facts');need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Native owners must be closed')
    resultfile=P/'estados/REPLAYRP01/RESULTADO_REPRODUCCION.json';result=read(resultfile);comparison=read(a.comparison);need(result.get('owner_closed_coherently')is True,'Actual public replay owner closure')
    parserfile=RP/'observador_pasivo.py';need(sha(parserfile)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Frozen passive parser');parser=load('PI11_final_saved_parser',parserfile)
    parentcard,parentview,parentmeta,selected=state(S,PARENT,parser);active=read(S/'estado/ACTIVO.json');need(active['life_id']==PARENT and parentcard['physical']['tick']==947395 and parentcard['snapshot_sha256']=='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc','Original selected PI10 must remain literal')
    selected.update(status=read(S/'contratos/PI10_USO_OPERATIVO_R01.json')['status'],ACTIVO=ref(S/'estado/ACTIVO.json'),contract=ref(S/'contratos/PI10_USO_OPERATIVO_R01.json'),last_material_use_tick=947395)
    ccard,cv,cm,candidate=state(P/'estados/MAIN01/sistema',MAIN,parser);candidate.update(status='SAVED_HOST_SAFETY_STOP_NOT_ADOPTED',operationally_usable=False,PI11_transaction_pending_in_saved_metadata=bool(cm[KEY].get('pending')),PI11_transaction_pending_keys=sorted(cm[KEY]['pending'])if isinstance(cm[KEY].get('pending'),dict)else[],completed_habitat_opportunities=cm[KEY]['ordinal'],new_FI8_was_external_supply_not_learning=True)
    rcard,rv,rm,replay=state(P/'estados/REPLAYRP01/sistema',REPLAY,parser);replay.update(status=result['status'],recipe='pi11_habitat16_familia_desde_REAL2_R02',result=ref(resultfile),comparison=ref(a.comparison),overall_exact=comparison.get('overall'),Native_strict_equal=comparison.get('Native_strict_equal'),public_verification=ref(a.RP_verification))
    postpath=P/'control/PI11_MAIN01_POST4_OWNER_R01.json';post=read(postpath);failedpath=P/'ensayos/PI11_MAIN01_POST4_OWNER_R01_02.json';failed=read(failedpath);error=json.loads(failed['error']);need(failed['status']=='failed_preserved'and error['type']=='HostSafetyStop','Exact reached adverse future')
    postfacts={'planned':4,'completed':2,'completed_useful':0,'safety_truncated':1,'not_executed':1,'closed':post['closed'],'supervisor_error':post['error'],'proof':ref(postpath),'completed_requests':[{'id':r['id'],'initial_tick':r['before_tick'],'final_tick':r['after_tick'],'ticks':r['ticks'],'primary':ref(r['primary'])}for r in post['records']],'failed_request':{'id':failed['id'],'primary':ref(failedpath),'status':failed['status'],'result_is_null':failed['result']is None,'type':error['type'],'detail':error['detail'],'external_execution_may_be_uncertain':error['external_execution_may_be_uncertain'],'native_tick_after_attempt':error['native_tick_after_attempt'],'partial_Native_ticks':post['final_tick']-post['records'][-1]['after_tick']},'no_retry_or_restore':True,'SafetyStop_is_not_a_cognitive_NULL':True}
    postfacts.update(requested_opportunities=4,admitted_opportunities=3,environmental_actuations_observed=3,environmental_deliveries=0,complete_Native_protocols=2,third_environmental_outcome={'ordinal':18,'tick':979181,'actual_route':0,'available_bin':1,'certificate_valid':True,'physical_delivered':False,'full_experience_protocol_completed':False,'Q2_return_not_executed':True,'Q1_return_not_executed':True},autopsy=ref(P/'fuentes/AUTOPSIA_CIERRE_PI11_R01.json'))
    metrics={}
    for label,folder in(('MAIN16','RECALCULO_MAIN16_R01'),('HEREDADO16','RECALCULO_HEREDADO16_R01'),('YOKE16','RECALCULO_YOKE16_R02')):
        file=P/'fuentes'/folder/'RESUMEN_PI11.json';v=next(iter(read(file)['by_life'].values()));metrics[label]={'source':ref(file),**{k:v[k]for k in('life_id','completed_opportunities','reserved_opportunities','Native_span','totals','reserved_totals','Native_inputs_unique','last_remaining_stock','last_permissions')}}
    panelpath=P/'control/PI11_MAIN01_PANEL12_OWNER_R01.json';panel=read(panelpath);panelrows=[r for r in panel['records']if 'expected'in r];need(len(panelrows)==12 and all(r['correct']for r in panelrows),'Actual closed twelve-use core')
    ledger=load('PI11_final_exact_ledger',H/'ledger_continuidad_PI11_R02.py').ledger();ownerproofs=[]
    for path in sorted((P/'control').glob('PI11_*_OWNER_R*.json')):
        v=read(path)
        if v.get('schema')=='DEE.PI11.actual.finite_owner_plan.R01':ownerproofs.append({'proof':ref(path),**{k:v.get(k)for k in('life_id','closed','status','error','initial_tick','final_tick','new_Native_ticks')}})
    queues={}
    for life,world in ledger['worlds'].items():queues[life]=queue(Path(world['system']),life)
    queues[PARENT]=queue(S,PARENT)
    guard=load('PI11_actual_final_process_guard',H/'comprobar_proceso_PI11_R01.py');processes={}
    for life,world in ledger['worlds'].items():processes[life]=guard.inspect('PI11_final_documentary_closure',Path(world['system']),life)
    processes[PARENT]=guard.inspect('PI11_final_selected_original_closure',S,PARENT)
    need(all(v.get('no_live_affected_writer')is True for v in processes.values()),'A real affected process is not proven closed')
    processfile=P/'control'/('PROCESOS_FINALES_CIERRE_NATIVE_PI11_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
    with processfile.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI11.final_scoped_process_checks.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_ticks':0,'no_live_affected_writers':True,'worlds':processes},f,ensure_ascii=False,indent=2);f.write('\n')
    facts={'schema':'DEE.PI11.actual_closed_Native_facts.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'new_Native_ticks_by_this_collector':0,'DEE_imported_by_this_collector':False,'selected':selected,'candidate':candidate,'replay':replay,'central_metrics':metrics,'panel12':{'proof':ref(panelpath),'initial_tick':panel['initial_tick'],'final_tick':panel['final_tick'],'native_ticks':panel['new_Native_ticks'],'correct_uses':12,'denominator_uses':12,'other_operations':['explicit new FI8 admission0t','state0t'],'results':[{'label':r['label'],'actual':r['actual'],'expected':r['expected'],'correct':r['correct']}for r in panelrows]},'post_reopening':postfacts,'adoption':{'executed':False,'interface_test_executed':False,'whole_state_movement_executed':False,'PI11_public_use_deployed_or_executed':False,'decision':'KEEP_ORIGINAL_PI10_COMMITTED','reasons':['0/2 useful completed later habitat opportunities; requested fixed4 not completed','Third later request hit inherited RAW_nonzero_support>3000 HostSafetyStop; preserve current future','No usable final source for full successor adoption or IF test'],'gates':{'functional_tradeoff_central':'MET:8/16 useful versus9/16 inherited, FI10 versus16','causal_controls':'Local Native history and prepared continuation control; no exclusive real-return superiority overYOKE8/16/FI9','conservation':'12/12 atT975259; no assertion at halted final cut','source_reopening':'Actual reload occurred; fixed4 continuation failed/truncated','new_function_at_final_cut':'BLOCKED: no useful completed post use and host safety stop','decisive_recipe_replay':bool(comparison.get('overall'))}},'selectors':{name:ref(C/name)for name in SELECTORS},'PI11_operational_contract_present':(S/'contratos/PI11_USO_OPERATIVO_R01.json').exists(),'owner_proofs':ownerproofs,'queues':queues,'ledger':ledger,'global_Native_writer_marker_present':False,'public_RP_material_lock_present':False,'preserved_sets':{'original_full_pair':ref(P/'pares/PRINCIPAL_REAL2_T947395/EXPORTACION_SERVICIO.json'),'central_full_pair':ref(P/'pares/MAIN16_T972419/EXPORTACION_SERVICIO.json'),'current_original_product_system':str(S),'adverse_candidate_complete_system':str(P/'estados/MAIN01/sistema'),'public_replay_complete_system':str(P/'estados/REPLAYRP01/sistema')},'commands_tested':{'public_reproduction':[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(RP/'reproducir.py'),'reproducir','pi11_habitat16_familia_desde_REAL2_R02','--variante','real16','--vida',REPLAY,'--destino',str(P/'estados/REPLAYRP01'),'--material'],'public_verification':[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(RP/'reproducir.py'),'verificar','pi11_habitat16_familia_desde_REAL2_R02']},'limits':['FI18/7 is fixed comparison, not an acquired algorithm','Cached RAW age9 and certificates/permissions are external','37.5percent fewer FI operations is whole central16 tradeoff; no saving demonstrated in reserved4','No tick/energy saving, initiative, biological life, consciousness or general intelligence claim','Saved adverse candidate is not the selected operational principal','No Native after this closure; Root continues documents/ZIP only']}
    facts['commands_tested']['public_verification']=[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(S/'gestionar.py'),'reproducibilidad','verificar','pi11_habitat16_familia_desde_REAL2_R02']
    facts.update(closed_for_documentary_read=True,native_running=False,principal_adopted=False,main_experimental={'life_id':MAIN,'N':67,'last_observed_tick':979389,'last_saved_tick':ccard['physical']['tick']},fresh_scoped_process_proof=ref(processfile))
    with a.output.open('x',encoding='utf8')as f:json.dump(facts,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'facts':str(a.output),'sha256':sha(a.output),'selected':PARENT,'selected_tick':947395,'candidate_tick':ccard['physical']['tick'],'replay_exact':comparison.get('overall'),'observed_ticks':ledger['observed_saved_ticks'],'charged_ticks':ledger['charged_ticks'],'worlds':ledger['world_count'],'Native_imported':False},ensure_ascii=False))
if __name__=='__main__':main()
