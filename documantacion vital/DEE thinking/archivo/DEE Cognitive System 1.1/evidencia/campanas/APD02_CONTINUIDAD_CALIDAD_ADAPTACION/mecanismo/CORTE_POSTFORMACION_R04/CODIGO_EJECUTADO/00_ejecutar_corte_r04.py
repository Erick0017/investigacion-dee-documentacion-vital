"""R04-specific postformed native trace cut, equal dose sham, unchanged common quality."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Fresh controls only; preserve all earlier evidence')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import aritmetica_apd_01 as arithmetic,asistente_proposito_01 as apd,mente_acumulativa_r02 as ma,evaluador_calidad_apd02 as quality,proveedores_prueba_apd02 as effects
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r04.py';protocol=here/'PROTOCOLO_CORTE_R04.json';proto=json.loads(protocol.read_bytes())
    if sha(source)!=proto['module_sha256']:raise ValueError('Frozen R04 source changed')
    spec=importlib.util.spec_from_file_location('APD02_R04_POSTFORMED_CUT',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    store=Store(args.system);parent=store.record(proto['parent'])
    if parent['snapshot_sha256']!=proto['parent_snapshot_sha256']:raise ValueError('Prepared parent changed; no alternate favorable past')
    sources=[]
    for i,f in enumerate((Path(__file__),source,protocol,args.system/'capacidades/selector_acrecion_nativo.py',Path(arithmetic.__file__),Path(apd.__file__),Path(quality.__file__),Path(effects.__file__),args.system/'app/process_control.py')):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    began=time.monotonic();outcomes=[]
    for mode in proto['arms']:
        if time.monotonic()-began>proto['budget_seconds']:
            outcomes.append({'mode':mode,'not_executed':'Frozen finite budget'});continue
        folder=args.out/mode;folder.mkdir();life='APD02_R04_POSTFORMED_'+mode
        emit(folder/'00_FORK.json.gz',store.fork(proto['parent'],life,kind='APD02_R04_POSTFORMED_TRACE_CAUSAL_INTERVENTION'))
        def one(a):
            if a.tick!=proto['parent_tick']:raise ValueError('No seed or clock reset allowed')
            a.save(folder/'ANTES_COMPLETO.deetsnap.gz');use=m.use(a);q=use['query_tick'];choice=use['reader']['choice']
            if q!=proto['query_tick']or a.tick!=proto['reader_tick']or use['boundary']!=proto['boundary']:raise ValueError('Frozen intervention timing not reached; preserve actual future')
            a.save(folder/'ACCION_FORMADA_ANTES_CORTE_COMPLETO.deetsnap.gz');sinks=[];pre=[]
            if mode!='retain':
                for i,site in enumerate(proto['cut_sites']if mode=='cut'else proto['sham_sites']):
                    o=m.obs(a,site);pre.append(o)
                    if int(o['raw']):raise ValueError('NonzeroRAW diagnostic site; cut not performed, never overwrite')
                    name='APD02.R04.postformed.'+mode+'.'+str(i);m.declare(a,name,site,(0,0,0),0,4);sinks.append(m.submit(a,name,0,proto['sinks_injected_tick']))
            public={'task_id':'cut_task','text':'suma','operands':proto['task']['operands']};native=None;external=None;procedure='native'if choice==-1 else'external'if choice in(0,1)else None
            def native_cb(op,values):
                nonlocal native
                native=arithmetic.native_pair(a,'suma'if op=='add'else'diferencia',*values,detailed=False);return native['numeric_reader']['numeric_result']
            def external_cb(op,values):
                nonlocal external
                external=apd.external_calculator(1 if op=='add'else-1,*values);return external['value']
            if procedure:
                price=proto['task']['prices'][0 if procedure=='native'else 1]
                committed=effects.execute_selected(public,{'operation':'add','procedure':procedure},sandbox_root=folder,native_value_reader=native_cb,external_calculator=external_cb,law={'price':price,'delay_ticks':0,'available':True},synthetic_fixture=False)
            else:committed={'task_id':public['task_id'],'state':'no_output','selected_operation':'add','selected_procedure':None,'artifact':None,'price':0,'delay_ticks':0,'provider_calls':{'native':0,'external':0},'no_silent_replacement':True}
            committed_at=physical(a.world)
            if committed['state']=='uncertain':raise RuntimeError('Preserve real uncertain effect; no retry or fabricated feedback')
            report=quality.evaluate_literal_committed(public,committed,sandbox_root=folder,policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True});projected=quality.actor_feedback(report,binary=True)
            if a.tick<q+proto['delay_after_query']:a.run_until(q+proto['delay_after_query'])
            trace=m.trace_observations(a,q);a.save(folder/'ANTES_FEEDBACK_COMPLETO.deetsnap.gz');outcome=m.consequence(a,projected['category']);a.save(folder/'DESPUES_FEEDBACK_COMPLETO.deetsnap.gz')
            probe=m.use(a);reader=probe['reader'];cleanup=m.consequence(a,'SUCCESS',mode='omit')
            old6=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
            a.save(folder/'FINAL_COMPLETO.deetsnap.gz')
            return{'mode':mode,'use':use,'native_choice':choice,'sink_targets_before':pre,'sink_requests':m.receipts(a,sinks),'public_request':public,'native_arithmetic':native,'external_calculator':external,'committed_effect':committed,'committed_at':committed_at,'quality':report,'actor_feedback':projected,'trace_after_processing':trace,'consequence':outcome,'subsequent_first_reader_without_feedback':reader,'subsequent_probe_generic_cleanup_only':cleanup,'old6_without_teaching':old6,'after':physical(a.world,occupation=True),'scope':proto['scope']}
        try:
            result=store.mutate(life,'APD02_R04_LEGAL_CUT_SHAM_OF_ALREADY_FORMED_TRACE',one);emit(folder/'RESULTADO_COMPLETO.json.gz',result);v=result['result'];record=store.record(life)
            row={'mode':mode,'action_before_cut':v['native_choice'],'quality':v['quality']['feedback']['category'],'category':v['actor_feedback']['category'],'refs_after':[o['s_reg']for o in v['consequence']['after']],'later':v['subsequent_first_reader_without_feedback']['choice'],'sink_statuses':[r['receipt']['status']for r in v['sink_requests']],'old6':[r['result']['reader']['formed_native_command']for r in v['old6_without_teaching']],'life':life,'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256']}
        except Exception as error:
            row={'mode':mode,'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',row)
        outcomes.append(row);print(json.dumps({k:v for k,v in row.items()if k!='reached'}),flush=True);gc.collect()
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.R04.postformed_trace.cut_sham.v1','parent':parent,'protocol':proto,'sources':sources,'outcomes':outcomes,'resources':current_resources(),'elapsed_seconds':time.monotonic()-began});return 0
if __name__=='__main__':raise SystemExit(main())
