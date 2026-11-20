"""Execute only the frozen R02 delayed native-action-trace sensitivity controls."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--parent',default='APD02_BASELINE');args=p.parse_args()
    if args.out.exists():raise FileExistsError('Fresh revision only')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import selector_acrecion_nativo as sel
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r02.py';protocol=here/'PROTOCOLO_TRAZA_DEMORADA_R02.json';proto=json.loads(protocol.read_bytes())
    spec=importlib.util.spec_from_file_location('APD02_TRACE_R02',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    store=Store(args.system);parent=store.record(args.parent);sources=[]
    for i,f in enumerate((Path(__file__),source,protocol,args.system/'capacidades/selector_acrecion_nativo.py',args.system/'app/process_control.py')):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    started=time.monotonic();prep='APD02_TRACE_R02_PREP';emit(args.out/'00_FORK.json.gz',store.fork(args.parent,prep,kind='APD02_PHYSICAL_AUX_DELAYED_TRACE_PREPARATION'))
    prepared=store.mutate(prep,'APD02_R02_RAW0_GEOMETRY_NO_ACQUIRED_CONTENT',m.prepare);emit(args.out/'01_PREPARACION.json.gz',prepared)
    seeds={}
    for label,side in(('positive','B'),('negative','A')):
        life='APD02_TRACE_R02_'+label+'_SEED';emit(args.out/(label+'_FORK.json.gz'),store.fork(prep,life,kind='APD02_R02_MATCHED_EXPLICIT_SEED'))
        lesson=store.mutate(life,'APD02_R02_ONE_EXPLICIT_SEED',lambda a,side=side:m.seed(a,side));emit(args.out/(label+'_SEMILLA.json.gz'),lesson);seeds[label]=life
    outcomes=[]
    for i,(seed,category,mode,query)in enumerate(proto['arms']):
        if time.monotonic()-started>proto['budget_seconds']:
            outcomes.append({'arm':i,'not_executed':'Frozen300sbudget'});continue
        folder=args.out/('ARM'+str(i));folder.mkdir();life='APD02_TRACE_R02_ARM'+str(i)
        emit(folder/'00_FORK.json.gz',store.fork(seeds[seed],life,kind='APD02_R02_NATIVE_TRACE_DELAYED_CONTROL'))
        def trial(a):
            a.save(folder/'ANTES_COMPLETO.deetsnap.gz');before=physical(a.world)
            use=m.use(a,query=query);q=use['query_tick'];a.save(folder/'ACCION_COMPROMETIDA_COMPLETO.deetsnap.gz')
            trajectory=[]
            for offset in(10,69,70,71,77,144,211,479,1006):
                a.run_until(q+offset);trajectory.append(m.trace_observations(a,q))
            a.save(folder/'ANTES_RETORNO_COMPLETO.deetsnap.gz')
            returned=m.consequence(a,category,mode=mode);a.save(folder/'DESPUES_RETORNO_COMPLETO.deetsnap.gz')
            rq=a.tick+4;rs=sel.query(a.world,rq,5,m.P);a.run_until(rq+6);later=m.read(a);a.run_until(rq+8)
            a.save(folder/'DESPUES_PRIMER_USO_COMUN_COMPLETO.deetsnap.gz')
            return{'before':before,'query_present':query,'use':use,'passive_work_delay_ticks':1000,
                    'trajectory':trajectory,'outcome':returned,'later_query_tick':rq,'later_reader':later,
                    'later_requests':[sel.receipt(a.world,r)for r in rs],'after':physical(a.world,occupation=True),
                    'scope':'Synthetic generic failure AFTER1000ticks, not task learning. No host routing of returned category; actor not rerun/reinjected from observations. Physical AUX only, no persistent-service clone asserted.'}
        try:
            result=store.mutate(life,'APD02_R02_FROZEN_DELAYED_SENSITIVITY',trial);emit(folder/'RESULTADO.json.gz',result);v=result['result']
            row={'arm':i,'seed':seed,'mode':mode,'query':query,'action':v['use']['reader']['choice'],
                 'before_refs':[o['s_reg']for o in v['outcome']['before']],'after_refs':[o['s_reg']for o in v['outcome']['after']],
                 'later':v['later_reader']['choice'],'loop_1000_observations':v['trajectory'][-1],
                 'life':life,'snapshot':store.record(life)['snapshot'],'snapshot_sha256':store.record(life)['snapshot_sha256']}
        except Exception as error:
            row={'arm':i,'seed':seed,'mode':mode,'query':query,'error':{'type':type(error).__name__,'message':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',row)
        outcomes.append(row);print(json.dumps({k:v for k,v in row.items()if k not in('loop_1000_observations','reached')},ensure_ascii=False),flush=True);gc.collect()
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.delayed_native_trace.sensitivity.v1','protocol':proto,'parent':parent,'outcomes':outcomes,'elapsed_seconds':time.monotonic()-started,'resources':current_resources()})
    return 0
if __name__=='__main__':raise SystemExit(main())
