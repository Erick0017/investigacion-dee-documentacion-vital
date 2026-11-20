"""Prepared O2 routing with actual math, modelled cost and common returns."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v):
    if p.exists():raise FileExistsError('Preserve primary '+str(p))
    b=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')+b'\n'
    p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--parent',default='APD01_BASE_LEXICA');args=ap.parse_args()
    if args.out.exists():raise FileExistsError('Fresh experiment directory only')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current
    from capacidades import asistente_proposito_01 as apd
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import mente_unificada_01 as mu
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out/'RECURSOS.json')
    here=Path(__file__).parent;module_file=here/'selector_ruta_o2_candidato_r3.py';spec=importlib.util.spec_from_file_location('APD01_ROUTE_O2_R3',module_file);route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
    proto_file=here/'PROTOCOLO_RUTA_O2_R3.json';proto=json.loads(proto_file.read_text(encoding='utf-8'));store=Store(args.system);parent=store.record(args.parent)
    sources=[Path(__file__),module_file,proto_file,args.system/'capacidades/asistente_proposito_01.py',args.system/'capacidades/aritmetica_apd_01.py',args.system/'capacidades/selector_acrecion_nativo.py']
    archive=args.out/'CODIGO_EJECUTADO';archive.mkdir();frozen=[]
    for n,source in enumerate(sources):
        destination=archive/(str(n).zfill(2)+'_'+source.name);shutil.copyfile(source,destination);frozen.append({'source':str(source.resolve()),'file':destination.relative_to(args.out).as_posix(),'sha256':sha(source),'bytes':source.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':frozen,'native_not_yet_started':True})
    start=time.monotonic();seed='APD01_ROUTE_O2_R3_SEED';fork=store.fork(args.parent,seed,kind='APD01_NEW_ROUTE_ANATOMY_SAME_EXISTING_WORLD');emit(args.out/'00_FORK_SEED.json.gz',fork)
    def teach(a):
        preparation=route.prepare(a)
        if not preparation['all_admitted']:raise ValueError('Partial anatomy preserved, cannot call it ready')
        before=physical(a.world);lesson=route.seed_B(a)
        return{'preparation':preparation,'before_seed':before,'seed':lesson,'after_seed':physical(a.world)}
    try:seed_result=store.mutate(seed,'APD01_ROUTE_O2_PREPARE_AND_ONE_EXPLICIT_B_SEED',teach)
    except Exception as error:
        emit(args.out/'01_SEED_ERROR_CONSERVADO.json',{'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(seed)});raise
    emit(args.out/'01_SEED_COMPLETO.json.gz',seed_result);outcomes=[]
    for mode in proto['three_arms']:
        if time.monotonic()-start>=proto['budget_seconds']:
            outcomes.append({'mode':mode,'not_executed':'Fixed300s budget'});continue
        life='APD01_ROUTE_O2_R3_'+mode;folder=args.out/mode;folder.mkdir();fork=store.fork(seed,life,kind='APD01_MATCHED_ROUTE_COMMON_COST_CONTROL');emit(folder/'00_FORK.json.gz',fork)
        def run(a):
            rows=[];before=physical(a.world)
            for n,operands in enumerate(proto['task_opportunities']):
                a.save(folder/('OP'+str(n)+'_ANTES_COMPLETO.deetsnap.gz'))
                use=route.use(a);choice=use['reader']['choice'];native=None;external=None;numeric=None
                action_started=time.perf_counter()
                if choice==-1:
                    native=arithmetic.native_pair(a,'suma',*operands,detailed=False);numeric=native['numeric_reader']['numeric_result']
                elif choice in(0,1):
                    external=apd.external_calculator(1,*operands);numeric=external['value']
                artifact=None
                if numeric is not None:
                    path=folder/('OP'+str(n)+'_RESULTADO.bin');b=str(numeric).encode('ascii')
                    with path.open('xb')as handle:handle.write(b)
                    artifact={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'result_integer':numeric,
                              'conversion':'Actual selected-route numeric result serialized to a synthetic local file. No target/readback correction.'}
                action_wall=time.perf_counter()-action_started
                completed=artifact is not None
                price=(1 if choice==-1 else 5)if completed else 5
                returned=route.return_cost(a,price,mode=mode)
                row={'opportunity':n,'operands':operands,'route':use,'native_route':choice,
                     'native_calculation':native,'external_calculator':external,'numeric_result':numeric,
                     'artifact':artifact,'completed':completed,'modelled_price':price,'actual_action_host_seconds':action_wall,
                     'environmental_return':returned,'references_after':route.refs(a)}
                rows.append(row);emit(folder/('OP'+str(n)+'_RESULTADO.json.gz'),row)
            a.save(folder/'02_POST_TAREAS_COMPLETO.deetsnap.gz')
            old_six=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
            old_cmp=[mu.current(a,value,detail=False)for value in(13,32)]
            return{'before':before,'rows':rows,'old_six':old_six,'old_comparison13_32':old_cmp,'final':physical(a.world,occupation=True),'route_references_final':route.refs(a)}
        try:
            result=store.mutate(life,'APD01_ROUTE_O2_THREE_ACTUAL_TASKS_COMMON_COST',run,{'mode':mode,'protocol_sha256':sha(proto_file)})
            emit(folder/'03_RESULTADO_COMPLETO.json.gz',result);v=result['result']
            row={'mode':mode,'life':life,'routes':[r['native_route']for r in v['rows']],
                 'numeric':[r['numeric_result']for r in v['rows']], 'completed':sum(r['completed']for r in v['rows']),
                 'modelled_prices':[r['modelled_price']for r in v['rows']],
                 'route_refs':[[o['s_reg']for o in r['references_after']]for r in v['rows']],
                 'old_six':[r['result']['reader']['formed_native_command']for r in v['old_six']],
                 'old_cmp':[r['reader']['choice']for r in v['old_comparison13_32']],
                 'final_record':store.record(life)}
        except Exception as error:
            row={'mode':mode,'life':life,'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'03_ERROR_CONSERVADO.json.gz',row)
        outcomes.append(row);gc.collect();print(json.dumps({k:v for k,v in row.items()if k not in('final_record','reached')},ensure_ascii=False),flush=True)
    emit(args.out/'RESULTADOS.json',{'schema':'APD01.O2.common_cost.actual_task_controls.v1','elapsed':time.monotonic()-start,'parent':parent,'seed_record':store.record(seed),'outcomes':outcomes,
                                    'scope':'Same-world prepared route anatomy and explicit seed; actual native/external math follows fixed native-emission transduction. Environmental price/excess/cadence are designed, not learned credit assignment or generalR2.'})
    return 0

if __name__=='__main__':raise SystemExit(main())
