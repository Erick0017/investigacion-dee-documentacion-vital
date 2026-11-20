"""MA02 service 01: archived RAW, fence, receipts, bytes and continuity only.

No engine import, worker execution, live snapshot load or new DEE tick.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import zlib

SPEC=importlib.util.spec_from_file_location('archived_common',Path(__file__).with_name('recalcular_entrada_comun.py'))
common=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(common)
N=67;I=(33,33,33)
V={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0)}
HISTORY_FOR_SCORING={'alfa':-1,'beta':-1,'gamma':1,'delta':-1}

def position(v,k,z=0):return tuple((I[j]+k*v[j]+(z if j==2 else 0))%N for j in range(3))
GATES=[position(v,4,s)for v in V.values()for s in(-1,1)]
def digest(data):return hashlib.sha256(data).hexdigest()
def fingerprint(p):return{key:p[key]for key in('N','tick','RAW_sha256','clocks_sha256')}
def result_physical(r):return r.get('physical',r.get('INSTRUMENTO',{}).get('physical'))


def calculate(root,phase='01'):
    audit=common.Audit(root)
    names=['01_IMPORTAR_MAIN','02_ADMITIR_MAIN','03_ESTADO_MAIN','04_PANEL_HEREDADO_MAIN',
           '05_FORK_NULLED','06_FORK_OMIT','07_JOBS_MAIN','08_JOBS_NULLED','09_JOBS_OMIT',
           '10_POSTJOBS_ANTERIORES_MAIN','11_GUARDAR_MAIN','12_CONTINUAR_OTRO_PROCESO_MAIN']
    if phase=='02':
        names=['13_PRESERVAR_MEMORIA_SEPARADA','14_FORK_COMP_NULLED','15_FORK_COMP_OMIT','16_COMPOSICION_TRABAJO_MAIN',
               '17_COMPOSICION_NULLED','18_COMPOSICION_OMIT','19_PRIMER_USO_TRAS_COMPOSICION_MAIN','20_READQUIRIR_EXPLICITO_MAIN',
               '21_PRIMER_USO_TRAS_READQUIRIR_MAIN','22_GUARDAR_COMPUESTA_MAIN','23_REABRIR_COMPUESTA_MAIN']
    if phase=='04':
        names=['36_EMPAREJAR_OPPOSITE_EXPOSICION','37_TRANSFERIR_EPSILON_TRABAJO_MAIN_5','38_OPPOSITE_TRABAJO',
               '39_USO_5_TRAS_TRABAJO','40_DEMORA_201','41_RESERVA_ORDEN_NUEVO','42_DEMORA_68',
               '43_USO_REPETIDO_64','44_GUARDAR_CORTE_5','45_REABRIR_CORTE_5']
    if phase=='05':
        names=['46_PREPARAR_PENDIENTE_MAIN5','47_GUARDAR_PENDIENTE_MAIN5','48_FORK_PENDIENTE',
               '49_VERIFICAR_EN_NUEVA_CARPETA','50_VERIFICAR_TRAS_CARGA_MAIN5','51_PANEL_FINAL_CINCO_MAIN5',
               '52_GUARDAR_FINAL_MAIN5','53_ESTADO_FINAL_MAIN5']
    primaries={name:audit.load(name+'.json.gz') for name in names}
    sessions=[];fences=[];workers=[];external_files=[]
    checks=[];histories=dict(HISTORY_FOR_SCORING);vectors=dict(V);gates=GATES
    if phase in('04','05'):
        histories.update(beta=1,epsilon=-1);vectors['epsilon']=(1,-1,0)
        gates=[position(v,4,s)for v in vectors.values()for s in(-1,1)]
    def check(name,value):
        checks.append({'check':name,'observed':bool(value)})
        if not value:audit.issues.append({'check':name,'issue':'condition not met'})
    for name,x in primaries.items():
        check(name+': successful archived command',x['returncode']==0 and not x['timed_out'])
        check(name+': JSON stdout exact record',json.loads(x['stdout'])==x['result'])
        r=x['result'];fence=r.get('INSTRUMENTO_FENCE')
        if fence is not None:
            fences.append({'case':name,'denied':fence['denied'],'external_calls':len(fence['exact_environment_processes']),
                           'scope':fence['scope']})
            check(name+': no denied fence operation',fence['denied']==[])
        content=r.get('result',{})
        if 'rows' not in content:continue
        rows=[];receipts=[];pending=None;teaching=[]
        if phase=='05'and name in('49_VERIFICAR_EN_NUEVA_CARPETA','50_VERIFICAR_TRAS_CARGA_MAIN5'):
            pending=primaries['46_PREPARAR_PENDIENTE_MAIN5']['result']['result']['rows'][0]['external']['worker_receipt']['pending_transaction']
        life=r['INSTRUMENTO']['life_id']
        for i,row in enumerate(content['rows']):
            if row['kind'] in('explicit_teaching','explicit_revision'):
                audit.check_observation(row['hub'],name+':teaching'+str(i))
                check(name+': explicit teaching physical sign'+str(i),c_pure_z(row['hub'])==row['teaching_signal'])
                histories[row['context_signal']]=row['teaching_signal']
                teaching.append({'context':row['context_signal'],'kind':row['kind'],'input_tick':row['input_tick'],
                    'teaching_signal':row['teaching_signal'],'hub_RAW':row['hub']['raw'],'receipts':common.receipt_summary(row['requests'])})
                receipts.extend(row['requests']);continue
            panel=row['reader']['panel']
            for o in panel:audit.check_observation(o,name+':panel'+str(i))
            is_joint=row['kind']=='joint'
            answer=common.decode(panel,[(33,33,27),(33,33,39)]) if is_joint else common.decode(panel,gates,{position(v,4,s):s for v in vectors.values()for s in(-1,1)})
            formed=answer['decoded_sign']
            check(name+': fixed decoded action'+str(i),formed==row['reader']['formed_native_command'])
            check(name+': read window'+str(i),row['read_tick']==(row['second_tick']+9 if is_joint else row['input_tick']+4) and all(o['tick']==row['read_tick']for o in panel))
            frame_by_tick={f['tick']:f for f in row['frames']}
            for frame in row['frames']:
                for o in frame['sites']:audit.check_observation(o,name+':frame'+str(frame['tick']))
            if row['frames']:
                check(name+': all fixed gate frames agree'+str(i),all(next(o for o in frame_by_tick[row['read_tick']]['sites'] if o['site']==p['site'])==p for p in panel))
            rs=row['requests'];receipts.extend(rs)
            resources=[q for q in rs if q['value']==7];cues=[q for q in rs if q['value']==5]
            each_sign=5 if is_joint else 3
            check(name+(': seven symmetric generic query inputs'if phase=='01'else': symmetric generic query inputs')+str(i),len(rs)==(12 if is_joint else 7) and len(cues)==(2 if is_joint else 1) and len(resources)==each_sign*2 and sorted(int(q['channel'].rsplit('.',1)[-1])for q in resources)==[-1]*each_sign+[1]*each_sign)
            expected=(histories['alfa'] if histories['alfa']==histories['beta']else None) if is_joint else histories[row['context_signal']]
            if phase=='04'and name in('36_EMPAREJAR_OPPOSITE_EXPOSICION','38_OPPOSITE_TRABAJO')and row['context_signal']=='epsilon':expected=1
            item={'context_for_scoring_only':row['context_signal'],'input_tick':row['input_tick'],
                  'read_tick':row['read_tick'],'query_end_tick_before_feedback':row['end_tick'],
                  **answer,'historical_sign_for_scoring_only':expected,
                  'correct_historical_sign':formed is not None and formed==expected,
                  'receipts':common.receipt_summary(rs)}
            external=row.get('external')
            if external:
                worker=external['worker_receipt'];returned=external['outcome_return'];ret=external['return_requests'];receipts.extend(ret)
                check(name+': formed action not replaced'+str(i),external['formed_native_action']==formed and external['executed_action']==(formed if external['actuator_mode']=='closed'else None))
                item['external']={'formed':formed,'executed':external['executed_action'],'worker_present':worker is not None,
                                  'feedback':external['feedback_mode'],'return_receipts':common.receipt_summary(ret)}
                if worker:
                    public=worker['raw_observations'];left=sum(public[::2]);right=sum(public[1::2])
                    if worker['operation']=='verify_commit':
                        check(name+': prior transaction physically recorded'+str(i),pending is not None)
                        payload=base64.b64decode(pending['payload_base64']);prepared=base64.b64decode(pending['prepared_output_base64'])
                        check(name+': embedded preparation bytes'+str(i),digest(prepared)==pending['prepared_output_sha256'])
                        check(name+': predecessor content verified'+str(i),(zlib.decompress(prepared)==payload) if pending['prepared_by']==1 else(prepared==hashlib.sha256(payload).digest()))
                        expected_accepted=worker['worker']!=pending['prepared_by'] and digest(payload)==pending['payload_sha256']
                        pc=worker['prepared_artifact_check']
                        check(name+': actual prepared artifact readback'+str(i),pc['actual_file_read'] and pc['valid'] and pc['bytes']==len(prepared) and pc['sha256']==digest(prepared))
                        if phase=='05':
                            artifact=root/'servicios_05'/life/pending['prepared_output_name']
                            check(name+': preserved or restored real prepared file'+str(i),artifact.read_bytes()==prepared)
                            extra={'file':artifact.relative_to(root).as_posix(),'bytes':len(prepared),'sha256':digest(prepared)}
                            if extra not in external_files:external_files.append(extra)
                    else:
                        payload=bytes(public)*max(1,32+left)
                        expected_accepted=worker['worker']==(1 if left+worker['modelled_capacity_credit_not_actor_input']>=right else -1)
                    output=zlib.compress(payload,9)if worker['worker']==1 else hashlib.sha256(payload).digest()
                    path=root/('servicios_'+phase)/life/worker['output_name'];actual=path.read_bytes()
                    external_files.append({'file':path.relative_to(root).as_posix(),'bytes':len(actual),'sha256':digest(actual)})
                    check(name+': archived worker bytes exact'+str(i),actual==output and len(actual)==worker['output_bytes'] and digest(actual)==worker['output_sha256'])
                    check(name+': archived worker input exact'+str(i),len(payload)==worker['input_bytes'] and digest(payload)==worker['input_sha256'])
                    check(name+': worker follows native sign'+str(i),worker['worker']==formed)
                    check(name+': modelled environment outcome'+str(i),worker['accepted']==expected_accepted)
                    pending=worker['pending_transaction']
                    workers.append({'case':name,'index':i,'native_tick':worker['native_tick'],'worker':worker['worker'],
                                    'operation':worker['operation'],'accepted_recalculated':expected_accepted,
                                    'transaction_completed':worker['transaction_completed'],'input_bytes':len(payload),
                                    'output_bytes':len(actual),'output_sha256':digest(actual)})
                    item['external'].update({'accepted':expected_accepted,'operation':worker['operation'],'output_bytes':len(actual),
                                             'transaction_completed':worker['transaction_completed']})
                    if returned:
                        quantized=min(64,len(actual));post=returned['post_content'];audit.check_observation(post,name+':return'+str(i))
                        check(name+': return is byte count, not correct action'+str(i),returned['quantized_value']==quantized and len(ret)==2 and all(q['value']==quantized for q in ret))
                        check(name+': fixed symmetric return vectors'+str(i),sorted(q['direction']for q in ret)==[[-1,0,formed],[1,0,formed]])
                        if is_joint:
                            last=next(o for o in frame_by_tick[row['end_tick']]['sites']if tuple(o['site'])==(33,33,(33+8*formed)%67))
                            expected_return_tick=row['end_tick']+2
                        else:
                            v=vectors[row['context_signal']];last=next(o for o in frame_by_tick[row['input_tick']+7]['sites']if tuple(o['site'])==position(v,3,4*formed))
                            expected_return_tick=row['input_tick']+9
                        postraw=common.raw_fields(post['raw']);last_raw=common.raw_fields(last['raw'])
                        added=postraw['s_reg']-last_raw['s_reg']
                        check(name+': observed native byte-count accumulation'+str(i),added==2*quantized and postraw['direction']==[0,0,formed] and post['tick']==expected_return_tick)
                        item['external']['return_physical_witness']={'before_raw':last['raw'],'before_clock':last['clock'],
                            'post_raw':post['raw'],'post_clock':post['clock'],'load_delta':added,'expected_two_pulses':2*quantized}
                    else:check(name+': omitted return has no inputs'+str(i),ret==[])
                else:check(name+': null actuator neither worker nor return'+str(i),ret==[] and returned is None)
            rows.append(item)
        worker_count=sum(q['external']['worker_present']for q in rows if 'external'in q)
        if fence is not None:check(name+': exact worker call count',len(fence['exact_environment_processes'])==worker_count)
        sessions.append({'case':name,'life':life,'rows':rows,'requested':len(rows),
                         'responded':sum(q['decoded_sign']is not None for q in rows),
                         'correct':sum(q['correct_historical_sign']for q in rows),
                         'receipts':common.receipt_summary(receipts),'final_physical':fingerprint(r['physical'])})
        if phase=='02':sessions[-1]['explicit_teaching']=teaching
    R={k:v['result']for k,v in primaries.items()}
    if phase=='01':
        _continuity01(R,check)
    elif phase=='02':
        prefix=fingerprint(R['13_PRESERVAR_MEMORIA_SEPARADA']['physical'])
        check('all composition forks share native prefix',prefix==fingerprint(R['14_FORK_COMP_NULLED']['physical'])==fingerprint(R['15_FORK_COMP_OMIT']['physical']))
        for name in('16_COMPOSICION_TRABAJO_MAIN','17_COMPOSICION_NULLED','18_COMPOSICION_OMIT'):
            check(name+': first query continues preserved prefix',prefix==fingerprint(R[name]['result']['rows'][0]['before']))
        for prev,nxt in [('16_COMPOSICION_TRABAJO_MAIN','19_PRIMER_USO_TRAS_COMPOSICION_MAIN'),('19_PRIMER_USO_TRAS_COMPOSICION_MAIN','20_READQUIRIR_EXPLICITO_MAIN'),('20_READQUIRIR_EXPLICITO_MAIN','21_PRIMER_USO_TRAS_READQUIRIR_MAIN'),('22_GUARDAR_COMPUESTA_MAIN','23_REABRIR_COMPUESTA_MAIN')]:
            check(nxt+': continues preceding MAIN physical cut',fingerprint(R[prev]['physical'])==fingerprint(R[nxt]['result']['rows'][0]['before']))
        check('explicit save keeps native cut',fingerprint(R['21_PRIMER_USO_TRAS_READQUIRIR_MAIN']['physical'])==fingerprint(R['22_GUARDAR_COMPUESTA_MAIN']['physical']))
        check('omitted/null composition final native fields equal',fingerprint(R['17_COMPOSICION_NULLED']['physical'])==fingerprint(R['18_COMPOSICION_OMIT']['physical']))
    elif phase=='04':
        base=audit.load('35_REABRIR_MAIN_5.json.gz')['result']
        check('main fifth-content work continues saved previous state',fingerprint(base['physical'])==fingerprint(R['37_TRANSFERIR_EPSILON_TRABAJO_MAIN_5']['result']['rows'][0]['before']))
        check('opposite matched exposure reaches same tick before service',R['36_EMPAREJAR_OPPOSITE_EXPOSICION']['physical']['tick']==base['physical']['tick'])
        check('opposite work continues its own matched-exposure state',fingerprint(R['36_EMPAREJAR_OPPOSITE_EXPOSICION']['physical'])==fingerprint(R['38_OPPOSITE_TRABAJO']['result']['rows'][0]['before']))
        for prev,nxt in [('37_TRANSFERIR_EPSILON_TRABAJO_MAIN_5','39_USO_5_TRAS_TRABAJO'),('40_DEMORA_201','41_RESERVA_ORDEN_NUEVO'),('42_DEMORA_68','43_USO_REPETIDO_64'),('44_GUARDAR_CORTE_5','45_REABRIR_CORTE_5')]:
            check(nxt+': continues preceding MAIN_5 physical cut',fingerprint(R[prev]['physical'])==fingerprint(R[nxt]['result']['rows'][0]['before']))
        check('passive first delay201 ticks',R['40_DEMORA_201']['physical']['tick']-R['39_USO_5_TRAS_TRABAJO']['physical']['tick']==201)
        check('passive second delay68 ticks',R['42_DEMORA_68']['physical']['tick']-R['41_RESERVA_ORDEN_NUEVO']['physical']['tick']==68)
        check('explicit save keeps64-use cut',fingerprint(R['43_USO_REPETIDO_64']['physical'])==fingerprint(R['44_GUARDAR_CORTE_5']['physical']))
        check('all phase04 inputs remain aligned to prepared period67',all(q['input_tick']%67==0 for s in sessions for q in s['rows']))
    else:
        base=audit.load('45_REABRIR_CORTE_5.json.gz')['result']
        check('pending preparation continues exact previous MAIN5 cut',fingerprint(base['physical'])==fingerprint(R['46_PREPARAR_PENDIENTE_MAIN5']['result']['rows'][0]['before']))
        check('save pending native state unchanged',fingerprint(R['46_PREPARAR_PENDIENTE_MAIN5']['physical'])==fingerprint(R['47_GUARDAR_PENDIENTE_MAIN5']['physical']))
        check('fork pending has identical native fields',fingerprint(R['47_GUARDAR_PENDIENTE_MAIN5']['physical'])==fingerprint(R['48_FORK_PENDIENTE']['physical']))
        check('fork parent identifies exact pending snapshot',R['48_FORK_PENDIENTE']['parent']['snapshot_sha256']==R['47_GUARDAR_PENDIENTE_MAIN5']['INSTRUMENTO']['snapshot_sha256'])
        for prev,nxt in[('48_FORK_PENDIENTE','49_VERIFICAR_EN_NUEVA_CARPETA'),('47_GUARDAR_PENDIENTE_MAIN5','50_VERIFICAR_TRAS_CARGA_MAIN5'),('50_VERIFICAR_TRAS_CARGA_MAIN5','51_PANEL_FINAL_CINCO_MAIN5')]:
            check(nxt+': continues corresponding saved native cut',fingerprint(R[prev]['physical'])==fingerprint(R[nxt]['result']['rows'][0]['before']))
        check('both verification worlds finish with same native fields',fingerprint(R['49_VERIFICAR_EN_NUEVA_CARPETA']['physical'])==fingerprint(R['50_VERIFICAR_TRAS_CARGA_MAIN5']['physical']))
        forkworker=R['49_VERIFICAR_EN_NUEVA_CARPETA']['result']['rows'][0]['external']['worker_receipt']
        mainworker=R['50_VERIFICAR_TRAS_CARGA_MAIN5']['result']['rows'][0]['external']['worker_receipt']
        check('new-directory verification restored exact pending bytes',forkworker['prepared_artifact_check']['restored_from_exact_snapshot_external_bytes']is True)
        check('MAIN verification used its own extant prepared bytes',mainworker['prepared_artifact_check']['restored_from_exact_snapshot_external_bytes']is False)
        final=R['53_ESTADO_FINAL_MAIN5']['INSTRUMENTO']['physical']
        check('final save and passive state preserve native fields',fingerprint(R['51_PANEL_FINAL_CINCO_MAIN5']['physical'])==fingerprint(R['52_GUARDAR_FINAL_MAIN5']['physical'])==fingerprint(final))
    result={'schema':'DEE.MA02.archived_service'+phase+'.v1','new_dee_ticks':0,'sources':audit.sources,
            'worker_output_files':external_files,'sessions':sessions,'fences':fences,'workers':workers,
            'checks':checks,'observations_checked':audit.observations,'issues':audit.issues,
            'scope_and_limits':[
                ('Decode uses only all eight fixed RAW gates. Context and historical signs are used later for external scoring only.' if phase=='01' else 'Decode uses only all eight fixed RAW gates, or the two fixed central gates for explicitly requested material composition. Context and historical signs are used later for external scoring only.'),
                'Context routing, calendar, generic resources and when to request a worker remain prepared/operator supplied P0.',
                'Public job observations are not transduced into DEE by this interface. Successful fixed contexts do not prove new learned comparison of those external values.',
                'The worker enforces a modelled environment acceptance law and performs real file operations; it never chooses a replacement action for E1.',
                'Actual output byte count12/32 returns through symmetric pulses, changing native load. The return does not carry the accepted/correct flag or compute a new choice.',
                ('MAIN and OMIT both execute4/4 accepted operations and one commit. Their action signs remain identical. This is usable memory-driven service selection, not learning of a useful action policy from return.' if phase=='01' else 'MAIN and OMIT both execute two accepted preparation/verification operations and one commit. MAIN uses a native compound product to choose the verifier. Null actions run no worker. This is prepared compound access/use, not a newly learned task policy.' if phase=='02' else 'The fifth acquired sign selects a real verifier: MAIN gamma+/epsilon− completes one transaction with2/2 accepted, opposite gamma+/epsilon+ has1/2 accepted and no commit. Worker byte return does not teach the opposite sign to become useful; no revised task policy is established.' if phase=='04' else 'MAIN saves while an actual prepared file is pending; its own next process verifies it. A diagnostic fork restores exact embedded artifact bytes into another directory and also verifies them. These are separate continuations, not two commits lived by MAIN.'),
                ('MAIN final1952 and omitted/null finals1950 are not final age-matched worlds. Causal local load additions are checked at matched action windows; do not use final inequality alone as evidence.' if phase=='01' else 'MAIN final2693 and omitted/null finals2691 are not final age-matched worlds. Material composition reduces the old-access panel to2/4. Alpha− and beta+ are explicitly taught anew, not recovered without re-teaching; subsequent4/4 and reload4/4 are new acquired contents with gamma/delta retained.' if phase=='02' else 'The same MAIN_5 preserves5/5 after work,10/10 in a different request order,64/64 repeated uses and5/5 in another process throughT10727. These are repeated uses of one life, not independent samples. Delays201/68 are real but the codec realigns every input to a multiple of67; no arbitrary-phase generalization.' if phase=='04' else 'Final MAIN_5 T11196 uses5/5 after verification and remains the same life. Pending external file bytes preserve the environment, not a correct-action table or a strategy learned by DEE.'),
                'Native fingerprints cover N,tick,RAW and clocks; whole-snapshot metadata or all interfaces are not equated by these particular fingerprint checks.',
                'Fence records zero denied Python operations and exact worker calls, not an OS sandbox or proof against all possible native I/O.',
                'Save and continuation are separate archived processes using MA02_MAIN; these calculations do not rerun them.' ]}
    if phase=='05':
        final=R['53_ESTADO_FINAL_MAIN5'];m=final['ENTE']['operational']
        result['final_cut_reference']={'life':final['life_id'],'tick':final['INSTRUMENTO']['tick'],
            'snapshot_sha256':R['52_GUARDAR_FINAL_MAIN5']['INSTRUMENTO']['snapshot_sha256'],
            'physical':fingerprint(final['INSTRUMENTO']['physical']),
            'operational_counters':{k:m[k]for k in('episodes','requests','jobs')},
            'reported_requests_counter_scope':'Row requests since service admission only; excludes byte-return pulses and anatomical extension inputs. Not total lifetime admissions.',
            'reference_source':'52_GUARDAR_FINAL_MAIN5.json.gz and passive53; no native state regenerated'}
    return result


def c_pure_z(observation):return common.pure_z(observation)


def _continuity01(R,check):
    initial=fingerprint(R['01_IMPORTAR_MAIN']['physical'])
    check('admission metadata does not reset or change physical fields',initial==fingerprint(R['02_ADMITIR_MAIN']['physical'])==fingerprint(R['03_ESTADO_MAIN']['INSTRUMENTO']['physical']))
    pre_jobs=fingerprint(R['04_PANEL_HEREDADO_MAIN']['physical'])
    check('job controls share exact declared physical prefix',pre_jobs==fingerprint(R['05_FORK_NULLED']['physical'])==fingerprint(R['06_FORK_OMIT']['physical']))
    for name in ('07_JOBS_MAIN','08_JOBS_NULLED','09_JOBS_OMIT'):
        check(name+': first query from matched prefix',pre_jobs==fingerprint(R[name]['result']['rows'][0]['before']))
    check('main prior panel continues admitted state',initial==fingerprint(R['04_PANEL_HEREDADO_MAIN']['result']['rows'][0]['before']))
    check('postwork panel continues MAIN final',fingerprint(R['07_JOBS_MAIN']['physical'])==fingerprint(R['10_POSTJOBS_ANTERIORES_MAIN']['result']['rows'][0]['before']))
    check('save keeps physical state',fingerprint(R['10_POSTJOBS_ANTERIORES_MAIN']['physical'])==fingerprint(R['11_GUARDAR_MAIN']['physical']))
    check('next-process query continues saved physical state',fingerprint(R['11_GUARDAR_MAIN']['physical'])==fingerprint(R['12_CONTINUAR_OTRO_PROCESO_MAIN']['result']['rows'][0]['before']))
    check('omitted and null final native fields match despite worker existence',fingerprint(R['08_JOBS_NULLED']['physical'])==fingerprint(R['09_JOBS_OMIT']['physical']))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],'workers':len(x['workers']),
                      'sessions':[{'case':q['case'],'correct':q['correct'],'requested':q['requested'],'receipts':q['receipts']}for q in x['sessions']]},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
