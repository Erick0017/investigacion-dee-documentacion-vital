"""Own synthetic fixture: verify CAS helpers without real experiments, ZIP, or DEE."""
import argparse,gzip,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def run(cmd,cwd=None):
    p=subprocess.run([sys.executable,'-I','-B','-X','utf8',*map(str,cmd)],cwd=cwd,capture_output=True,text=True,encoding='utf8');return{'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent
    if a.out.exists():raise FileExistsError('New fixture revision only')
    a.out.mkdir(parents=True);stages=[]
    for name,field in(('FIX_A','files'),('FIX_B','members')):
        root=a.out/name;(root/'CODIGO').mkdir(parents=True);shutil.copyfile(here/'fixture_recalculo_stdlib.py',root/'CODIGO/calcular.py');(root/'DATOS.json.gz').write_bytes(gzip.compress(b'[3,5]',mtime=0))
        emit(root/'REFERENCIA.json',{'fixture_only':True,'native_ticks':0,'values':[3,5],'external_Python_sum':8})
        job={'script':'CODIGO/calcular.py','args':['--evidence','DATOS.json.gz'],'reference':'REFERENCIA.json'}
        if name=='FIX_B':job.update({'name':'EXPLICIT_OUTPUT','args':['--evidence','DATOS.json.gz','--output','{output}']})
        emit(root/'PLAN_RECALCULO.json',{'cases':[job]})
        rows=[{'file':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(root.rglob('*'))if f.is_file()];emit(root/'MANIFIESTO.json',{field:rows})
        stages.append({'namespace':name,'source':name,'status':'CLOSED','manifest':'MANIFIESTO.json','manifest_sha256':sha(root/'MANIFIESTO.json'),'plan':'PLAN_RECALCULO.json'})
    note=a.out/'NOTA_FIXTURE.md';note.write_text('Synthetic technical fixture; no DEE experiment.\n',encoding='utf8',newline='\n')
    config={'status':'PREPARACION_NO_FINAL','source_root':str(a.out.resolve()),'root_final_assembly_authorized':False,'stages':stages,'expected_case_count':2,'public_files':[{'source':note.name,'to':name,'sha256':sha(note)}for name in('NOTA_A.md','NOTA_B.md')],'pending_components':['REAL_APD02_CAMPAIGN_NOT_BUILT_BY_THIS_FIXTURE']};emit(a.out/'CONFIG.json',config)
    stage=a.out/'PREPARACION_NO_FINAL';assembled=run([here/'ensamblar_analisis_apd02_cas.py','--config',a.out/'CONFIG.json','--stage',stage]);emit(a.out/'ENSAMBLADO.json',assembled)
    if assembled['returncode']:raise RuntimeError(assembled['stderr'])
    restored=run([stage/'REPETIR_TODO.py','--salida',a.out/'RESULTADOS','--permitir-preparacion']);emit(a.out/'REPETIDO.json',restored)
    report=json.loads((a.out/'RESULTADOS/VERIFICACION_RECALCULOS.json').read_bytes());assert restored['returncode']==0 and len(report['cases'])==2 and report['all_selected_cases_exact']and not report['issues']
    assert(stage/'NOTA_A.md').read_bytes()==note.read_bytes()==(stage/'NOTA_B.md').read_bytes()
    spec=importlib.util.spec_from_file_location('CAS_APD02',here/'ensamblar_analisis_apd02_cas.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rejected=[]
    for name in('../escape','/absolute','C:/drive','a/./b','AUX/x','a//b'):
        try:m.relative(name)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Unsafe path accepted:'+name)
    for name in('bad.deetsnap.gz','bad.sqlite3','bad.whl'):
        f=a.out/name;f.write_bytes(b'Technical rejection fixture, not a world')
        try:m.ensure_analysis(f)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Forbidden file accepted')
    refused_seal=run([here/'sellar_probar_zip_analisis_apd02.py','--stage',stage,'--zip',a.out/'SHOULD_NOT_EXIST.zip','--extraction',a.out/'SHOULD_NOT_EXTRACT','--results',a.out/'SHOULD_NOT_RECALCULATE','--proof',a.out/'SHOULD_NOT_PROVE.json','--expected-cases','2'])
    assert refused_seal['returncode']!=0 and not(a.out/'SHOULD_NOT_EXIST.zip').exists()
    idx=json.loads((stage/'INDICE_OBJETOS_Y_ALIASES.json').read_bytes());logical=sum(len(s['members'])for s in idx['namespaces']);assert len(idx['objects'])<logical
    result={'status':'TECHNICAL_FIXTURE_VERIFIED_NOT_CAMPAIGN_CLOSURE','native_ticks':0,'actual_scientific_recalculations_rerun':0,'ZIP_generated':False,'cases_byte_identical':2,'manifest_schemas_verified':['files','members'],'unnamed_and_missing_output_normalized_only_in_global_plan':True,'duplicate_public_files_both_readable':True,'logical_namespace_files':logical,'unique_objects':len(idx['objects']),'unsafe_or_forbidden_fixture_inputs_rejected':rejected,'final_seal_without_authorization_refused':True,'refused_seal':refused_seal,'helper_hashes':{f.name:sha(f)for f in(here/'ensamblar_analisis_apd02_cas.py',here/'repetir_todo_apd02_cas.py',here/'sellar_probar_zip_analisis_apd02.py')},'scope':'Synthetic stdlib arithmetic fixtures only; external Python calculation is not a DEE skill. No real primary, source system, life or snapshot was modified.'};emit(a.out/'PRUEBA_TECNICA_CAS_N0.json',result);print(json.dumps({k:v for k,v in result.items()if k!='refused_seal'},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
