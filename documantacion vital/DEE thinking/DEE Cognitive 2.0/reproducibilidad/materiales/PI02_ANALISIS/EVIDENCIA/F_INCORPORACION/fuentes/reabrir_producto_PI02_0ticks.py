"""Affected product import/load/save/close check only, no repeated experiment."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sqlite3,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo import Owner,P
R=P.parent.parent.parent;C=R/'DEE Cognitive 2.0';S=C/'sistema';LIFE='ECI02_PI02_MAIN';out=P/'control/REAPERTURA_PRODUCTO_PI02.json'
attempt=P/'control/REAPERTURA_PRODUCTO_PI02_EN_CURSO.json';capture=P/'ensayos/PI02_PRODUCT_GUARDAR_0T.json'
if out.exists()or attempt.exists()or capture.exists()or(P/'ensayos/PI02_PRODUCT_STATE0.json').exists():raise ValueError('Existing product reopening attempt; reconcile it and never repeat blindly')
prepared=json.loads((P/'control/PREPARACION_PRODUCTO_PI02.json').read_text(encoding='utf-8'))
before=json.loads((S/'estado/vidas'/LIFE/'VIDA.json').read_text(encoding='utf-8'));before_snapshot=S/before['snapshot']
if before['physical']['tick']!=prepared['desired_cut']['tick']:raise ValueError('Product cut differs from the actual final prepared source')
source_db=S/'estado/pares_iniciales'/LIFE/'cola.sqlite3'
source_wal=source_db.with_name(source_db.name+'-wal')
if source_wal.exists()and source_wal.stat().st_size:raise ValueError('Frozen source pair unexpectedly has a nonempty WAL; no immutable read')
con=sqlite3.connect(source_db.as_uri()+'?mode=ro&immutable=1',uri=True)
try:
    latest=con.execute("SELECT value FROM meta WHERE key='latest_checkpoint'").fetchone()
    if latest is None:raise ValueError('Final pair lacks its actual operational-dependency checkpoint')
    source_dependencies=json.loads(latest[0])['operational_dependencies'];source_r04=source_dependencies['PI02']['R04']
finally:con.close()
attempt.write_text(json.dumps({'schema':'PI02.product.reopening.attempt.v1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'before_tick':before['physical']['tick'],'before_snapshot_sha256':before['snapshot_sha256'],'expected_action':'Paused owner, technical guardar, then detener; no reanudar/material query','status':'IN_PROGRESS'},ensure_ascii=False,indent=2),encoding='utf-8')
with Owner(LIFE,'PI02_PRODUCT_REOPEN',system=S)as owner:
    if any(owner.initial['physical'][k]!=before['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Product restoration differs')
    if owner.initial.get('paused')is not True:raise ValueError('The product owner did not start paused; do not open an idle-time window')
    saved=owner.control('guardar');capture.write_text(json.dumps(saved,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state=json.loads(saved['result'])
    if state['after_tick']!=before['physical']['tick']or state['before_tick']!=state['after_tick']:raise ValueError('0tick product witness actually advanced; preserve exact future')
    target_dependencies=state['committed_snapshot']['operational_dependencies'];target_r04=target_dependencies['PI02']['R04']
    if target_r04!=source_r04:raise ValueError('Paired R04 progress/resource status changed on product restore/save')
after=json.loads((S/'estado/vidas'/LIFE/'VIDA.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('passive_parser',R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_01/codigo/PROMOVER_PI01.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
comparison=parser.compare_native(parser.snapshot_view(before_snapshot),parser.snapshot_view(S/after['snapshot']),allow_service=True)
db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty product WAL remains after close; no incoherent immutable read')
con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
try:
    pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
    own=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
finally:con.close()
if pending or own['running']or owner.proc.poll()!=0:raise ValueError('Product owner/queue not closed and reconciled')
if after['physical']['tick']!=before['physical']['tick']:raise ValueError('Final tick changed')
proof={'schema':'PI02.product.actual.reopening0tick.v2','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'new_ticks':0,'physical_unchanged':True,'pending_reconciled':True,'operational_state_valid':True,'owner_closed':True,'snapshot_sha256':after['snapshot_sha256'],'before':before['physical'],'after':after['physical'],'native_comparison':comparison,'initial_status':owner.initial,'closed_owner':own,'pending':pending,'source_R04_operational_state':source_r04,'target_R04_operational_state':target_r04,'source_target_R04_progress_equal':True,'technical_save_receipt':state,'technical_save_primary':{'path':str(capture),'sha256':hashlib.sha256(capture.read_bytes()).hexdigest()},'preserved_main_PI01':json.loads((S/'estado/ACTIVO.json').read_text(encoding='utf-8')),'scope':'Actual product restored through its complete imported pair, artifact/journal dependencies validated, loaded/technically saved/closed while paused at0NativeTicks. No reanudar, idle opportunity, material state query or scientific trial repeated.'}
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'life':LIFE,'tick':after['physical']['tick'],'new_ticks':0,'proof':str(out)},ensure_ascii=False))
attempt.write_text(json.dumps({'schema':'PI02.product.reopening.attempt.v1','status':'COMPLETED','proof':str(out),'proof_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'new_ticks':0},ensure_ascii=False,indent=2),encoding='utf-8')
