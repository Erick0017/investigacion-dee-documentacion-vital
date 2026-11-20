"""Integridad y cierre de un árbol propio de procesos inertes; cero Native."""
from pathlib import Path
import importlib.util,json,gzip,hashlib,subprocess,sys,uuid
HERE=Path(__file__).resolve().parent;BUILD=HERE.parents[1];spec=importlib.util.spec_from_file_location('launcher',BUILD/'package/reproducir.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=HERE/'paquete_integridad';root.mkdir(exist_ok=True);objects=root/'objetos';objects.mkdir(exist_ok=True);data=b'inert data witness';blob=objects/'obj.gz';blob.write_bytes(gzip.compress(data));entry=root/'INICIAR.bat';entry.write_bytes(b'@echo off\r\n')
cat={'files':[{'path':'datos/test.txt','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'storage':'objetos/obj.gz','compression':'gzip'}],'entrypoints':[{'path':entry.name,'sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'bytes':entry.stat().st_size}]};(root/'CATALOGO.json').write_text(json.dumps(cat),encoding='utf8');m.ROOT=root
m.verify(cat);entry.write_bytes(b'changed');entry_blocked=False
try:m.verify(cat)
except ValueError:entry_blocked=True
assert entry_blocked;entry.write_bytes(b'@echo off\r\n')
out=HERE/('salida_cache_'+uuid.uuid4().hex[:6]);target=m.materialize(cat,out);assert m.materialize(cat,out)==target;(target/'datos/test.txt').write_bytes(b'changed');cache_blocked=False
try:m.materialize(cat,out)
except ValueError:cache_blocked=True
assert cache_blocked
code="import subprocess,sys,json,time,os;p=subprocess.Popen([sys.executable,'-I','-B','-c','import time;time.sleep(90)']);print(json.dumps({'parent':os.getpid(),'child':p.pid}),flush=True);time.sleep(90)"
proc=subprocess.Popen([sys.executable,'-I','-B','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 ids=json.loads(proc.stdout.readline());termination=m.terminate_owned_tree(proc)
finally:
 if proc.poll()is None:m.terminate_owned_tree(proc)
result={'native_ticks':0,'entrypoint_tamper_blocked':entry_blocked,'materialized_cache_tamper_blocked':cache_blocked,'created_inert_processes':ids,'termination':termination,'parent_finished':proc.poll()is not None};assert result['parent_finished']
(HERE/'RESULTADO_INTEGRIDAD_TIMEOUT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
