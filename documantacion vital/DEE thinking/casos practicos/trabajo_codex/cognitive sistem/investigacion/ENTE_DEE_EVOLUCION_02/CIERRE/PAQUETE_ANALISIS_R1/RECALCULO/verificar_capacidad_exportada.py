"""Technical independence check of the already-closed capacity records.
Copies exact bytes to one fresh retained temporary directory; no DEE ticks.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,shutil,subprocess,sys,tempfile

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--primarios',type=Path,required=True);p.add_argument('--codigo',type=Path,required=True);p.add_argument('--script',type=Path,required=True);p.add_argument('--referencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--prohibir-raiz',type=Path,action='append',required=True);a=p.parse_args()
    if a.worker:
        roots=[r.resolve()for r in a.prohibir_raiz];denied=[]
        def hook(event,args):
            if event in('socket.connect','socket.connect_ex','subprocess.Popen','os.system')or(event=='import'and args and str(args[0]).startswith('dee_thinking')):
                denied.append(event);raise PermissionError('No engine, process or network in archived capacity recalculation')
            if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
                path=Path(os.fsdecode(args[0])).resolve()
                if any(path==root or path.is_relative_to(root)for root in roots):denied.append(str(path));raise PermissionError('Original project root is forbidden')
        sys.addaudithook(hook);sys.argv=[str(a.script),'--primarios',str(a.primarios),'--codigo',str(a.codigo),'--salida',str(a.salida)]
        try:runpy.run_path(str(a.script),run_name='__main__')
        except SystemExit as result:
            if result.code not in(0,None):raise
        actual=digest(a.salida);expected=digest(a.referencia);data=json.loads(a.salida.read_bytes())
        if actual!=expected or denied or data['issues']:raise ValueError('Portable capacity calculation differs')
        print(json.dumps({'byte_identical':True,'sha256':actual,'denied_attempts':denied,'totals':data['totals'],'new_DEE_ticks':0},ensure_ascii=False));return
    if a.salida.exists():raise FileExistsError('Prior verification receipt protected')
    temp=Path(tempfile.mkdtemp(prefix='EO02-capacidad-exportada-'));prim=temp/'primarios';code=temp/'revisiones';prim.mkdir();code.mkdir()
    for source in a.primarios.iterdir():
        if source.is_file()and(source.name.endswith('.json')or source.name.endswith('.json.gz')):shutil.copyfile(source,prim/source.name)
    for source in a.codigo.rglob('*.py'):
        target=code/source.relative_to(a.codigo);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    script=temp/'recalcular_capacidad.py';shutil.copyfile(a.script,script);reference=temp/'referencia.json';shutil.copyfile(a.referencia,reference)
    worker=temp/'verificar_capacidad_exportada.py';shutil.copyfile(Path(__file__),worker);out=temp/'RECALCULADO.json'
    argv=[sys.executable,'-I','-B','-X','utf8',str(worker),'--worker','--primarios',str(prim),'--codigo',str(code),'--script',str(script),'--referencia',str(reference),'--salida',str(out)]
    for root in a.prohibir_raiz:argv+=['--prohibir-raiz',str(root.resolve())]
    r=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=240)
    if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    proof=json.loads(r.stdout.splitlines()[-1]);proof.update(schema='EO02.capacity.export_independence.v1',retained_extraction=str(temp),command=argv,script_sha256=digest(script),reference_sha256=digest(reference),native_reproduction=False,new_worker_executions=0)
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
