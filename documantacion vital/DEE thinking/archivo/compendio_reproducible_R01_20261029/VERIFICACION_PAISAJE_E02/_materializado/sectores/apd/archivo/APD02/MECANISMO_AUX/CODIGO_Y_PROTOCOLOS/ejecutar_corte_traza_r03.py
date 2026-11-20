"""Selective native trace interception after output, with equal-dose sham."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Fresh controls only')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import asistente_proposito_01 as apd
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r03.py';protocol=here/'PROTOCOLO_CORTE_TRAZA_R03.json';proto=json.loads(protocol.read_bytes())
    spec=importlib.util.spec_from_file_location('APD02_R03_CUT',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    store=Store(args.system);parent=store.record(proto['parent']);sources=[]
    for i,f in enumerate((Path(__file__),source,protocol,args.system/'capacidades/selector_acrecion_nativo.py',args.system/'capacidades/aritmetica_apd_01.py',args.system/'capacidades/asistente_proposito_01.py')):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    started=time.monotonic();outcomes=[]
    for mode in proto['arms']:
        if time.monotonic()-started>proto['budget_seconds']:
            outcomes.append({'mode':mode,'not_executed':'Frozen450sbudget'});continue
        folder=args.out/mode;folder.mkdir();life='APD02_R03_POSTFORMED_'+mode
        emit(folder/'00_FORK.json.gz',store.fork(proto['parent'],life,kind='APD02_SELECTIVE_POSTFORMED_TRACE_INTERVENTION'))
        def trial(a):
            a.save(folder/'ANTES_COMPLETO.deetsnap.gz');use=m.use(a);q=use['query_tick'];choice=use['reader']['choice']
            a.save(folder/'ACCION_FORMADA_ANTES_CORTE_COMPLETO.deetsnap.gz');sinks=[];pre=[]
            if mode!='retain':
                z=-2 if mode=='cut'else-6
                for x in(-1,0,1):
                    site=m.at((16*x,16,z));old=m.obs(a,site);pre.append(old)
                    if int(old['raw']):raise ValueError('Diagnostic sink target hasnonzeroRAW; neveroverwrite')
                    name='APD02.R03.postformed.'+mode+'.'+str(x);m.declare(a,name,site,(0,0,0),0,4);sinks.append(m.submit(a,name,0,q+19))
            native=None;external=None;number=None
            if choice==-1:
                native=arithmetic.native_pair(a,'suma',7,8,detailed=False);number=native['numeric_reader']['numeric_result']
            elif choice in(0,1):external=apd.external_calculator(1,7,8);number=external['value']
            artifact=None
            if type(number)is int:
                path=folder/'ARTEFACTO_REAL.json';emit(path,{'operation':'sum','operands':[7,8],'value':number});artifact={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path)}
            committed=a.tick;valid=artifact is not None and number==15;price=1 if choice==-1 else 5
            category='SUCCESS'if valid and price<=2 else'FAILURE'
            if a.tick<q+1006:a.run_until(q+1006)
            trace=m.trace_observations(a,q);a.save(folder/'ANTES_FEEDBACK_COMPLETO.deetsnap.gz')
            outcome=m.consequence(a,category);a.save(folder/'DESPUES_FEEDBACK_COMPLETO.deetsnap.gz')
            newuse=m.use(a);post_reader=newuse['reader'];cleanup=m.consequence(a,'SUCCESS',mode='omit')
            old6=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
            a.save(folder/'FINAL_COMPLETO.deetsnap.gz')
            return{'mode':mode,'use':use,'native_choice_before_cut':choice,'sink_targets_before':pre,'sink_requests':m.receipts(a,sinks),
                    'native_calculation':native,'external_calculator':external,'actual_number':number,'artifact':artifact,
                    'effect_committed_tick':committed,'postcommit_quality':{'numeric_correct':number==15,'artifact_valid':artifact is not None,'actual_action_price':price,'category_only':category},
                    'trace_after1000':trace,'outcome':outcome,'subsequent_first_reader_without_feedback':post_reader,
                    'subsequent_probe_generic_cleanup_only':cleanup,'old6_without_teaching':old6,'final':physical(a.world,occupation=True)}
        try:
            result=store.mutate(life,'APD02_R03_CUT_OR_SHAM_ALREADY_FORMED_TRACE',trial);emit(folder/'RESULTADO_COMPLETO.json.gz',result);v=result['result'];record=store.record(life)
            row={'mode':mode,'action':v['native_choice_before_cut'],'category':v['postcommit_quality']['category_only'],
                 'refs_after':[o['s_reg']for o in v['outcome']['after']],
                 'later':v['subsequent_first_reader_without_feedback']['choice'],
                 'old6':[r['result']['reader']['formed_native_command']for r in v['old6_without_teaching']],
                 'life':life,'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256']}
        except Exception as error:
            row={'mode':mode,'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',row)
        outcomes.append(row);print(json.dumps({k:v for k,v in row.items()if k!='reached'}),flush=True);gc.collect()
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.postformed_trace.cut_sham.v1','parent':parent,'protocol':proto,'outcomes':outcomes,'resources':current_resources(),'elapsed_seconds':time.monotonic()-started})
    return 0
if __name__=='__main__':raise SystemExit(main())
