"""Explicit full-state plus local transport import; never creates an empty world."""
import hashlib,json,shutil,sqlite3
from pathlib import Path,PurePosixPath


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_export(directory):
    root=Path(directory).resolve(strict=True);index=root/'EXPORTACION_SERVICIO.json'
    m=json.loads(index.read_bytes())
    if m.get('schema')!='DEE.persistent_service.paired_export.v1'or m.get('backend')not in('ma02','mente_unificada')or m.get('queue_journal_required')is not True:
        raise ValueError('Unrecognized full paired-service export; no recipe fallback.')
    expected=set();total=0
    for item in m['members']:
        name=item['file'];relative=PurePosixPath(name)
        if not isinstance(name,str)or '\\'in name or ':'in name or relative.is_absolute()or any(p in('..','.')for p in relative.parts):raise ValueError('Unsafe exported member path')
        if name in expected:raise ValueError('Repeated export member')
        p=(root/relative).resolve(strict=True)
        if not p.is_relative_to(root)or not p.is_file()or p.is_symlink():raise ValueError('Exported file outside declared package')
        if p.stat().st_size!=item['bytes']or sha(p)!=item['sha256']:raise ValueError('Export member size/hash mismatch: '+name)
        expected.add(name);total+=item['bytes']
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p!=index}
    if actual!=expected:raise ValueError('Export has missing or unindexed files')
    if not{'VIDA.deetsnap.gz','cola.sqlite3'}<=expected or m['native_snapshot']!='VIDA.deetsnap.gz' or sha(root/'VIDA.deetsnap.gz')!=m['snapshot_sha256']:
        raise ValueError('Complete native state and matching queue are mandatory')
    # Read-only SQLite check: no owner, actor, physics or answer calculation.
    # The manifest already requires a standalone closed export, never a live
    # writer/WAL. Immutable read-only validation must not create new -shm/-wal
    # members and invalidate the same package on its next explicit import.
    con=sqlite3.connect((root/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Corrupt operational transport journal')
        rows=con.execute("SELECT id,payload,payload_sha,status FROM requests").fetchall()
        for identifier,payload,recorded,status in rows:
            canonical=json.dumps(json.loads(payload),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
            if hashlib.sha256(canonical.encode('utf8')).hexdigest()!=recorded:raise ValueError('Transport payload identity mismatch')
            if status not in('queued','processing','completed','uncertain','failed_preserved','rejected_invalid'):raise ValueError('Unknown transport status')
    finally:con.close()
    return root,m,{'manifest_sha256':sha(index),'members_verified':len(expected),'bytes_verified':total,'requests_preserved':len(rows),'new_ticks':0}


def import_pair(store,directory,life):
    # All portable bytes are checked before loading one native world.
    source,m,verification=verify_export(directory)
    from app.lives import validate_id
    from app.native_tools import atomic_json
    validate_id(life)
    if store.life_dir(life).exists():raise FileExistsError('Import requires an explicit unused life identity; existing lives are never replaced.')
    folder=store.state/'servicios_persistentes'/life
    if folder.exists():raise FileExistsError('Existing transport identity is protected.')
    folder.mkdir(parents=True)
    marker=folder/'IMPORTACION_EN_CURSO.json'
    mapping={'schema':'DEE.persistent_service.explicit_import.v1','source_life_id':m['life_id'],'new_life_id':life,
        'source_snapshot_sha256':m['snapshot_sha256'],'source_world_id':m.get('source_record',{}).get('world_id'),
        'new_world_id':life,'inherited_transport_ids_preserved':True,'no_reexecution_of_archived_actions':True,
        'identity_scope':'Explicit imported continuation in a new world identity, not evolution of the protected original and not new T0 acquisition.',
        'verification':verification}
    atomic_json(marker,mapping)
    try:
        for row in m['members']:
            name=row['file']
            if name=='VIDA.deetsnap.gz':continue
            if name.startswith('artefactos_trabajador/'):
                target=store.state/'servicios_locales'/life/Path(name).relative_to('artefactos_trabajador')
            else:target=folder/name
            target.parent.mkdir(parents=True,exist_ok=True)
            with(source/name).open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
        try:from .estructuras_externas_pi03 import restore_known_device_directories
        except ImportError:from estructuras_externas_pi03 import restore_known_device_directories
        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)
        atomic_json(marker,mapping)
        record=store.import_state(source/'VIDA.deetsnap.gz',life,m['profile'],expected=m['snapshot_sha256'])
        for key in('N','tick','RAW_sha256','clocks_sha256'):
            if record['physical'][key]!=m['physical'][key]:raise ValueError('Import altered native physical field: '+key)
        try:from .cola_local import QueueDB
        except ImportError:from cola_local import QueueDB
        queue=QueueDB(folder/'cola.sqlite3')
        queue.meta('imported_identity_mapping',mapping)
        queue.meta('owner',{'schema':'DEE.local.persistent.status.v1','life_id':life,'running':False,
            'tick':record['physical']['tick'],'imported_not_yet_started':True,'not_instantaneous':True,
            'scope':'Imported complete world and journal. No service auto-start, no retry of uncertain jobs. Start explicitly to reconcile the last committed receipt.'})
        atomic_json(folder/'IMPORTACION.json',{**mapping,'imported_snapshot_sha256':record['snapshot_sha256'],'physical':record['physical']})
        marker.unlink()
        return {'life_id':life,'profile':record['profile'],'backend':m['backend'],'snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],
            'verification':verification,'transport_directory':str(folder),'identity':mapping,'service_started':False}
    except BaseException as error:
        atomic_json(marker,{**mapping,'error':{'type':type(error).__name__,'detail':str(error)},'partial_import_preserved':True,'no_automatic_retry':True})
        if store.life_dir(life).exists():atomic_json(store.life_dir(life)/'FUTURO_INTERRUMPIDO.json',{'kind':'INCOMPLETE_PAIRED_IMPORT','marker':str(marker),'no_implicit_continuation':True})
        raise
