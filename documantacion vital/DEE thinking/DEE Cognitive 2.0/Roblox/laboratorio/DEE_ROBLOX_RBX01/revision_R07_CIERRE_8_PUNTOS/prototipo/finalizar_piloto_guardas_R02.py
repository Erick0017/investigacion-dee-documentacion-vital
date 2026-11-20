"""Version the prepared pilot driver before material use; FS/compile only."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent/'NATIVE_LIMPIO_R07'
old=P/'ejecutar_piloto_R07_preparado.py'
source=old.read_text(encoding='utf-8')
source=source.replace('{"Main","BackendBinding","LiveAdapters_R07"}',
                      '{"Main","BackendBinding","LiveAdapters_R07","MotorPathfinding_R07"}')
source=source.replace("for n in('Main','BackendBinding','LiveAdapters_R07')",
                      "for n in('Main','BackendBinding','LiveAdapters_R07','MotorPathfinding_R07')")
source=source.replace("'Declared PILOT/DEV4/teacher omitted')",
                      "'Declared PILOT/PAR28/teacher scope paired; no new teaching performed')")
marker="    imported=read(a.destination/'IMPORTACION_DIAGNOSTICA.json')"
assert source.count(marker)==1
source=source.replace(marker,
    "    need(scope['parent_native_cycles']==24 and scope['parent_last_sequence']==56,'Preserved PAR28 ancestry counters')\n"+marker)
out=P/'ejecutar_piloto_R07_preparado_R02.py'
if out.exists():raise ValueError('Fresh driver destination required')
compile(source,str(out),'exec')
out.write_text(source,encoding='utf-8',newline='\n')
proof={'schema':'DEE.R07.pilot.driver_guard.R02','file':str(out),
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'parent_driver_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
 'changes':['Verify actual Main/BackendBinding/LiveAdapters_R07/MotorPathfinding_R07 Sources using LF normalization',
 'Require parent_native_cycles24/parent_last_sequence56'],
 'Native_ticks':0,'MCP_calls':0,'model_calls':0,
 'status':'PREPARED_NOT_MATERIALLY_REPRODUCED'}
proof_path=P/'DRIVER_PREPARADO_R02.json'
proof_path.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(proof,indent=2,ensure_ascii=False))
