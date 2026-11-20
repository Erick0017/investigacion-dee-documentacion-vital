"""Optional supervised owner advancement, never a decision or physics layer.

Time bounds may end an operation, not select responses or input schedules.
Store.mutate preserves the actually reached complete state after exceptions.
"""
import time

def run_bounded(adapter,callback,seconds=None):
    if seconds is None:return callback(adapter)
    if type(seconds)is not int or not 5<=seconds<=240:raise ValueError('Explicit operation wall bound must be an integer5..240seconds')
    original=adapter.run_until;deadline=time.perf_counter()+seconds
    def advance(target):
        while adapter.tick<target:
            if time.perf_counter()>deadline:raise TimeoutError('OPERATION_WALL_BOUND: preserve reached state and pending protocol; no rollback or implicit retry')
            original(min(target,adapter.tick+4))
    adapter.run_until=advance
    try:return callback(adapter)
    finally:adapter.run_until=original
