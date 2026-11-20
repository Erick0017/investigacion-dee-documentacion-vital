"""Ejecuta un protocolo archivado con acceso a archivos limitado al paquete.

No decide respuestas. Las referencias se verifican después de la ejecución.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,tempfile,time

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--script',required=True);ap.add_argument('--out',required=True);ap.add_argument('args',nargs=argparse.REMAINDER);n=ap.parse_args()
    package=Path(__file__).resolve().parents[1];output=Path(n.out).resolve();output.mkdir(parents=True,exist_ok=True)
    script=(package/n.script).resolve(strict=True)
    if not script.is_relative_to(package):raise ValueError('El protocolo debe pertenecer al paquete')
    temp=Path(tempfile.mkdtemp(prefix='DEE_COMP_'))
    os.environ.update(TEMP=str(temp),TMP=str(temp),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    sys.dont_write_bytecode=True
    common=package/'codigo_comun/cognitive';third=package/'codigo_comun/terceros'
    sys.path[:0]=[str(common),str(third),str(script.parent)]
    allowed=[package,output,temp,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()]
    reads=set();blocked=[]
    def audit(event,args):
        if event!='open' or not args or isinstance(args[0],int):return
        value=args[0]
        if not isinstance(value,(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(value)).resolve()
        if str(path).lower() in ['nul','con','\\\\.\\nul']:return
        mode=args[1] if len(args)>1 else None
        writing=isinstance(mode,str) and any(x in mode for x in 'wax+')
        flags=args[2] if len(args)>2 and isinstance(args[2],int) else 0
        writing=writing or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        valid=any(path.is_relative_to(p) for p in ([output,temp] if writing else allowed))
        if not valid:
            blocked.append(dict(event=event,path=str(path),write=writing));raise PermissionError('Acceso fuera de la copia aislada: '+str(path))
        if not writing:reads.add(str(path))
    sys.addaudithook(audit)
    sys.argv=[str(script)]+(n.args[1:] if n.args[:1]==['--'] else n.args)
    started=time.monotonic();error=None
    try:runpy.run_path(str(script),run_name='__main__')
    except BaseException as exc:
        if not isinstance(exc,SystemExit) or exc.code not in (0,None):error=repr(exc)
        raise
    finally:
        (output/'AISLAMIENTO.json').write_text(json.dumps(dict(schema='DEE.comp.pending_read_audit.v1',script=n.script,python=sys.executable,package=str(package),output=str(output),native_temp=str(temp),allowed_roots=list(map(str,allowed)),read_files=sorted(reads),blocked=blocked,wall_seconds=time.monotonic()-started,error=error),ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
