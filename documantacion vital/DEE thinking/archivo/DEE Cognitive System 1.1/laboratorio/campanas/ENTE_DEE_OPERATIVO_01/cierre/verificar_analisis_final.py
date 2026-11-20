"""Verifica el recálculo desde este ZIP extraído, sin leer la instalación original."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys
def main():
    p=argparse.ArgumentParser();p.add_argument('--prohibir-raiz',action='append',required=True,type=Path);a=p.parse_args()
    base=Path(__file__).resolve().parent.parent
    forbidden=[q.resolve()for q in a.prohibir_raiz]
    def audit(event,args):
        if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve()
            if any(path==root or path.is_relative_to(root)for root in forbidden):raise PermissionError('Original installation access forbidden: '+str(path))
        if event in('socket.connect','socket.connect_ex','subprocess.Popen','os.system'):raise PermissionError('Archived calculation: no network or decision subprocess')
    sys.addaudithook(audit)
    script=base/'RECALCULO/recalcular.py';out=base/'RECALCULADO_DESDE_ZIP'
    sys.argv=[str(script),'--primarios',str(base/'EVIDENCIA_CAUSAL'),'--codigos',str(base/'EVIDENCIA_CAUSAL/codigo_ejecutado'),'--salida',str(out)]
    try:runpy.run_path(str(script),run_name='__main__')
    except SystemExit as e:
        if e.code not in(None,0):raise
    result=(out/'RECALCULO_RESULTADOS.json').read_bytes();reference=(base/'RECALCULO/REFERENCIA_RESULTADOS.json').read_bytes()
    report={'same_computer_new_path_fresh_process':True,'original_roots_forbidden':[str(q)for q in forbidden],'native_ticks':0,'byte_identical_to_closed_reference':result==reference,'result_sha256':hashlib.sha256(result).hexdigest(),'episodes':len(json.loads(result)['episodes']),'mismatches':json.loads(result)['mismatches']}
    (out/'VERIFICACION_RECALCULO_DESDE_ZIP.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))
    return int(result!=reference)
if __name__=='__main__':raise SystemExit(main())
