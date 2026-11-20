"""Close the existing measured cut after the immutable deadline. No simulation."""
import hashlib,json,os,shutil,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
def put(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    build=json.loads((ROOT/'BUILD_PATHS.json').read_text(encoding='utf-8-sig'));compiled=Path(build['source']);patches=[]
    # Preserve every later change before matching the delivered source to the
    # source tree that produced wheel05. Never alter a parent product.
    for p in compiled.rglob('*'):
        rel=p.relative_to(compiled)
        if not p.is_file() or any(x in {'build','__pycache__','dist'} or x.endswith('.egg-info') for x in rel.parts):continue
        dest=ROOT/'source'/rel
        if dest.exists() and sha(dest)!=sha(p):
            saved=ROOT/'evidence/UNBUILT_CLOSURE_FIXES/source'/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,saved)
            patches.append({'path':rel.as_posix(),'compiled_sha256':sha(p),'unbuilt_sha256':sha(dest)})
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    # Additional stubs not present in the compiled candidate are useful but
    # must not be mistaken for files shipped in that candidate WHL.
    wheel=ROOT/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    with zipfile.ZipFile(wheel) as z:
        package={n:z.read(n) for n in z.namelist() if n.startswith('dee_thinking/') and not n.endswith('/')}
        for name,data in package.items():
            rel=Path(name).relative_to('dee_thinking');p=ROOT/'source/python/dee_thinking'/rel
            if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(data).hexdigest(),name
        for name in ('cognition.pyi','dialogue.pyi'):
            p=ROOT/'source/python/dee_thinking'/name
            if 'dee_thinking/'+name not in package and p.exists():
                dest=ROOT/'evidence/UNBUILT_CLOSURE_FIXES/source/python/dee_thinking'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(dest))
    put(ROOT/'evidence/UNBUILT_CLOSURE_FIXES/INDEX.json',{'status':'NOT_BUILT_NOT_VALIDATED_NOT_IN_DELIVERED_WHEEL','files':patches,'cause':'deadline expired while waiting for an OS permission; no extension of budget'})
    unit=[]
    for p in sorted((ROOT/'validation/python_02').glob('test*.json')):
        x=json.loads(p.read_text());unit.append({'file':p.name,'tests':x['run'],'success':x['success'],'errors':x['errors'],'failures':x['failures'],'skipped':x['skipped']})
    cpp={}
    for name in ('ctest.xml','ctest_timeout_retry.xml'):
        p=ROOT/'validation'/name
        if p.exists():
            t=ET.parse(p).getroot();cpp[name]=[{'name':n.get('name'),'status':n.get('status'),'time':n.get('time'),'failure':[x.text for x in n.findall('failure')]} for n in t.iter('testcase')]
    originals=[]
    for parent in json.loads((ROOT/'PARENTS.json').read_text()):
        p=Path(parent['path']);value=sha(p);originals.append({'path':str(p),'expected_sha256':parent['sha256'],'actual_sha256':value,'unchanged':value==parent['sha256']})
    assert all(x['unchanged'] for x in originals)
    now=datetime.now(timezone.utc);budget=json.loads((ROOT/'BUDGET.json').read_text());elapsed=(now-datetime.fromisoformat(budget['start_utc'])).total_seconds()
    report={'status':'PARTIAL_NOT_RELEASE_VERIFIED','version':'4.0.0','kernel':27,'wheel_sha256':sha(wheel),'kernel_sha256':sha(ROOT/'source/src/kernel_v27.cpp'),'block_I':{'new_native_wheel_built':True,'installed_noneditable':True,'cpp_tests':cpp,'python_test_modules':unit,'python_tests_completed':sum(x['tests'] for x in unit),'pending_python_modules':['test_organizational_api.py','test_mbp4_regressions.py'],'reference_comparisons':['validation/cognitive_parity_01/COMPARISON.json','validation/informative_parity_01/COMPARISON_REPORT.json'],'backend_passive_cross_language':'validation/cognitive_technical_01/TECHNICAL_CHECKS.json','external_cpp_consumer_exit':0,'new_hotfixes_not_built':'evidence/UNBUILT_CLOSURE_FIXES/INDEX.json'},'block_II':{'status':'NO_EJECUTADO_POR_PRESUPUESTO','new_trajectories':0,'qualification_seal_created':False,'reason':'Absolute deadline expired during permission wait; no late experiment or reset of budget'},'final_clean_extraction_install':{'status':'NOT_EXECUTED','reason':'budget expired; only container/byte verification performed at closure'},'originals':originals,'budget':budget,'elapsed_including_wait_seconds':elapsed,'overrun_reason':'OS permission request returned after the absolute deadline; closure only after resumption','operational_errors':['VS PATH import corrected; CXX/SDK tools pinned','stale intermediate C++ source sync caused unresolved fork symbols; synchronized build passed','initial Python import exported missing SpanishParser; corrected','two C++180s timeouts; same tests passed unchanged with900s limit','Python240s supervisor termination denied; natural child completion preserved; orchestration stopped before two remaining modules'],'automatic_scientific_verdict':False}
    put(ROOT/'VALIDATION_REPORT.json',report)
    put(ROOT/'BUILD_PROVENANCE.json',{'status':'COMPILED_CANDIDATE_NOT_RELEASE_VERIFIED','build_wheel':json.loads((ROOT/'BUILD_wheel.json').read_text(encoding='utf-8-sig')),'build_cpp':json.loads((ROOT/'BUILD_cpp.json').read_text(encoding='utf-8-sig')),'consumer':json.loads((ROOT/'BUILD_consumer.json').read_text(encoding='utf-8-sig')),'build_source_matches_delivered_source':True,'wheel_source_python_bytes_equal':True,'wheel_sha256':sha(wheel),'new_native_module_compiled':True,'dependencies':{'CPython':'3.13.11 x64','pybind11':'3.1.0','setuptools':'81.0.0','wheel':'0.48.0','build':'1.5.0'},'pending_unbuilt_fixes':patches,'originals':originals})
    contract=json.loads((ROOT/'PRODUCT_CONTRACT.json').read_text());contract['release_status']='PARTIAL_NOT_RELEASE_VERIFIED';contract['validation_report']='VALIDATION_REPORT.json';contract['block_II_executed']=False;put(ROOT/'PRODUCT_CONTRACT.json',contract)
    for name in ('build40.ps1','supervise40.py','prepare40.py','bootstrap40.py','read_directed40.py','close_partial40.py'):
        p=ROOT/name
        if p.exists():shutil.copy2(p,ROOT/'tools'/name)
    if (ROOT/'jobs').exists():shutil.copytree(ROOT/'jobs',ROOT/'validation/jobs',dirs_exist_ok=True)
    put(ROOT/'results/CLOSURE.json',{'status':report['status'],'new_scientific_trajectories':0,'technical_tests_completed':report['block_I']['python_tests_completed'],'elapsed_including_wait_seconds':elapsed})
    put(ROOT/'CLOSED.json',{'utc':now.isoformat(),'status':'PARTIAL_BUDGET_EXPIRED','no_new_experiments':True})
    print(json.dumps({'status':report['status'],'elapsed_seconds':elapsed,'wheel':report['wheel_sha256'],'python_tests':report['block_I']['python_tests_completed'],'unbuilt_changed_files':len(patches)},indent=2))
if __name__=='__main__':main()
