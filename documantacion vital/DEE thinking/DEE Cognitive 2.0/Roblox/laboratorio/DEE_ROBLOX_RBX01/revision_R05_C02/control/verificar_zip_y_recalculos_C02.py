"""Final analysis ZIP QA: literal clean extraction + three README passive commands.

No DEE/SQLite/model/MCP/HTTP. Run only after Root builds the one final ZIP.
The child audit hook restricts all analysis file opens to the clean extraction
or read-only Python runtime, and forbids Native/network/process imports/effects.
"""
from pathlib import Path, PurePosixPath
import argparse, csv, hashlib, io, json, os, shlex, subprocess, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 15000000
TARGETS = ('RECALCULO_FUNCIONES_Y_MUNDO_C02.py', 'RECALCULO_COMPARATIVA_C02_R02.py',
           'RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R04.py')

def need(ok, message):
    if not ok: raise ValueError(message)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for raw in iter(lambda:f.read(1048576),b''):h.update(raw)
    return h.hexdigest()

def name_safe(name):
    need(isinstance(name,str)and name and ':'not in name and '\\'not in name,'Portable member path required')
    p=PurePosixPath(name)
    need(not p.is_absolute()and all(x not in ('','.','..')for x in p.parts),'Unsafe archive member')
    return p

def no_link(path):
    for part in (path,*path.parents):
        need(not part.is_symlink()and not(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&1024),'No symlink/reparse QA paths')

def fresh(path):
    path=path.absolute();no_link(path)
    need(path.resolve().is_relative_to(ROOT),'QA paths remain inside this C02 campaign')
    need(not path.exists(),'Fresh QA output required')
    return path

def readable(name, raw):
    text=raw.decode('utf-8-sig')
    suffix=PurePosixPath(name).suffix.lower()
    if suffix=='.json':json.loads(text)
    elif suffix=='.jsonl':
        for line in text.splitlines():
            if line.strip():json.loads(line)
    elif suffix=='.csv':list(csv.reader(io.StringIO(text,newline='')))
    return text

# This wrapper is supplied literally to a clean stdlib Python child; it imports
# no project module until the restrictive hook is installed.
CHILD = r'''
import builtins,json,os,pathlib,runpy,sys,sysconfig
cfg=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf8'))
root=pathlib.Path(cfg['root']).resolve()
runtime=[pathlib.Path(sys.base_prefix).resolve(),pathlib.Path(sys.executable).resolve().parent]
opened=[];denied=[];effects=[];selftest=False
def inside(path,base):
    try:return path.is_relative_to(base)
    except (ValueError,AttributeError):return False
def deny(event,path):
    row={'event':event,'path':str(path)}
    if not selftest:denied.append(row)
    raise RuntimeError('C02_AUDIT_BLOCKED_'+event)
def hook(event,args):
    if event=='import':
        name=str(args[0]).split('.')[0]
        if name in ('dee_thinking','sqlite3','socket','_socket','ctypes','_ctypes','subprocess','http','urllib','requests'):
            effects.append({'event':event,'name':name});deny(event,name)
    if event.startswith(('socket.','subprocess.'))or event in ('os.system','os.exec','os.posix_spawn','ctypes.dlopen'):
        effects.append({'event':event});deny(event,'external effect')
    if event!='open':return
    path=args[0]
    if isinstance(path,int):return
    if not isinstance(path,(str,bytes,os.PathLike)):deny(event,repr(path))
    path=pathlib.Path(os.fsdecode(path)).absolute().resolve()
    mode=args[1]if len(args)>1 else None
    flags=args[2]if len(args)>2 and isinstance(args[2],int)else 0
    write=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))or(isinstance(mode,str)and any(c in mode for c in 'wax+'))
    row={'path':str(path),'mode':str(mode),'write':write}
    if not selftest:opened.append(row)
    if inside(path,root):return
    # Runtime files are read-only; site-packages is not part of this allowance.
    if not write and not any(x.lower()in('site-packages','dist-packages')for x in path.parts)and any(inside(path,b)for b in runtime):return
    deny(event,path)
sys.addaudithook(hook)
selftest=True
try:
    try:open(root.parent/'C02_FORBIDDEN_ORIGINAL_PROBE.txt','rb')
    except RuntimeError:blocked=True
    else:blocked=False
finally:selftest=False
code=0;error=None
try:
    if not blocked:raise RuntimeError('Audit self-test did not block external file open')
    os.chdir(root);sys.argv=cfg['argv'];runpy.run_path(str(root/cfg['argv'][0]),run_name='__main__')
except SystemExit as e:
    code=e.code if isinstance(e.code,int)else(0 if e.code is None else 1)
except BaseException as e:
    code=1;error=type(e).__name__+': '+str(e)
finally:
    report={'script':cfg['argv'][0],'exit_code':code,'error':error,'audit_self_test_blocked':blocked,
            'opened':opened,'denied_analysis_opens':denied,'blocked_effects':effects,
            'all_analysis_opens_inside_extraction_or_read_only_stdlib':not denied,
            'Native_imports':0,'Native_ticks':0,'MCP_HTTP_model_calls':0}
    pathlib.Path(cfg['audit']).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sys.exit(code)
'''

