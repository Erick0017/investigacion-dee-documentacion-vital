"""Run the canonical portable PI02 documentary checks with Python stdlib only.

Usage: python -I -B -X utf8 RECALCULO/RECALCULO_TODO.py --root EXTRACTED
       --out-dir NEW_EMPTY_OUTPUT
Every verifier receives only files inside EXTRACTED and output paths. Workers
reject reads outside that evidence/stdlib and writes outside NEW_EMPTY_OUTPUT.
No motor, owner, Native reconstruction, teaching or material experience occurs.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,runpy,subprocess,sys,sysconfig,traceback

TAGS=('DEV_HAB','RES_MAIN','RES_UNPAIRED','RES_NO_TRAIN','RES_WARNING_CUT','RES_VALENCE_OMIT','RES_ACTUATOR_NULL')
def digest(data):return hashlib.sha256(data).hexdigest()
def desc(path):return {'file':str(path),'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())}
def safe(root,relative):
    p=Path(relative)
    if p.is_absolute()or'..'in p.parts or ':'in str(relative):raise ValueError('Relative packaged path required')
    target=(root/p).resolve(strict=True)
    if not target.is_relative_to(root.resolve(strict=True))or not target.is_file():raise ValueError('Input escapes evidence root')
    for parent in (target,*target.parents):
        if parent==root.parent:break
        if parent.is_symlink()or getattr(parent.lstat(),'st_file_attributes',0)&1024:raise ValueError('Linked/reparse evidence refused')
        if parent==root:break
    return target
def jobs(groups):
    result=[]
    def add(name,script,args,outputs):result.append({'name':name,'script':'RECALCULO/'+script,'args':args,'outputs':outputs})
    if'A'in groups:add('A_R01_R02A','RECALCULAR_PI02.py',['--root','@ROOT','--out-dir','@OUT/A','--strict'],['A/RECALCULO_PI02.json','A/RECALCULO_PI02_R02A.csv'])
    if'B'in groups:add('B_R02','RECALCULAR_PI02_B_R02.py',['--root','@ROOT','--out-dir','@OUT/B'],['B/RECALCULO_PI02_B_R02.json'])
    if'C'in groups:add('C_ADVERTENCIA','RECALCULAR_ADVERTENCIA_R03.py',['--evidence','@ROOT/EVIDENCIA/C_ADVERTENCIA','--code','@ROOT/CODIGO/C_ADVERTENCIA/pi02_advertencia_R03.py','--expected','@ROOT/EVIDENCIA/C_ADVERTENCIA/RESULTADO_CIENTIFICO_ADVERTENCIA_R03.json','--output','@OUT/C/RECALCULO_ADVERTENCIA_R03.json','--strict'],['C/RECALCULO_ADVERTENCIA_R03.json'])
    if'D'in groups:
        for tag in TAGS:
            home='@ROOT/EVIDENCIA/D_R04/'+tag
            add('D_'+tag,'RECALCULAR_HABITAT_R04.py',['--journal',home+'/eventos.jsonl.gz','--summary',home+'/summary.json.gz','--bank',home,'--output','@OUT/D/'+tag+'.json','--strict'],['D/'+tag+'.json'])
    if'OH'in groups:add('OH_CONTROL','RECALCULAR_OH_COMPACTO_R04.py',['--evidence','@ROOT/EVIDENCIA/D_R04/OH_CONTROL','--result','@OUT/OH/RECALCULO_OH.json'],['OH/RECALCULO_OH.json'])
    if'PRIMER_AVISO'in groups:
        main='@ROOT/EVIDENCIA/D_R04/RES_MAIN'
        for tag in('RES_UNPAIRED','RES_WARNING_CUT'):
            control='@ROOT/EVIDENCIA/D_R04/'+tag
            add('PRIMER_AVISO_'+tag,'COMPARAR_PRIMER_AVISO_R04.py',['--main-summary',main+'/summary.json.gz','--main-journal',main+'/eventos.jsonl.gz','--control-summary',control+'/summary.json.gz','--control-journal',control+'/eventos.jsonl.gz','--output','@OUT/PRIMER_AVISO/'+tag+'.json','--strict'],['PRIMER_AVISO/'+tag+'.json'])
    if'E'in groups:add('E_FINAL','RECALCULAR_FINAL_PI02.py',['--root','@ROOT','--output','@OUT/E/RECALCULO_FINAL_PI02.json'],['E/RECALCULO_FINAL_PI02.json'])
    return result

def worker(root,out,job):
    # All support code is stdlib, loaded before the guard to avoid an audit loop.
    script=safe(root,job['script']);stdlib=Path(sysconfig.get_path('stdlib')).resolve()
    runtime=Path(sys.base_prefix).resolve();reads=set();writes=set();denied=[]
    def inside(path,parent):return path==parent or path.is_relative_to(parent)
    def audit(event,args):
        if event=='import'and args and(str(args[0]).startswith('dee_thinking')or str(args[0])=='_native'):
            denied.append({'event':'import','name':str(args[0])});raise PermissionError('DEE/Native imports are forbidden')
        if event!='open'or not args:return
        value=args[0]
        if isinstance(value,int):return
        if not isinstance(value,(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(value)).resolve(strict=False);mode=args[1]if len(args)>1 else'';flags=args[2]if len(args)>2 and isinstance(args[2],int)else 0
        writing=(isinstance(mode,str)and any(c in mode for c in'wax+'))or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if writing:
            if not inside(path,out):denied.append({'event':'write','path':str(path)});raise PermissionError('Write outside explicit output folder')
            writes.add(str(path));return
        allowed_library=(inside(path,stdlib)or inside(path,runtime))and not any(part.lower()in('site-packages','dist-packages')for part in path.parts)
        if not inside(path,root)and not inside(path,out)and not allowed_library:
            denied.append({'event':'read','path':str(path)});raise PermissionError('Read outside exported evidence/stdlib')
        reads.add(str(path))
    sys.addaudithook(audit)
    args=[value.replace('@ROOT',str(root)).replace('@OUT',str(out))for value in job['args']]
    for relative in job['outputs']:(out/relative).parent.mkdir(parents=True,exist_ok=True)
    code=0;error=None
    try:
        sys.argv=[str(script),*args];runpy.run_path(str(script),run_name='__main__')
    except SystemExit as exc:
        code=0 if exc.code is None else exc.code if isinstance(exc.code,int)else 1
    except BaseException as exc:
        code=3;error=repr(exc);traceback.print_exc()
    forbidden=[name for name in sys.modules if name.startswith('dee_thinking')or name=='_native']
    if forbidden or denied:code=3
    proof={'job':job['name'],'root':str(root),'exit_code':code,'error':error,'DEE_modules_loaded':forbidden,'denied_accesses':denied,
           'evidence_reads':sorted(str(Path(p).relative_to(root))for p in reads if Path(p).is_relative_to(root)),
           'external_stdlib_reads_count':sum(not Path(p).is_relative_to(root)and not Path(p).is_relative_to(out)for p in reads),
           'writes':sorted(str(Path(p).relative_to(out))for p in writes),'new_native_ticks':0,
           'scope':'Python audit of file opens and imports for this pure-stdlib verifier. No OS process sandbox or universal noninterference claim.'}
    (out/(job['name']+'.audit.json')).write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return code

def main(args):
    root=args.root.resolve(strict=True);out=args.out_dir.resolve()
    if args._worker:return worker(root,out,json.loads(args._worker))
    if out==root or out.is_relative_to(root/'EVIDENCIA')or out.is_relative_to(root/'CODIGO')or out.is_relative_to(root/'RECALCULO'):raise ValueError('Output must not overwrite packaged evidence/code')
    if out.exists()and any(out.iterdir()):raise ValueError('Use a new empty output folder; prior verification protected')
    selected=jobs(args.groups)
    # Fail early on absent mandatory scripts, rather than report a partial PASS.
    for job in selected:safe(root,job['script'])
    out.mkdir(parents=True,exist_ok=True);reports=[]
    for job in selected:
        command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--root',str(root),'--out-dir',str(out),'--_worker',json.dumps(job,separators=(',',':'))]
        result=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        (out/(job['name']+'.stdout.txt')).write_text(result.stdout,encoding='utf-8');(out/(job['name']+'.stderr.txt')).write_text(result.stderr,encoding='utf-8')
        audit_path=out/(job['name']+'.audit.json');audit_report=json.loads(audit_path.read_text(encoding='utf-8'))if audit_path.is_file()else None
        outputs=[];reported_errors=[]
        for relative in job['outputs']:
            path=out/relative
            if path.is_file():
                outputs.append(desc(path))
                if path.suffix=='.json':
                    value=json.loads(path.read_text(encoding='utf-8-sig'))
                    for key in('inconsistencies','identity_or_structure_errors','errors'):
                        if value.get(key):reported_errors.append({'output':relative,'field':key,'value':value[key]})
            else:reported_errors.append({'missing_output':relative})
        clean=result.returncode==0 and audit_report is not None and not audit_report['denied_accesses']and not audit_report['DEE_modules_loaded']and not reported_errors
        row={'job':job['name'],'script':job['script'],'script_sha256':digest(safe(root,job['script']).read_bytes()),'arguments_relative_to_export':job['args'],'exit_code':result.returncode,'selected_documentary_check_clean':clean,'outputs':outputs,'reported_errors':reported_errors,'audit_file':None if audit_report is None else desc(audit_path)}
        reports.append(row);print(json.dumps({'job':job['name'],'exit_code':result.returncode,'clean':clean},ensure_ascii=False),flush=True)
    final={'schema':'PI02.portable.all_selected_recalculations.v2','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':args.groups,'checks':reports,
           'all_selected_documentary_checks_clean':all(row['selected_documentary_check_clean']for row in reports),'new_native_ticks':0,'DEE_imports':0,
           'scope':'A/B_R02/C/D/OH plus first-warning and E_FINAL retention/reopening documentary evidence. Not a new Native reproduction, general cognitive PASS, or full operational backup. F incorporation is static and covered by its index/global manifest, not presented as another reproduction.'}
    (out/'RECALCULO_TODO_RESULTADO.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if final['all_selected_documentary_checks_clean']else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--out-dir',type=Path,required=True);parser.add_argument('--groups',nargs='+',choices=('A','B','C','D','OH','PRIMER_AVISO','E'),default=['A','B','C','D','OH','PRIMER_AVISO','E']);parser.add_argument('--_worker',help=argparse.SUPPRESS);raise SystemExit(main(parser.parse_args()))
