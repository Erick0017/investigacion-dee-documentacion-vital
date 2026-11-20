"""Root authorized one exact SAFE full-pair fork, without preparation or ticks.

Installing ACT_R03 and the persistent view belongs to a later material plan,
not this import. No memories from post10, controls, seed or later futures enter.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];S=ROOT/'sistema'
PAIR=S/'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PAIR_SHA='5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAP_SHA='771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
LIFE='APD04_PERSISTENCIA_TEMPRANA_RESERVA_R01'
OUT=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PERSISTENCIA_TEMPRANA_IMPORTACION_N0_R01'
def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def rows(path):
    c=sqlite3.connect(Path(path).as_uri()+'?mode=ro&immutable=1',uri=True)
    try:return c.execute('SELECT id,payload,payload_sha,status,result FROM requests ORDER BY id').fetchall()
    finally:c.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-go',required=True,choices=('ROOT_GO_EARLY_PERSISTENCE_SAFE_FULL_IMPORT_N0',))
    parser.parse_args()
    if OUT.exists()or(S/'estado/vidas'/LIFE).exists()or(S/'estado/entrada_sencilla/vidas'/LIFE).exists():
        raise FileExistsError('Preserve existing identity/attempt; no repeated import or fallback.')
    assert sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_SHA and sha(PAIR/'VIDA.deetsnap.gz')==SNAP_SHA
    manifest=read(PAIR/'EXPORTACION_SERVICIO.json')
    assert manifest['life_id']=='APD04_MAIN'and manifest['physical']['tick']==639374
    ui=load('early_persistence_existing_UI',S/'app/usar_dee.py')
    observer=load('early_persistence_saved_snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py')
    config=dict(ui.read(ui.selected_config_path(ROOT)))
    config.update(source_alias='APD04_SAFE_EARLY_PERSISTENCE',source_life='APD04_MAIN',source_tick=639374,
        source_snapshot_sha256=SNAP_SHA,paired_export_manifest_sha256=PAIR_SHA,
        source_paired_export_manifest=(PAIR/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    protected_paths=[S/'estado/ACTIVO.json',S/'estado/vidas/APD04_SEMILLA_COLABORADOR_R01/VIDA.json',
        S/read(S/'estado/vidas/APD04_SEMILLA_COLABORADOR_R01/VIDA.json')['snapshot'],PAIR/'EXPORTACION_SERVICIO.json',PAIR/'VIDA.deetsnap.gz']
    protected={str(p):sha(p)for p in protected_paths}
    source_hashes={str(S/p['file'].removeprefix('sistema/')):sha(ROOT/p['file'])for p in read(HERE/'PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01/MANIFIESTO_PROPUESTA_N0.json')['members']}
    OUT.mkdir();shutil.copy2(__file__,OUT/Path(__file__).name)
    emit(OUT/'ANTES_N0.json',{'life':LIFE,'source_full':str(PAIR),'manifest_sha256':PAIR_SHA,'snapshot_sha256':SNAP_SHA,
        'local_config_not_installed':config,'protected':protected,'source_hashes':source_hashes,
        'new_native_ticks':0,'owner_started':False,'actuator_or_view_not_configured':True})
    backend=ui.OriginalBackend(ROOT,config);session=ui.Supervisor(ROOT,LIFE,backend,config)
    # import_new invokes the existing verifier once; do not duplicate its scan.
    with ui.SessionLock(backend.protocol_home/LIFE/'SUPERVISOR.lock'):card=session.open(new=True)
    parent=observer.Snapshot(PAIR/'VIDA.deetsnap.gz',verify_checksum=False)
    child=observer.Snapshot(S/card['snapshot'],verify_checksum=False)
    assert card['parent']['encoded_sha256']==SNAP_SHA and card['physical']['tick']==639374
    assert parent.raw==child.raw and parent.clocks==child.clocks and parent.channels==child.channels
    assert parent.pending==child.pending and parent.receipts==child.receipts
    assert rows(PAIR/'cola.sqlite3')==rows(S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3')
    assert backend.process is None and backend.job is None and not session.owned
    assert not session.state.get('pending_material')and not session.state.get('uncertain_preserved')
    assert all(sha(p)==h for p,h in protected.items())and all(sha(p)==h for p,h in source_hashes.items())
    emit(OUT/'IMPORTACION_N0.json',{'record':card,'protocol':session.state,
        'source_full':str(PAIR),'manifest_sha256':PAIR_SHA,'RAW_clocks_channels_pending_receipts_equal':True,
        'SQLite_requests_equal':True,'new_native_ticks':0,'Runtime_owner_started':False,
        'protected_and_source_hashes_unchanged':True,'actuator_or_view_not_configured':True,
        'scope':'Another explicitly named SAFE-history trajectory; not continuation of late post10 or a favorable control future, not T0 or new learning.'})
    print(json.dumps({'life':LIFE,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],
        'out':str(OUT),'new_native_ticks':0,'owner_started':False},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
