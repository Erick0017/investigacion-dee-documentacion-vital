"""Compara logging mínimo y detallado desde snapshots completos ya producidos."""
from pathlib import Path
import sys,json,hashlib
here=Path(__file__).resolve().parent;root=here.parents[2];system=root/'sistema'
sys.path.insert(0,str(system))
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
lives=['EO01_OBSERVACION_MIN','EO01_OBSERVACION_DET']
rec=[json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes())for life in lives]
snap=[Snapshot(system/r['snapshot'])for r in rec]
report={'operation':'Saved bytes comparison only','native_ticks':0,'lives':lives,'snapshots':[s.summary()for s in snap],'comparison':compare(*snap),
        'method':'Same complete native prefix, raw inputs, calibration, fixed reader, resources and actuator; only external passive recording coverage differs.',
        'expected_documentary_difference':'SYSTEM life/world identity differs between diagnostic forks; these metadata are not kernel inputs.',
        'failed_prior_cli_inspection':'A preceding read-only inspection used an incomplete filename and returned FileNotFoundError before loading or advancing; no simulation result is inferred.'}
dest=root/'evidencia/campanas/ENTE_DEE_OPERATIVO_01/OBSERVACION_EQUIVALENCIA.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'comparison':report['comparison'],'output':str(dest)},ensure_ascii=False))
