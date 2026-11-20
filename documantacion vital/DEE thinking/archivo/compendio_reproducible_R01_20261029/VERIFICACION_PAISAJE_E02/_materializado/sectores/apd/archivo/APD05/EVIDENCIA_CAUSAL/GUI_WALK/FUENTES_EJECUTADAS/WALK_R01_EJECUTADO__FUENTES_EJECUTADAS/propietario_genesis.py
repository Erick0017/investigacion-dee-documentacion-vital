"""GENESIS owner adapter: existing NativeWorld + PersistentService, one Runtime.

Only the passive publication hook is extended. No actor code or physics changes.
No HTTP socket exists in this process. The web process reads immutable frames.
"""
from pathlib import Path
import argparse
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'sistema'), str(ROOT / 'sistema/app'), str(HERE)]
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
from app.servicio_persistente import NativeWorld, PersistentService
from app.cola_local import QueueDB
from visor_pasivo import make_frame


class ViewerService(PersistentService):
    def __init__(self, *args, viewer=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_enabled = viewer
        self.view_last = 0.0
        self.view_previous = None
        self.view_home = self.world.folder / 'genesis_observador'
        self.view_home.mkdir(parents=True, exist_ok=True)
        self.view_error = None

    def publish(self):
        status = super().publish()
        config_file = self.view_home / 'CONFIGURACION.json'
        config = json.loads(config_file.read_text(encoding='utf8')) if config_file.is_file() else {}
        enabled = self.view_enabled and config.get('enabled', True)
        interval = max(.5, min(60.0, float(config.get('interval_seconds', 2))))
        if enabled and time.monotonic() - self.view_last >= interval:
            try:
                frame, self.view_previous = make_frame(self.world, self.queue, config, self.view_previous)
                self.world.atomic_json(self.view_home / 'FOTOGRAMA.json', frame)
                self.view_error = None
            except Exception as error:
                # A viewer failure must not masquerade as a physical failure or
                # alter the agenda. The last coherent frame remains available.
                self.view_error = {'type': type(error).__name__, 'detail': str(error)}
            self.view_last = time.monotonic()
        self.queue.meta('genesis_observer', {'enabled': enabled, 'error': self.view_error,
            'interval_seconds': interval, 'scope': 'External prepared instrument, not acquired actor capability.'})
        return status


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--vida', required=True)
    p.add_argument('--pausado', action='store_true')
    p.add_argument('--sin-visor', action='store_true')
    p.add_argument('--intervalo', type=float, default=.1)
    p.add_argument('--guardar-cada', type=float, default=15)
    p.add_argument('--max-segundos', type=float, default=7200)
    a = p.parse_args()
    world = NativeWorld(ROOT / 'sistema', a.vida, 'mente_unificada').open()
    try:
        queue = QueueDB(world.folder / 'cola.sqlite3')
        service = ViewerService(world, queue, idle_seconds=a.intervalo, save_seconds=a.guardar_cada,
            max_seconds=a.max_segundos, start_paused=a.pausado, viewer=not a.sin_visor)
        print(json.dumps(service.run(), ensure_ascii=False), flush=True)
    finally:
        world.close()


if __name__ == '__main__':
    main()