def commands(readme):
    selected={}
    for line in readme.splitlines():
        if not line.startswith('python '):continue
        argv=shlex.split(line)
        scripts=[(i,x)for i,x in enumerate(argv)if PurePosixPath(x).name in TARGETS]
        if not scripts:continue
        need(len(scripts)==1,'One passive script per README command')
        i,script=scripts[0]
        need(PurePosixPath(script).name not in selected,'Duplicate README passive command')
        need(argv[1:i]==['-I','-B'],'README command requires isolated no-bytecode Python')
        tail=argv[i:]
        need('--output'in tail and tail.index('--output')+1<len(tail),'Fresh passive output required')
        selected[PurePosixPath(script).name]=dict(literal=line,argv=tail)
    need(set(selected)==set(TARGETS),'All three exact passive commands must be present in README')
    return [selected[x]for x in TARGETS]

def verify(a):
    archive=a.zip.absolute();no_link(archive)
    need(archive.is_file()and archive.stat().st_size<=LIMIT,'Final ZIP exists and is <=15000000 bytes')
    extraction=a.extraction.absolute();no_link(extraction)
    need(extraction.resolve().is_relative_to(ROOT),'Extraction remains inside C02')
    output=fresh(a.output);need(output.parent.is_dir(),'Output parent must exist')
    with zipfile.ZipFile(archive)as z:
        info=z.infolist();need(len(info)<=503 and all(x.compress_type==zipfile.ZIP_DEFLATED for x in info),'Standard bounded Deflate ZIP')
        names=z.namelist();need(len(names)==len(set(x.casefold()for x in names)),'No duplicate ZIP members')
        for name in names:name_safe(name)
        need(z.testzip()is None,'ZIP CRC failure')
        manifest=json.loads(z.read('CONTROL/MANIFIESTO_SHA256.json').decode('utf8'))
        rows=manifest['members'];expected={r['archive']for r in rows}|{'CONTROL/MANIFIESTO_SHA256.json'}
        need(set(names)==expected,'ZIP member set agrees with manifest')
        need(sum(x.file_size for x in info)<=81000000 and all(x.file_size<=5100000 for x in info),'Bounded content size')
        byname={r['archive']:r for r in rows}
        if extraction.exists():
            need(extraction.is_dir(),'Existing extraction must be directory')
            actual=set()
            for path in extraction.rglob('*'):
                no_link(path)
                if path.is_file():actual.add(path.relative_to(extraction).as_posix())
            need(actual==expected,'Reused extraction must contain exactly the clean ZIP member set')
        else:
            extraction.mkdir()
            for name in names:
                dest=extraction.joinpath(*name_safe(name).parts);dest.parent.mkdir(parents=True,exist_ok=True)
                with dest.open('xb')as f:f.write(z.read(name))
        for name in names:
            raw=z.read(name);path=extraction.joinpath(*name_safe(name).parts)
            need(path.read_bytes()==raw,'Literal extraction differs from ZIP')
            if name in byname:
                row=byname[name]
                need(len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],'Member SHA/size mismatch')
            readable(name,raw)
    readmes=[r['archive']for r in rows if r.get('role')=='readme']
    need(len(readmes)==1,'One unambiguous README')
    readme=extraction/readmes[0]
    planned=commands(readme.read_text(encoding='utf-8-sig'))
    # Each analysis output is a new directory inside the extraction, exactly as
    # the delivered README requests. Refuse absolute/outside/previous outputs.
    for item in planned:
        argv=item['argv'];script=extraction.joinpath(*name_safe(argv[0]).parts)
        need(script.is_file(),'Delivered passive script absent')
        target=extraction/argv[argv.index('--output')+1]
        need(not target.exists()and target.resolve().is_relative_to(extraction),'README analysis output must be fresh inside extraction')
    output.mkdir();results=[]
    for index,item in enumerate(planned,1):
        cfg=output/(str(index)+'_CONFIG.json');audit=output/(str(index)+'_AUDIT.json')
        cfg.write_text(json.dumps(dict(root=str(extraction),argv=item['argv'],audit=str(extraction/('_QA_AUDIT_'+str(index)+'.json')))),encoding='utf8')
        completed=subprocess.run([sys.executable,'-I','-B','-c',CHILD,str(cfg)],cwd=extraction,
                                 capture_output=True,text=True,encoding='utf8',errors='replace',timeout=300)
        (output/(str(index)+'_STDOUT.txt')).write_text(completed.stdout,encoding='utf8')
        (output/(str(index)+'_STDERR.txt')).write_text(completed.stderr,encoding='utf8')
        local_audit=extraction/('_QA_AUDIT_'+str(index)+'.json')
        need(local_audit.is_file(),'Analysis audit report missing')
        raw=local_audit.read_bytes();audit.write_bytes(raw);proof=json.loads(raw)
        result=dict(command=item['literal'],returncode=completed.returncode,audit=str(audit),
            audit_sha256=sha(audit),opened_count=len(proof['opened']),denied_count=len(proof['denied_analysis_opens']),
            audit_self_test_blocked=proof['audit_self_test_blocked'])
        results.append(result)
        need(completed.returncode==0 and proof['exit_code']==0 and not proof['denied_analysis_opens']and not proof['blocked_effects'],'Passive recalculation failed or tried external access: '+item['argv'][0])
    for row in rows:
        need(sha(extraction/row['archive'])==row['sha256'],'Delivered member changed during QA')
    report=dict(schema='DEE.RBX01.C02.final_zip_passive_QA.R01',zip=str(archive),bytes=archive.stat().st_size,
        zip_sha256=sha(archive),members=len(names),manifest_sha256=sha(extraction/'CONTROL/MANIFIESTO_SHA256.json'),
        extraction=str(extraction),literal_clean_extraction_verified=True,readme=str(readme),readme_sha256=sha(readme),
        recalculations=results,originals_outside_extraction_blocked=True,delivered_member_hashes_unchanged=True,
        Native_imports=0,Native_ticks=0,model_calls=0,MCP_calls=0,HTTP_calls=0,SQLite_connections=0,
        scope='CRC/SHA/text/member extraction plus exact README passive commands; not Native reproduction or a new scientific trial.')
    report_path=output/'VERIFICACION_FINAL_ZIP_C02.json'
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return dict(report=str(report_path),report_sha256=sha(report_path),zip_bytes=report['bytes'],zip_sha256=report['zip_sha256'],recalculations=len(results),status='VERIFIED')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip',type=Path,required=True);p.add_argument('--extraction',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(verify(p.parse_args()),ensure_ascii=False,indent=2))
