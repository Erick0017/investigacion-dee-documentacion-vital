"""Stage the current manager plus two fixed PI10 entrypoints; no deployment."""
from pathlib import Path
import ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';source=C/'sistema/gestionar.py';stage=H/'GESTOR_PUBLICO_PI10_R02_PREPARADO';text=source.read_text('utf-8-sig');before=hashlib.sha256(source.read_bytes()).hexdigest();anchor='# Debe estar ANTES de cualquier import app/DEE, incluso en los modos de lectura.\n';assert text.count(anchor)==1
addition='''# PI10 public adapter: state reads saved files; use transports one fixed EP
# to an already existing paused owner. No Store/Native import by this branch.
if len(sys.argv)>1 and sys.argv[1]in('pi10-estado','pi10-usar'):
    helper=Path(__file__).resolve().parent/'app/pi10_gestor_publico_R02.py'
    completed=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(helper),*sys.argv[1:]],cwd=helper.parent.parent,shell=False,capture_output=True,text=True,encoding='utf-8',errors='strict',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if completed.stdout:sys.stdout.write(completed.stdout);sys.stdout.flush()
    if completed.stderr:sys.stderr.write(completed.stderr);sys.stderr.flush()
    raise SystemExit(completed.returncode)

'''
text=text.replace(anchor,addition+anchor);ast.parse(text);helper=H/'pi10_gestor_publico_R02.py';ast.parse(helper.read_text('utf8'));stage.mkdir(exist_ok=True);(stage/'app').mkdir(exist_ok=True)
def exact(p,data):
 if p.exists():assert p.read_bytes()==data
 else:
  with p.open('xb')as f:f.write(data)
exact(stage/'gestionar.py',text.encode('utf8'));exact(stage/'app/pi10_gestor_publico_R02.py',helper.read_bytes());report={'schema':'DEE.PI10.public_manager.staged_exact_delta.R02','source_manager':str(source),'source_manager_sha256':before,'Native_executed':False,'product_modified':False,'additional_code_files':[{'file':p.relative_to(stage).as_posix(),'source':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'before_sha256':before if p.name=='gestionar.py'else None}for p in(stage/'gestionar.py',stage/'app/pi10_gestor_publico_R02.py')],'commands':['gestionar.py pi10-estado','gestionar.py pi10-usar --id ID_NUEVO --esperar 120'],'scope':'Only actual selected COMMITTED REAL2. Estado is frozen-file observation, no Runtime. Usar requires existing paused live owner and reconciled queue; exact EP only, no automatic owner, answer, retry, reset or resupply.'};exact(stage/'DELTA.json',(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'stage':str(stage),'manifest_sha256':hashlib.sha256((stage/'DELTA.json').read_bytes()).hexdigest(),'files':report['additional_code_files'],'Native':0}))
