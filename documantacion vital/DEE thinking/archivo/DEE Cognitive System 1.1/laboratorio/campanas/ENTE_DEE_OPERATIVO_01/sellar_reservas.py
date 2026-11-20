"""Sello de evaluación: no ejecuta DEE ni entrega soluciones al participante."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
here=Path(__file__).resolve().parent;root=here.parents[2]
target=here/'SELLO_RESERVAS.json'
if target.exists():raise FileExistsError(target)
files=[root/'sistema/gestionar.py',root/'sistema/capacidades/ente_operativo_01.py',root/'sistema/capacidades/ente_operativo_01_core.py',root/'sistema/capacidades/cierre_funcional_cf01.py',here/'PROTOCOLO_Y_RESERVAS.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((root/'sistema/estado/vidas/EO01_MAIN/VIDA.json').read_bytes())
r={'frozen_utc':datetime.now(timezone.utc).isoformat(),'life':'EO01_MAIN','tick_before_reserves':state['physical']['tick'],'snapshot_before_reserves':state['snapshot'],'snapshot_sha256':state['snapshot_sha256'],'files':{p.relative_to(root).as_posix():sha(p)for p in files},'one_schedule_revision':'R01 role0 reached too late; R02 only role0 shifted2ticks earlier. First two MAIN experiences wereR01; later episodesR02, not retroactively retested. No anatomical transplant.','future_protocol':'Three exact8job sequences from PROTOCOLO_Y_RESERVAS; no design/readers/codec changes; plasticity active; explicit external reset only; all first attempts counted.','social_limit_known_before_reserves':'New B messages do not yet alter useful actions with both inherited context sites occupied. No social-acquisition success claim.'}
target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r))
