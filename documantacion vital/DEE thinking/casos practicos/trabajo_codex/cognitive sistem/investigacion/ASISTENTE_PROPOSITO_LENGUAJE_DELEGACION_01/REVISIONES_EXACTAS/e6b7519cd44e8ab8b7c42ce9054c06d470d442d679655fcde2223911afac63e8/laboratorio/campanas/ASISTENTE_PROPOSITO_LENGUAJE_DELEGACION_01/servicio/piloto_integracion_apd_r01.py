"""Short APD service handoff on one explicitly authorized existing life.

No Runtime is opened by this harness. The existing manager owns the real world;
this program submits fixed literal requests and observes their archived results.
It never substitutes an answer, retries an action or imports a favorable past.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,sqlite3,subprocess,sys,time
from datetime import datetime
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def summary(p):
    d=read(p);return{k:d.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical','persistent_service')}
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sistema',type=Path,required=True);parser.add_argument('--vida',required=True);parser.add_argument('--snapshot-sha256',required=True);parser.add_argument('--signos-antiguos',help='Frozen auditor-only JSON sign map; never forwarded to DEE. If absent, no retention match is claimed.');parser.add_argument('--salida',type=Path,required=True);a=parser.parse_args()
    system=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);life=a.vida;card=system/'estado/vidas'/life/'VIDA.json';before=summary(card)
    if before['snapshot_sha256']!=a.snapshot_sha256 or sha(system/before['snapshot'])!=a.snapshot_sha256:raise ValueError('Exact handoff snapshot differs; no fallback, fork or new individual')
    if(system/'estado/locks'/(before['world_id']+'.lock')).exists():raise ValueError('Another writer still owns the selected life')
    queue_module=module('frozen_pilot_queue',system/'app/cola_local.py');audit_module=module('frozen_pilot_audit',Path(__file__).with_name('auditar_apd_archivado.py'))
    queue_path=system/'estado/servicios_persistentes'/before['world_id']/'cola.sqlite3'
    if not queue_path.is_file():raise ValueError('Selected real life lacks its complete inherited paired queue; no bare fork fallback')
    if queue_path.with_name(queue_path.name+'-wal').exists()and queue_path.with_name(queue_path.name+'-wal').stat().st_size:raise ValueError('Unsettled WAL before exclusive handoff; do not infer a closed queue from partial bytes')
    with sqlite3.connect(queue_path.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        if any(r[0].startswith('apdpilot_')for r in con.execute('SELECT id FROM requests')):raise ValueError('Pilot prefix was already used; do not replay this protocol or rewind')
    budget=read(system.parent/'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/PRESUPUESTO.json')
    protected={v['path']:v['sha256']for v in budget['parent_and_protected'].values()if isinstance(v,dict)and'path'in v and'sha256'in v}
    if not all(sha(Path(p))==digest for p,digest in protected.items()):raise ValueError('A declared protected original differs before pilot')
    paths={Path('gestionar.py'),*(p.relative_to(system)for p in(system/'app').glob('*.py'))}
    paths.update(p.relative_to(system)for p in(system/'capacidades').glob('*apd*.py'))
    paths.update(Path('capacidades')/name for name in('mente_unificada_01.py','mente_acumulativa_r02.py','percepcion_cruda_fi01.py','selector_acrecion_nativo.py','eo02_trabajador_local.py'))
    sources=[]
    for relative in sorted(paths):
        p=system/relative;target=out/'codigo'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);sources.append({'file':relative.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    for p in(Path(__file__),Path(__file__).with_name('auditar_apd_archivado.py')):shutil.copyfile(p,out/p.name)
    panel=[{'modo':'memoria','contexto':c}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
    expected_signs=json.loads(a.signos_antiguos)if a.signos_antiguos else None
    if expected_signs is not None and(set(expected_signs)!={r['contexto']for r in panel}or any(type(v)is not int or v not in(-1,1)for v in expected_signs.values())):raise ValueError('Auditor history requires exactly six distinct context/sign entries; no actor target field')
    requests=[('apdpilot_apd',{'operacion':'sesion','situaciones':[{'modo':'apd','texto':'suma','operandos':[7,13]}],'retorno':'omit'}),('apdpilot_old6',{'operacion':'sesion','situaciones':panel,'retorno':'omit'}),('apdpilot_count',{'operacion':'sesion','situaciones':[{'modo':'apd-conteo','presencias':[1,0,1]}],'retorno':'omit'})]
    pending={'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'gamma'}],'retorno':'omit'}
    protocol={'schema':'DEE.APD01.prospective_short_service.R01','life_id':life,'initial':before,'source':sources,
              'requests':requests,'queued_after_pause':{'id':'apdpilot_queued_gamma','payload':pending},
              'idle_ticks_minimum':10,'owner_start_paused':True,'max_owner_seconds':300,
              'auditor_only_prior_signs_not_actor_input':expected_signs,
              'new_forms_total_quita_not_queried':True,'teaching':None,
              'scope':'One operational service window on the same actual life. Omitted cost returns retain their native generic query schedule; no new policy-learning claim. The token is an actual queued old-memory request, not a fictional pending APD tool.'}
    (out/'PROTOCOLO.json').write_text(json.dumps(protocol,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    process=None;q=None;records={};commands=[];checks={};functional=[];started=time.monotonic();index=0
    def command(label,args):
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),*args];p=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=120);commands.append({'label':label,'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        if p.returncode:raise RuntimeError('Manager command failed: '+label)
        return json.loads(p.stdout)
    def wait(identifier,timeout=90):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            row=q.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError('Request stopped in '+row['status']+': '+identifier)
                return json.loads(row['result'])
            time.sleep(.05)
        raise TimeoutError('Same request still unresolved: '+identifier)
    def submit(identifier,payload):
        admission=q.put(identifier,payload);records[identifier+'_admission']=admission
        if admission.get('admission')!='queued':raise ValueError('No new literal request queued; not replaying prior result: '+identifier)
        return wait(identifier)
    def start():
        nonlocal process,q,index
        if not all(sha(system/r['file'])==r['sha256']for r in sources):raise ValueError('Actor/owner sources changed after protocol freeze')
        index+=1;argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--guardar-cada','60','--max-segundos','300'];launched=time.time()
        env=dict(os.environ);env['OMP_NUM_THREADS']='1'
        process=subprocess.Popen(argv,stdout=(out/('OWNER_'+str(index)+'.txt')).open('x',encoding='utf8'),stderr=(out/('OWNER_'+str(index)+'_ERROR.txt')).open('x',encoding='utf8'),env=env)
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            if process.poll()is not None:raise RuntimeError('Own pilot owner exited before readiness')
            q=queue_module.QueueDB(queue_path);owner=q.get_meta('owner')
            if owner and owner.get('running')and datetime.fromisoformat(owner['wall_utc']).timestamp()>=launched:
                records['owner_'+str(index)+'_ready']=owner;return owner
            time.sleep(.05)
        raise TimeoutError('Pilot readiness')
    def stop(identifier):
        nonlocal process
        result=submit(identifier,{'operacion':'detener'});process.wait(timeout=60);commands.append({'label':identifier,'owner_returncode':process.returncode})
        if process.returncode:raise RuntimeError('Owner process exit failed')
        process=None;return result
    try:
        owner=start();checks['exact_same_initial_cut']=owner['life_id']==life and owner['tick']==before['physical']['tick'];submit('apdpilot_resume1',{'operacion':'reanudar'})
        for identifier,payload in requests:
            value=submit(identifier,payload);native=value['result'];fence=native.get('INSTRUMENTO_FENCE')
            if not fence or fence.get('denied')or fence.get('no_lab_evidence_or_history_reads_allowed')is not True:raise ValueError('Missing or denied declared reading perimeter')
            if identifier in('apdpilot_apd','apdpilot_count'):
                audited=audit_module.audit(native['rows'][0],system/'estado/servicios_locales'/life);records[identifier+'_independent_audit']=audited
                if audited['issues']:raise ValueError('RAW/receipt/auditor disagreement: '+str(audited['issues']))
                if audited.get('correct_when_responded')is not True:functional.append(identifier+'_not_a_correct_numeric_response')
            else:
                old=[r['result']['rows'][0]for r in native['rows']];records['old_panel']=[{'context':r['context_signal'],'sign':r['reader']['formed_native_command']}for r in old]
                if len(old)!=6 or len({r['context_signal']for r in old})!=6:raise ValueError('Missing or duplicated old-memory panel')
                if any(r['reader']['formed_native_command']not in(-1,1)for r in old):functional.append('old_panel_not_six_valid_emissions')
                if expected_signs is not None:
                    observed={r['context_signal']:r['reader']['formed_native_command']for r in old};records['old_panel_history_comparison']={'observed':observed,'prior_signs':expected_signs,'matches':sum(observed.get(k)==v for k,v in expected_signs.items()),'total':6,'not_actor_input':True}
                    if observed!=expected_signs:functional.append('old_panel_differs_from_frozen_prior_history')
        idle_start=q.get_meta('owner')['idle_ticks'];deadline=time.monotonic()+8
        while time.monotonic()<deadline and q.get_meta('owner')['idle_ticks']<idle_start+10:time.sleep(.1)
        checks['at_least10_idle_ticks']=q.get_meta('owner')['idle_ticks']>=idle_start+10
        paused=submit('apdpilot_pause',{'operacion':'pausar'});admitted=q.put('apdpilot_queued_gamma',pending);records['literal_pending_admission']=admitted
        if admitted.get('admission')!='queued':raise ValueError('Actual pilot token not queued')
        pending_before=q.get('apdpilot_queued_gamma');saved=submit('apdpilot_pending_save',{'operacion':'guardar'});records['saved_pending']=saved
        checks['pause_exact_tick']=paused['after_tick']==saved['after_tick']
        stop('apdpilot_stop1');start();reloaded=submit('apdpilot_reloaded_save',{'operacion':'guardar'});records['reloaded']=reloaded;pending_after=q.get('apdpilot_queued_gamma')
        checks['same_pending_FIFO_row']=pending_before==pending_after and pending_after['status']=='queued'
        first=saved['committed_snapshot'];second=reloaded['committed_snapshot'];checks['same_native_fields_on_reload']=first['physical']==second['physical'];checks['same_full_environment_and_external_protocol']=first['operational_dependencies']==second['operational_dependencies']
        submit('apdpilot_resume2',{'operacion':'reanudar'});records['queued_gamma_executed_once']=wait('apdpilot_queued_gamma');submit('apdpilot_final_pause',{'operacion':'pausar'});submit('apdpilot_final_save',{'operacion':'guardar'});stop('apdpilot_stop2')
        after_stop=summary(card);records['after_stop']=after_stop;owner=q.get_meta('owner');records['owner_final']=owner
        checks['same_life_and_real_continuation']=all(before[k]==after_stop[k]for k in('life_id','world_id','parent'))and after_stop['physical']['tick']>before['physical']['tick']
        checks['no_pending_or_uncertain']=not q.outstanding()and not owner.get('running')and not owner.get('uncertain_external_result')
        records['explicit_zero_tick_finalize']=command('close_transport_epoch_only_after_stopped_and_empty',['mente-unificada-finalizar-protocolo','--vida',life])
        final=summary(card);records['final']=final;checks['finalize_did_not_advance_or_edit_native_fields']=after_stop['physical']==final['physical'];checks['full_final_snapshot_bytes']=sha(system/final['snapshot'])==final['snapshot_sha256']
    except Exception as error:
        records['harness_error']={'type':type(error).__name__,'detail':str(error)}
        if process and process.poll()is None:
            try:stop('apdpilot_emergency_stop')
            except Exception as stop_error:
                records['own_owner_stop_error']=str(stop_error)
                try:process.wait(timeout=305)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=20);records['only_own_process_terminated_after_safety_horizon']=True
    protected_after={p:sha(Path(p))for p in protected};checks['protected_originals_unchanged']=protected_after==protected;checks['frozen_source_bytes_unchanged']=all(sha(system/r['file'])==r['sha256']for r in sources)
    value={'schema':'DEE.APD01.actual_short_service.R01','protocol':protocol,'records':records,'checks':checks,'functional_issues':functional,'commands':commands,'protected_before':protected,'protected_after':protected_after,'host_seconds':time.monotonic()-started,
           'scope':'One actual ASISTENTE_MAIN service trajectory, not independent learners, policy evidence or the sixty-minute reserve. Requests are operator initiated and raw/result interpretation is separate from transport success. Both successful and adverse outputs are preserved.'}
    target=out/'PILOTO_APD.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'checks':checks,'functional_issues':functional,'error':records.get('harness_error'),'final':records.get('final'),'host_seconds':value['host_seconds']}));return bool(records.get('harness_error')or not all(checks.values()))

if __name__=='__main__':raise SystemExit(main())
