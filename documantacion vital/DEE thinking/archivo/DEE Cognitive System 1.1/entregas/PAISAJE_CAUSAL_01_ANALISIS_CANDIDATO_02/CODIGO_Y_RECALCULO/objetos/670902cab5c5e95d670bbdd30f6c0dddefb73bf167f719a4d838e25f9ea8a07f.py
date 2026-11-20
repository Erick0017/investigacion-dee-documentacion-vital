"""Engine-free verification subprocess with a declared Python read/write guard.

This is an additional observable Python audit boundary, not an OS sandbox.
"""
from pathlib import Path
import argparse, json, os, runpy, sys

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--operation',choices=('data','recalculate'),required=True);a=p.parse_args()
    root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if out==root or root in out.parents:raise ValueError('Write derived outputs outside the sealed extraction')
    allowed_read=(root,out,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),Path(sys.executable).resolve().parent)
    opened=[];denied=[]
    def under(path,base):return path==base or base in path.parents
    def audit(event,args):
        if event=='import'and str(args[0]).split('.')[0]=='dee_thinking':
            denied.append({'event':event,'module':str(args[0])});raise PermissionError('No native engine imports in data recalculation')
        if event!='open'or isinstance(args[0],int):return
        path=Path(os.fsdecode(args[0])).resolve();mode=str(args[1]or'');flags=int(args[2]or 0)
        writing=any(c in mode for c in'wax+')or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        permitted=under(path,out)if writing else any(under(path,b)for b in allowed_read)
        row={'path':str(path),'mode':mode,'write':writing,'permitted':permitted};opened.append(row)
        if not permitted:denied.append(row);raise PermissionError('Read/write outside declared analysis and interpreter paths: '+str(path))
    sys.addaudithook(audit)
    program=root/'CODIGO_Y_RECALCULO'/('extraer_registros.py'if a.operation=='data'else'recalcular_analisis.py')
    output=out/('DATOS_VERIFICADOS.json'if a.operation=='data'else'RECALCULO_REHECHO.json')
    sys.argv=[str(program),'--root',str(root),'--report'if a.operation=='data'else'--out',str(output)]
    code=0
    try:runpy.run_path(str(program),run_name='__main__')
    except SystemExit as exc:code=exc.code or 0
    finally:
        report={'scope':'Python open/import audit only, not a claim of an OS sandbox','operation':a.operation,'read_roots':[str(q)for q in allowed_read],'write_root':str(out),'open_events':opened,'denied':denied,'engine_imported':any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules),'exit_code':code,'no_history_or_laboratory_read_authorized':True}
        (out/('LECTURAS_'+a.operation+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if code or denied:raise SystemExit(code or 1)

if __name__=='__main__':main()
