"""Run one trusted audit script with read/write boundaries and no DEE/network."""
from pathlib import Path
import argparse,json,runpy,sys,os
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--script',required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args();root=a.root.resolve(strict=True);work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
    source=root/'CONFIGURACIONES_Y_REPRODUCCION'/a.script
    allowed={'recalcular_esencial.py','preparar_tablas.py','contrastar_historicos.py'}
    if a.script not in allowed or not source.is_file():raise ValueError('Unapproved audit entry point')
    runtime=[Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()];denied=[]
    def inside(p,bases):return any(p==b or p.is_relative_to(b)for b in bases)
    def audit(event,args):
        if event=='import'and str(args[0]).startswith('dee_thinking'):
            denied.append({'event':event,'module':args[0]});raise RuntimeError('Scientific engine import forbidden')
        if event in('socket.connect','socket.connect_ex','subprocess.Popen','os.system'):
            denied.append({'event':event});raise RuntimeError('External execution/network forbidden in recalculation')
        if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
            file=Path(os.fsdecode(args[0])).resolve();mode=args[1]if len(args)>1 else'';flags=args[2]if len(args)>2 else 0
            write=isinstance(mode,str)and any(c in mode for c in' wax+')or isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if not inside(file,[work]if write else[root,work,*runtime]):
                denied.append({'event':event,'file':str(file),'write':bool(write)});raise RuntimeError('Undeclared filesystem access')
    sys.addaudithook(audit);args=a.args[1:]if a.args[:1]==['--']else a.args;sys.argv=[str(source),*args]
    runpy.run_path(str(source),run_name='__main__')
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('Engine unexpectedly present')
    with a.receipt.open('x',encoding='utf8')as f:json.dump({'status':'PASS','script':a.script,'engine_imported':False,'denied_operations':denied,'scope':'Python audit hooks, not an OS sandbox'},f,indent=2);f.write('\n')
if __name__=='__main__':main()
