"""Compare actual closed versus post-output-null complete native states."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
original=json.loads((E/'MI01_413_MAIN_RESERVA_3.json').read_bytes())['result'];target=original['INSTRUMENTO']['snapshot_sha256'];p=None
for candidate in(S/'estado/checkpoints').glob('E1_MI01_MAIN.T27834.*.deetsnap.gz'):
    if sha(candidate)==target:p=candidate;break
if p is None:raise FileNotFoundError('Exact frozen MAIN final boundary required')
d=json.loads((E/'MI01_452_ACTUADOR_ANULADO.json').read_bytes());q=S/d['after']['snapshot'];x=Snapshot(p);y=Snapshot(q);c=compare(x,y);out={'native_ticks':0,'closed_snapshot':str(p.relative_to(R)),'closed_sha256':sha(p),'null_snapshot':str(q.relative_to(R)),'null_sha256':sha(q),'comparison':c,'interpretation':'The external post-output torque cut changes the environment and its fixed sensor/cost return. Native RAW differences demonstrate physical sensitivity of the whole organization, not necessarily changed S choices, useful learning or a competent Pendulum policy. No identical external future was imposed after different actions.'};atomic_json(E/'SENSIBILIDAD_FISICA_EXTERNA_483_0TICKS.json',out);print(json.dumps(out,ensure_ascii=False))
