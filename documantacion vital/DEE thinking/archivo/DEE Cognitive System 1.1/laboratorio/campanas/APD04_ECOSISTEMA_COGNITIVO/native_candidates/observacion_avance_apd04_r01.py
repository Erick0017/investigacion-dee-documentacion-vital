"""Prospective bounded-call progress observer, not a Runtime or decision layer.

Every subcall uses the original Adapter.run_until / OrganizationalWorld owner.
No target is skipped and no input, clock, support or learned field is edited.
Equivalence must be tested before adoption: a finite call decomposition is not
assumed to be physically/protocol-equivalent merely because its target agrees.
The writer is never read by an actor. No snapshot or answer is loaded here.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time


VERSION = 'APD04.passive_bounded_owner_call_progress.prospective.R01'


@contextmanager
def record_progress(adapter, destination, *, quantum=67):
    if type(quantum) is not int or not 1 <= quantum <= 67:
        raise ValueError('A fixed exact1..67 tick observation quantum is required')
    if getattr(adapter, '_apd04_progress_active', False):
        raise ValueError('Nested observer prohibited; retain one original owner')
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    original = adapter.run_until
    had_override = 'run_until' in vars(adapter)
    previous_override = vars(adapter).get('run_until')
    adapter._apd04_progress_active = True
    sequence = 0

    def append(kind, **fields):
        nonlocal sequence
        row = {'version': VERSION, 'seq': sequence, 'kind': kind,
            'wall_utc': datetime.now(timezone.utc).isoformat(),
            'monotonic_ns': time.monotonic_ns(),
            'process_cpu_ns': time.process_time_ns(), **fields}
        with path.open('a', encoding='utf8', newline='\n') as stream:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':'))+'\n')
            stream.flush()
        sequence += 1

    def observed(target):
        before = int(adapter.tick)
        if type(target) is not int or target <= before:
            # Preserve original validation and equal-target call behavior.
            return original(target)
        append('call_begin', before_tick=before, target_tick=target, quantum=quantum)
        result = None
        while int(adapter.tick) < target:
            start = int(adapter.tick)
            endpoint = min(target, start+quantum)
            append('subcall_begin', before_tick=start, endpoint_tick=endpoint,
                original_target_tick=target)
            result = original(endpoint)
            after = int(adapter.tick)
            append('subcall_return', before_tick=start, after_tick=after,
                endpoint_tick=endpoint, original_target_tick=target)
            if after != endpoint:
                raise RuntimeError('Owner did not reach the requested exact endpoint; preserve actual future')
        append('call_return', before_tick=before, after_tick=int(adapter.tick), target_tick=target)
        return result

    adapter.run_until = observed
    try:
        append('observer_enter', tick=int(adapter.tick), quantum=quantum,
            does_not_choose_or_read_an_answer=True, does_not_use_Runtime_run=True)
        yield
    finally:
        if had_override:
            adapter.run_until = previous_override
        else:
            del adapter.run_until
        del adapter._apd04_progress_active
        append('observer_leave', tick=int(adapter.tick), method_override_restored=True)
