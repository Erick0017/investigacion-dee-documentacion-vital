"""Read-only post-STOP audit after the declared file-export wall guard.

Does not import the motor/application, reopen an owner, advance a tick, edit an
original journal or complete the partial export. It examines copied transport.
"""
from pathlib import Path
import hashlib,importlib.util,json,shutil,sqlite3,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SYSTEM=ROOT/'sistema'
LIFE='APD05_CTL_PREV_ORD_REAL_R04'
EV=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles'
OUT=EV/'CIERRE_EXPORT_TRUNCADO_R04_N0_R01'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main():
    OUT.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('existing_offline_snapshot_reader',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py')
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    life=SYSTEM/'estado/vidas'/LIFE;record_path=life/'VIDA.json';record=read(record_path)
    if(life/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('This witness requires no unsaved Native future marker')
    snapshot_path=SYSTEM/record['snapshot'];state=parser.Snapshot(snapshot_path)
    if state.encoded_sha256!=record['snapshot_sha256']:raise ValueError('Record and exact saved snapshot differ')
    if state.pending:raise ValueError('Native pending events are not silently discarded')
    if record['operations'][-1]['kind']!='PERSISTENT_GRACEFUL_CLOSE':raise ValueError('No recorded graceful-close checkpoint')
    protocol=json.loads(state.metadata['DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'])
    if protocol['native_tick_at_checkpoint']!=state.tick:raise ValueError('Saved owner protocol is out of sync')
    slots=[json.loads(state.metadata['DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.'+str(i)])for i in range(16)]
    if any(slot!={'empty':True}for slot in slots):raise ValueError('Pending operational slots are not ignored')
    supervisor_path=EV/'REPOSO_Y_ACCESO_R04'/LIFE/'SUPERVISION.json';supervisor=read(supervisor_path)
    if supervisor['timeout']!='per_arm_wall_limit'or supervisor['resources']['job_active_processes']!=0:raise ValueError('Expected terminated owned export job not established')
    folder=SYSTEM/'estado'/record['persistent_service']['sidecar_directory'];originals=[]
    for suffix in('','-wal','-shm'):
        source=folder/('cola.sqlite3'+suffix)
        if source.is_file():
            target=OUT/source.name;digest=sha(source);shutil.copy2(source,target)
            if sha(target)!=digest or sha(source)!=digest:raise ValueError('Source journal changed during closed read-only copy')
            originals.append({'source':str(source),'sha256':digest,'bytes':source.stat().st_size,'copy_sha256':sha(target)})
    db=OUT/'cola.sqlite3';con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Copied transport integrity failed')
        outstanding=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
        if outstanding:raise ValueError('This post-STOP cut has unresolved transport')
        own=[dict(zip(('id','payload','payload_sha','status'),row))for row in con.execute('SELECT id,payload,payload_sha,status FROM requests WHERE id LIKE ? ORDER BY seq',(LIFE.lower()+'_%',)).fetchall()]
        if len(own)!=23 or any(x['status']!='completed'for x in own):raise ValueError('All exact23 new requests were not committed')
        stop=own[-1]
        if json.loads(stop['payload'])!={'operacion':'detener'}:raise ValueError('Last committed own request was not STOP')
        stop_row=con.execute('SELECT result FROM requests WHERE id=?',(stop['id'],)).fetchone();stop_result=json.loads(stop_row[0])
    finally:con.close()
    receipt=protocol['last_completed_receipt'];outbox=folder/'resultados'/(stop['id']+'.json')
    if receipt['id']!=stop['id']or receipt['payload_sha256']!=stop['payload_sha']or receipt['result_sha256']!=sha(outbox):raise ValueError('Native saved STOP witness and exact outbox/journal differ')
    if not stop_result['result']['graceful_stop']or stop_result['after_tick']!=state.tick:raise ValueError('STOP result does not confirm saved tick')
    native_dir=SYSTEM/'estado/observatorios/APD05_CONTROLES_R04'/LIFE
    sessions=[json.loads(x)for x in(native_dir/'SESIONES.jsonl').read_text(encoding='utf8').splitlines()if x]
    panel=[x for x in sessions if x['label'].startswith('common_panel_')]
    if len(panel)!=7:raise ValueError('The achieved common panel is incomplete')
    partial=folder/'exportaciones/APD05_CONTROL_COMPLETO_R01'
    if(partial/'EXPORTACION_SERVICIO.json').exists():raise ValueError('A complete paired manifest now exists; do not misclassify it as truncated')
    value={'schema':'APD05.closed_stop.export_truncated.N0.R01','Native_ticks':0,'life':LIFE,
           'status':'CLOSED_STOP_EXPORT_TRUNCATED','saved_snapshot':state.summary(),
           'record':{'source':str(record_path),'sha256':sha(record_path),'last_operation':record['operations'][-1]},
           'protocol':protocol,'all16_operational_slots_empty':True,'Native_pending':state.pending,
           'complete_common_panel_transport_requests':len(panel),'own23_transport_requests':own,'outstanding':outstanding,
           'STOP':{'id':stop['id'],'result':stop_result,'outbox':str(outbox),'outbox_sha256':sha(outbox)},
           'copied_original_transport_files':originals,'supervision':supervisor,
           'partial_export':{'directory':str(partial),'manifest_present':False,'never_marked_complete':True},
           'scope':'Native panel, explicit save, STOP and graceful-close snapshot all committed before the fixed3000s process guard. The guard interrupted only filesystem paired export. No new Native action or uncertain material future is inferred. This witness does not manufacture a full paired export or prove every worker artifact was copied.'}
    with(OUT/'CIERRE_VALIDADO_N0.json').open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    shutil.copy2(__file__,OUT/Path(__file__).name)
    print(json.dumps({'Native_ticks':0,'status':value['status'],'tick':state.tick,'snapshot_sha256':state.encoded_sha256,'out':str(OUT)}))


if __name__=='__main__':main()
