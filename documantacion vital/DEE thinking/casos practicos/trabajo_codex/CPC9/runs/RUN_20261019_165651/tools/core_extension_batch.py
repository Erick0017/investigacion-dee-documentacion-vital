"""Sequential bounded native recoveries, one Core slot at a time."""
from pathlib import Path
import json,sys,time
RUN=Path(__file__).resolve().parents[1];sys.path.insert(0,str(RUN/'tools'))
import supervisor
CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized';OUT=RUN/'notes/core_extension_v2'
groups=('stream','network','architectures','bridge','capacity','longitudinal','policy','native_loop','qfm','l15');results=[];start=time.monotonic()
for group in groups:
 if supervisor.remaining()<supervisor.BUDGET['reserve_close_seconds']+1200:break
 limit=512 if group in('capacity','longitudinal','l15')else 384
 record=supervisor.run('core_EXTENSION_'+group.upper()+'_01',[sys.executable,'-I','-B',str(CORE/'reproduccion/worker_extension.py'),group,'--materialized',str(MAT),'--out',str(OUT/(group.upper()+'_v1'))],timeout=600,native=True,memory_mib=limit)
 results.append(record);(OUT/'BATCH.json').write_text(json.dumps({'groups':results,'elapsed_seconds':time.monotonic()-start},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'groups':[(r['name'],r['status'],r.get('exit_code'))for r in results],'elapsed_seconds':time.monotonic()-start}))
