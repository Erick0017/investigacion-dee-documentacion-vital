"""Entry point using the installed official4.5 instrument, not a workspace engine."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def identity():
 import platform,dee_thinking
 from dee_thinking import _native
 sha=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()
 result={'python':sys.executable,'version_python':platform.python_version(),'arquitectura':platform.architecture()[0],'producto':dee_thinking.__version__,'importado':dee_thinking.__file__,'extension':_native.__file__,'extension_sha256':sha}
 if sys.version_info[:2]!=(3,13)or sys.maxsize<=2**32 or dee_thinking.__version__!='4.5.0'or sha!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d':raise RuntimeError('Instrumento distinto del contrato oficial4.5/CP313x64')
 return result
def main():
 p=argparse.ArgumentParser(description='CPC8 privado; gramática experimental finita, no chatbot.')
 sub=p.add_subparsers(dest='comando',required=True);sub.add_parser('identidad')
 demo=sub.add_parser('demo');demo.add_argument('--eventos',type=Path);demo.add_argument('--salida',type=Path,required=True);demo.add_argument('--interactivo',action='store_true')
 a=p.parse_args();print(json.dumps({'origen':'INSTRUMENTO','identidad':identity()},ensure_ascii=False),flush=True)
 if a.comando=='demo':
  sys.path.insert(0,str(ROOT));from app.experimento import main as run
  if not a.eventos and not a.interactivo:p.error('Use --eventos o --interactivo')
  run(a.eventos,a.salida,a.interactivo)
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 main()
