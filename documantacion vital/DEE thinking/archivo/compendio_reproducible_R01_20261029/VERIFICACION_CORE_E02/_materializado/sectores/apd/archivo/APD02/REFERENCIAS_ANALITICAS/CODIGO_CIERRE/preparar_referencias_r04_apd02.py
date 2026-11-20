"""N0 preparation/finalization of external analytical references, never DEE execution."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def cp(source,target):target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aux',type=Path,required=True);p.add_argument('--main-protocol',type=Path,required=True);p.add_argument('--main-closed',type=Path);p.add_argument('--stage',type=Path,required=True);args=p.parse_args();here=Path(__file__).parent
    if args.stage.exists():raise FileExistsError('New stage/revision required')
    args.stage.mkdir(parents=True);ev=args.stage/'EVIDENCIA'
    cp(args.aux/'CODIGO_EJECUTADO/02_PROTOCOLO_R04_ABAB.json',ev/'AUXILIAR/PROTOCOLO.json')
    for i in range(8):cp(args.aux/'real'/('OP'+str(i))/'RESULTADO_COMPLETO.json.gz',ev/'AUXILIAR'/('OP'+str(i))/'RESULTADO_COMPLETO.json.gz')
    cp(args.main_protocol,ev/'MAIN/PROTOCOLO.json')
    if args.main_closed:
        for name in('RESUMEN.json','REGISTROS_VENTANA.json.gz'):cp(args.main_closed/name,ev/'MAIN'/name)
    cp(here/'comparar_politicas_r04_apd02.py',args.stage/'RECALCULO/comparar_politicas_r04_apd02.py');cp(Path(__file__),args.stage/'CODIGO_CIERRE'/Path(__file__).name)
    for source in sorted(here.glob('*_NO_NATIVE.py')):cp(source,args.stage/'INSTRUMENTACION'/source.name)
    for source in(here/'REFERENCIAS_R04_PREPARACION_R01/ERROR_N0.json',here/'POLITICAS_R04_R2/PRUEBA_PORTABLE.json',here/'POLITICAS_R04_R2/ERROR_N0.json'):
        if source.is_file():cp(source,args.stage/'INSTRUMENTACION'/source.parent.name/source.name)
    spec=__import__('importlib.util',fromlist=['util']);s=spec.spec_from_file_location('POLICYMODEL',here/'comparar_politicas_r04_apd02.py');m=spec.module_from_spec(s);s.loader.exec_module(m)
    auxiliary=m.public_laws_aux(json.loads((ev/'AUXILIAR/PROTOCOLO.json').read_bytes()));main=m.public_laws_main(json.loads((ev/'MAIN/PROTOCOLO.json').read_bytes()));checks=[]
    for name,laws,wanted in(('AUX',auxiliary,[28,20,24,8]),('MAIN',main,[32,40,28,12])):
        got=[m.simulate(laws,policy)['metrics']['total_modelled_price']for policy in('always_native','always_external','conventional_WSLS','private_oracle')]
        if got!=wanted:raise AssertionError((name,got,wanted))
        checks.append({'domain':name,'costs_AlwaysN_AlwaysE_WSLS_Oracle':got,'expected':wanted,'passed':True})
    emit(args.stage/'PRUEBAS_MODELO_N0.json',{'native_ticks':0,'synthetic_unit_checks':checks,'scope':'Algebraic model checks only, not replaying actions or certifying counterfactual arithmetic'})
    output=args.stage/'REFERENCIA.json';r=m.calculate(ev);emit(output,r)
    test=Path(tempfile.mkdtemp(prefix='apd02_policy_n0_'));target=test/'COPIA';shutil.copytree(args.stage,target);out=test/'RESULTADO.json'
    run=subprocess.run([sys.executable,'-I','-B',str(target/'RECALCULO/comparar_politicas_r04_apd02.py'),'--evidencia',str(target/'EVIDENCIA'),'--salida',str(out)],capture_output=True,text=True,encoding='utf8')
    equal=out.is_file()and out.read_bytes()==output.read_bytes()
    emit(args.stage/'PRUEBA_PORTABLE.json',{'exit_code':run.returncode,'byte_identical':equal,'reference_sha256':sha(output),'recomputed_sha256':sha(out)if out.is_file()else None,'stdout':run.stdout,'stderr':run.stderr,'native_ticks':0,'DEE_import':False})
    if run.returncode or not equal:raise RuntimeError('Failed portable model recalculation')
    emit(args.stage/'PLAN_RECALCULO.json',{'jobs':[{'id':'REFERENCIAS_EXTERNAS_ANALITICAS_R04','name':'REFERENCIAS_EXTERNAS_ANALITICAS_R04','base':'.','script':'RECALCULO/comparar_politicas_r04_apd02.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIA.json'}]})
    emit(args.stage/'ESTADO.json',{'status':'CLOSED'if args.main_closed else'PREPARACION_NO_FINAL','native_ticks':0,'closed_AUX_actual_rows':8,'closed_MAIN_actual_rows':len(r['studies']['MAIN']['observed_learner']['rows'])if r['studies']['MAIN']['observed_learner']else 0,'prospective_MAIN_law_model_is_not_MAIN_result':not bool(args.main_closed),'runtime_or_actor_policy_installed':False,'scope':'Separate analytic external comparison, not new reference-controller executions. No learner history, artifact or quality label changed.'})
    files=[{'file':p.relative_to(args.stage).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(args.stage.rglob('*'))if p.is_file()]
    emit(args.stage/'MANIFIESTO.json',{'files':files,'no_self_hash':True});print(json.dumps({'stage':str(args.stage),'manifest_sha256':sha(args.stage/'MANIFIESTO.json'),'state':'CLOSED'if args.main_closed else'PREPARACION_NO_FINAL','portable_byte_identical':equal}));return 0
if __name__=='__main__':raise SystemExit(main())
