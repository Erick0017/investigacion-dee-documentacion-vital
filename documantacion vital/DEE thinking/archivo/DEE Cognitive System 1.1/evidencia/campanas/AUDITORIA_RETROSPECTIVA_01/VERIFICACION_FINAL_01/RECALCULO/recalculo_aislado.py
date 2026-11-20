"""Run exported calculations while refusing historical reads and DEE imports."""
from pathlib import Path
import argparse,sys,json,importlib.abc
p=argparse.ArgumentParser();p.add_argument('--paquete',type=Path,required=True);p.add_argument('--prohibir',type=Path,action='append',default=[]);a=p.parse_args();base=a.paquete.resolve();blocked=[x.resolve()for x in a.prohibir];denied=[];allowed_opens=0
class NoEngine(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname=='dee_thinking'or fullname.startswith('dee_thinking.'):
            denied.append({'engine_import':fullname});raise ImportError('Engine is forbidden in retrospective recalculation')
def hook(event,args):
    global allowed_opens
    if event in('subprocess.Popen','socket.connect','socket.connect_ex','os.system'):
        denied.append({'event':event});raise PermissionError('External actions forbidden')
    if event=='open'and args and isinstance(args[0],(str,bytes)):
        v=Path(args[0].decode()if isinstance(args[0],bytes)else args[0]).resolve()
        if not v.is_relative_to(base)and any(v==b or v.is_relative_to(b)for b in blocked):
            denied.append({'historical_read':str(v)});raise PermissionError('Historical source unavailable in clean recalculation')
        allowed_opens+=1
sys.dont_write_bytecode=True;sys.meta_path.insert(0,NoEngine());sys.addaudithook(hook);sys.path.insert(0,str(base/'RECALCULO'))
from recalcular import run
r=run(base)
(base/'calculos_independientes.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report={'scope':'External software/evidence check, not native experiment','native_ticks':0,'engine_import_forbidden':True,'historical_roots_forbidden':[str(x)for x in blocked],'only_package_exception':str(base),'denied_attempts':denied,'allowed_file_opens':allowed_opens,'result':'Completed from exported primary bytes'}
(base/'RECALCULO_AISLADO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
