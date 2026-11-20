"""Root records the successfully completed documents marker, before authoring."""
from pathlib import Path
import datetime,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];f=P/'documentos/HECHOS_A_1_35.json'
d=json.loads(f.read_text(encoding='utf8'))
if d['actual_authoring_marker_registered_by_root']is not False:raise ValueError('Marker already registered; do not repeat')
backup=f.with_name('HECHOS_A_1_35_ANTES_MARCADOR.json')
if backup.exists():raise FileExistsError('Prior marker registration preserved')
shutil.copyfile(f,backup)
d['actual_authoring_marker_registered_by_root']=True
d['Root_marker_registration']={'operation_kind':'edit','expected_output_count':2,'output_format':'docx','marker_command_successfully_executed':True,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'facts_before_sha256':hashlib.sha256(backup.read_bytes()).hexdigest()}
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'facts':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'marker_registered':True}))
