"""Root-only C02 source installation into a closed diagnostic clone.
No Native import, owner opening, request, snapshot write or replay occurs here.
"""
from pathlib import Path
import argparse, hashlib, json, os, sqlite3

ROOT=Path(__file__).resolve().parents[1]
FILES=('cache_fuentes_C02.py','servicio_eventos_C02.py')
CUTOFF=1794738600

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def regular(path):
    for p in (path,*path.parents):
        if p.is_symlink() or (p.exists() and getattr(p.lstat(),'st_file_attributes',0)&1024):
            raise ValueError('No linked/reparse C02 paths')

def install(destination,*,source_cache=True):
    original_destination=Path(destination).absolute()
    regular(original_destination)
    destination=original_destination.resolve(strict=True)
    if not destination.is_relative_to(ROOT)or destination==ROOT:
        raise ValueError('New C02 clone only')
    regular(destination)
    context=json.loads((destination/'CONTEXTO_EJECUCION.json').read_text('utf8'))
    imported=json.loads((destination/'IMPORTACION_DIAGNOSTICA.json').read_text('utf8'))
    system=(destination/'sistema').resolve(strict=True);life=context['life']
    if (Path(context['system']).resolve()!=system or imported['new_native_ticks']!=0
            or not imported['comparison']['physical_equal']
            or not imported['comparison']['causal_prefix_equal']):
        raise ValueError('Closed official full import0 equality required first')
    card_path=system/'estado/vidas'/life/'VIDA.json';card=json.loads(card_path.read_text('utf8'))
    database=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    if any((system/'estado/locks').glob('*.lock')):
        raise RuntimeError('Owner lock present; never install into a running world')
    if any(Path(str(database)+s).exists()and Path(str(database)+s).stat().st_size for s in('-wal','-journal')):
        raise RuntimeError('Open transport sidecar; preserve')
    con=sqlite3.connect(database.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        if not row or json.loads(row[0]).get('running')is not False:
            raise RuntimeError('Closed paired owner status required')
        if con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:
            raise RuntimeError('Outstanding request; preserve without installing')
    finally:con.close()
    paths=[card_path,system/card['snapshot'],database]
    before={str(p):sha(p)for p in paths}
    targets=[system/'app'/name for name in(*FILES,'HOST_C02.json')]
    if any(p.exists()for p in targets):
        raise FileExistsError('Prior C02 host source/scope exists; preserve exact evidence')
    for name in FILES:
        source=ROOT/'fuentes'/name
        with(system/'app'/name).open('xb')as out:
            out.write(source.read_bytes());out.flush();os.fsync(out.fileno())
    scope={'schema':'DEE.RBX01.C02.host_scope.v1','sealed':True,'system':str(system),'life':life,
           'native_cutoff_utc_epoch':CUTOFF,'event_driven':True,'single_initial_resume':True,
           'immutable_source_cache':bool(source_cache),'operational_state_cached':False,
           'host_sources_sha256':{name:sha(system/'app'/name)for name in FILES},
           'inherited_sources_sha256':{name:sha(system/'app'/name)
                for name in('servicio_persistente.py','mundo_genesis_apd05.py','lives.py','cola_local.py')},
           'scope':'Host scheduling/locked source bytes only. Original execute, validate, perform, checkpoint, agenda, receipts and queue finish remain authoritative.'}
    with(system/'app/HOST_C02.json').open('x',encoding='utf8')as out:
        json.dump(scope,out,ensure_ascii=False,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    after={str(p):sha(p)for p in paths}
    if before!=after:raise RuntimeError('Operational bytes changed; preserve and block owner')
    return{'installed':FILES,'scope_sha256':sha(system/'app/HOST_C02.json'),
           'operational_bytes_unchanged':True,'critical_before':before,'critical_after':after,
           'new_native_ticks':0,'new_world_created':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-install',action='store_true',required=True)
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--no-source-cache',action='store_true')
    a=p.parse_args();print(json.dumps(install(a.destination,source_cache=not a.no_source_cache),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
