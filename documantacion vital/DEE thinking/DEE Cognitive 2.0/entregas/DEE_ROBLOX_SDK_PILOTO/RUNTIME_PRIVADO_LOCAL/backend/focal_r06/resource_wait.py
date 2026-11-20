"""Finite resource admission only; no adapter, queue, Native or host RAM reader.

memory() is injected and must return a nonnegative integer of free physical
bytes. on_sample receives a diagnostic dict; a successful call returns that
same sample. A high sample never overrides either finite deadline. Callers may
classify these exceptions as pre-Native only when they have not entered the
actual adapter/queue; this module does not classify failures from Native work.
"""
import math
import time

BOOT_FREE_BYTES = 3758096384
PHASE_FREE_BYTES = 1073741824
MAX_RESOURCE_WAIT_SECONDS = 900


class ResourceUnavailableBeforeNative(RuntimeError):
    """Factory-raised only before entering actual.execute / Native admission."""


class ResourceWaitExpired(ResourceUnavailableBeforeNative):
    """Admission expired without executing or admitting Native work."""
    def __init__(self, sample, reason='RESOURCE_WAIT_EXPIRED_BEFORE_NATIVE'):
        self.sample = dict(sample)
        self.reason = reason
        super().__init__(reason)


def _finite_seconds(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(name + ' must be finite seconds')
    return float(value)


def wait_for_resource(required, *, deadline_utc, memory, on_sample=lambda sample: None,
                      clock=time.time, sleep=time.sleep, poll_seconds=1.0):
    """Sample immediately, then wait at most min(deadline UTC, start + 900 s).

    No callables for execution/adapters are accepted. Clock regression fails
    closed. Requested sleeps also have a 900-second cumulative budget, so a
    frozen injected wall clock cannot create an unbounded wait. Sleep is never
    requested past the remaining deadline/budget. Deadline checking follows
    sampling AND callback, before the free-RAM result can authorize admission.
    """
    if type(required) is not int or required not in (BOOT_FREE_BYTES, PHASE_FREE_BYTES):
        raise ValueError('Only the fixed BOOT/PHASE physical RAM guards are allowed')
    if not all(callable(value) for value in (memory, on_sample, clock, sleep)):
        raise TypeError('memory, on_sample, clock and sleep must be callable')
    deadline_utc = _finite_seconds(deadline_utc, 'deadline_utc')
    poll_seconds = _finite_seconds(poll_seconds, 'poll_seconds')
    if poll_seconds <= 0:
        raise ValueError('poll_seconds must be positive')
    started = _finite_seconds(clock(), 'clock')
    deadline = min(deadline_utc, started + MAX_RESOURCE_WAIT_SECONDS)
    previous = started
    slept = 0.0
    last = {'required': required, 'free': None, 'sampleUtc': started, 'startedUtc': started,
            'deadlineUtc': deadline, 'elapsedSeconds': 0.0,
            'remainingSeconds': max(0.0, deadline - started)}

    def now():
        nonlocal previous
        value = _finite_seconds(clock(), 'clock')
        if value < previous:
            raise ResourceWaitExpired(last, 'RESOURCE_CLOCK_REGRESSED_BEFORE_NATIVE')
        previous = value
        return value

    while True:
        free = memory()
        if type(free) is not int or free < 0:
            raise ValueError('memory() must return nonnegative integer physical bytes')
        sampled = now()
        remaining = max(0.0, min(deadline - sampled, MAX_RESOURCE_WAIT_SECONDS - slept))
        last = {'required': required, 'free': free, 'sampleUtc': sampled, 'startedUtc': started,
                'deadlineUtc': deadline, 'elapsedSeconds': max(sampled - started, slept),
                'remainingSeconds': remaining}
        # Give diagnostics a copy: callback mutations cannot change admission.
        on_sample(dict(last))
        checked = now()
        remaining = min(deadline - checked, MAX_RESOURCE_WAIT_SECONDS - slept)
        if remaining <= 0:
            raise ResourceWaitExpired(last)
        if free >= required:
            return last
        delay = min(poll_seconds, remaining)
        if delay <= 0 or slept + delay == slept:
            raise ResourceWaitExpired(last, 'RESOURCE_WAIT_CANNOT_PROGRESS_BEFORE_NATIVE')
        sleep(delay)
        slept += delay
