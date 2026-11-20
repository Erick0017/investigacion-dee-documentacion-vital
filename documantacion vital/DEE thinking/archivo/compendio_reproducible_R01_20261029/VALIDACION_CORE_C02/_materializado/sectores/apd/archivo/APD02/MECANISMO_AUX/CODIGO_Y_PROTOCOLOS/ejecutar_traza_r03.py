"""Prospective R03 delayed generic-quality sensitivity in physical AUX copies."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--parent',default='APD02_BASELINE');args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve earlier attempts')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r03.py';protocol=here/'PROTOCOLO_TRAZA_R03.json';proto=json.loads(protocol.read_bytes())
    spec=importlib.util.spec_from_file_location('APD02_TRACE_R03',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    store=Store(args.system);parent=store.record(args.parent);sources=[]
    for i,f in enumerate((Path(__file__),source,protocol,args.system/'capacidades/selector_acrecion_nativo.py',args.system/'app/process_control.py')):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    started=time.monotonic();prep='APD02_TRACE_R03_PREP';emit(args.out/'00_FORK.json.gz',store.fork(args.parent,prep,kind='APD02_R03_PHYSICAL_AUX_NO_SERVICE_CLONE'))
    prepared=store.mutate(prep,'APD02_R03_P0_ONE_SELECTIVE_ABSORBER',m.prepare);emit(args.out/'01_PREPARACION.json.gz',prepared)
    seeds={}
    for label,side in(('positive','B'),('negative','A')):
        life='APD02_TRACE_R03_'+label+'_SEED';emit(args.out/(label+'_FORK.json.gz'),store.fork(prep,life,kind='APD02_R03_MATCHED_ONE_EXPLICIT_SEED'))
        lesson=store.mutate(life,'APD02_R03_EXPLICIT_SEED_NOT_OUTCOME_LEARNING',lambda a,side=side:m.seed(a,side));emit(args.out/(label+'_SEMILLA.json.gz'),lesson);seeds[label]=life
    summaries=[]
    for i,(seed,mode,categories,query)in enumerate(proto['arms']):
        if time.monotonic()-started>proto['budget_seconds']:
            summaries.append({'arm':i,'not_executed':'Frozen300sbudget'});continue
        folder=args.out/('ARM'+str(i));folder.mkdir();life='APD02_TRACE_R03_ARM'+str(i)
        emit(folder/'00_FORK.json.gz',store.fork(seeds[seed],life,kind='APD02_R03_DELAYED_NATIVE_QUALITY_CONTRAST'))
        def trial(a):
            rows=[]
            for j,category in enumerate(categories):
                a.save(folder/('OP'+str(j)+'_ANTES_COMPLETO.deetsnap.gz'));before=physical(a.world)
                use=m.use(a,query=query);q=use['query_tick'];a.save(folder/('OP'+str(j)+'_ACCION_COMPROMETIDA_COMPLETO.deetsnap.gz'))
                trajectory=[]
                for offset in(10,69,70,71,77,144,211,479,1006+(100 if j else 0)):
                    a.run_until(q+offset);trajectory.append(m.trace_observations(a,q))
                a.save(folder/('OP'+str(j)+'_ANTES_RETORNO_COMPLETO.deetsnap.gz'))
                returned=m.consequence(a,category,mode=mode)
                a.save(folder/('OP'+str(j)+'_DESPUES_RETORNO_COMPLETO.deetsnap.gz'))
                row={'opportunity':j,'before':before,'use':use,'synthetic_category':category,
                     'passive_delay_ticks_after_commit':1000+(100 if j else 0),'trajectory':trajectory,
                     'consequence':returned,'physical_after':physical(a.world,occupation=True)}
                rows.append(row);emit(folder/('OP'+str(j)+'_RESULTADO.json.gz'),row)
            return{'rows':rows,'final':physical(a.world,occupation=True),'references':m.refs(a),
                    'scope':'Two consecutive synthetic-category sensitivity trials in ONE physical AUX life, no reseed/no learned-field replacement. Not actual worker-quality adaptation yet.'}
        try:
            result=store.mutate(life,'APD02_R03_TWO_FROZEN_DELAYED_CONSEQUENCES',trial);emit(folder/'RESULTADO_COMPLETO.json.gz',result);v=result['result'];record=store.record(life)
            row={'arm':i,'seed':seed,'mode':mode,'query':query,'actions':[r['use']['reader']['choice']for r in v['rows']],
                 'before_refs':[[o['s_reg']for o in r['consequence']['before']]for r in v['rows']],
                 'after_refs':[[o['s_reg']for o in r['consequence']['after']]for r in v['rows']],
                 'life':life,'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256']}
        except Exception as error:
            row={'arm':i,'seed':seed,'mode':mode,'query':query,'error':{'type':type(error).__name__,'message':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',row)
        summaries.append(row);print(json.dumps({k:v for k,v in row.items()if k!='reached'},ensure_ascii=False),flush=True);gc.collect()
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.R03.selective_delayed_quality_controls.v1','protocol':proto,'parent':parent,'outcomes':summaries,'elapsed_seconds':time.monotonic()-started,'resources':current_resources()})
    return 0
if __name__=='__main__':raise SystemExit(main())
