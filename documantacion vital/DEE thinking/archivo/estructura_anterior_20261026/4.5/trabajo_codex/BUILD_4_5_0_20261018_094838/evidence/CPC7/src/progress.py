"""Incremental campaign ledger, never imported by a participant."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha
from supervisor import remaining
jobs=[]
for p in sorted((ROOT/'jobs').glob('*/COMMAND.json')):
    m=json.loads(p.read_text(encoding='utf-8'));jobs.append({'job':p.parent.name,'status':m['status'],'exit_code':m['exit_code'],'elapsed_seconds':m['elapsed_seconds']})
primaries=[p.relative_to(ROOT).as_posix() for p in (ROOT/'resultados').rglob('MEASUREMENTS.json')]
put(ROOT/'REANUDACION.json',{'schema':'CPC7.progress.v1','updated_utc':datetime.now(timezone.utc).isoformat(),
    'budget_file_sha256':sha(ROOT/'BUDGET.json'),'remaining_seconds_original':remaining(),'budget_restarted':False,
    'completed_native_primaries':primaries,'completed_supervised_jobs':jobs,
    'latest_completed_frontier':primaries[-1] if primaries else None,
    'next_tasks':['Terminar integración de acceso nativo al repertorio propio','Controles y reservas de continuidad','Demostración y restauración','Reconciliar evidencia, prueba limpia del ZIP exacto y publicar'],
    'resume_authority':'Otra ejecución sólo con autorización nueva; este archivo no programa trabajo en segundo plano.'})
print(json.dumps({'remaining_original_seconds':remaining(),'native_primaries':len(primaries),'completed_jobs':len(jobs)}))
