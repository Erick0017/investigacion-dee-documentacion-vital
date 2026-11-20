from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parent
SPECS={
 'M039':[(15,'NEW_RUNNERS/run_expansion_holdouts.py','NEW_RAW_TELEMETRY/EXPANSION_FRESH_CONFIRMATION.json')],
 'M040':[(16,'RUNNERS_NEW/run_operator_holdouts.py','FINAL_HOLDOUTS/OPERATOR_HOLDOUT_RESULTS.json'),(16,'RUNNERS_NEW/run_capability_holdout.py','FINAL_HOLDOUTS/CAPABILITY_HOLDOUT_RESULTS.json'),(16,'RUNNERS_NEW/run_probability_holdout.py','FINAL_HOLDOUTS/PROBABILITY_HOLDOUT_RESULTS.json'),(16,'RUNNERS_NEW/run_quantum_scale_holdout.py','FINAL_HOLDOUTS/QUANTUM_SCALE_HOLDOUT_RESULTS.json')],
 'M041':[(17,'EXTENSION/RUNNERS/run_e03_policy_repair_holdout.py','EXTENSION/HOLDOUT/C17E03_POLICY_REPAIR_HOLDOUT.json'),(17,'EXTENSION/RUNNERS/run_e05_r0_factor_holdout.py','EXTENSION/HOLDOUT/C17E05_R0_FACTOR_HOLDOUT.json')]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def scientific(v):
    if isinstance(v,dict):return {k:scientific(x) for k,x in v.items() if k not in ('runtime','environment','completed_utc','executed_utc','created_utc','content_sha256')}
    if isinstance(v,list):return [scientific(x) for x in v]
    return v
def execute(identifier,mat,out,package):
    from ejecutar_cpc9 import compare
    work=out/'experimento';assert not work.exists();work.mkdir()
    shutil.copytree(mat/'cores',work/'cores',ignore=shutil.ignore_patterns('CHECKPOINTS','__pycache__','*.pyc'))
    tests=work/'cores';wheel=package/'motor/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl';assert sha(wheel)=='69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'
    shutil.copyfile(wheel,tests/wheel.name)
    extracted=tests/'DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK/ANALYSIS/binary_api/wheel_extracted'
    with zipfile.ZipFile(wheel) as z:
        for n in z.namelist():
            if n.startswith('dee_universe_v27/') and not n.endswith('/'):
                assert '..' not in Path(n).parts;p=extracted/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
    rows=[]
    for number,entry,result in SPECS[identifier]:
        case=out/Path(entry).stem;case.mkdir();script=tests/('CORE'+str(number))/entry
        command=[sys.executable,'-I','-B',ROOT/'replay_native.py','--script',script,'--output',case,'--allow-root',work,'--module-path',package/'codigo_comun/terceros','--']
        with (case/'stdout.log').open('w',encoding='utf8') as so,(case/'stderr.log').open('w',encoding='utf8') as se:
            child=subprocess.Popen(list(map(str,command)),cwd=work,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:code=child.wait(timeout=2400)
            except subprocess.TimeoutExpired:child.kill();child.wait();code=-1
        actual_path=tests/('CORE'+str(number))/result;ref=mat/'cores'/('CORE'+str(number))/result
        actual=json.loads(actual_path.read_bytes()) if actual_path.is_file() else {};expected=json.loads(ref.read_bytes());diff=compare(scientific(actual),scientific(expected))
        identity=actual.get('runtime',actual.get('environment',{})).get('observed_hashes')==expected.get('runtime',expected.get('environment',{})).get('observed_hashes')
        access=case/'ACCESOS_DEL_PROCESO.json';audit=json.loads(access.read_bytes()) if access.is_file() else {'denied_files':['missing audit report']}
        # A historical failing canary is preserved as failing; the reproduction
        # succeeds only when its entire scientific record matches exactly.
        acceptable_exit=code==0 or code==2 and (expected.get('verdict')=='FAIL' or expected.get('passed') is False)
        row={'entry':entry,'status':'PASS' if acceptable_exit and not diff and identity and not audit['denied_files'] else 'FAIL','exit_code':code,'scientific_difference_count':len(diff),'differences':diff[:100],'identity_hashes_equal':identity,'blocked_reads':audit['denied_files'],'reference_sha256':sha(ref),'actual_sha256':sha(actual_path) if actual_path.exists() else None,'command':list(map(str,command)),'historical_verdict':expected.get('verdict',expected.get('passed',expected.get('summary',{}).get('overall_pass')))}
        rows.append(row);put(out/'RESULTADO.json',{'mechanism':identifier,'status':'RUNNING','cases':rows})
    return {'mechanism':identifier,'mode':'NATIVE_LEGACY_REPRODUCTION','status':'PASS' if rows and all(x['status']=='PASS' for x in rows) else 'FAIL','cases':rows,'scope':'Original frozen holdouts, challenges, canaries and complete physical digests on isolated copies; no 4.5 port and no historical archive required at runtime. A matching historical negative remains negative.'}
