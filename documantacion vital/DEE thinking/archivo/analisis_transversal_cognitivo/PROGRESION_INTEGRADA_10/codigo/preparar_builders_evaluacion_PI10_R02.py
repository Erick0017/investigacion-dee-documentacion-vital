"""Generate prospective pure12/18 R02 plan/scope continuations from R01."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
outputs=[]
for srcname,dstname in(('preparar_evaluacion_PI10_R01.py','preparar_evaluacion_PI10_R02.py'),('preparar_continuacion_cerrada_PI10_R01.py','preparar_continuacion_cerrada_PI10_R02.py')):
 src=H/srcname;dst=H/dstname;t=src.read_text('utf8')
 for old,new in(('DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01','DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'),('DEE.PI10.adaptive_query.two_native_traces.R01','DEE.PI10.adaptive_query.two_native_traces.R02'),('PROTOCOLO_PI10_R01.json','PROTOCOLO_PI10_R02.json'),('PI10_EXPERIMENTO_R01.json','PI10_EXPERIMENTO_R02.json'),('DEE.PI10.fixed_experiment_scope.R01','DEE.PI10.fixed_experiment_scope.R02'),('pi10_consulta_adaptativa_R01.py','pi10_consulta_adaptativa_R02.py'),("'_R01.json'","'_R02.json'"),('Real18','Real12'),('real18','real12'),('24 if','18 if'),("else 18","else 12"),('<=24','<=18'),('==18','==12'),('range(18)','range(12)'),('%18','%12')):
  t=t.replace(old,new)
 # Generic max-lot literals occur only in the declared real/control bounds.
 t=t.replace("'planned_final_ordinal'", "'planned_final_ordinal'")
 ast.parse(t)
 if dst.exists():assert dst.read_text('utf8')==t
 else:
  with dst.open('x',encoding='utf8')as f:f.write(t)
 outputs.append({'file':str(dst),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
print(json.dumps({'outputs':outputs,'Native':0,'R01_preserved':True}))
