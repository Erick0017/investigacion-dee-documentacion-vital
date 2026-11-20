"""Root-authorized N0 administrative locator repair for the own untouched seed.

Only VIDA.persistent_service is added using the installed atomic writer. The
imported complete Native state and operational journal/artifacts are immutable.
No owner, Runtime, material input, snapshot rewrite or tick is executed here.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
S=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
LIFE='APD04_SEMILLA_COLABORADOR_R01'
OUT=EV/'SEMILLA_REGISTRO_LOCALIZADOR_N0_R01'


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-go',required=True,choices=('ROOT_GO_SEMILLA_TECHNICAL_LOCATOR_N0',))
    parser.parse_args()
    if OUT.exists():raise FileExistsError('Preserve the attempted locator repair; never repeat automatically.')
    record_path=S/'estado/vidas'/LIFE/'VIDA.json';card=read(record_path)
    imported=read(EV/'WAIT_R03_REAL_SEMILLA_IMPORTACION_N0_R01/IMPORTACION_N0.json')
    if card!=imported['record']or imported['owner_started']or imported['new_native_ticks']:
        raise ValueError('The seed changed since its authorized exact N0 import; no substitute or repair.')
    if 'persistent_service'in card:raise ValueError('The index already exists; no overwrite.')
    if card['life_id']!=LIFE or card['snapshot_sha256']!='52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc':
        raise ValueError('Wrong seed identity; do not alter another record.')
    side=S/'estado/servicios_persistentes'/LIFE;worker=S/'estado/servicios_locales'/LIFE
    snapshot=S/card['snapshot'];journal=side/'cola.sqlite3'
    if(S/'estado/locks'/(card['world_id']+'.lock')).exists():raise ValueError('A writer lock is present; no locator write.')
    if not side.is_dir()or not worker.is_dir():raise ValueError('The full operational imported paths are missing.')
    wal=journal.with_name(journal.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL is not cleared or hidden.')
    connection=sqlite3.connect(journal.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        assert connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        owner=json.loads(connection.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        pending=connection.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
        assert owner.get('running')is False and owner.get('imported_not_yet_started')is True
        assert owner.get('life_id')==LIFE and owner['tick']==card['physical']['tick']
        assert not pending
    finally:connection.close()
    paths=[snapshot,S/'estado/ACTIVO.json',S/'estado/entrada_sencilla/vidas'/LIFE/'PROTOCOLO.json']
    paths+=sorted(p for base in(side,worker)for p in base.rglob('*')if p.is_file())
    immutable={str(p):sha(p)for p in paths}
    observer=load('seed_pure_saved_snapshot',S/'capacidades/observador_causal_retrospectivo_01.py')
    saved=observer.Snapshot(snapshot,verify_checksum=False)
    physical={'N':saved.N,'tick':saved.tick,'RAW_sha256':observer.sha(observer.pbytes(saved.raw)),
        'clocks_sha256':observer.sha(observer.pbytes(saved.clocks))}
    assert saved.encoded_sha256==card['snapshot_sha256']and not saved.pending
    assert all(physical[k]==card['physical'][k]for k in physical)
    OUT.mkdir();shutil.copy2(__file__,OUT/Path(__file__).name);shutil.copy2(record_path,OUT/'VIDA_ANTES_BYTES.json')
    descriptor={'schema':'DEE.persistent_service.record_index.v1','backend':'mente_unificada',
        'sidecar_directory':side.relative_to(S/'estado').as_posix(),
        'worker_directory':worker.relative_to(S/'estado').as_posix(),
        'snapshot_alone_is_not_complete_transport':True,
        'scope':'Technical state locator, no learned contents or answers. Native metadata and the paired journal remain authoritative.'}
    after={**card,'persistent_service':descriptor}
    emit(OUT/'ANTES_DE_ESCRITURA_N0.json',{'record_sha256':sha(record_path),'physical':physical,
        'descriptor_to_add':descriptor,'immutable_members_before':immutable,'owner_imported_not_started':owner,
        'pending_transport':pending,'new_native_ticks':0,'owner_started':False,
        'Root_authorization':'Explicit N0 repair of only missing technical locator on own seed; not cognition.'})
    ui=load('seed_existing_atomic_writer_only',S/'app/usar_dee.py')
    ui.write_atomic(record_path,after)
    actual=read(record_path)
    assert actual==after and{key:value for key,value in actual.items()if key!='persistent_service'}==card
    assert set(actual)-set(card)=={'persistent_service'}
    assert all(sha(path)==h for path,h in immutable.items())
    shutil.copy2(record_path,OUT/'VIDA_DESPUES_BYTES.json')
    emit(OUT/'REPARACION_N0_VERIFICADA.json',{'life':LIFE,'only_added_field':'persistent_service',
        'VIDA_before_sha256':sha(OUT/'VIDA_ANTES_BYTES.json'),'VIDA_after_sha256':sha(record_path),
        'native_snapshot_sha256_unchanged':sha(snapshot),'physical_exactly_unchanged':physical,
        'identity_parent_tick_snapshot_fields_unchanged':True,'all_operational_bytes_unchanged':True,
        'immutable_members_after':{str(p):sha(p)for p in paths},'new_native_ticks':0,'Runtime_created':False,
        'owner_started':False,'no_material_input':True,'not_learning_or_functional_recovery':True})
    seal=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/sellar_corte_poststop_apd04_n0_r01.py'
    command=[sys.executable,'-I','-B','-X','utf8',str(seal),'--root',str(ROOT),'--life',LIFE,
        '--tick',str(card['physical']['tick']),'--snapshot-sha256',card['snapshot_sha256'],
        '--target-name',LIFE+'_T'+str(card['physical']['tick'])+'_COMPLETO_N0_R01',
        '--out',str(OUT/'SELLO_COMPLETO_N0'),'--scope','N0 own collaborator seed, exact post10 REAL Native state and operational queue; only missing technical VIDA locator registered administratively, no owner/ticks/probes.',
        '--root-go','APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
    subprocess.run(command,cwd=Path(sys.executable).parent,check=True)
    sealed=read(OUT/'SELLO_COMPLETO_N0/CORTE_COMPLETO_POSTSTOP.json')
    print(json.dumps({'life':LIFE,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],
        'pair':sealed['pair']['directory'],'manifest_sha256':sealed['pair']['manifest_sha256'],
        'only_added_field':'persistent_service','new_native_ticks':0,'owner_started':False},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
