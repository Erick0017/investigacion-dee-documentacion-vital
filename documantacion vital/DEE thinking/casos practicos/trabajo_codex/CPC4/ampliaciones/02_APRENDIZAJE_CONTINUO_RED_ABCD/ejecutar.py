"""Single portable entry point for CPC4 A02; no historical campaign imports."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,zipfile

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from campaign import PARENT,identity,put,sha
from supervision import owned_job

def controlled(argv,timeout,out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    with (out/'stdout.log').open('w',encoding='utf-8') as stdout,(out/'stderr.log').open('w',encoding='utf-8') as stderr:
        p=subprocess.Popen(argv,cwd=str(ROOT),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        job,info=owned_job(p)
        try:p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if job:job[0].TerminateJobObject(job[1],124)
            else:p.kill()
            p.wait(timeout=20)
        finally:
            if job:job[0].CloseHandle(job[1])
    result={'argv':argv,'timeout':timeout,'elapsed_seconds':time.monotonic()-started,'exit_code':p.returncode,'owned_job':info}
    put(out/'COMMAND.json',result);print(json.dumps(result,ensure_ascii=False));return p.returncode

def verify():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    for row in manifest['files']:
        p=(ROOT/row['path']).resolve()
        assert p.is_relative_to(ROOT) and p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
    for line in (ROOT/'HASHES.sha256').read_text(encoding='utf-8').splitlines():
        h,name=line.split('  ',1);p=(ROOT/name).resolve()
        assert p.is_relative_to(ROOT) and sha(p)==h,name
    # The inherited manifest retains its own historical root and scope.
    previous=json.loads((PARENT/'MANIFEST.json').read_text(encoding='utf-8'))
    for row in previous['files']:
        p=(PARENT/row['path']).resolve();assert p.is_relative_to(PARENT) and sha(p)==row['sha256'],row['path']
    additions=PARENT/'HASHES_AMPLIACION_02.sha256'
    if additions.exists():
        for line in additions.read_text(encoding='utf-8').splitlines():
            h,name=line.split('  ',1);target=(PARENT/name).resolve()
            assert target.is_relative_to(PARENT) and sha(target)==h,name
    print(json.dumps({'new_payload_hashes':len(manifest['files']),'historical_manifest_payload':len(previous['files']),'verified':True}))

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    sub.add_parser('identidad');sub.add_parser('verificar');sub.add_parser('estado')
    d=sub.add_parser('demostrar');d.add_argument('--eventos',type=Path);d.add_argument('--salida',type=Path,required=True);d.add_argument('--timeout',type=int,default=600)
    r=sub.add_parser('reproducir');r.add_argument('--tipo',choices=['red-v2','red-v3','regulacion','acceso-heredado'],required=True);r.add_argument('--caso',type=Path,required=True);r.add_argument('--id');r.add_argument('--salida',type=Path,required=True);r.add_argument('--timeout',type=int,default=600)
    b=sub.add_parser('confirmar-regulacion');b.add_argument('--salida-comandos',type=Path,required=True);b.add_argument('--timeout',type=int,default=900)
    a=p.parse_args()
    if a.mode=='identidad':print(json.dumps(identity(),ensure_ascii=False,default=str));return 0
    if a.mode=='verificar':verify();return 0
    if a.mode=='estado':print((ROOT/'REANUDACION.json').read_text(encoding='utf-8'));return 0
    if not 1<=a.timeout<=1800:p.error('Per-operation timeout must be1..1800seconds')
    if a.mode=='demostrar':
        args=[sys.executable,str(ROOT/'demostracion.py'),'--salida',str(a.salida.resolve())]
        if a.eventos:args+=['--eventos',str(a.eventos.resolve())]
        return controlled(args,a.timeout,a.salida.with_name(a.salida.name+'_command'))
    if a.mode=='confirmar-regulacion':return controlled([sys.executable,str(ROOT/'src/run_sustained_batch.py')],a.timeout,a.salida_comandos)
    if a.id and a.tipo!='acceso-heredado':p.error('--id selects a case only from an inherited-access multi-case config; other workers take one physical --caso JSON')
    workers={'red-v2':'red/run_roles.py','red-v3':'red/run_roles_v3.py','regulacion':'dual_sustained.py','acceso-heredado':'reproduce_temporal.py'}
    worker=ROOT/'src'/workers[a.tipo]
    if not worker.is_file():raise FileNotFoundError('Worker not available for this cut: '+str(worker))
    args=[sys.executable,str(worker),'--case',str(a.caso.resolve()),'--output',str(a.salida.resolve())]
    if a.id:args+=['--id',a.id]
    return controlled(args,a.timeout,a.salida.with_name(a.salida.name+'_command'))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');raise SystemExit(main())
