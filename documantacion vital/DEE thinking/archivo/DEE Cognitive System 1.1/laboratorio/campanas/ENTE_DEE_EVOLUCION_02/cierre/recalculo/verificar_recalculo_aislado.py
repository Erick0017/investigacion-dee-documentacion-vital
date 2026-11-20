"""Run the exported recalculation in a fresh process with original roots denied.

This worker does not create an export: call it on an already copied/extracted
analysis tree. It never imports DEE or starts an external environment.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys

def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--codigos',type=Path,required=True);p.add_argument('--artefactos',type=Path);p.add_argument('--indice-artefactos',type=Path);p.add_argument('--referencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--prohibir-raiz',type=Path,action='append',required=True);args=p.parse_args()
    script=Path(__file__).resolve().with_name('recalcular_eo02.py');forbidden=[x.resolve()for x in args.prohibir_raiz];denied=[]
    def hook(event,values):
        if event in('socket.connect','socket.connect_ex','subprocess.Popen','os.system'):
            denied.append({'event':event});raise PermissionError('Recalculation cannot use network or subprocesses')
        if event=='import'and values and str(values[0]).startswith('dee_thinking'):
            denied.append({'event':event,'module':str(values[0])});raise PermissionError('No DEE import in archived recalculation')
        if event=='open'and values and isinstance(values[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(values[0])).resolve()
            if any(path==root or path.is_relative_to(root)for root in forbidden):
                denied.append({'event':event,'path':str(path)});raise PermissionError('Original data/system path is forbidden')
    sys.addaudithook(hook)
    argv=[str(script),'--primarios',str(args.primarios),'--codigos',str(args.codigos),'--salida',str(args.salida)]
    if args.artefactos:argv+=['--artefactos',str(args.artefactos)]
    if args.indice_artefactos:argv+=['--indice-artefactos',str(args.indice_artefactos)]
    sys.argv=argv
    try:runpy.run_path(str(script),run_name='__main__')
    except SystemExit as result:
        if result.code not in(None,0):raise
    output=args.salida/'RECALCULO_EO02.json';actual=hashlib.sha256(output.read_bytes()).hexdigest();expected=hashlib.sha256(args.referencia.read_bytes()).hexdigest()
    result=json.loads(output.read_bytes());proof={'schema':'EO02.exported_recalculation_independence.v1','produced_sha256':actual,'reference_sha256':expected,'byte_identical':actual==expected,
        'discrepancies':result['discrepancies'],'cases':len(result['cases']),'episodes':sum(c['totals']['attempts']for c in result['cases']),
        'original_roots_forbidden':[str(x)for x in forbidden],'denied_attempts':denied,'new_DEE_ticks':0,'new_worker_executions':0,
        'scope':'Archived recalculation from the supplied exported bytes, not native physical replay or package operation test.'}
    if actual!=expected or result['discrepancies']or denied:raise ValueError(json.dumps(proof))
    (args.salida/'INDEPENDENCIA_RECALCULO.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
