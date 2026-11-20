"""Parse the example only. Do not execute or construct a native life."""
from pathlib import Path
import argparse,sys,json,shlex,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from gestionar import parser
source=a.system/'app/ESPANOL_FUNCIONAL_01_CONTINUAR.eventos';rows=[]
for n,line in enumerate(source.read_text(encoding='utf8').splitlines(),1):
 if not line.strip()or line.lstrip().startswith('#'):continue
 parsed=parser().parse_args(shlex.split(line,posix=True))
 if hasattr(parsed,'parametros'):json.loads(parsed.parametros)
 rows.append({'line':n,'command':parsed.command,'syntactically_valid':True})
a.out.write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':rows,'executed_example_file':False,'created_native_runtime':False,'physical_component_commands_verified_separately':'API_RESERVA_FINAL_30; this is only event-file syntax validation'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'valid_lines':len(rows),'physical_evolution':False}))
