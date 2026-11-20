"""Two actual opportunities from the negative O2 state, no reseeding."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v):
    if p.exists():raise FileExistsError('Preserve primary '+str(p))
    b=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')+b'\n';p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--system',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Fresh directory required')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current
    from capacidades import asistente_proposito_01 as apd
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import mente_unificada_01 as mu
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out/'RECURSOS.json')
    here=Path(__file__).parent;module_file=here/'selector_ruta_o2_candidato_r3.py';spec=importlib.util.spec_from_file_location('APD01_O2_UNCHANGED_R3',module_file);route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
    protofile=here/'PROTOCOLO_REVERSION_O2_R3.json';protocol=json.loads(protofile.read_text(encoding='utf-8'));store=Store(args.system);parent=store.record('APD01_ROUTE_O2_R3_real')
    sources=[Path(__file__),protofile,module_file,args.system/'capacidades/asistente_proposito_01.py',args.system/'capacidades/aritmetica_apd_01.py'];archive=args.out/'CODIGO_EJECUTADO';archive.mkdir();frozen=[]
    for n,p in enumerate(sources):
        dst=archive/(str(n).zfill(2)+'_'+p.name);shutil.copyfile(p,dst);frozen.append({'source':str(p.resolve()),'file':dst.relative_to(args.out).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':protocol,'actual_parent':parent,'sources':frozen,'no_reseed':True})
    outcomes=[];start=time.monotonic()
    for condition in protocol['worlds']:
        life='APD01_ROUTE_O2_R3_'+condition['label'];folder=args.out/condition['label'];folder.mkdir();fork=store.fork(parent['life_id'],life,kind='APD01_AFTER_ACTUAL_NEGATIVE_ROUTE_REVERSE_CONTROL');emit(folder/'00_FORK.json.gz',fork)
        def run(a):
            before=physical(a.world);rows=[]
            for n,operands in enumerate(protocol['opportunities']):
                a.save(folder/('OP'+str(n)+'_ANTES_COMPLETO.deetsnap.gz'));use=route.use(a);choice=use['reader']['choice'];native=None;external=None;numeric=None
                if choice==-1:
                    native=arithmetic.native_pair(a,'suma',*operands,detailed=False);numeric=native['numeric_reader']['numeric_result']
                elif choice in(0,1):
                    external=apd.external_calculator(1,*operands);numeric=external['value']
                artifact=None
                if numeric is not None:
                    path=folder/('OP'+str(n)+'_RESULTADO.bin');data=str(numeric).encode('ascii')
                    with path.open('xb')as handle:handle.write(data)
                    artifact={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'numeric_result':numeric}
                price=condition['prices'][0 if choice==-1 else 1];actualcost=price+(0 if artifact else 4)
                returned=route.return_cost(a,actualcost,mode='real')
                row={'opportunity':n,'operands':operands,'route':use,'native_route':choice,'native_calculation':native,'external_calculator':external,'numeric_result':numeric,
                     'artifact':artifact,'completed':artifact is not None,'declared_prices':condition['prices'],'modelled_price':price,'actual_modelled_cost':actualcost,'environmental_return':returned,'references_after':route.refs(a)}
                emit(folder/('OP'+str(n)+'_RESULTADO.json.gz'),row);rows.append(row)
            a.save(folder/'02_POST_DOS_USOS_COMPLETO.deetsnap.gz')
            oldsix=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
            oldcmp=[mu.current(a,v,detail=False)for v in(13,32)]
            return{'before':before,'rows':rows,'old_six':oldsix,'old_comparison13_32':oldcmp,'final':physical(a.world,occupation=True),'route_references_final':route.refs(a)}
        try:
            result=store.mutate(life,'APD01_O2_ACTUAL_LAW_REVERSAL_AFTER_ACQUISITION',run,{'condition':condition,'protocol_sha256':sha(protofile)})
            emit(folder/'03_RESULTADO_COMPLETO.json.gz',result);v=result['result'];summary={'condition':condition,'life':life,'routes':[r['native_route']for r in v['rows']],
                'numeric':[r['numeric_result']for r in v['rows']],'costs':[r['actual_modelled_cost']for r in v['rows']],
                'route_refs':[[o['s_reg']for o in r['references_after']]for r in v['rows']],
                'old_six':[r['result']['reader']['formed_native_command']for r in v['old_six']],'old_cmp':[r['reader']['choice']for r in v['old_comparison13_32']],'final_record':store.record(life)}
        except Exception as error:
            summary={'condition':condition,'life':life,'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'03_ERROR_CONSERVADO.json.gz',summary)
        outcomes.append(summary);gc.collect();print(json.dumps({k:v for k,v in summary.items()if k not in('final_record','reached')},ensure_ascii=False),flush=True)
    emit(args.out/'RESULTADOS.json',{'schema':'APD01.O2.reverse_after_actual_learning.histories.v1','actual_parent':parent,'outcomes':outcomes,'elapsed':time.monotonic()-start,
        'scope':'New continuations from own actually acquired negative state, not reset or positive-prefix comparison. Fixed asymmetric common cost bias is not bidirectional optimal regulation.'})
    return 0

if __name__=='__main__':raise SystemExit(main())
