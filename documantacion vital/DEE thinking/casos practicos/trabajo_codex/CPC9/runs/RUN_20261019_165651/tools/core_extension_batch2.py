from pathlib import Path
import json,sys,time
RUN=Path(__file__).resolve().parents[1];sys.path.insert(0,str(RUN/'tools'));import supervisor
CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized';OUT=RUN/'notes/core_extension_v2';rows=[]
tasks=[('stream','worker_extension.py','STREAM_v2'),('central','worker_extension.py','CENTRAL_v1'),('early','worker_retention.py','RETENTION_EARLY_v1'),('word','worker_retention.py','RETENTION_WORD_v1'),('late','worker_retention.py','RETENTION_LATE_v1')]
for group,script,target in tasks:
 r=supervisor.run('core_RECOVERY2_'+target,[sys.executable,'-I','-B',str(CORE/'reproduccion'/script),group,'--materialized',str(MAT),'--out',str(OUT/target)],timeout=600,native=True,memory_mib=384);rows.append(r);(OUT/'BATCH2.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'tasks':[(r['name'],r.get('exit_code'))for r in rows]}))
