"""Runpy diagnóstico: deniega orígenes y creación de procesos/red. No importa DEE."""
from pathlib import Path
import argparse,json,os,runpy,sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--denegar',action='append',default=[]);p.add_argument('script',type=Path);p.add_argument('argumentos',nargs=argparse.REMAINDER);a=p.parse_args()
script=a.script.resolve(strict=True);roots=[os.path.normcase(str(Path(x).absolute()))for x in a.denegar]
def hook(event,args):
 if event in('subprocess.Popen','os.system','socket.connect','socket.bind'):raise PermissionError('Pure diagnostic forbids processes/network')
 if event in('open','os.scandir','os.listdir','ctypes.dlopen','os.add_dll_directory')and args and isinstance(args[0],(str,bytes,os.PathLike)):
  name=os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
  if any(name==r or name.startswith(r+os.sep)for r in roots):raise PermissionError('Original installation explicitly denied')
 if event=='import'and args and isinstance(args[0],str)and args[0].startswith(('dee_thinking','dee_universe')):raise PermissionError('No Native import in pure run')
sys.addaudithook(hook);sys.argv=[str(script),*a.argumentos];runpy.run_path(str(script),run_name='__main__')
