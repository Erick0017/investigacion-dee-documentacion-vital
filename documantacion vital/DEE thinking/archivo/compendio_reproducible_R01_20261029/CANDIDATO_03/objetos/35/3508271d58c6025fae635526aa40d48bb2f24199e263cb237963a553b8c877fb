"""N0 seal of the selected closed distribution cut, not a scientific PASS.

Run once after Root has installed the actual manual/continuity/contracts.
It does not create a Runtime, load an actor, teach or evolve any life.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sqlite3

LIFE = 'APD04_SEMILLA_COLABORADOR_R01'
SNAP = '52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc'
PAIR = '0658ca4404f1d676cb9d496f2c1d4f5fbdfee98188a5c717db68e760088f9b2c'
ACTIVO = '5af64dc7211c6d12255dbb172e5f19c34bdda27b487d2d418838a6607f21c819'
MANUAL = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_18_APD04_ECOSISTEMA_SIN_VALIDACION_VISUAL.docx'
FIXED_ACTORS = {
    'sistema/app/protocolo_apd04.py':'f66989c3d9fb6779029d6ba626f4c366633d4f9d97006ae5e42f910dac3f0fe5',
    'sistema/capacidades/ecosistema_apd04.py':'6e829bc1ec7c5920613878718068b5b158d99993cec56fafa7c79e3ba5a31013',
    'sistema/app/usar_dee.py':'a63e4a9fba9b675c9beac7a4fabfc11c852b36aa508d00ba257052f87451e594',
}

def read(p):
    return json.loads(Path(p).read_bytes())

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--root',type=Path,required=True)
    a.add_argument('--manual-report',type=Path,required=True)
    a.add_argument('--closed-experiment-report',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--root-go',choices=['APD04_SELECTED_SOURCE_CLOSED_N0'],required=True)
    p=a.parse_args(); root=p.root.resolve(strict=True); out=p.out.resolve()
    if not out.is_relative_to(root/'entregas') or out.exists():
        raise ValueError('Use a new seal inside the canonical source entregas')
    source=read(root/'sistema/contratos/ENTRADA_SENCILLA_APD03.json')
    assert source['source_life']==LIFE and source['source_alias']=='APD04_ECOSISTEMA'
    assert source['source_snapshot_sha256']==SNAP and source['paired_export_manifest_sha256']==PAIR
    record=read(root/'sistema/estado/vidas'/LIFE/'VIDA.json')
    assert record['physical']['tick']==654959 and record['snapshot_sha256']==SNAP
    assert sha(root/'sistema'/record['snapshot'])==SNAP
    pair=root/source['source_paired_export_manifest']; assert sha(pair)==PAIR
    assert sha(root/'sistema/estado/ACTIVO.json')==ACTIVO
    assert not (root/'sistema/estado/locks'/ (LIFE+'.lock')).exists()
    folder=root/'sistema/estado'/record['persistent_service']['sidecar_directory']
    db=folder/'cola.sqlite3'; wal=folder/'cola.sqlite3-wal'
    assert db.is_file() and (not wal.exists() or wal.stat().st_size==0)
    conn=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        row=conn.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        owner=json.loads(row[0]) if row else {}
        assert owner.get('running') is False
        pending=conn.execute("SELECT id,payload_sha,status FROM requests WHERE status IN ('queued','processing','uncertain')").fetchall()
        assert pending==[]
    finally:
        conn.close()
    mr=read(p.manual_report); manual=root/MANUAL
    assert mr['logical_document_id']=='DCS11-MM-001' and sha(manual)==mr['sha256']
    assert mr['all_previous_chapters_and_appendices_XML_preserved'] is True
    assert mr['unique_current_manual'] is True
    continuity=root/'CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json'
    continuation=read(continuity)
    assert continuation['selected_life']==LIFE and continuation['selected_tick']==654959
    assert continuation['manual']==MANUAL
    assert continuation['protected_default_unchanged'] is True
    # External report must exist and be closed. Its result is never promoted to
    # scientific success just to permit a distribution seal.
    closed=read(p.closed_experiment_report)
    for rel,expected in FIXED_ACTORS.items():
        assert sha(root/rel)==expected, rel
    members=[]
    for folder_name in ('app','capacidades','contratos','organizaciones','documentacion'):
        for path in sorted((root/'sistema'/folder_name).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                members.append({'file':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    proof={
        'schema':'APD04.closed_selected_source_for_distribution.N0.v1',
        'status':'CLOSED_SELECTED_SOURCE_NOT_FULL_PROOF_OR_SCIENTIFIC_PASS',
        'utc':datetime.now(timezone.utc).isoformat(),
        'campaign':'APD04_ECOSISTEMA_COGNITIVO',
        'source_life':LIFE,'source_tick':654959,'source_snapshot_sha256':SNAP,
        'paired_manifest':pair.relative_to(root).as_posix(),'paired_manifest_sha256':PAIR,
        'owner_running':False,'unresolved_transport_ids':pending,
        'native_agenda_scope':'Preserved in the complete pair; not inferred empty from an empty UI transport queue.',
        'selected_pair_not_queried_by_sealing':True,'new_native_ticks':0,
        'protected_ACTIVO_sha256':ACTIVO,'protected_default_unchanged':True,
        'manual':MANUAL,'manual_sha256':sha(manual),'manual_visual_validation':mr['visual_validation'],
        'manual_report':str(p.manual_report),'manual_report_sha256':sha(p.manual_report),
        'closed_experiment_report':str(p.closed_experiment_report),
        'closed_experiment_report_sha256':sha(p.closed_experiment_report),
        'closed_experiment_status':closed.get('status',closed.get('schema')),
        'continuity_sha256':sha(continuity),'source_members':members,
        'Full_exact_archive_verification':'Must follow this source seal and the actual Full ZIP. Not certified here.',
        'scope':'Logistics closure of the selected complete safe seed; later adverse experimental lives remain separate and are not promoted or merged.'
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf8',newline='\n') as f:
        json.dump(proof,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps({'seal':str(out),'sha256':sha(out),'source_members':len(members),'new_native_ticks':0},ensure_ascii=False))

if __name__=='__main__': main()
