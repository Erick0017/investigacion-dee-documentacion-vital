"""Directed source map; no historical campaign is executed."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent;vital=root.parents[2];path=vital/'procesos/PROCESOS_03_DEE_V27_NATIVE_THERMODYNAMICS_REFOUNDATION_R4_NEW_RESULTADOS.zip'
with zipfile.ZipFile(path) as z:
    names=z.namelist();choices=[n for n in names if n.endswith(('SUMMARY.json','FROZEN_ANALYSIS_LOCK.json')) or n=='dee_r4_new_discovery_runner_v1.py']
    out=root/'evidence/thermal_sources';out.mkdir(parents=True,exist_ok=True);records=[]
    for n in choices:
        data=z.read(n);dest=out/Path(n).name;dest.write_bytes(data);records.append({'member':n,'destination':str(dest.relative_to(root)),'sha256':hashlib.sha256(data).hexdigest()})
    record={'archive':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'members':len(names),'selected':records}
(out/'PROVENANCE.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record))
