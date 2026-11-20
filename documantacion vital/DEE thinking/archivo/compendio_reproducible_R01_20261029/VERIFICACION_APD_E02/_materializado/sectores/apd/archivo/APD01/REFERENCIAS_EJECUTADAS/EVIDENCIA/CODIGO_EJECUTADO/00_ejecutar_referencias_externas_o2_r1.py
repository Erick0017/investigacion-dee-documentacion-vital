"""Declared HOST policy controls on complete O2 copies. NEVER a MAIN/DEE policy."""
import argparse,gc,gzip,hashlib,importlib.util,json,os,shutil,sys,time
from pathlib import Path

BUDGET=2
POLICIES=('always_native','always_external','stay_until_last_cost_exceeds_budget_then_alternate')

def choose(policy,previous_action,previous_cost,initial_action):
    # The public environmental law, operands, target and DEE response are NOT arguments.
    if policy=='always_native':return'native'
    if policy=='always_external':return'external'
    if policy!=POLICIES[2]:raise ValueError('Unknown external reference')
    if previous_action is None:return initial_action
    if previous_cost is None:raise ValueError('No observed preceding consequence')
    if previous_cost>BUDGET:return'external'if previous_action=='native'else'native'
    return previous_action

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v):
    if p.exists():raise FileExistsError('Preserve reached reference data: '+str(p))
    b=(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--domains',choices=('initial','both'),default='both')
    ap.add_argument('--approved',action='store_true',help='Run only after Root reviews frozen protocol/source and grants the native slot')
    a=ap.parse_args()
    if not a.approved:raise ValueError('PREPARATION ONLY: explicit Root GO required before native ticks')
    if a.out.exists():raise FileExistsError('Fresh reference directory required')
    for key in('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
        if os.environ.get(key)!='1':raise ValueError('One native thread must be set before engine import: '+key)
    here=Path(__file__).resolve().parent;protocol_path=here/'PROTOCOLO_REFERENCIAS_EJECUTADAS_O2_R1.json';protocol=json.loads(protocol_path.read_text(encoding='utf8'))
    if protocol['memory_limit_bytes']!=536870912 or protocol['maximum_concurrent_auxiliary_Runtime']!=1:raise ValueError('Original resource contract changed')
    a.out.mkdir(parents=True);sys.path.insert(0,str(a.system.resolve()))
    from app.process_control import protect_current
    protect_current(output=a.out/'RECURSOS_DEL_WORKER.json',memory_limit=protocol['memory_limit_bytes'])
    from app.lives import Store
    from app.native_tools import physical
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import asistente_proposito_01 as assistant
    source=here/'selector_ruta_o2_candidato_r3.py';spec=importlib.util.spec_from_file_location('APD_O2_REFERENCE_BODY_UNCHANGED',source);route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
    store=Store(a.system);domains=protocol['sources'][:1]if a.domains=='initial'else protocol['sources'];parents=[]
    for item in domains:
        rec=store.record(item['parent_life'])
        if rec['snapshot']!=item['parent_snapshot']or rec['snapshot_sha256']!=item['parent_snapshot_sha256']or rec['physical']['tick']!=item['parent_tick']or rec['physical']['RAW_sha256']!=item['parent_RAW_sha256']or rec['physical']['clocks_sha256']!=item['parent_clocks_sha256']:
            raise ValueError('Named actual full parent changed; never substitute latest/favorable source')
        if sha(a.system/rec['snapshot'])!=item['parent_snapshot_sha256']:raise ValueError('Actual parent snapshot bytes changed')
        parents.append(rec)
    source_files=[Path(__file__),protocol_path,source,*[a.system/x for x in('capacidades/aritmetica_apd_01.py','capacidades/percepcion_cruda_fi01.py','capacidades/mente_unificada_01.py','capacidades/mente_acumulativa_r02.py','capacidades/selector_acrecion_nativo.py','capacidades/asistente_proposito_01.py','app/lives.py','app/native_tools.py')]]
    archive=a.out/'CODIGO_EJECUTADO';archive.mkdir();frozen=[]
    for index,p in enumerate(source_files):
        dest=archive/(str(index).zfill(2)+'_'+p.name);shutil.copyfile(p,dest)
        if sha(dest)!=sha(p):raise ValueError('Source changed while freezing')
        frozen.append({'source_local_locator':str(p.resolve()),'file':dest.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    emit(a.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':protocol,'selected_domains':a.domains,'parents':parents,'sources':frozen,
           'classification':'DECLARED_EXTERNAL_CONTROLLER_REFERENCES_NOT_DEE_SELECTION','main_touched':False,'native_not_yet_started':True})
    start=time.monotonic();outcomes=[]
    for domain in domains:
        for number,policy in enumerate(POLICIES):
            if time.monotonic()-start>=protocol['budget_seconds_total']:
                outcomes.append({'domain':domain['domain'],'policy':policy,'not_executed':'One total300s bound reached; no restart'});continue
            label=domain['domain']+'__'+policy;folder=a.out/label;folder.mkdir()
            life='APD01_HOSTREF_'+('INITIAL'if domain['domain'].startswith('INITIAL')else'REVERSE')+'_'+str(number)
            fork=store.fork(domain['parent_life'],life,kind='APD01_DECLARED_HOST_CONTROLLED_REFERENCE_NOT_DEE_POLICY');emit(folder/'00_FORK_COMPLETO.json.gz',fork)
            def run(owner):
                before=physical(owner.world);rows=[];previous_action=None;previous_cost=None
                for index,operands in enumerate(domain['opportunities']):
                    if time.monotonic()-start>=protocol['budget_seconds_total']:raise TimeoutError('One total300s reference bound; current future is preserved')
                    owner.save(folder/('OP'+str(index)+'_ANTES_COMPLETO.deetsnap.gz'))
                    native_query=route.use(owner)
                    action=choose(policy,previous_action,previous_cost,domain['initial_adaptive_action'])
                    native=None;external=None;numeric=None;started=time.perf_counter()
                    if action=='native':
                        native=arithmetic.native_pair(owner,'suma',*operands,detailed=False);numeric=native['numeric_reader']['numeric_result']
                    else:external=assistant.external_calculator(1,*operands);numeric=external['value']
                    artifact=None
                    if numeric is not None:
                        path=folder/('OP'+str(index)+'_RESULTADO.bin');payload=str(numeric).encode('ascii')
                        with path.open('xb')as f:f.write(payload)
                        artifact={'file':path.name,'bytes':len(payload),'sha256':sha(path),'actual_numeric_result':numeric}
                    action_seconds=time.perf_counter()-started;price=domain['prices'][action]
                    cost=(price if artifact else 5)if domain['missing_artifact_rule']=='fixed_deadline5'else price+(0 if artifact else 4)
                    returned=route.return_cost(owner,cost,mode='real')
                    row={'opportunity':index,'public_operands':operands,'operation':'prepared_SUM',
                         'classification':'HOST_REFERENCE_ACTION_NOT_A_DEE_DECISION',
                         'native_query':native_query,'native_route_observed_but_not_used_for_reference_choice':native_query['reader']['choice'],
                         'host_reference_policy':policy,'host_reference_action':action,
                         'policy_information_before_action':{'previous_action':previous_action,'previous_own_actual_cost':previous_cost,'initial_action':domain['initial_adaptive_action'],'budget':BUDGET},
                         'native_calculation':native,'external_calculator':external,'numeric_result':numeric,
                         'artifact':artifact,'completed':artifact is not None,'modelled_price':price,'actual_modelled_cost':cost,
                         'action_host_seconds':action_seconds,'common_return':returned,'references_after':route.refs(owner),
                         'resources_scope':'Every reference receives O2 query/common-return family. Actual native arithmetic additionally consumes its128 raw channels/resources; external arithmetic does not. Calendar follows reached tick; no phase rescue or dose equality claim.'}
                    emit(folder/('OP'+str(index)+'_RESULTADO.json.gz'),row);rows.append(row)
                    owner.save(folder/('OP'+str(index)+'_DESPUES_COMPLETO.deetsnap.gz'))
                    previous_action=action;previous_cost=cost
                return {'domain':domain['domain'],'policy':policy,'before':before,'rows':rows,'final':physical(owner.world,occupation=True),'final_route_references':route.refs(owner),
                        'scope':'Actual numeric/file/cost reference execution under an external controller, not acquired route selection, new semantic acquisition or a MAIN continuation.'}
            try:
                result=store.mutate(life,'APD01_HOST_REFERENCE_ACTUAL_TOOL_AND_COMMON_RETURN',run,{'domain':domain['domain'],'policy':policy,'protocol_sha256':sha(protocol_path),'host_override_explicit_reference_only':True})
                emit(folder/'01_RESULTADO_COMPLETO.json.gz',result);data=result['result']
                outcome={'domain':domain['domain'],'policy':policy,'life':life,'actions':[r['host_reference_action']for r in data['rows']],
                         'observed_native_queries':[r['native_route_observed_but_not_used_for_reference_choice']for r in data['rows']],
                         'numeric':[r['numeric_result']for r in data['rows']],'completed':[r['completed']for r in data['rows']],
                         'costs':[r['actual_modelled_cost']for r in data['rows']],'final_record':store.record(life)}
            except Exception as error:
                outcome={'domain':domain['domain'],'policy':policy,'life':life,'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback_or_retry':True};emit(folder/'01_ERROR_CONSERVADO.json.gz',outcome)
            outcomes.append(outcome);gc.collect();print(json.dumps({k:v for k,v in outcome.items()if k not in('final_record','reached')},ensure_ascii=False),flush=True)
    emit(a.out/'RESULTADOS.json',{'schema':'APD01.host_reference_policy.actual_executions.v1','elapsed_seconds':time.monotonic()-start,'outcomes':outcomes,
                                 'native_tasks_requested_maximum':sum(len(d['opportunities'])*len(POLICIES)for d in domains),'main_modified':False,
                                 'scope':'Actual externally controlled reference branches only. Do not count these reference choices as DEE learning, generalR2, independent learners or CPU/energy superiority.'})
    return 0

if __name__=='__main__':raise SystemExit(main())
