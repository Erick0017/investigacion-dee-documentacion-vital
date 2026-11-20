"""Prueba instrumental del launcher; no Native, pip ni creación de vidas."""
from pathlib import Path
import importlib.util,json,gzip,hashlib,shutil
HERE=Path(__file__).resolve().parent;BUILD=HERE.parents[1];source=BUILD/'package/reproducir.py'
spec=importlib.util.spec_from_file_location('launcher',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
test=HERE/'prueba_launcher';test.mkdir(exist_ok=True);sector=test/'sectores/paisaje';sector.mkdir(parents=True,exist_ok=True);original=json.loads((HERE.parent/'stage/sector.json').read_bytes());(sector/'sector.json').write_text(json.dumps(original),encoding='utf8')
python=BUILD/'entorno313/Scripts/python.exe';p312=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
checks=[]
for id in ['M101','M123','M130','M140']:
 item=dict(next(x for x in original['mechanisms']if x['id']==id),sector='paisaje')
 for mode in ['ejecutar','recalcular']:
  command,limit=m.native_args(item,mode,python,test,test/'salida',p312)
  flags,script,args=m.script_command(command);assert script.is_relative_to(sector)
  assert (('--external-python'in args)==(id in['M130','M140']and mode=='ejecutar'))
  checks.append({'id':id,'mode':mode,'script':script.name,'external_arg':'--external-python'in args,'timeout':limit})
failed=False
try:m.native_args(dict(next(x for x in original['mechanisms']if x['id']=='M130'),sector='paisaje'),'ejecutar',python,test,test/'salida',None)
except ValueError:failed=True
assert failed
flags,script,args=m.script_command([str(python),'-I','-B','-X','utf8',str(sector/'a.py'),'arg']);assert flags==['-I','-B','-X','utf8']and script.name=='a.py'and args==['arg']
payload=b'compressed content witness, not an installed wheel';blob=test/'objeto.bin.gz';blob.write_bytes(gzip.compress(payload));m.ROOT=test
decoded=m.content({'storage':blob.name,'path':'motor/test.whl','compression':'gzip','bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()});assert decoded==payload
result={'native_ticks':0,'installations':0,'checks':checks,'external_required_rejected_without_python312':failed,'interpreter_flags_preserved':True,'content_store_decompression_and_sha':True,'wheel_preparation_source_uses_verified_materialized_bytes':"wheel.write_bytes(content(row))"in source.read_text(encoding='utf8')}
(HERE/'RESULTADO_LAUNCHER.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
