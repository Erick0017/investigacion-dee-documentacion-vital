"""One unseeded physical AUX: actual selected arithmetic/files and common quality."""
import argparse,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve previous output')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import asistente_proposito_01 as apd
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r03.py';protocol=here/'PROTOCOLO_UNSEEDED_ABAB_R03.json';proto=json.loads(protocol.read_bytes())
    spec=importlib.util.spec_from_file_location('APD02_R03_UNSEEDED',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    store=Store(args.system);parent=store.record(proto['parent']);sources=[]
    for i,f in enumerate((Path(__file__),source,protocol,args.system/'capacidades/selector_acrecion_nativo.py',args.system/'capacidades/aritmetica_apd_01.py',args.system/'capacidades/asistente_proposito_01.py',args.system/'app/process_control.py')):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'parent':parent,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    life='APD02_TRACE_R03_UNSEEDED_REAL';emit(args.out/'00_FORK.json.gz',store.fork(proto['parent'],life,kind='APD02_R03_UNSEEDED_CONTINUOUS_ACTUAL_TASKS'))
    started=time.monotonic();summary=[]
    for i,case in enumerate(proto['cases']):
        if time.monotonic()-started>proto['budget_seconds']:
            summary.append({'opportunity':i,'not_executed':'Frozen450sbudget'});break
        folder=args.out/('OP'+str(i));folder.mkdir()
        def one(a):
            a.save(folder/'ANTES_COMPLETO.deetsnap.gz');before=physical(a.world)
            use=m.use(a);q=use['query_tick'];choice=use['reader']['choice'];a.save(folder/'ACCION_SELECCIONADA_COMPLETO.deetsnap.gz')
            operands=case['operands'];native=None;external=None;number=None;action_error=None
            action_start=time.perf_counter()
            try:
                if choice==-1:
                    native=arithmetic.native_pair(a,'suma',*operands,detailed=False);number=native['numeric_reader']['numeric_result']
                elif choice in(0,1):
                    external=apd.external_calculator(1,*operands);number=external['value']
            except Exception as error:
                action_error={'type':type(error).__name__,'detail':str(error)}
            artifact=None
            if type(number)is int:
                document={'operation':'sum','operands':operands,'value':number}
                path=folder/'RESULTADO_REAL.json';emit(path,document)
                artifact={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'actual_json':document}
            committed_tick=a.tick;action_seconds=time.perf_counter()-action_start
            # The complete effect has been committed before the independent
            # quality/cost check. Its reference is never fed to either tool.
            expected=operands[0]+operands[1]
            check={'requested_operation':'sum','exact_operands':operands,'numeric_correct':type(number)is int and number==expected,
                   'actual_artifact_exists':artifact is not None,'operation_and_operands_preserved':artifact is not None and artifact['actual_json']['operation']=='sum'and artifact['actual_json']['operands']==operands,
                   'target_used_only_by_post_commit_external_auditor':expected}
            route_index=0 if choice==-1 else 1 if choice in(0,1)else None
            price=case['prices'][route_index]if route_index is not None else None
            valid=all(check[k]for k in('numeric_correct','actual_artifact_exists','operation_and_operands_preserved'))
            category='SUCCESS'if valid and price is not None and price<=2 else'FAILURE'
            until=q+proto['delays_after_route_query'][i]
            if a.tick<until:a.run_until(until)
            trace=m.trace_observations(a,q);a.save(folder/'ANTES_CONSECUENCIA_COMPLETO.deetsnap.gz')
            outcome=m.consequence(a,category)
            a.save(folder/'DESPUES_CONSECUENCIA_COMPLETO.deetsnap.gz')
            return{'opportunity':i,'before':before,'use':use,'native_choice':choice,'native_calculation':native,'external_calculator':external,
                    'actual_result':number,'artifact':artifact,'action_error':action_error,'effect_committed_tick':committed_tick,
                    'selected_action_host_seconds':action_seconds,'post_commit_external_validation':check,
                    'hidden_law_auditor_only':case['law'],'modelled_price_of_actual_action':price,'fixed_budget':2,
                    'only_category_returned':category,'trace_after_declared_processing_delay':trace,'consequence':outcome,
                    'after':physical(a.world,occupation=True)}
        try:
            result=store.mutate(life,'APD02_R03_ACTUAL_TASK_AFTER_NATIVE_CHOICE_AND_QUALITY',one)
            emit(folder/'RESULTADO_COMPLETO.json.gz',result);v=result['result']
            row={'opportunity':i,'law':case['law'],'choice':v['native_choice'],'numeric':v['actual_result'],
                 'correct':v['post_commit_external_validation']['numeric_correct'],'artifact':v['artifact']is not None,
                 'price':v['modelled_price_of_actual_action'],'category':v['only_category_returned'],
                 'refs_after':[o['s_reg']for o in v['consequence']['after']],'tick':v['after']['tick']}
        except Exception as error:
            row={'opportunity':i,'law':case['law'],'error':{'type':type(error).__name__,'detail':str(error)},'reached':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',row)
            summary.append(row);print(json.dumps({k:v for k,v in row.items()if k!='reached'}),flush=True);break
        summary.append(row);print(json.dumps(row),flush=True)
    def old_panel(a):
        rows=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
        return{'rows':rows,'final':physical(a.world,occupation=True),'new_route_refs':m.refs(a),'scope':'No teaching or feedback, first old-association responses after the actual shared AUX history.'}
    panel=store.mutate(life,'APD02_R03_OLD6_FIRST_RESPONSE_AFTER_ACTUAL_TASKS',old_panel);emit(args.out/'PANEL_6_ANTERIORES.json.gz',panel)
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.R03.unseeded_actual_ABAB.v1','protocol':proto,'parent':parent,'opportunities':summary,
            'old6':[r['result']['reader']['formed_native_command']for r in panel['result']['rows']],
            'final_record':store.record(life),'resources':current_resources(),'elapsed_seconds':time.monotonic()-started,
            'scope':'One unseeded physical AUX, actual selected computation/JSONeffects and generic postcommit quality. Prepared arithmetic/codecs/timing/neutralHELP remain P0. No MAIN experience or service clone claimed.'})
    return 0
if __name__=='__main__':raise SystemExit(main())
