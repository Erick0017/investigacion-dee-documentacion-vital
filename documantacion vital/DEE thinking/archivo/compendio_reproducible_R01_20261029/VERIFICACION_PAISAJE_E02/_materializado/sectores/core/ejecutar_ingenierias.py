from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess,sys,types
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def clean(value):return {k:v for k,v in value.items() if k not in ('runtime','created_utc','content_sha256')}
def execute(identifier,mat,out,package,recalc=False):
    from ejecutar_cpc9 import compare
    sys.path.insert(0,str(package/'codigo_comun/terceros'))
    import numpy as np
    assert np.__version__=='2.2.6'
    if identifier=='M045':return execute_proc02(mat,out,package,recalc,np)
    if identifier=='M046':return recalc_proc03(mat,out,package,np)
    spec=json.loads((ROOT/'configuraciones/INGENIERIAS_RECUPERACION.json').read_text(encoding='utf8'));selected=[x for x in spec['cases'] if x['mechanism']==identifier]
    report={'mechanism':identifier,'mode':'ARCHIVED_RECALCULATION' if recalc else 'NATIVE_LEGACY_REPRODUCTION','status':'RUNNING','cases':[],'engine':'Original dee_universe_v27 27.0.0 cp313, not a4.5 port','historical_folders_required':False}
    code_root=mat/'ingenierias/codigo'
    for item in selected:
        refs=item['references'];reference=mat/refs['results']['path'];telemetry=mat/refs['telemetry']['path'] if 'telemetry' in refs else None
        assert sha(reference)==refs['results']['sha256'] and (telemetry is None or sha(telemetry)==refs['telemetry']['sha256'])
        expected=json.loads(reference.read_text(encoding='utf8'))
        if recalc:
            row=recalculate(item,expected,telemetry,code_root,np)
            report['cases'].append(row);continue
        run=out/'casos'/item['id'];assert not run.exists();run.mkdir(parents=True)
        work=run/'experimento';shutil.copytree(code_root,work)
        for folder in list(work.rglob('RUNNERS')):
            (folder.parent/'RESULTS').mkdir(exist_ok=True);(folder.parent/'TELEMETRY').mkdir(exist_ok=True)
        module_paths=[package/'codigo_comun/terceros',work/'INGENIERIA_05/04_RAW_CAUSAL_MINIMUM/RUNNERS',work/'INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/RUNNERS',work/'INGENIERIA_05/06_HISTORY_SPECIFICITY/RUNNERS',work/'INGENIERIA_05/04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/INGENIERIA_02_RUNNERS']
        argv=[sys.executable,'-I','-B',ROOT/'replay_native.py','--script',work/item['entry'],'--output',run,'--allow-root',work,'--legacy-wheel',package/'motor/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl']
        for path in module_paths:argv.extend(['--module-path',path])
        argv+=['--',*item['arguments']]
        with (run/'stdout.log').open('w',encoding='utf8') as so,(run/'stderr.log').open('w',encoding='utf8') as se:
            child=subprocess.Popen(list(map(str,argv)),cwd=work,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:exitcode=child.wait(timeout=2400)
            except subprocess.TimeoutExpired:child.kill();child.wait();exitcode=-1
        result=work/item['output_result'];observed=json.loads(result.read_text(encoding='utf8')) if result.exists() else {}
        diffs=compare(clean(observed),clean(expected));identities=observed.get('runtime',{}).get('observed_hashes')==expected.get('runtime',{}).get('observed_hashes')
        actual_npz=work/item['output_telemetry'] if item.get('output_telemetry') else None;arrays=[]
        if telemetry is None:keys_equal=True
        elif actual_npz.exists():
            with np.load(telemetry,allow_pickle=False) as exp,np.load(actual_npz,allow_pickle=False) as act:
                keys_equal=set(exp.files)==set(act.files)
                for key in exp.files:
                    same=key in act and exp[key].dtype==act[key].dtype and exp[key].shape==act[key].shape and bool(np.array_equal(exp[key],act[key]))
                    arrays.append({'array':key,'equal':same,'bytes':int(exp[key].nbytes)})
        else:keys_equal=False
        access=run/'ACCESOS_DEL_PROCESO.json';audit=json.loads(access.read_text(encoding='utf8')) if access.exists() else {'denied_files':['missing audit']}
        ok=exitcode==0 and not diffs and identities and keys_equal and all(x['equal'] for x in arrays) and not audit['denied_files']
        row={'id':item['id'],'status':'PASS' if ok else 'FAIL','exit_code':exitcode,'reference_sha256':sha(reference),'identity_hashes_equal':identities,'physical_JSON_difference_count':len(diffs),'differences':diffs[:100],'array_keys_equal':keys_equal,'arrays_compared':len(arrays),'array_comparison':arrays,'blocked_reads':audit['denied_files'],'command':list(map(str,argv))}
        report['cases'].append(row);put(out/'RESULTADO.json',report)
    report['status']='PASS' if all(x['status']=='PASS' for x in report['cases']) else 'FAIL'
    report['scope']='Misma preparación histórica, originales separados de salidas. Reproducción técnica, no aprendizaje nuevo del ente activo. En recálculo se utilizan datos archivados y no se llama al kernel.'
    return report
def recalculate(item,expected,telemetry,code_root,np):
    # Los arreglos completos se reabren con allow_pickle=False. Sus resúmenes
    # se recomputan sin ejecutar ninguna transición DEE.
    if telemetry is None:
        return {'id':item['id'],'status':'PASS','mode':'ARCHIVED_INSPECTION','recorded_summary':expected.get('summary'),'qualifier':'Primario escalar y terminales conservados; la reproducción nativa verifica su ejecución. Esta vía no hace nueva adjudicación funcional.'}
    arrays=[]
    with np.load(telemetry,allow_pickle=False) as z:
        for key in z.files:
            a=z[key];arrays.append({'name':key,'shape':list(a.shape),'dtype':str(a.dtype),'bytes':int(a.nbytes),'sha256':hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()})
        issues=[];recomputed={}
        if item['id']=='NRD05':
            paths=[code_root/'INGENIERIA_05/04_RAW_CAUSAL_MINIMUM/RUNNERS',code_root/'INGENIERIA_05/04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/INGENIERIA_02_RUNNERS',code_root/'INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/RUNNERS']
            sys.path[:0]=list(map(str,paths));import run_nrd05_history_conditioned_transformation as nrd05
            from ejecutar_cpc9 import compare
            for config,case in expected['executed_cases'].items():
                recomputed[config]={}
                for stage in ('D0','D64'):
                    states={h:(z[f'{config}_{stage}_{h}_raw_a'],z[f'{config}_{stage}_{h}_clock_a']) for h in nrd05.WORLDS}
                    diagnostics={h:{c:{t:(z[f'{config}_{stage}_{h}_{c}_h{t}_raw'],z[f'{config}_{stage}_{h}_{c}_h{t}_clock']) for t in nrd05.HORIZONS} for c in ('C0','C3','RESPONSE')} for h in nrd05.WORLDS}
                    value=nrd05.analyze_stage(states,diagnostics);recomputed[config][stage]=value
                    issues+=compare(value,case['stages'][stage])
        else:
            # Las series preservan resultados y soportes completos. Esta vía
            # enumera y hashea arrays exactos; la prueba física y sus dictámenes
            # completos pertenecen a la opción nativa, no a esta inspección.
            recomputed={'archive_arrays_indexed':len(arrays),'recorded_status':expected['status'],'functional_adjudication_recalculated':False}
    return {'id':item['id'],'status':'PASS' if not issues else 'FAIL','mode':'ARCHIVED_RECALCULATION','arrays':arrays,'recomputed':recomputed,'issues':issues[:100],'scope':'NRD05: factorial y efectos futuros recomputados desdeRAW/clocks. Otros: índice exacto de arrays, sin nueva evolución ni adjudicación funcional recalculada.'}

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def clean_proc(value):
    if isinstance(value,dict):return {k:clean_proc(v) for k,v in value.items() if k not in ('runtime','elapsed_seconds','created_utc','content_sha256')}
    if isinstance(value,list):return [clean_proc(x) for x in value]
    return value
def execute_proc02(mat,out,package,recalc,np):
    from ejecutar_cpc9 import compare
    expected=json.loads((mat/'procesos02/primarios/results.json').read_text(encoding='utf8'));ref_npz=mat/'procesos02/primarios/telemetry.npz'
    if recalc:
        module=load_module('proc02_pure_observers',mat/'procesos02/codigo/runner_procesos02.py');rows=[]
        with np.load(ref_npz,allow_pickle=False) as z:
            for config,branches in expected['component_measurements'].items():
                for branch,reference in branches.items():
                    a=z[f'{config}__{branch}__component_raw_vectors'];changed=np.flatnonzero(np.any(a!=a[0],axis=1));first=None if not len(changed) else int(changed[0]);stable=None
                    if first is not None:
                        stable=next((t for t in range(first,len(a)) if bool(np.all(a[t:]==a[t]))),None)
                    indices=np.flatnonzero(a[-1]!=a[0]);actual={'first_change':first,'stable_from':stable,'changed_record_indices':[int(x) for x in indices],'terminal_records':[module.decode_record(int(a[-1,x])) for x in indices]}
                    projected={k:reference[k] for k in actual};diff=compare(actual,projected);rows.append({'configuration':config,'branch':branch,'actual':actual,'differences':diff,'status':'PASS' if not diff else 'FAIL'})
        return {'mechanism':'M045','mode':'ARCHIVED_RECALCULATION','status':'PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL','cases':rows,'scope':'Cambio y estabilización del componente recomputados desde los vectoresRAW; no nueva transición nativa ni nuevo diagnóstico de restauración.'}
    work=out/'experimento';assert not work.exists();shutil.copytree(mat/'procesos02/codigo',work);calls=[]
    for args in [['--configuration',n] for n in ['MAIN_S0','FRESH_V1','FRESH_V2']]+[['--analyze-main'],['--combine']]:
        name='_'.join(x.replace('--','') for x in args);audit_out=out/'auditorias'/name;audit_out.mkdir(parents=True)
        argv=[sys.executable,'-I','-B',ROOT/'replay_native.py','--script',work/'runner_procesos02.py','--output',audit_out,'--allow-root',work,'--module-path',package/'codigo_comun/terceros','--legacy-wheel',package/'motor/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl','--flat-legacy-runtime','--',*args]
        with (audit_out/'stdout.log').open('w',encoding='utf8') as so,(audit_out/'stderr.log').open('w',encoding='utf8') as se:
            child=subprocess.Popen(list(map(str,argv)),cwd=work,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:code=child.wait(timeout=1800)
            except subprocess.TimeoutExpired:child.kill();child.wait();code=-1
        access=audit_out/'ACCESOS_DEL_PROCESO.json';audit=json.loads(access.read_text(encoding='utf8')) if access.exists() else {'denied_files':['missing audit']};calls.append({'arguments':args,'command':list(map(str,argv)),'exit_code':code,'blocked_reads':audit['denied_files']})
        if code:break
    f=work/'results.json';act=json.loads(f.read_text(encoding='utf8')) if f.exists() else {};diffs=compare(clean_proc(act),clean_proc(expected));rows=[];keys_equal=False
    produced=work/'telemetry.npz'
    if produced.exists():
        with np.load(ref_npz,allow_pickle=False) as exp,np.load(produced,allow_pickle=False) as actual:
            keys_equal=set(exp.files)==set(actual.files)
            for k in exp.files:rows.append({'name':k,'equal':k in actual and bool(np.array_equal(actual[k],exp[k])),'dtype_equal':k in actual and actual[k].dtype==exp[k].dtype})
    identity_checks={n:act.get('configurations',{}).get(n,{}).get('runtime',{}).get('kernel_sha256')==expected['configurations'][n]['runtime']['kernel_sha256'] for n in expected['configurations']}
    passed=len(calls)==5 and all(x['exit_code']==0 and not x['blocked_reads'] for x in calls) and not diffs and keys_equal and all(x['equal'] and x['dtype_equal'] for x in rows) and all(identity_checks.values())
    return {'mechanism':'M045','mode':'NATIVE_LEGACY_REPRODUCTION','status':'PASS' if passed else 'FAIL','calls':calls,'scientific_differences':diffs[:100],'difference_count':len(diffs),'arrays':rows,'array_keys_equal':keys_equal,'identity_checks':identity_checks,'scope':'Tres geometrías completas más diagnóstico y combinación originales; sin comando de empaquetado histórico ni modificación del original.'}
def recalc_proc03(mat,out,package,np):
    from ejecutar_cpc9 import compare
    work=mat/'procesos03';module=load_module('proc03_archived_analysis',work/'dee_r4_new_discovery_runner_v1.py');fake=types.SimpleNamespace(work=work)
    cal=module.calibration_analysis(fake);expected_cal=json.loads((work/'modules/CALIBRATION_ANALYSIS.json').read_text(encoding='utf8'));dc=compare(cal,expected_cal)
    disc=module.discovery_analysis(fake,cal);expected_disc=json.loads((work/'modules/DISCOVERY_ANALYSIS.json').read_text(encoding='utf8'));dd=compare(disc,expected_disc)
    put(out/'CALIBRACION_RECALCULADA.json',cal);put(out/'DISCOVERY_RECALCULADA.json',disc)
    return {'mechanism':'M046','mode':'ARCHIVED_RECALCULATION','status':'PASS' if not dc and not dd else 'FAIL','calibration_differences':dc[:100],'discovery_differences':dd[:100],'difference_count':len(dc)+len(dd),'recorded_status':disc.get('status'),'scope':'Estadísticos, calibración y selección originales recomputados desde seriesJSONmedidas con semillas congeladas. No se ejecutaNative ni se presentaUNINFORMATIVEcomo capacidadtermodinámica/cognitiva.'}
