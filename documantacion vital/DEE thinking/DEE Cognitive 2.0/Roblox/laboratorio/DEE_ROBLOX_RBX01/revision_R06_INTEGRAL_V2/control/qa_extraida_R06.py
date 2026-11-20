"""Recalculate explicit manifest recipes inside a NEW extracted R06 ZIP.

Only stdlib children, no Native/Studio/model/database. A child audit hook refuses
file reads outside the extraction and the selected Python runtime, plus network,
subprocesses and Native imports. Provenance strings are not opened as filenames.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, runpy, subprocess, sys, sysconfig
from pathlib import Path, PurePosixPath

def js(value):return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def digest(raw):return hashlib.sha256(raw).hexdigest()

def child(root,script,args,audit_path):
    root=Path(root).resolve(strict=True)
    script=Path(script).resolve(strict=True)
    runtime={Path(sys.base_prefix).resolve(),Path(sys.prefix).resolve()}
    for key in ('stdlib','platstdlib'):
        p=sysconfig.get_path(key)
        if p:runtime.add(Path(p).resolve())
    counts={'allowed_open':0,'denied':0,'Native_network_process_calls':0}; observed=[]
    blocked_imports=('dee_thinking','numpy','sqlite3','ctypes','socket','requests','urllib','http','ollama')
    def inside(path,roots):return any(path==r or r in path.parents for r in roots)
    def hook(event,values):
        if event=='import' and isinstance(values[0],str) and any(values[0]==x or values[0].startswith(x+'.')for x in blocked_imports):
            counts['denied']+=1;raise PermissionError('QA_IMPORT_REFUSED: '+values[0])
        if event.startswith(('socket.','subprocess.','ctypes.')) or event in ('os.system','os.spawn','os.exec','os.posix_spawn','os.fork','os.forkpty'):
            counts['denied']+=1;raise PermissionError('QA_EFFECT_REFUSED: '+event)
        if event in ('open','os.listdir','os.scandir'):
            name=values[0]
            if isinstance(name,int):return
            if not isinstance(name,(str,bytes,os.PathLike)):
                counts['denied']+=1;raise PermissionError('QA_UNKNOWN_PATH_TYPE')
            path=Path(os.fsdecode(name)).resolve()
            writing=event=='open' and ((isinstance(values[1],str)and any(c in values[1]for c in 'wax+'))or(isinstance(values[2],int)and values[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            allowed=inside(path,{root}) or (not writing and inside(path,runtime))
            if not allowed:
                counts['denied']+=1;observed.append({'event':event,'path':str(path),'blocked':True})
                raise PermissionError('QA_ORIGINAL_OR_EXTERNAL_PATH_REFUSED')
            counts['allowed_open']+=1
            if len(observed)<150:observed.append({'event':event,'path':str(path),'writing':bool(writing),'scope':'extraction'if inside(path,{root})else'PythonRuntime'})
    if not inside(script,{root}):raise ValueError('RECALC_SCRIPT_MUST_BE_EXTRACTED')
    sys.addaudithook(hook)
    try:
        sys.argv=[str(script),*args]
        runpy.run_path(str(script),run_name='__main__')
    finally:
        Path(audit_path).write_text(js({'schema':'DEE.INTEGRAL.V2.passive_recalc_audit.R01',
            'scope':'File data opens/listing after hook installation; metadata and already-loaded Python startup are not a whole-system audit.',
            'root':str(root),'script':str(script),'counts':counts,'path_samples':observed}),encoding='utf-8')

def run(root,output):
    root=Path(root).resolve(strict=True);output=Path(output).absolute()
    if output.exists() or output.parent!=root:raise ValueError('FRESH_QA_OUTPUT_DIRECTLY_IN_EXTRACTION_REQUIRED')
    manifest_path=root/'CONTROL/MANIFIESTO_SHA256.json'
    raw=manifest_path.read_bytes();manifest=json.loads(raw.decode('utf-8'))
    if manifest.get('schema')!='DEE.INTEGRAL.V2.content_manifest.R01':raise ValueError('MANIFEST_SCHEMA')
    by_archive={x['archive']:x for x in manifest['files']}
    if len(by_archive)!=len(manifest['files']):raise ValueError('DUPLICATE_MEMBERS')
    for name,row in by_archive.items():
        p=PurePosixPath(name)
        if p.is_absolute()or '..'in p.parts or '\\'in name or ':'in name:raise ValueError('UNSAFE_MANIFEST_PATH')
        file=root.joinpath(*p.parts)
        if file.is_symlink()or not root in file.resolve().parents:raise ValueError('LINK_OR_EXTERNAL_MEMBER')
        value=file.read_bytes()
        if len(value)!=row['bytes']or digest(value)!=row['sha256']:raise ValueError('EXTRACTED_MEMBER_HASH_MISMATCH: '+name)
    recipes=manifest.get('recalculations',[])
    if not recipes:raise ValueError('NO_RECALCULATION_RECIPES_CONFIGURED; do not claim portable recalculation')
    if len(recipes)>8:raise ValueError('FINITE_RECALCULATION_BUDGET')
    output.mkdir();rows=[]
    for index,recipe in enumerate(recipes):
        name=recipe['script'];p=PurePosixPath(name)
        known_recalc=p.name.startswith('RECALCULO_')or name in {
            'analisis/RECURSOS_RECALCULO_R06.py','analisis/LATENCIAS_Q1_Q2_VIDEO_R06_R01.py',
            'analisis/CONSOLIDAR_COMPARACION_R06_R01.py'}
        if name not in by_archive or p.parts[0]!='analisis' or not known_recalc or p.suffix!='.py':
            raise ValueError('ONLY_SELECTED_PASSIVE_RECALCULATION_SCRIPT_ALLOWED')
        result_dir=output/f'{index+1:02d}_resultados'
        args=[]
        for arg in recipe['args']:
            if not isinstance(arg,str)or '\x00'in arg:raise ValueError('STRING_CLI_ARGUMENT_REQUIRED')
            args.append(arg.replace('{root}',str(root)).replace('{out}',str(result_dir)))
        audit_path=output/f'{index+1:02d}_audit.json'
        command=[sys.executable,'-I','-B','-S',str(Path(__file__).resolve()),'_worker',str(root),str(root.joinpath(*p.parts)),str(audit_path),*args]
        timeout=recipe.get('timeout_seconds',120)
        if not isinstance(timeout,int)or not 1<=timeout<=180:raise ValueError('FINITE_TIMEOUT_REQUIRED')
        proc=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        (output/f'{index+1:02d}_stdout.txt').write_text(proc.stdout,encoding='utf-8')
        (output/f'{index+1:02d}_stderr.txt').write_text(proc.stderr,encoding='utf-8')
        audit=json.loads(audit_path.read_text(encoding='utf-8'))if audit_path.exists()else None
        expected=recipe.get('expected_outputs',[])
        produced=[]
        for rel in expected:
            q=PurePosixPath(rel)
            if q.is_absolute()or '..'in q.parts:raise ValueError('UNSAFE_EXPECTED_OUTPUT')
            actual=result_dir.joinpath(*q.parts)
            produced.append({'path':str(actual.relative_to(root)),'exists':actual.is_file(),
                             'sha256':digest(actual.read_bytes())if actual.is_file()else None})
        okay=proc.returncode==0 and audit is not None and audit['counts']['denied']==0 and all(x['exists']for x in produced)
        rows.append({'id':recipe['id'],'script':name,'args':args,'returncode':proc.returncode,'audit':str(audit_path.relative_to(root)),
                     'outputs':produced,'passive_execution_finished':okay})
        if not okay:break
    report={'schema':'DEE.INTEGRAL.V2.extracted_passive_QA.R01','manifest_sha256':digest(raw),
            'all_content_hashes_before_recalc':True,'all_configured_recalculations_finished':len(rows)==len(recipes)and all(x['passive_execution_finished']for x in rows),
            'Native_Studio_model_calls':0,'scientific_approval':False,'recipes':rows}
    # Recheck only manifest content; QA outputs are new derived files, never replace delivered primaries.
    for name,row in by_archive.items():
        if digest(root.joinpath(*PurePosixPath(name).parts).read_bytes())!=row['sha256']:raise ValueError('CONTENT_CHANGED_DURING_RECALC')
    (output/'RESULTADO_QA.json').write_text(js(report),encoding='utf-8')
    if not report['all_configured_recalculations_finished']:raise ValueError('PASSIVE_RECALCULATION_FAILED; inspect new QA outputs')
    return report

def cli():
    if len(sys.argv)>1 and sys.argv[1]=='_worker':
        child(sys.argv[2],sys.argv[3],sys.argv[5:],sys.argv[4]);return
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(js(run(a.root,a.output)))
if __name__=='__main__':cli()
