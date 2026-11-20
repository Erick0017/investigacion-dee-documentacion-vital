"""Prospective pure R02 scope generator adaptation; preserve R01 tools."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'preparar_scope_PI10_R01.py';target=H/'preparar_scope_PI10_R02.py';t=source.read_text('utf8')
for old,new in(('PROTOCOLO_PI10_R01.json','PROTOCOLO_PI10_R02.json'),('pi10_consulta_adaptativa_R01.py','pi10_consulta_adaptativa_R02.py'),('DEE.PI10.fixed_experiment_scope.R01','DEE.PI10.fixed_experiment_scope.R02'),("'PI10_EXPERIMENTO_'+a.slug+'_R01.json'","'PI10_EXPERIMENTO_'+a.slug+'_R02.json'"),('PI10_EXPERIMENTO_R01.json','PI10_EXPERIMENTO_R02.json')):
 assert old in t,old;t=t.replace(old,new)
anchor="force={'null':None,'true':True,'false':False}[a.force_query];need(force is None or a.rol=='calibration','Forcing only in declared separate calibration')";assert t.count(anchor)==1;t=t.replace(anchor,anchor+";need(a.rol!='calibration'or force is True,'R02 uses one global all-query forced calibration, never per-row choices')")
ast.parse(t)
if target.exists():assert target.read_text('utf8')==t
else:
 with target.open('x',encoding='utf8')as f:f.write(t)
print(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'Native':0,'R01_preserved':True}))
