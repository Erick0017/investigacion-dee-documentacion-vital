"""Frozen R04 AUX: delayed generic quality, actual one-provider effects, old functions."""
import argparse,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve every prior attempt')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import aritmetica_apd_01 as arithmetic,asistente_proposito_01 as prior,mente_acumulativa_r02 as ma
    from capacidades import evaluador_calidad_apd02 as quality,proveedores_prueba_apd02 as effects,lexico_apd02_01 as words,acumulador_recirculante_apd02 as accumulator
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).parent;source=here/'traza_retorno_demorado_r04.py';protocol=here/'PROTOCOLO_R04_ABAB.json';proto=json.loads(protocol.read_bytes())
    if sha(source)!=proto['module_sha256']:raise ValueError('Frozen mechanism source changed')
    parent=args.system/proto['parent_snapshot']
    if sha(parent)!=proto['parent_sha256']:raise ValueError('Pinned complete adverse future mismatch')
    spec=importlib.util.spec_from_file_location('APD02_R04_PINNED_AUX',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    files=[Path(__file__),source,protocol,args.system/'app/lives.py',args.system/'app/process_control.py']+[Path(x.__file__)for x in(arithmetic,prior,ma,quality,effects,words,accumulator)]
    files += [args.system/'capacidades/selector_acrecion_nativo.py']
    sources=[]
    for i,f in enumerate(files):
        dest=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dest.parent.mkdir(exist_ok=True);shutil.copyfile(f,dest);sources.append({'source':str(f),'file':dest.relative_to(args.out).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'sources':sources,'parent_snapshot_sha256':sha(parent),'native_not_yet_started':True,'resources':current_resources()})
    store=Store(args.system);started=time.monotonic();prepared='APD02_R04_PREPARADO_AUX';emit(args.out/'00_IMPORTACION_FISICA.json.gz',store.import_state(parent,prepared,'fisica_directa',expected=proto['parent_sha256']))
    def prepare(a):
        if a.tick!=proto['parent_tick']:raise ValueError('No clock reset or alternate parent')
        pre=m.preflight(a);a.save(args.out/'ANTES_PREPARACION_COMPLETO.deetsnap.gz')
        result=m.prepare(a);a.save(args.out/'DESPUES_PREPARACION_COMPLETO.deetsnap.gz')
        return{'preflight':pre,'preparation':result,'scope':'New P0 translated anatomy in the existing full adverse future; no teaching or seed'}
    emit(args.out/'01_PREPARACION.json.gz',store.mutate(prepared,'APD02_R04_RAW0_TRANSLATED_BODY_NO_SEED',prepare))
    results=[]
    def panel(a,folder):
        before=physical(a.world);rows=[{'context':c,'result':ma.query(a,c,detail=False)}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
        lex=[{'form':f,'result':words.query(a,f,detailed=False)}for f in words.FORM_CODEC]
        acc=accumulator.accumulate(a,proto['accumulator_public_increment'])
        a.save(folder/'PANEL_FINAL_COMPLETO.deetsnap.gz')
        return{'before':before,'memory':rows,'lexical':lex,'accumulator':acc,'after':physical(a.world),'route_refs':m.refs(a),'scope':'First responses in this branch without teaching; material questions and a declared increment, not passive observation'}
    for mode in ['real']+proto['matched_short_controls']:
        life='APD02_R04_ACTUAL_'+mode;emit(args.out/(mode+'_FORK.json.gz'),store.fork(prepared,life,kind='APD02_R04_SHARED_PREPARED_PREFIX_'+mode))
        count=len(proto['cases'])if mode=='real'else proto['control_cases'];rows=[]
        for i,case in enumerate(proto['cases'][:count]):
            if time.monotonic()-started>proto['budget_seconds']:
                rows.append({'opportunity':i,'not_executed':'Frozen total finite budget reached before starting this opportunity'});break
            folder=args.out/mode/('OP'+str(i));folder.mkdir(parents=True)
            def one(a):
                a.save(folder/'ANTES_COMPLETO.deetsnap.gz');before=physical(a.world);use=m.use(a);q=use['query_tick'];choice=use['reader']['choice'];a.save(folder/'ACCION_FORMADA_COMPLETO.deetsnap.gz')
                operands=case['operands'];native=None;tool=None;public={'task_id':'task_'+str(i),'text':'suma','operands':operands};procedure='native'if choice==-1 else'external'if choice in(0,1)else None
                def native_cb(op,values):
                    nonlocal native
                    native=arithmetic.native_pair(a,'suma'if op=='add'else'diferencia',*values,detailed=False);return native['numeric_reader']['numeric_result']
                def external_cb(op,values):
                    nonlocal tool
                    tool=prior.external_calculator(1 if op=='add'else-1,*values);return tool['value']
                if procedure is not None:
                    ix=0 if procedure=='native'else 1
                    committed=effects.execute_selected(public,{'operation':'add','procedure':procedure},sandbox_root=folder,native_value_reader=native_cb,external_calculator=external_cb,law={'price':case['prices'][ix],'delay_ticks':0,'available':True},synthetic_fixture=False)
                else:committed={'task_id':public['task_id'],'state':'no_output','selected_operation':'add','selected_procedure':None,'artifact':None,'price':0,'delay_ticks':0,'provider_calls':{'native':0,'external':0},'no_silent_replacement':True}
                committed_at=physical(a.world)
                if committed['state']=='uncertain':raise RuntimeError('Real uncertain file effect preserved; no retry or feedback')
                report=quality.evaluate_literal_committed(public,committed,sandbox_root=folder,policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True})
                projected=quality.actor_feedback(report,binary=True)
                until=q+proto['processing_delays_after_query'][i]
                if a.tick<until:a.run_until(until)
                trace=m.trace_observations(a,q);a.save(folder/'ANTES_RETORNO_COMPLETO.deetsnap.gz');outcome=m.consequence(a,projected['category'],mode=mode);a.save(folder/'DESPUES_RETORNO_COMPLETO.deetsnap.gz')
                return{'before':before,'use':use,'native_choice':choice,'selected_procedure':procedure,'native_arithmetic':native,'external_calculator':tool,'public_request':public,'committed_effect':committed,'committed_at':committed_at,'quality':report,'actor_feedback':projected,'mode':mode,'law_auditor_only':case['law'],'trace_after_processing':trace,'consequence':outcome,'after':physical(a.world),'scope':'Prepared SUM-only source task, not lexical/general language selection. The sole selected provider produces a real file before private verification; no expected value or route enters the common return.'}
            try:
                result=store.mutate(life,'APD02_R04_SELECTED_ACTUAL_EFFECT_POSTCOMMIT_GENERIC_QUALITY',one);emit(folder/'RESULTADO_COMPLETO.json.gz',result);v=result['result'];r={'opportunity':i,'law':case['law'],'choice':v['native_choice'],'procedure':v['selected_procedure'],'numeric_correct':v['quality']['axes']['numeric_correct_for_original_request'],'completed_task':v['quality']['completed_task'],'quality':v['quality']['feedback']['category'],'price':v['committed_effect']['price'],'category_returned':v['actor_feedback']['category'],'refs_after':[o['s_reg']for o in v['consequence']['after']],'tick':v['after']['tick']}
            except Exception as e:
                r={'opportunity':i,'error':{'type':type(e).__name__,'detail':str(e)},'reached_record':store.record(life),'no_rollback':True};emit(folder/'ERROR_CONSERVADO.json',r);rows.append(r);print(json.dumps({k:v for k,v in r.items()if k!='reached_record'}),flush=True);break
            rows.append(r);print(json.dumps({'mode':mode,**r}),flush=True)
            if mode=='real'and i+1 in proto['old_functions_after_opportunities']:
                pf=args.out/mode/('PANEL_TRAS_'+str(i+1));pf.mkdir();rr=store.mutate(life,'APD02_R04_OLD14_AND_ACQUIRED_ACCUMULATOR_NO_TEACHING',lambda a:panel(a,pf));emit(pf/'RESULTADO_COMPLETO.json.gz',rr)
                print(json.dumps({'mode':mode,'panel_after':i+1,'memory':[x['result']['reader']['formed_native_command']for x in rr['result']['memory']],'lexical':[x['result']['reader']['formed_native_command']for x in rr['result']['lexical']],'accumulator':rr['result']['accumulator']['numeric_result']}),flush=True)
        results.append({'mode':mode,'rows':rows,'final_record':store.record(life)})
        emit(args.out/(mode+'_RESULTADOS.json'),results[-1])
    emit(args.out/'RESULTADOS.json',{'schema':'APD02.R04.actual_ABAB_and_short_controls.v1','protocol':proto,'sources':sources,'arms':results,'elapsed_seconds':time.monotonic()-started,'resources':current_resources(),'scope':proto['scope']})
    return 0
if __name__=='__main__':raise SystemExit(main())
