"""Pure admission fixtures: injected memory, clock and sleep; no host resources."""
from pathlib import Path
import importlib.util
import math
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SOURCE = Path(__file__).with_name('resource_wait.py')
SPEC = importlib.util.spec_from_file_location('_sdk_r06_resource_fixture', SOURCE)
resource = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = resource
SPEC.loader.exec_module(resource)


class ControlledClock:
    def __init__(self, now=1000.0, *, frozen=False):
        self.now = float(now)
        self.frozen = frozen
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        if not math.isfinite(seconds) or seconds <= 0:
            raise AssertionError('Invalid simulated sleep')
        self.sleeps.append(float(seconds))
        if len(self.sleeps) > 64:
            raise AssertionError('Unbounded resource wait in controlled fixture')
        if not self.frozen:
            self.now += seconds


class MemorySequence:
    def __init__(self, *values):
        self.values = values
        self.calls = 0

    def __call__(self):
        index = min(self.calls, len(self.values) - 1)
        self.calls += 1
        return self.values[index]


class ResourceWaitFixtures(unittest.TestCase):
    def setUp(self):
        self.time = ControlledClock()
        self.samples = []

    def wait(self, memory, **overrides):
        # Every call overrides production time/sleep/memory, including bad-input tests.
        kwargs = {'required': resource.PHASE_FREE_BYTES,
                  'deadline_utc': self.time.now + 30, 'memory': memory,
                  'on_sample': self.samples.append, 'clock': self.time.clock,
                  'sleep': self.time.sleep, 'poll_seconds': 1.0}
        kwargs.update(overrides)
        return resource.wait_for_resource(**kwargs)

    def test_constants_and_exception_hierarchy(self):
        self.assertEqual(resource.BOOT_FREE_BYTES, 3758096384)
        self.assertEqual(resource.PHASE_FREE_BYTES, 1073741824)
        self.assertEqual(resource.MAX_RESOURCE_WAIT_SECONDS, 900)
        self.assertTrue(issubclass(resource.ResourceUnavailableBeforeNative, RuntimeError))
        self.assertTrue(issubclass(resource.ResourceWaitExpired, resource.ResourceUnavailableBeforeNative))

    def test_immediate_threshold_admission_has_exact_sample_fields(self):
        expected_fields = {'required', 'free', 'sampleUtc', 'startedUtc', 'deadlineUtc',
                           'elapsedSeconds', 'remainingSeconds'}
        for required in (resource.BOOT_FREE_BYTES, resource.PHASE_FREE_BYTES):
            self.time = ControlledClock(); self.samples = []
            memory = MemorySequence(required)
            sample = self.wait(memory, required=required, deadline_utc=1010.0)
            with self.subTest(required=required):
                self.assertEqual(set(sample), expected_fields)
                self.assertEqual(sample, {'required': required, 'free': required,
                                         'sampleUtc': 1000.0, 'startedUtc': 1000.0,
                                         'deadlineUtc': 1010.0, 'elapsedSeconds': 0.0,
                                         'remainingSeconds': 10.0})
                self.assertEqual(memory.calls, 1)
                self.assertEqual(self.time.sleeps, [])
                self.assertEqual(self.samples, [sample])
                self.assertIsNot(self.samples[0], sample)

    def test_low_memory_then_free_admits_only_after_recovery(self):
        required = resource.PHASE_FREE_BYTES
        memory = MemorySequence(required - 1, required - 10, required)
        result = self.wait(memory, deadline_utc=1020.0, poll_seconds=3.5)
        self.assertEqual(memory.calls, 3)
        self.assertEqual(self.time.sleeps, [3.5, 3.5])
        self.assertEqual([row['free'] for row in self.samples], [required - 1, required - 10, required])
        self.assertEqual(result['sampleUtc'], 1007.0)
        self.assertEqual(result['elapsedSeconds'], 7.0)
        self.assertEqual(result['remainingSeconds'], 13.0)

    def test_expired_high_memory_still_samples_and_never_admits(self):
        memory = MemorySequence(resource.PHASE_FREE_BYTES)
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=999.0)
        self.assertEqual(memory.calls, 1)
        self.assertEqual(len(self.samples), 1)
        self.assertEqual(self.time.sleeps, [])
        self.assertEqual(caught.exception.sample['free'], resource.PHASE_FREE_BYTES)
        self.assertEqual(caught.exception.sample['remainingSeconds'], 0.0)

    def test_zero_deadline_at_zero_clock_is_expired_even_with_free_memory(self):
        self.time = ControlledClock(0.0)
        memory = MemorySequence(resource.PHASE_FREE_BYTES)
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=0.0)
        self.assertEqual(memory.calls, 1)
        self.assertEqual(caught.exception.sample['deadlineUtc'], 0.0)
        self.assertEqual(self.time.sleeps, [])

    def test_only_fixed_exact_integer_guards_are_accepted(self):
        memory = mock.Mock(side_effect=AssertionError('Invalid guard must not sample'))
        for value in (0, -1, 1, resource.BOOT_FREE_BYTES - 1, resource.PHASE_FREE_BYTES + 1,
                      True, float(resource.PHASE_FREE_BYTES), None, '1073741824'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.wait(memory, required=value)
        memory.assert_not_called()

    def test_invalid_deadline_and_poll_values_fail_before_sampling(self):
        memory = mock.Mock(side_effect=AssertionError('Invalid argument must not sample'))
        for value in (None, True, 'later', float('nan'), float('inf'), -float('inf')):
            with self.subTest(deadline=value), self.assertRaises(ValueError):
                self.wait(memory, deadline_utc=value)
        for value in (0, -1, True, 'slow', float('nan'), float('inf')):
            with self.subTest(poll=value), self.assertRaises(ValueError):
                self.wait(memory, poll_seconds=value)
        memory.assert_not_called()

    def test_all_injected_dependencies_must_be_callable(self):
        memory = mock.Mock(side_effect=AssertionError('Bad dependency must not sample'))
        for name in ('memory', 'on_sample', 'clock', 'sleep'):
            with self.subTest(name=name), self.assertRaises(TypeError):
                self.wait(memory, **{name: None}) if name != 'memory' else self.wait(None)
        memory.assert_not_called()

    def test_bad_memory_values_never_admit_or_sleep(self):
        for value in (None, True, False, -1, 1.5, 'free', float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.wait(MemorySequence(value))
        self.assertEqual(self.samples, [])
        self.assertEqual(self.time.sleeps, [])

    def test_memory_reader_exception_is_not_hidden_or_retried(self):
        error = OSError('synthetic memory reader failure')
        memory = mock.Mock(side_effect=error)
        with self.assertRaises(OSError) as caught:
            self.wait(memory)
        self.assertIs(caught.exception, error)
        self.assertEqual(memory.call_count, 1)
        self.assertEqual(self.samples, [])
        self.assertEqual(self.time.sleeps, [])

    def test_nonfinite_clock_sample_cannot_authorize_high_memory(self):
        readings = iter((1000.0, float('nan')))
        memory = MemorySequence(resource.PHASE_FREE_BYTES)
        with self.assertRaises(ValueError):
            self.wait(memory, clock=lambda: next(readings))
        self.assertEqual(memory.calls, 1)
        self.assertEqual(self.samples, [])
        self.assertEqual(self.time.sleeps, [])

    def test_external_deadline_is_clipped_to_nine_hundred_seconds(self):
        memory = MemorySequence(0)
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=1000000.0, poll_seconds=400.0)
        self.assertEqual(self.time.sleeps, [400.0, 400.0, 100.0])
        self.assertEqual(sum(self.time.sleeps), 900.0)
        self.assertEqual(caught.exception.sample['deadlineUtc'], 1900.0)
        self.assertEqual(caught.exception.sample['elapsedSeconds'], 900.0)
        self.assertEqual(caught.exception.sample['remainingSeconds'], 0.0)
        self.assertEqual(memory.calls, 4)

    def test_sleep_is_clipped_to_remaining_external_deadline(self):
        memory = MemorySequence(0, resource.PHASE_FREE_BYTES)
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=1002.25, poll_seconds=10.0)
        self.assertEqual(self.time.sleeps, [2.25])
        self.assertEqual(self.time.now, 1002.25)
        self.assertEqual(caught.exception.sample['free'], resource.PHASE_FREE_BYTES)
        self.assertEqual(caught.exception.sample['remainingSeconds'], 0.0)

    def test_callback_consuming_deadline_prevents_high_memory_admission(self):
        def callback(sample):
            self.samples.append(sample)
            self.time.now += 1.0
        with self.assertRaises(resource.ResourceWaitExpired):
            self.wait(MemorySequence(resource.PHASE_FREE_BYTES),
                      deadline_utc=1001.0, on_sample=callback)
        self.assertEqual(len(self.samples), 1)
        self.assertEqual(self.time.sleeps, [])

    def test_slow_memory_sample_cannot_admit_after_deadline(self):
        def memory():
            self.time.now += 1.0
            return resource.PHASE_FREE_BYTES
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=1001.0)
        self.assertEqual(caught.exception.sample['sampleUtc'], 1001.0)
        self.assertEqual(self.time.sleeps, [])

    def test_callback_mutates_only_its_copy_not_admission_data(self):
        def callback(sample):
            self.samples.append(sample)
            sample.update(required=0, free=10 ** 30, deadlineUtc=10 ** 30,
                          sampleUtc=-1, remainingSeconds=10 ** 30)
        memory = MemorySequence(0, resource.PHASE_FREE_BYTES)
        result = self.wait(memory, on_sample=callback)
        self.assertEqual(self.time.sleeps, [1.0])
        self.assertEqual(memory.calls, 2)
        self.assertEqual(result['required'], resource.PHASE_FREE_BYTES)
        self.assertEqual(result['free'], resource.PHASE_FREE_BYTES)
        self.assertEqual(result['deadlineUtc'], 1030.0)
        self.assertEqual(result['sampleUtc'], 1001.0)
        self.assertIsNot(result, self.samples[-1])

    def test_frozen_clock_expires_on_logical_sleep_budget_even_if_memory_recovers(self):
        self.time = ControlledClock(frozen=True)
        memory = MemorySequence(0, 0, 0, resource.PHASE_FREE_BYTES)
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(memory, deadline_utc=1000000.0, poll_seconds=400.0)
        self.assertEqual(self.time.now, 1000.0)
        self.assertEqual(self.time.sleeps, [400.0, 400.0, 100.0])
        self.assertEqual(memory.calls, 4)
        self.assertEqual(caught.exception.sample['elapsedSeconds'], 900.0)
        self.assertEqual(caught.exception.sample['remainingSeconds'], 0.0)
        self.assertEqual(caught.exception.sample['free'], resource.PHASE_FREE_BYTES)

    def test_clock_backwards_during_sampling_fails_closed(self):
        readings = iter((1000.0, 999.0))
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(MemorySequence(resource.PHASE_FREE_BYTES), clock=lambda: next(readings))
        self.assertEqual(caught.exception.reason, 'RESOURCE_CLOCK_REGRESSED_BEFORE_NATIVE')
        self.assertEqual(self.samples, [])
        self.assertEqual(self.time.sleeps, [])

    def test_clock_backwards_in_callback_cannot_admit_high_memory(self):
        def callback(sample):
            self.samples.append(sample)
            self.time.now -= 1.0
        with self.assertRaises(resource.ResourceWaitExpired) as caught:
            self.wait(MemorySequence(resource.PHASE_FREE_BYTES), on_sample=callback)
        self.assertEqual(caught.exception.reason, 'RESOURCE_CLOCK_REGRESSED_BEFORE_NATIVE')
        self.assertEqual(caught.exception.sample['free'], resource.PHASE_FREE_BYTES)
        self.assertEqual(self.time.sleeps, [])

    def test_exception_preserves_a_copy_of_diagnostic_sample(self):
        sample = {'required': resource.PHASE_FREE_BYTES, 'free': 0}
        error = resource.ResourceWaitExpired(sample)
        sample['free'] = resource.PHASE_FREE_BYTES
        self.assertEqual(error.sample['free'], 0)
        self.assertIsNot(error.sample, sample)
        self.assertEqual(error.reason, 'RESOURCE_WAIT_EXPIRED_BEFORE_NATIVE')


if __name__ == '__main__':
    unittest.main()
