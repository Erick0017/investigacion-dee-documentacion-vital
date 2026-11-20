"""Relocate analysis and recalculate under an explicit read/import fence.

No ZIP and no Native. The original package is copied, not changed. Each
archived calculator can read only the relocated package, its new outputs,
the interpreter/stdlib or temporary files. Historical provenance names are
not allowed roots. The fence is testing instrument, not cognitive policy.
"""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path

CHILD=r'''
import json,os,runpy,sys,tempfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();script=Path(sys.argv[3]).resolve()
args=sys.argv[4:];reads=[root,out,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),Path(tempfile.gettempdir()).resolve()]
writes=[out,Path(tempfile.gettempdir()).resolve()]
def permitted(path,roots):
    if isinstance(path,int):return True
    try:p=Path(os.fsdecode(path)).resolve()
    except(TypeError,ValueError):return False
    return any(p.is_relative_to(base)for base in roots)
def audit(event,args):
    if event=='open':
        path,mode,flags=args
        write=(isinstance(mode,str)and any(mark in mode for mark in('w','a','x','+')))or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if not permitted(path,writes if write else reads):raise PermissionError('Archived evidence fence rejected '+str(path))
    elif event=='import'and isinstance(args[0],str):
        if args[0].split('.')[0].lower()in('dee','dee_thinking','dee_universe','dee_v27','kernel_v27'):raise PermissionError('DEE import forbidden in archived recalculation')
    elif event in('socket.connect','subprocess.Popen'):raise PermissionError('Network/new process forbidden inside archived calculator')
sys.addaudithook(audit);sys.argv=[str(script),*args];runpy.run_path(str(script),run_name='__main__')
'''

DRIVER=r'''
import json,runpy,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();child=sys.argv[3]
original=subprocess.run;commands=[]
def fenced(command,**kwargs):
    if not isinstance(command,list)or command[:3]!=[sys.executable,'-I','-B']:raise ValueError('Unexpected calculator command')
    commands.append(command)
    return original([sys.executable,'-I','-B','-c',child,str(root),str(out),*command[3:]],**kwargs)
subprocess.run=fenced
sys.argv=[str(root/'RECALCULO/recalcular_todo_apd03.py'),'--root',str(root),'--out',str(out)]
runpy.run_path(sys.argv[0],run_name='__main__')
with(out/'FRONTERA_LECTURAS.json').open('x',encoding='utf8')as stream:
    json.dump({'fenced_actual_calculator_processes':len(commands),'original_paths_allowed':False,
        'new_native_ticks':0,'scope':'Python open/import/process audit instrument; not OS sandbox or Native reproduction.'},stream,sort_keys=True,indent=2);stream.write('\n')
'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    source=args.source.resolve();work=args.out.resolve()
    if work.exists()or work.is_relative_to(source):raise ValueError('Use a new independent proof directory')
    package=work/'package';proof=work/'proof';work.mkdir(parents=True)
    before={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()}
    shutil.copytree(source,package)
    if before!={p.relative_to(package).as_posix():sha(p)for p in package.rglob('*')if p.is_file()}:raise ValueError('Relocation changed package')
    command=[sys.executable,'-I','-B','-c',DRIVER,str(package),str(proof),CHILD]
    result=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=600)
    unchanged=before=={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()}
    value={'source':str(source),'relocated':str(package),'original_members_unchanged':unchanged,
        'files':len(before),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'new_native_ticks':0,'ZIP_created':False,'source_modified':False}
    with(work/'RESULTADO_PORTABLE.json').open('x',encoding='utf8')as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    if result.returncode or not unchanged:raise ValueError('Portable archived read-fence proof failed; preserved diagnostic '+str(work))
    print(json.dumps({'portable':str(work),'files':len(before),'all_exact_and_recalculated':True,'fenced_calculators':15,'ZIP_created':False}))


if __name__=='__main__':main()
