"""Finite technical reference/control batch; never combines individuals."""
import json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cases=['K65_OPPOSITE','K65_NO_SYMBOL','K65_UNPAIRED','K65_RESERVE','K65_REVISION_OFFPATH']
records=[]
for case in cases:
    started=time.perf_counter()
    out=ROOT/'resultados'/'repertorio65_referencia'/case
    command=[sys.executable,'-I','-B',str(ROOT/'base_validada'/'reproducir_repertorio65.py'),'--case',case,'--out',str(out)]
    p=subprocess.run(command,capture_output=True,text=True,timeout=90)
    record={'case':case,'exit_code':p.returncode,'seconds':time.perf_counter()-started,'stdout':p.stdout,'stderr':p.stderr,'command':command}
    records.append(record)
    print(json.dumps(record,ensure_ascii=False),flush=True)
    if p.returncode:
        raise SystemExit(p.returncode)
(ROOT/'resultados'/'repertorio65_referencia'/'CONTROL_BATCH.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
