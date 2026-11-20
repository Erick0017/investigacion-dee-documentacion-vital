"""Bounded operational proof from an exact extracted collaboration archive.

Delegates all inputs/physics/persistence to the existing manager. It never reads
historical scientific targets, chooses a favorable branch or retries an action.
"""
import hashlib,json,subprocess,time
from pathlib import Path
from datetime import datetime


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(root,life,alias,sequence,call):
    settings=sequence['service_protocol'];python=root/'motor/python313/python.exe';launcher=root/'actualizaciones/arrancar.py';result={'schema':'DEE.collaboration.paired_service_operational_proof.v1','protocol':settings,'parents_are_not_merged':True,'commands_use_only_this_archive':True,'functional_issues':[],'sensor_checks':{}};owner=None;index=0
    folder=root/'trabajo_personal/resultados'/('ENTREGA_'+life);folder.mkdir(parents=True,exist_ok=False)
    def cmd(label,argv):return json.loads(call(label,['gestor',*argv]))
    def native_result(value):return json.loads(value['request']['result'])['result']
    def check_fence(value,identifier):
        fence=native_result(value).get('INSTRUMENTO_FENCE')
        if not isinstance(fence,dict)or fence.get('denied')or fence.get('no_lab_evidence_or_history_reads_allowed')is not True:raise ValueError('Missing/denied operational perimeter: '+identifier)
        return fence
    def control(identifier,op):
        value=cmd(identifier,['mente-unificada-'+op,'--vida',life,'--id',identifier,'--esperar','40'])
        row=value.get('request')or value
        if row.get('status')!='completed':raise ValueError('Technical control not completed: '+identifier)
        return json.loads(row['result'])if isinstance(row.get('result'),str)else row['result']
    def request(identifier,row,*,wait=True):
        value=cmd(identifier,['mente-unificada-pedir','--vida',life,'--id',identifier,'--situaciones',json.dumps(row,separators=(',',':')),'--retorno','omit','--esperar','40'if wait else'0'])
        if wait and(value.get('request')or value).get('status')!='completed':raise ValueError('New material request not completed; actual state preserved: '+identifier)
        if wait:check_fence(value,identifier)
        return value
    def start():
        nonlocal owner,index
        index+=1;start_wall=time.time();argv=[str(python),'-I','-B','-X','utf8',str(launcher),'gestor','mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--guardar-cada','60','--max-segundos','180']
        owner=subprocess.Popen(argv,cwd=root,stdout=(folder/('OWNER_'+str(index)+'.txt')).open('x',encoding='utf8'),stderr=(folder/('OWNER_'+str(index)+'_ERROR.txt')).open('x',encoding='utf8'))
        limit=time.monotonic()+45
        while time.monotonic()<limit:
            if owner.poll()is not None:raise RuntimeError('Extracted native owner failed before readiness')
            state=cmd('owner_'+str(index)+'_readiness',['mente-unificada-estado','--vida',life])
            cached=state.get('observation')or state.get('owner')or state
            if cached.get('running')and cached.get('wall_utc')and datetime.fromisoformat(cached['wall_utc']).timestamp()>=start_wall:return cached
            time.sleep(.1)
        raise TimeoutError('Extracted owner readiness')
    def stop(identifier):
        nonlocal owner
        value=control(identifier,'detener');owner.wait(timeout=45)
        if owner.returncode:raise RuntimeError('Extracted owner exited with failure')
        owner=None;return value
    call('open_complete_paired_copy_not_bare_snapshot_fork',['abrir',alias,life])
    card=root/'trabajo_personal/estado/vidas'/life/'VIDA.json';initial=read(card);chosen=next(r for r in read(root/'entes/CATALOGO.json')['cuts']if r['alias']==alias)
    keys=('N','tick','RAW_sha256','clocks_sha256')
    if any(initial['physical'][k]!=chosen['physical'][k]for k in keys):raise ValueError('Imported physical cut differs before any input')
    if initial['branch']!='EXPLICIT_IMPORTED_CONTINUITY'or initial['parent']['encoded_sha256']!=chosen['snapshot_sha256']:raise ValueError('A recipe or another biography replaced the imported complete state')
    result['exact_import']={'initial':initial['physical'],'source_snapshot_sha256':chosen['snapshot_sha256'],'source_life':chosen['source_life'],'branch':initial['branch'],'life_id':life,'world_id':initial['world_id'],'no_T0':True,'transport_bundle':chosen.get('persistent_service')}
    try:
        result['owner1']=start();control('delivery_resume1','reanudar')
        result['old_panel_before']=request('delivery_old_before',settings['old_panel'])
        result['new_scalar']=request('delivery_new_scalar',[settings['new_scalar']])
        result['new_raw_frame']=request('delivery_new_raw_frame',[settings['new_raw_frame']])
        for label in('new_scalar','new_raw_frame'):
            row=native_result(result[label])['rows'][0];reader=row.get('reader',{});candidates=[]
            expected_sites={(15+2*x,17,15+2*z)for x in(-1,0,1)for z in(0,-1)}
            if len(reader.get('observations',[]))!=6 or{tuple(o['site'])for o in reader['observations']}!=expected_sites:raise ValueError('New sensor use did not expose exactly the six frozen physical output classes')
            for observation in reader['observations']:
                raw=int(observation['raw']);direction=[((raw>>k)&15)-16 if((raw>>k)&15)>=8 else((raw>>k)&15)for k in(48,52,56)]
                x=(observation['site'][0]-15)//2;z=(observation['site'][2]-15)//2
                if raw&0xffffffff and(raw>>60)&15==1 and direction==[x,1,z]:candidates.append(x)
            independently_decoded=candidates[0]if len(candidates)==1 else None
            if reader.get('choice')!=independently_decoded:raise ValueError('Archived native reader disagrees with independently decoded RAW; instrument result invalid')
            admitted=sum(r['receipt']['status']=='applied'for r in row['requests'])
            result['sensor_checks'][label]={'requests':len(row['requests']),'applied':admitted,'candidates':candidates,'independently_decoded':independently_decoded,'current_physical_response_not_replaced':True}
            if len(candidates)!=1:result['functional_issues'].append(label+'_no_unique_native_output')
            if admitted!=len(row['requests']):result['functional_issues'].append(label+'_some_inputs_rejected')
            if label=='new_raw_frame'and'new_raw_expected_choice'in settings:
                result['sensor_checks'][label]['frozen_auditor_expected_choice_not_actor_input']=settings['new_raw_expected_choice']
                if independently_decoded!=settings['new_raw_expected_choice']:result['functional_issues'].append(label+'_does_not_match_frozen_task_relation')
        result['explicit_new_learning']=request('delivery_teaching',[settings['declared_teaching']])
        result['old_panel_after_teaching']=request('delivery_old_after_teach',settings['old_panel'])
        result['chain_begin']=request('delivery_chain_begin',[settings['chain_begin']])
        control('delivery_pause_pending','pausar')
        result['queued_finish']=request('delivery_chain_finish',[{'modo':'cadena-finalizar'}],wait=False)
        result['saved_pending']=control('delivery_pending_save','guardar')
        result['paired_pending_export']=control('delivery_pending_export','exportar')
        result['owner1_stop']=stop('delivery_stop1');cut=read(card)
        witness=result['saved_pending']['committed_snapshot'];dependency=witness['operational_dependencies']
        if not dependency['external_pending_present']or not dependency['cascade_pending_present']:raise ValueError('No actual pending artifact at the reserved boundary; do not manufacture a replacement')
        result['owner2']=start();result['reloaded_pending']=control('delivery_reloaded_save','guardar');reloaded=result['reloaded_pending']['committed_snapshot']
        if any(witness['physical'][k]!=reloaded['physical'][k]for k in keys)or witness['operational_dependencies']!=reloaded['operational_dependencies']:raise ValueError('Pending artifact/protocol or native fields changed on reload')
        control('delivery_resume2','reanudar')
        # The already queued FINISH is waited for, not submitted a second time.
        limit=time.monotonic()+40;poll=0
        while time.monotonic()<limit:
            poll+=1;finish=cmd('delivery_wait_already_queued_finish_'+str(poll),['mente-unificada-resultado','--vida',life,'--id','delivery_chain_finish'])
            if(finish.get('request')or{}).get('status')in('completed','uncertain','failed_preserved','rejected_invalid'):break
            time.sleep(.1)
        if(finish.get('request')or{}).get('status')!='completed':raise ValueError('Queued continuation did not complete after reload')
        result['finished_once_after_reload']=finish
        result['old_panel_after_reload']=request('delivery_old_after_reload',settings['old_panel'])
        def memory_panel(value):
            panel=[r['result']['rows'][0]for r in native_result(value)['rows']];expected=[r['contexto']for r in settings['old_panel']];contexts=[r['context_signal']for r in panel]
            if len(contexts)!=len(expected)or len(set(contexts))!=len(contexts)or set(contexts)!=set(expected):raise ValueError('The old-memory panel is incomplete or contains duplicate context addresses')
            return{r['context_signal']:r['reader']['formed_native_command']for r in panel}
        before_panel=memory_panel(result['old_panel_before']);after_teaching=memory_panel(result['old_panel_after_teaching']);after_reload_panel=memory_panel(result['old_panel_after_reload']);target=settings['declared_teaching']['contexto'];sign=settings['declared_teaching']['senal']
        result['memory_delivery_assertions']={'before':before_panel,'after_explicit_teaching':after_teaching,'after_reload':after_reload_panel,'teaching_is_operator_prepared_not_autonomous':True}
        if any(v not in(-1,1)for v in before_panel.values()):result['functional_issues'].append('initial_old_panel_not_fully_accessible')
        if target not in before_panel or before_panel[target]==sign:result['functional_issues'].append('declared_teaching_not_a_verified_new_revision')
        for context,previous in before_panel.items():
            expected=sign if context==target else previous
            if after_teaching.get(context)!=expected or after_reload_panel.get(context)!=expected:result['functional_issues'].append('memory_revision_or_retention_'+context+'_did_not_survive')
        finish_result=native_result(finish)['rows'][0];worker=finish_result['external']['worker_receipt']
        check_fence(finish,'delivery_chain_finish')
        if not worker:raise ValueError('The new two-stage operation has no actual worker receipt; no prepared outcome substitution')
        if not worker.get('transaction_completed'):result['functional_issues'].append('new_two_stage_transaction_did_not_commit')
        actuals=[]
        for stage in(result['chain_begin'],finish):
            receipt=native_result(stage)['rows'][0]['external']['worker_receipt']
            if not receipt:raise ValueError('No real worker receipt for the announced transaction')
            matches=[f for f in(root/'trabajo_personal/estado/servicios_locales'/life).rglob(receipt['output_name'])if f.is_file()and f.stat().st_size==receipt['output_bytes']and sha(f)==receipt['output_sha256']]
            if not matches:raise ValueError('Extracted native action did not leave the exact declared worker bytes')
            actuals.append({'name':receipt['output_name'],'file':str(matches[0]),'bytes':receipt['output_bytes'],'sha256':receipt['output_sha256'],'worker':receipt['worker'],'accepted':receipt['accepted'],'commit':receipt['transaction_completed']})
        result['actual_new_worker_files']=actuals
        control('delivery_final_pause','pausar');result['final_export']=control('delivery_final_export','exportar');result['owner2_stop']=stop('delivery_stop2');after=read(card)
        if after['life_id']!=initial['life_id']or after['world_id']!=initial['world_id']or after['physical']['tick']<=cut['physical']['tick']:raise ValueError('The next process did not continue the same life')
        snap=(root/'sistema'/after['snapshot']).resolve(strict=True)
        if not snap.is_relative_to(root/'trabajo_personal')or sha(snap)!=after['snapshot_sha256']:raise ValueError('Continued complete snapshot is not intact inside this extraction')
        result['continued_state']={'life_id':life,'world_id':after['world_id'],'tick':after['physical']['tick'],'snapshot':str(snap),'snapshot_sha256':after['snapshot_sha256'],'parent':after.get('parent')}
        result['pending_reload_verified']={'physical_fields_identical':True,'external_protocol_exact_SHA_identical':True,'no_new_world_or_T0':True,'same_literal_finish_not_requeued':True}
        if settings.get('auxiliary_after_main_stopped'):
            # Sequential separate participant, never an extra skill of MAIN.
            aux=settings['auxiliary_after_main_stopped'];auxlife=life+'_AUX';auxalias=aux['alias']
            call('open_separate_ready_auxiliary_copy',['abrir',auxalias,auxlife])
            acard=root/'trabajo_personal/estado/vidas'/auxlife/'VIDA.json';abefore=read(acard)
            achosen=next(r for r in read(root/'entes/CATALOGO.json')['cuts']if r['alias']==auxalias)
            if any(abefore['physical'][k]!=achosen['physical'][k]for k in keys):raise ValueError('Separate auxiliary did not import its own exact pre-use state')
            ast=cmd('auxiliary_passive_before',['unificada-acceso-estado','--vida',auxlife])
            if ast.get('operational',{}).get('used')is not False:raise ValueError('Selected auxiliary READY state was already consumed; no rewind or replacement')
            used=cmd('auxiliary_single_destructive_use',['unificada-acceso-usar','--vida',auxlife]);saved=cmd('auxiliary_explicit_save',['guardar','--vida',auxlife]);ast_after=cmd('auxiliary_next_process_state',['unificada-acceso-estado','--vida',auxlife]);afinal=read(acard)
            result['separate_finite_auxiliary']={'alias':auxalias,'life_id':auxlife,'initial':abefore['physical'],'state_before':ast,'one_use':used,'saved':saved,'next_process_state':ast_after,'final':afinal['physical'],'final_snapshot_sha256':afinal['snapshot_sha256'],'not_MAIN_knowledge':True}
            for name,value in(('before',ast),('use',used),('after',ast_after)):
                fence=value.get('INSTRUMENTO_FENCE')
                if not isinstance(fence,dict)or fence.get('denied')or fence.get('no_lab_evidence_or_history_reads_allowed')is not True:raise ValueError('Separate auxiliary lacks a clean declared instrument perimeter: '+name)
            reader=used['result']['reader'];allowed={(33+4*x,33+4*y,33+z):(x,y,z)for x,y in((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1))for z in(-1,1)};cs=[]
            if len(reader['panel'])!=12 or{tuple(p['observation']['site'])for p in reader['panel']}!=set(allowed):raise ValueError('Auxiliary did not expose exactly the twelve frozen gate sites')
            for p in reader['panel']:
                o=p['observation'];raw=int(o['raw']);v=[((raw>>k)&15)-16 if((raw>>k)&15)>=8 else((raw>>k)&15)for k in(48,52,56)]
                if raw&0xffffffff and(raw>>60)&15==1 and v==list(allowed[tuple(o['site'])]):cs.append(v[2])
            decoded=cs[0]if len(cs)==1 else None
            if reader['formed_native_command']!=decoded:raise ValueError('Auxiliary reader disagrees with independently decoded RAW')
            result['separate_finite_auxiliary']['independent_reader']={'candidate_signs':cs,'command':decoded,'all12_fixed_gates':True}
            if len(cs)!=1:result['functional_issues'].append('separate_auxiliary_no_unique_native_response')
            if afinal['life_id']!=abefore['life_id']or afinal['physical']['tick']<=abefore['physical']['tick']:raise ValueError('Auxiliary save/continuation identity or physical advance failed')
            if not ast_after.get('operational',{}).get('used'):raise ValueError('Separate one-use progress was not preserved in the next process')
        return result
    finally:
        if owner and owner.poll()is None:
            try:stop('delivery_emergency_stop')
            except Exception as error:
                result['owner_failure_preserved_without_forced_rewind']=str(error)
                try:owner.wait(timeout=185);result['own_owner_safety_horizon_exit']=owner.returncode
                except subprocess.TimeoutExpired:
                    owner.terminate();owner.wait(timeout=20);result['own_launcher_terminated_after_safety_horizon']=True
        (folder/'PRUEBA_SERVICIO.json').write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
