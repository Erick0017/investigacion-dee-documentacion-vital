"""Explicit full-pair fork from T639374, preserving the uncertain MAIN future.

Preparation is read-only. Execution delegates to the same existing import API
and UI metadata helper. It loads a complete checkpoint to assign a new world
identity but starts no owner, performs no experience and advances zero ticks.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAP_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
CHILD = 'APD04_CONTINUABLE_R01'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main_status(system):
    folder=system/'estado/servicios_persistentes/APD04_MAIN'
    journal=folder/'cola.sqlite3'
    with sqlite3.connect(journal.as_uri()+'?mode=ro',uri=True)as con:
        con.row_factory=sqlite3.Row
        owner=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        pending=[dict(r)for r in con.execute("SELECT seq,id,status,payload_sha FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
        last=[dict(r)for r in con.execute("SELECT seq,id,status,payload_sha FROM requests WHERE status='completed' ORDER BY seq DESC LIMIT 4")]
    card=read(system/'estado/vidas/APD04_MAIN/VIDA.json')
    markers=[]
    for p in (system/'estado/vidas/APD04_MAIN').glob('FUTURO*'):
        if p.is_file():
            markers.append({'path':str(p),'sha256':sha(p),'content':read(p)})
    return {'record':card,'owner_metadata_read_only':None if owner is None else json.loads(owner['value']),
            'pending':pending,'last_completed':last,'markers':markers,'journal_sha256':sha(journal),
            'scope':'Read-only durable transport and published snapshot only. A previously killed uncommitted Native future is not reconstructed or declared normal continuable.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--prepare-only',action='store_true')
    p.add_argument('--root-go',choices=('APD04_EXPLICIT_FORK_FROM_639374_N0',),required=True)
    a=p.parse_args()
    root=a.root.resolve(strict=True)
    out=a.out.resolve()
    system=root/'sistema'
    pair=system/'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
    manifest=pair/'EXPORTACION_SERVICIO.json'
    if out.exists()or(system/'estado/vidas'/CHILD).exists()or(system/'estado/servicios_persistentes'/CHILD).exists():
        raise FileExistsError('An existing fork/attempt is preserved; never recreate or overwrite it.')
    if sha(manifest)!=PAIR_SHA or sha(pair/'VIDA.deetsnap.gz')!=SNAP_SHA:
        raise ValueError('Declared safe full paired past changed. Do not search for a favorable fallback.')
    parent=read(manifest)
    if parent['life_id']!='APD04_MAIN'or parent['physical']['N']!=67 or parent['physical']['tick']!=639374:
        raise ValueError('Another physical parent.')
    status=main_status(system)
    current=system/'estado/vidas/APD04_MAIN/VIDA.json'
    protected_paths=[system/'estado/ACTIVO.json',current,system/status['record']['snapshot'],
                     system/'estado/servicios_persistentes/APD04_MAIN/cola.sqlite3',manifest,pair/'VIDA.deetsnap.gz']
    for marker in status['markers']:
        protected_paths.append(Path(marker['path']))
    protected={str(path):sha(path)for path in protected_paths}
    out.mkdir(parents=True)
    shutil.copyfile(__file__,out/Path(__file__).name)
    command=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),
             'mente-unificada-importar','--paquete',str(pair),'--vida',CHILD]
    plan={'schema':'APD04.explicit_fork_from_past.zero_tick.plan.v1','life':CHILD,
          'parent_life':'APD04_MAIN','parent_tick':639374,'parent_manifest':str(manifest),
          'parent_manifest_sha256':PAIR_SHA,'parent_snapshot_sha256':SNAP_SHA,
          'preserved_MAIN_latest_published_tick':status['record']['physical']['tick'],
          'fork_is_not_a_repair_or_rewind_of_MAIN':True,'no_future_or_memories_transplanted':True,
          'command':command,'protected':protected,'new_owner_started':False,'new_evolution_ticks':0,
          'deadline_utc':'2026-10-27T03:30:51+00:00','prepare_only':a.prepare_only}
    write(out/'PLAN_FORK_EXPLICITO.json',plan)
    write(out/'ESTADO_MAIN_INCIERTO_ANTES.json',status)
    if a.prepare_only:
        print(json.dumps(plan,ensure_ascii=False))
        return
    if sys.version_info[:2]!=(3,13):
        raise ValueError('Use the existing compatible CPython3.13, no installation or interpreter substitution.')
    pc=load('apd04_full_import_existing_process_control',system/'app/process_control.py')
    def run(label,argv):
        begun=time.monotonic()
        with(out/(label+'.stdout.json')).open('xb')as stdout,(out/(label+'.stderr.txt')).open('xb')as stderr:
            proc,job,name=pc.spawn_owned(argv,cwd=Path(sys.executable).parent,stdout=stdout,stderr=stderr,memory_limit=536870912)
            try:
                proc.wait(timeout=240)
                resources=pc.job_resources(job)
                until=time.monotonic()+5
                while resources.get('job_active_processes')and time.monotonic()<until:
                    time.sleep(.05)
                    resources=pc.job_resources(job)
                if resources.get('job_active_processes'):
                    raise RuntimeError('Import command job still active; no clean result or replacement import.')
            finally:
                pc.close_job(job)
        result={'command':argv,'pid':proc.pid,'job':name,'exit_code':proc.returncode,
                'wall_seconds':time.monotonic()-begun,'resources':resources,'no_native_owner_started':True}
        write(out/(label+'.EJECUCION.json'),result)
        if proc.returncode:
            raise RuntimeError('Existing import/metadata API failed and is preserved; no retry: '+label)
        return result
    runs=[run('IMPORTACION_COMPLETA',command)]
    child=read(system/'estado/vidas'/CHILD/'VIDA.json')
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        if child['physical'][key]!=parent['physical'][key]:
            raise ValueError('Full import changed native physical field: '+key)
    register=Path(__file__).with_name('registrar_importacion_ui_apd04_n0.py')
    register_command=[sys.executable,'-I','-B','-X','utf8',str(register),'--root',str(root),'--vida',CHILD,
        '--snapshot-sha256',child['snapshot_sha256'],'--parent-sha256',SNAP_SHA,
        '--paired-manifest',str(manifest),'--paired-sha256',PAIR_SHA,
        '--salida',str(out/'REGISTRO_UI_N0.json'),'--root-go','APD04_REGISTER_EXISTING_PAIRED_IMPORT_N0']
    runs.append(run('REGISTRO_UI',register_command))
    after={str(path):sha(path)for path in protected_paths}
    if protected!=after:
        raise ValueError('Protected past/MAIN state changed. Preserve evidence; no owner started.')
    final={'schema':'APD04.explicit_complete_fork_from_past.N0.v1','life':CHILD,'record':child,
           'parent_tick':639374,'parent_snapshot_sha256':SNAP_SHA,'parent_pair_sha256':PAIR_SHA,
           'MAIN_uncertain_future_preserved':True,'protected_before':protected,'protected_after':after,
           'runs':runs,'new_native_owner_started':False,'new_evolution_ticks':0,
           'scope':'New explicit branch from the complete T639374 past, not continuation of or repair to the uncertain T658938 MAIN future. Actual snapshot identity remapping is performed only by the existing importer.'}
    write(out/'FORK_COMPLETO_Y_UI_REGISTRADA.json',final)
    print(json.dumps({'life':CHILD,'tick':child['physical']['tick'],'snapshot_sha256':child['snapshot_sha256'],
                     'protected_unchanged':True,'new_owner_started':False,'new_ticks':0},ensure_ascii=False))


if __name__=='__main__':
    main()
