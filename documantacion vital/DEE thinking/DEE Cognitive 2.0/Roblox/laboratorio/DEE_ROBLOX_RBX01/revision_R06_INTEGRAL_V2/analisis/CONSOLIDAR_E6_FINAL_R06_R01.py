"""Passive final E6 transfer notes, only after exact CTRL1 feedback/owner closure.

Never opens Native, SQLite or MCP. No state traversal, report/Manual editing or
promotion. Inputs are the declared closed results, World, ledger and core notes.
"""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(rel):
    p=ROOT/rel;a=p.stat();raw=p.read_bytes();b=p.stat()
    if(a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns):raise ValueError('CLOSED_INPUT_CHANGED')
    return json.loads(raw.decode('utf-8-sig')),{'relative':rel,'absolute':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def new(rel,value):
    with(ROOT/rel).open('x',encoding='utf-8')as f:f.write(value if isinstance(value,str)else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    continuity,_=read('analisis/CONTINUIDAD_CORE_R06.json');omissions,_=read('analisis/OMISIONES_CORE_R06.json')
    stages=[]
    for stage in(1,2,3):
        result,source=read(f'load/evidencia/ETAPA_{stage:02d}/RESULTADO_ETAPA.json')
        owners=result['owners']
        if not all(x['result']and x['result']['closed']and x['result']['pending_global_intent']is None for x in owners):raise ValueError('LOAD_OWNER_NOT_CLOSED')
        stages.append({'stage':stage,'source':source,'status':result['status'],'abort_reason':result.get('abort_reason'),
            'owner_lifetime_overlap_seconds':result['owner_lifetime_common_overlap_seconds'],
            'completed_new_episodes':sum(len(x['result']['results'])for x in owners),
            'owners':[{'profile':x['profile'],'worker_exit_code':x['exit_code'],'owner_closed':x['result']['closed'],
                'episodes':len(x['result']['results']),'result_local':x['result_path']}for x in owners]})
    if stages[0]['completed_new_episodes']!=3 or stages[1]['completed_new_episodes']!=6 or stages[2]['completed_new_episodes']!=0:
        raise ValueError('EXPECTED_OBSERVED_LOAD_CUT_CHANGED')
    final,source=read('evidencia/NATIVE_CONECTOR_CONTINUACION_R03/RESULTADO_CONTINUACION.json')
    if final['status']!='ONE_ORIGINAL_EPISODE_CLOSED'or final['owner_closed']is not True or final['failure']is not None:raise ValueError('CTRL1_FINAL_FEEDBACK_NOT_CLOSED')
    if final['last_confirmed_tick']!=955215 or final['full_episode_ticks']!=1564 or final['new_episode_created']is not False:raise ValueError('EXACT_SAME_CTRL1_EPISODE_REQUIRED')
    module,world_source=read('evidencia/NATIVE_CONECTOR_CONTINUACION_R03/WORLD_MODULE_CHECKPOINT.json')
    if module['state']['phase']!='BOUNDARY'or module['state']['completedOpportunities']!=1 or module['state']['actionCursor']!=2 or module['state']['nativeTick']!=955215:
        raise ValueError('CTRL_MODULE_CLOSED_BOUNDARY_REQUIRED')
    ledger,ledger_source=read('control/LEDGER_R06.json')
    if ledger['intents']or ledger['consumed']!=sum(x['consumed']for x in ledger['worlds'].values())or ledger['consumed']>ledger['limit']:
        raise ValueError('GLOBAL_LEDGER_MUST_BE_RECONCILED')
    if any(x.get('reserved',0)for x in ledger['worlds'].values()):raise ValueError('NO_UNFINISHED_OPPORTUNITY_RESERVATIONS')
    acks=final['body_acks'];movement=acks[-1]['result']
    q2=[x for x in final['new_native_outputs']if x['kind']=='query_sensor']
    if len(q2)!=1:raise ValueError('ONE_REAL_Q2_REQUIRED')
    e6={'schema':'DEE.INTEGRAL.V2.E6_closed_sources.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'load':{'stages':stages,'max_simultaneous_owners_with_actual_task_execution':2,
            'three_process_lifetime_overlap_is_not_three_processing':'Stage3 owners were opened/closed with87.94888854s common lifetime but noGO,0new episodes and LAST_NEW_EPISODE_CUTOFF. No claim of3 concurrent task-processing Native lives.',
            'same_load_histories_preserved':'LOAD1 continued across stages; no shared-memory fusion; LOAD3 made0new task episodes.'},
        'live_connector':{'source':source,'World':world_source,'life':final['life'],'session_id':final['session_id'],'parent_tick':953651,
            'Q1_tick':954007,'final_tick':955215,'full_episode_new_ticks':1564,'new_ticks_in_resume':final['new_ticks_this_continuation'],
            'Q1_reexecuted':False,'new_episode_created':False,'Q1_real_action':final['original_q1']['result']['action'],
            'Q2_real_action':q2[0]['result']['action'],'actual_resource_collected':movement['resourceCollected'],
            'actual_resource_delivered':movement['resourceDelivered'],'pose_before':movement['before'],'pose_after':movement['after'],
            'actual_ACKs':len(acks),'module_cursor':module['state']['actionCursor'],'module_completed':1,'Native_owner_closed':True,
            'failed_attempts_preserved':[
                {'path':'evidencia/NATIVE_CONECTOR_LIMPIO_R01','scope':'CRLF/LF Source hash guard failed before Native,0ticks'},
                {'path':'evidencia/NATIVE_CONECTOR_LIMPIO_R02','scope':'NativeQ1 ASK completed; World rejected table where rawJSONString required (DEE_MESSAGE_BOUND),0World actions'},
                {'path':'evidencia/NATIVE_CONECTOR_CONTINUACION_R03','scope':'Same Q1 operation delivered once; only NativeQ2 and feedback new; actual body ACK/resource; not replayed cognition'}],
            'assistance':'Prepared anatomy/panel/opportunity and fixed transduction; Native route unchanged. One useful physical action is not a learning/control or agency-general demonstration.',
            'module_is_not_full_Native_backup':True},
        'global_ledger':{'source':ledger_source,'consumed_actual_ticks':ledger['consumed'],'limit':ledger['limit'],
            'intents':ledger['intents'],'worlds':ledger['worlds'],'max_worlds':ledger['max_worlds']},
        'video':'Pending final actual render/container/visual QA; this passive E6 closure does not approve video.'}
    continuity['status']='SCIENCE_AND_E6_CLOSED_FINAL_VIDEO_AND_PACKAGE_PENDING'
    continuity['E6_closed']=e6
    continuity['pending_E6']={'load':'CLOSED:1and2materially executed;3blocked0episodes, not3working Native lives.',
        'live_clean_connector':'CLOSED: original one Native episode, sameQ1 delivered, actualEXIT0/move/resource/ACK and feedback; separate from technical0Native proof.',
        'video':'Still pending final artifact and QC.'}
    continuity['finalization_required']=['video outputs/QC','final protected11 hash control','final ZIP/hash/extraction/passive recalculations']
    for item in omissions['items']:
        if item['category']=='LOAD_CTRL_states':item['status']='Closed results now inspected; full roots remain local and were not recursively hashed/copied here. See E6 closed source locators.'
    omissions['status']='SCIENCE_E6_CLOSED_VIDEO_PACKAGE_PENDING'
    omissions['unavailable_or_unverified']=['Final video/container/visual QC and final ZIP/extraction verification remain pending.',
        'No full-root hash audit of LOAD/CTRL was performed by this documentary helper; their actual closed proofs are included.']
    guide=(ROOT/'analisis/LEER_PRIMERO_CORE_R06.txt').read_text('utf-8')
    guide+='''\nACTUALIZACIÓN E6 CERRADA (consulteCONTINUIDAD_CIERRE_R06.json):\nCarga1:3episodios; carga2:3episodios por cada una de2vidas y899,0204s\nde solapamiento de propietarios. Carga3 cerró3propietarios pero quedó sinGO\npor03:10,0episodios nuevos; NO demuestra3entes trabajando simultáneamente.\n\nConector limpio LIVE:CTRL1 completó el MISMO episodio953651→955215.\nLa Q1 ASK ya formada a954007 no se repitió; se corrigió sólo el mensaje\nWorld JSON rechazado antes de admisión. NativeQ2 EXIT0 movió realmente0→6,\nrecogió1recurso y recibió ACK/retorno; owner cerrado y cursor módulo2/episodio1.\nLos fallosCRLF0Native y DEE_MESSAGE_BOUND quedaron preservados. Anatomía,\npanel y oportunidad fueron preparados; no prueba nuevo aprendizaje ni plan.\n\nLos apartados anteriores rotulados pendientesE6 son el corte históricoCORE.\nEsta actualización los resuelve con los cierres citados, manteniendo pendiente\núnicamente vídeo/QC,11críticos y empaquetado/verificación final.\n'''
    new('analisis/E6_CIERRE_COMPROBADO_R06.json',e6)
    new('analisis/CONTINUIDAD_CIERRE_R06.json',continuity)
    new('analisis/OMISIONES_CIERRE_R06.json',omissions)
    new('analisis/LEER_PRIMERO_CIERRE_R06.txt',guide)
    print(json.dumps({'E6_closed':True,'global_Native_ticks_actual':ledger['consumed'],'Native_MAIN_tick':991187,'CTRL1_tick':955215,
        'max_materially_processing_load':2,'stage3_new_episodes':0,'Native_Studio_SQLite_model_calls':0},indent=2))
if __name__=='__main__':main()
