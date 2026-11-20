"""One real owner, original paired import, fixed protocol, no wall idle loop."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = ROOT / 'sistema'
sys.path[:0] = [str(S), str(S / 'app'), str(HERE.parent)]
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[name] = '1'
from app.process_control import protect_current, current_resources
from app.lives import Store
from app.importacion_emparejada import import_pair
from app.servicio_persistente import NativeWorld
from app.cola_local import QueueDB
from propietario_genesis import ViewerService


def main():
    p = argparse.ArgumentParser(); p.add_argument('--condition', choices=['ON','OFF'], required=True)
    a = p.parse_args()
    protect_current(memory_limit=536870912)
    plan_path = HERE / 'PLAN_OBSERVADOR_ON_OFF_R01.json'
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    life = 'APD05_GUI_OBS_' + a.condition + '_R01'
    manifest = ROOT / plan['paired_manifest']
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != plan['paired_manifest_sha256']:
        raise ValueError('Parent paired manifest changed.')
    store = Store(S)
    if store.life_dir(life).exists(): raise FileExistsError('Existing diagnostic life is never silently reused.')
    code = {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in
        [Path(__file__), plan_path, HERE.parent/'visor_pasivo.py', HERE.parent/'propietario_genesis.py', S/'app/cola_local.py', S/'app/servicio_persistente.py']}
    begun = time.perf_counter(); initial_cost = current_resources()
    imported = import_pair(store, manifest.parent, life)
    import_seconds = time.perf_counter() - begun
    world = NativeWorld(S, life, 'mente_unificada').open()
    try:
        q = QueueDB(world.folder / 'cola.sqlite3')
        q.meta('genesis_view_config', {'enabled':a.condition=='ON','interval_seconds':.5,'max_points':12000})
        service = ViewerService(world,q,start_paused=True,viewer=a.condition=='ON',max_seconds=600)
        service.restore_transport()
        if q.outstanding(): raise ValueError('Original pair retained an unexpected input after legitimate receipt reconciliation; no deletion.')
        initial = world.fingerprint()
        service.publish()
        rows = []
        for operation in plan['operations_in_both']:
            admitted = q.put(operation['id'],operation['payload'])
            if admitted['admission'] != 'queued': raise RuntimeError('No repeat or overwrite of an existing protocol ID.')
            request = q.next(paused=service.paused)
            if request is None or request['id'] != operation['id']: raise RuntimeError('Safe protocol precedence differs; preserve instead of bypassing.')
            start = time.perf_counter()
            service.perform(request)
            result = q.get(operation['id'])
            rows.append({'operation':operation,'admission':admitted,'result':result,'wall_seconds':time.perf_counter()-start})
            if result['status'] != 'completed': raise RuntimeError('Native result preserved, no alternative reader or retry.')
        closed = service.checkpoint({'kind':'GENESIS_FIXED_PROTOCOL_GRACEFUL_CLOSE','no_idle_wall_loop':True})
        service.publish()
        report = {'schema':'GENESIS.real_passive_observer_fixed_protocol.R01','life_id':life,'condition':a.condition,
            'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'executed_sources':code,
            'import':imported,'import_wall_seconds':import_seconds,'initial_physical':initial,'final_physical':world.fingerprint(),
            'final_snapshot':closed,'rows':rows,'viewer':q.get_meta('genesis_observer'),
            'wall_seconds':time.perf_counter()-begun,'resources_at_start':initial_cost,'resources_final':current_resources(),
            'energy':'NO MEDIDA','no_idle_wall_loop':True,'one_runtime_load':True,'not_a_GUI_or_external_wall_time_benchmark':True}
        world.atomic_json(world.folder/'OBSERVADOR_FIJO_RESULTADO_R01.json',report)
        print(json.dumps({'life_id':life,'report':str(world.folder/'OBSERVADOR_FIJO_RESULTADO_R01.json'),
            'final_physical':report['final_physical'],'viewer':report['viewer']},ensure_ascii=False),flush=True)
    finally: world.close()


if __name__ == '__main__': main()
