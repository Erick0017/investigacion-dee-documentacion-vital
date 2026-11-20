"""Explicit C02 host entrypoint: official queue/perform/checkpoints, no idle ticks.

Root installs this file and cache_fuentes_C02.py inside an C02 clone's app.
Importing this module imports no DEE/Native code. Native opens only in main().
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time


def bounded_host_seconds(requested, cutoff, now=None):
    """Prospective host lifetime clipped at actual child/service start."""
    if type(requested) not in (int, float) or not 0 < requested <= 28800:
        raise ValueError('Finite positive C02 host lifetime required')
    remaining = float(cutoff) - (time.time() if now is None else float(now))
    if remaining <= 0:
        raise ValueError('Native cutoff reached before service start')
    return min(float(requested), remaining)


def event_driven_class(original):
    class EventDrivenService(original):
        def protocol(self, receipt=None):
            value = super().protocol(receipt)
            value['C02_host_event_driven'] = True
            value['wall_cadence_not_native_policy'] = 'No idle quanta; only admitted material operations evolve through the official agenda.'
            return value

        def status(self):
            return {**super().status(), 'C02_host_event_driven': True,
                    'C02_no_idle_native_advance': True}

        def run(self):
            # Original ordering, admission/uncertainty gates and safe boundaries.
            # Only the idle world.advance + idle_total increment branch is absent.
            self.restore_transport(); self.publish()
            try:
                while not self.stop:
                    t = time.monotonic()
                    if self.max_seconds is not None and t - self.started >= self.max_seconds:
                        self.stop = True; break
                    row = self.queue.next(paused=self.paused or self.uncertain)
                    if row:
                        self.perform(row); continue
                    if time.monotonic() - self.last_save >= self.save_seconds:
                        self.checkpoint({'kind': 'PERSISTENT_PERIODIC_IDLE_SAVE', 'idle_ticks': self.idle_total})
                    if time.monotonic() - self.last_publish >= .5:
                        self.publish()
                    time.sleep(min(.05, self.idle_seconds))
            except KeyboardInterrupt:
                self.stop = True
            finally:
                self.stop = True
                try:
                    self.checkpoint({'kind': 'PERSISTENT_GRACEFUL_CLOSE', 'idle_ticks': self.idle_total})
                    self.publish()
                finally:
                    self.world.close()
            return self.status()
    return EventDrivenService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system-root', type=Path, required=True)
    parser.add_argument('--vida', required=True)
    parser.add_argument('--scope-sha256', required=True)
    parser.add_argument('--intervalo', type=float, default=60)
    parser.add_argument('--guardar-cada', type=float, default=3600)
    parser.add_argument('--max-segundos', type=float, required=True)
    args = parser.parse_args()
    system = args.system_root.resolve(strict=True)
    here = Path(__file__).resolve()
    if here.parent != system / 'app':
        raise ValueError('C02 host entrypoint must be installed inside its exact clone/app')
    scope_path = system / 'app/HOST_INTEGRAL_V3.json'
    data = scope_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != args.scope_sha256:
        raise ValueError('Root-sealed C02 host scope changed')
    scope = json.loads(data)
    if (scope.get('schema') != 'DEE.RBX01.INTEGRAL.V3.host_scope.v1'
            or scope.get('life') != args.vida or scope.get('system') != '.'
            or scope.get('sealed') is not True
            or scope.get('event_driven') is not True
            or scope.get('single_initial_resume') is not True
            or time.time() >= scope['native_cutoff_utc_epoch']
            or not 0 < args.max_segundos <= 28800):
        raise ValueError('Finite exact C02 clone/host scope required')
    for name, expected in scope['host_sources_sha256'].items():
        if Path(name).name != name or hashlib.sha256((system / 'app' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned C02 host source changed')
    for name, expected in scope['inherited_sources_sha256'].items():
        if Path(name).name != name or hashlib.sha256((system / 'app' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Inherited service source changed')
    sys.path.insert(0, str(system))
    sys.path.insert(0, str(system / 'app'))
    from cache_fuentes_C02 import ImmutableSourceCache
    cache = ImmutableSourceCache(system).open() if scope.get('immutable_source_cache') is True else None
    world = None
    try:
        from app.servicio_persistente import PersistentService
        from app.mundo_genesis_apd05 import GenesisNativeWorld
        from app.cola_local import QueueDB
        class TimedWorld(GenesisNativeWorld):
            def _open_locked(self):
                original_commit = self.store.commit
                def commit(*pos, **kw):
                    started = time.monotonic()
                    try:
                        return original_commit(*pos, **kw)
                    finally:
                        self._r04_commit_seconds = time.monotonic() - started
                self.store.commit = commit
                return super()._open_locked()
            def operational_dependencies(self):
                started = time.monotonic()
                try:
                    return super().operational_dependencies()
                finally:
                    self._r04_dependencies_seconds = time.monotonic() - started
            def checkpoint(self, protocol, pending, operation):
                started = time.monotonic()
                result = super().checkpoint(protocol, pending, operation)
                value = {'kind': 'C02_HOST_CHECKPOINT_TIMING', 'operation': operation,
                         'host_utc_epoch': time.time(), 'native_tick_cached': self.tick,
                         'total_seconds': time.monotonic() - started,
                         'store_commit_seconds': self._r04_commit_seconds,
                         'operational_dependencies_seconds': self._r04_dependencies_seconds,
                         'source_cache_hits': 0 if cache is None else cache.hits}
                with (self.folder / 'INTEGRAL_V3_HOST_TIMINGS.jsonl').open('a', encoding='utf8') as out:
                    out.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + '\n')
                return result
        world = TimedWorld(system, args.vida, 'mente_unificada').open()
        if cache:
            (world.folder / 'INTEGRAL_V3_SOURCE_CACHE_ABIERTO.json').write_text(
                json.dumps(cache.witness(), ensure_ascii=False, indent=2), encoding='utf8')
        queue = QueueDB(world.folder / 'cola.sqlite3')
        value = event_driven_class(PersistentService)(world, queue, idle_seconds=args.intervalo,
                  save_seconds=args.guardar_cada, max_seconds=bounded_host_seconds(
                      args.max_segundos, scope['native_cutoff_utc_epoch']), start_paused=True).run()
        print(json.dumps(value, ensure_ascii=False), flush=True)
    finally:
        if world:
            world.close()
        if cache:
            witness = cache.witness()
            cache.close()
            if world:
                witness['fresh_close_hashes_equal'] = True
                (world.folder / 'INTEGRAL_V3_SOURCE_CACHE_CERRADO.json').write_text(
                    json.dumps(witness, ensure_ascii=False, indent=2), encoding='utf8')


if __name__ == '__main__':
    main()
