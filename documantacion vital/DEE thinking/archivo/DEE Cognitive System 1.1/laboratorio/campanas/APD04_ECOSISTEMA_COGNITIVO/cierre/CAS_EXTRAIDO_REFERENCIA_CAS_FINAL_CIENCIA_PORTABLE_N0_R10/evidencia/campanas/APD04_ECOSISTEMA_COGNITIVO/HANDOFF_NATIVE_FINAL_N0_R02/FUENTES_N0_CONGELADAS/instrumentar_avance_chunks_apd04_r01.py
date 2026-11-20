"""Prospective owner-level progress instrument. No Runtime, field or policy edits.

Equivalence to a single owner call is NOT assumed. Admit only after the declared
paired exact-state/agenda/receipt/control test. This is an investigator tool.
"""
from contextlib import contextmanager
from pathlib import Path
import json
import operator
import time

VERSION = 'APD04.owner_run_until_progress_chunks67.prospective.R01'
_MISSING = object()


@contextmanager
def owner_progress_chunks(adapter, path, *, chunk=67):
    if type(chunk) is not int or chunk != 67:
        raise ValueError('One prospectively fixed67tick chunk size only')
    if not hasattr(adapter, '__dict__') or type(adapter).__name__ != 'WorldAdapter':
        raise TypeError('Only the existing Python WorldAdapter owner contract is proposed')
    original = adapter.run_until
    previous_local = vars(adapter).get('run_until', _MISSING)
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Open this auditor-only stream outside the actor's ordinary file fence.
    stream = target_path.open('x', encoding='utf8', buffering=1)
    serial = 0

    def emit(kind, **fields):
        stream.write(json.dumps({'instrument_version': VERSION, 'kind': kind,
            'wall_monotonic_ns': time.monotonic_ns(), 'process_CPU_ns': time.process_time_ns(),
            **fields}, separators=(',', ':')) + '\n')

    def wrapped(target):
        nonlocal serial
        tick_target = operator.index(target)
        serial += 1
        call = serial
        initial = int(adapter.tick)
        emit('owner_call_begin', call=call, initial_tick=initial, target_tick=tick_target)
        if tick_target <= initial:
            # Preserve the original same-tick and past-target behavior once.
            result = original(target)
            emit('owner_call_end', call=call, actual_tick=int(adapter.tick), target_tick=tick_target, chunks=1)
            return result
        completed, result = 0, None
        while int(adapter.tick) < tick_target:
            before = int(adapter.tick)
            next_tick = min(tick_target, before + chunk)
            result = original(next_tick)  # The SAME OrganizationalWorld owner.
            completed += 1
            after = int(adapter.tick)
            emit('owner_chunk_end', call=call, before_tick=before, actual_tick=after,
                 requested_chunk_target=next_tick, target_tick=tick_target, chunks=completed)
            if after <= before:
                raise RuntimeError('The original future-target owner call did not advance; no Runtime fallback')
        emit('owner_call_end', call=call, actual_tick=int(adapter.tick), target_tick=tick_target, chunks=completed)
        return result

    try:
        adapter.run_until = wrapped
        emit('instrument_installed', actual_tick=int(adapter.tick), chunk=chunk,
             no_Runtime_run=True, no_field_or_agenda_edits=True)
        yield
    finally:
        if previous_local is _MISSING:
            del adapter.run_until
        else:
            adapter.run_until = previous_local
        emit('instrument_removed', actual_tick=int(adapter.tick), original_method_restored=True)
        stream.close()
