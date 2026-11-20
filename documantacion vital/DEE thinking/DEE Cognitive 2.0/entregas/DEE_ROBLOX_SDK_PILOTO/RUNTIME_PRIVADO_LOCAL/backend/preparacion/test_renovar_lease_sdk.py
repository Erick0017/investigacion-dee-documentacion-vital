"""Pure lease/metadata fixtures. Never stages or applies a material transaction."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SOURCE = Path(__file__).with_name('renovar_lease_sdk.py')
SPEC = importlib.util.spec_from_file_location('_sdk_lease_pure_fixture', SOURCE)
lease_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lease_module
SPEC.loader.exec_module(lease_module)

NOW = 2000000000
INSTANCE = 'SDK_DEMO_0123456789ABCDEF'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_' + INSTANCE
SESSION = 'SDK_SESSION_0123456789abcdef0123456789abcdef'
CAMPAIGN_SHA = '9' * 64
OLD_SNAPSHOT_SHA = 'c' * 64
EXPECTED_FIELDS = {'schema', 'leaseId', 'instanceId', 'lifeId', 'sessionId',
                   'startUtcEpoch', 'lastNewUtcEpoch', 'hardFinishUtcEpoch',
                   'additionalCycles', 'startingCompletedCycles', 'startingConsumedTicks',
                   'cumulativeCycleCap', 'validationCampaign', 'validationCampaignSha256'}


class MustNotResolve:
    def __fspath__(self):
        raise AssertionError('Filesystem resolution occurred before Root-only rejection')


class LeaseFixtures(unittest.TestCase):
    def setUp(self):
        self.cfg = {'instanceId': INSTANCE, 'lifeId': LIFE, 'sessionId': SESSION}
        self.lease = {'schema': 'DEE.Roblox.SDK.operational_lease.0.1.0',
                      'leaseId': 'SDK_LEASE_0123456789ABCDEF',
                      **self.cfg, 'startUtcEpoch': NOW - 10,
                      'lastNewUtcEpoch': NOW + 3600, 'hardFinishUtcEpoch': NOW + 7200,
                      'additionalCycles': 3, 'startingCompletedCycles': 0,
                      'startingConsumedTicks': 0, 'cumulativeCycleCap': 3,
                      'validationCampaign': False, 'validationCampaignSha256': None}
        self.campaign = {'startUtcEpoch': NOW - 100, 'lastNewUtcEpoch': NOW + 4000,
                         'hardFinishUtcEpoch': NOW + 8000}

    def validate(self, value=None, **kwargs):
        kwargs.setdefault('now', NOW)
        return lease_module.validate_lease(self.lease if value is None else value,
                                           self.cfg, **kwargs)

    def metadata(self):
        old_system = {'operation_count': 7, 'previous_checkpoint_sha256': '0' * 64,
                      'world_id': LIFE, 'retained': {'lineage': [1, 2]}}
        new_system = copy.deepcopy(old_system)
        new_system['operation_count'] += 1
        new_system['previous_checkpoint_sha256'] = OLD_SNAPSHOT_SHA
        before = {lease_module.SYSTEM_KEY: lease_module.canonical(old_system),
                  lease_module.ACTOR_KEY: lease_module.canonical(
                      {'phase': 'IDLE', 'cycles': 2, 'last_sequence': 4, 'pending': None}),
                  'RAW_LIKE_RETAINED': 'byte-for-byte', 'other_retained': 'unaltered'}
        after = copy.deepcopy(before)
        after[lease_module.LEASE_KEY] = lease_module.canonical(self.lease)
        after[lease_module.SYSTEM_KEY] = lease_module.canonical(new_system)
        return before, after, old_system, new_system

    def test_exact_root_dto_and_return_copy(self):
        self.assertEqual(set(self.lease), EXPECTED_FIELDS)
        self.assertEqual(lease_module.FIELDS, EXPECTED_FIELDS)
        self.assertEqual(lease_module.SCHEMA, 'DEE.Roblox.SDK.operational_lease.0.1.0')
        self.assertEqual(lease_module.LEASE_KEY, 'DEE.Cognitive.Roblox.SDK.LEASE.0.1.0')
        self.assertEqual(lease_module.SYSTEM_KEY, 'DEE.Cognitive.System.1.1.life.v1')
        self.assertEqual(lease_module.ACTOR_KEY, 'DEE.Cognitive.Roblox.SDK.native.0.1.0')
        result = self.validate()
        self.assertEqual(result, self.lease)
        self.assertIsNot(result, self.lease)
        result['additionalCycles'] = 1
        self.assertEqual(self.lease['additionalCycles'], 3)

    def test_schema_missing_or_extra_fields_rejected(self):
        cases = []
        changed = copy.deepcopy(self.lease); changed['schema'] = 'other'; cases.append(changed)
        changed = copy.deepcopy(self.lease); changed.pop('sessionId'); cases.append(changed)
        changed = copy.deepcopy(self.lease); changed['extra'] = True; cases.append(changed)
        for changed in cases:
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'EXACT_LEASE_DTO'):
                self.validate(changed)

    def test_lease_id_requires_uppercase_hex_namespace(self):
        for value in ('SDK_LEASE_0123456789abcdef', 'SDK_LEASE_0123456789ABCDE',
                      'SDK_LEASE_0123456789ABCDEF0', '../SDK_LEASE_0123456789ABCDEF',
                      'R07_LEASE_0123456789ABCDEF'):
            changed = {**self.lease, 'leaseId': value}
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'FINITE_LEASE_ID'):
                self.validate(changed)

    def test_every_identity_must_match_exactly(self):
        replacements = {'instanceId': 'SDK_DEMO_FEDCBA9876543210',
                        'lifeId': LIFE + '_OTHER',
                        'sessionId': 'SDK_SESSION_' + 'f' * 32}
        for key, value in replacements.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'SAME_SDK_IDENTITY'):
                self.validate({**self.lease, key: value})

    def test_integer_contract_rejects_booleans(self):
        for key in ('startUtcEpoch', 'lastNewUtcEpoch', 'hardFinishUtcEpoch',
                    'additionalCycles', 'startingCompletedCycles',
                    'startingConsumedTicks', 'cumulativeCycleCap'):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'EXACT_LEASE_INTEGER'):
                self.validate({**self.lease, key: True})

    def test_lifetime_cap_three_and_exact_counter_baseline(self):
        edge = {**self.lease, 'startingCompletedCycles': 2, 'additionalCycles': 1,
                'cumulativeCycleCap': 3, 'startingConsumedTicks': 12345}
        self.assertEqual(self.validate(edge), edge)
        cases = [{'startingCompletedCycles': -1}, {'startingCompletedCycles': 3},
                 {'startingConsumedTicks': -1}, {'startingConsumedTicks': 40001},
                 {'additionalCycles': 0}, {'additionalCycles': 4},
                 {'cumulativeCycleCap': 2}]
        for change in cases:
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'NO_COUNTER_RESET_OR_EXTRA_LIFETIME_CYCLES'):
                self.validate({**self.lease, **change})

    def test_window_order_and_six_hour_maximum(self):
        edge = {**self.lease, 'startUtcEpoch': NOW - 3600,
                'lastNewUtcEpoch': NOW + 3600, 'hardFinishUtcEpoch': NOW + 18000}
        self.assertEqual(self.validate(edge), edge)
        cases = [{**edge, 'hardFinishUtcEpoch': NOW + 18001},
                 {**self.lease, 'lastNewUtcEpoch': self.lease['startUtcEpoch']},
                 {**self.lease, 'hardFinishUtcEpoch': self.lease['lastNewUtcEpoch']}]
        for changed in cases:
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'FINITE_PROSPECTIVE_LEASE'):
                self.validate(changed)

    def test_admission_includes_start_but_excludes_last_new_boundary(self):
        self.assertEqual(self.validate(now=self.lease['startUtcEpoch']), self.lease)
        for now in (self.lease['startUtcEpoch'] - 1, self.lease['lastNewUtcEpoch'],
                    self.lease['hardFinishUtcEpoch']):
            with self.subTest(now=now), self.assertRaisesRegex(ValueError, 'PROSPECTIVE_LEASE_ADMISSION'):
                self.validate(now=now)

    def test_validation_mode_is_explicit_and_noncampaign_has_no_campaign_pin(self):
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_VALIDATION_MODE'):
            self.validate({**self.lease, 'validationCampaign': 1})
        with self.assertRaisesRegex(ValueError, 'NO_PRODUCT_EXPIRY_FROM_OLD_CAMPAIGN'):
            self.validate({**self.lease, 'validationCampaignSha256': CAMPAIGN_SHA})

    def test_campaign_is_pinned_and_clips_all_three_dates(self):
        value = {**self.lease, 'validationCampaign': True,
                 'validationCampaignSha256': CAMPAIGN_SHA}
        kwargs = {'campaign': self.campaign, 'campaign_sha': CAMPAIGN_SHA}
        self.assertEqual(self.validate(value, **kwargs), value)
        for key, changed_value in (
                ('startUtcEpoch', self.campaign['startUtcEpoch'] - 1),
                ('lastNewUtcEpoch', self.campaign['lastNewUtcEpoch'] + 1),
                ('hardFinishUtcEpoch', self.campaign['hardFinishUtcEpoch'] + 1)):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'VALIDATION_CAMPAIGN_CLIP'):
                self.validate({**value, key: changed_value}, **kwargs)
        with self.assertRaises(ValueError):
            self.validate(value, campaign=None, campaign_sha=CAMPAIGN_SHA)
        with self.assertRaises(ValueError):
            self.validate(value, campaign=self.campaign, campaign_sha='a' * 64)

    def test_campaign_requires_real_lowercase_sha_even_when_none_matches_none(self):
        for value in (None, '', 'a' * 63, 'G' * 64, True):
            changed = {**self.lease, 'validationCampaign': True,
                       'validationCampaignSha256': value}
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.validate(changed, campaign=self.campaign, campaign_sha=value)

    def test_old_validation_campaign_does_not_expire_product_lease(self):
        expired_campaign = {'startUtcEpoch': 1600000000, 'lastNewUtcEpoch': 1600003600,
                            'hardFinishUtcEpoch': 1600007200}
        self.assertEqual(self.validate(campaign=expired_campaign, campaign_sha='e' * 64), self.lease)

    def test_metadata_allows_only_canonical_lease_and_exact_system_delta(self):
        before, after, old_system, new_system = self.metadata()
        originals = copy.deepcopy((before, after, old_system, new_system, self.lease))
        lease_module.check_metadata(before, after, old_system, new_system, self.lease, OLD_SNAPSHOT_SHA)
        self.assertEqual((before, after, old_system, new_system, self.lease), originals)

    def test_metadata_rejects_noncanonical_lease_encoding(self):
        for encoded in (json.dumps(self.lease), self.lease, '{}'):
            before, after, old_system, new_system = self.metadata()
            after[lease_module.LEASE_KEY] = encoded
            with self.subTest(encoded=encoded), self.assertRaisesRegex(ValueError, 'EXACT_CANONICAL_NATIVE_LEASE'):
                lease_module.check_metadata(before, after, old_system, new_system, self.lease, OLD_SNAPSHOT_SHA)

    def test_metadata_rejects_actor_raw_like_other_key_addition_or_removal(self):
        for change in ('actor', 'raw', 'extra', 'removed'):
            before, after, old_system, new_system = self.metadata()
            if change == 'actor':
                after[lease_module.ACTOR_KEY] = lease_module.canonical({'cycles': 0})
            elif change == 'raw':
                after['RAW_LIKE_RETAINED'] = 'changed'
            elif change == 'extra':
                after['RAW_LIKE_EXTRA'] = 'new unauthorized key'
            else:
                after.pop('other_retained')
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'OTHER_METADATA_OR_ACTOR_COUNTERS_CHANGED'):
                lease_module.check_metadata(before, after, old_system, new_system, self.lease, OLD_SNAPSHOT_SHA)

    def test_metadata_rejects_extra_system_fields_wrong_counter_or_previous_hash(self):
        for change in ('extra', 'counter_same', 'counter_plus_two', 'previous', 'nested'):
            before, after, old_system, new_system = self.metadata()
            if change == 'extra': new_system['unauthorized'] = True
            elif change == 'counter_same': new_system['operation_count'] = old_system['operation_count']
            elif change == 'counter_plus_two': new_system['operation_count'] += 1
            elif change == 'previous': new_system['previous_checkpoint_sha256'] = 'd' * 64
            else: new_system['retained']['lineage'].append(3)
            after[lease_module.SYSTEM_KEY] = lease_module.canonical(new_system)
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'SYSTEM_COMMIT_DELTA_EXCEEDS_ROOT_AUTHORIZATION'):
                lease_module.check_metadata(before, after, old_system, new_system, self.lease, OLD_SNAPSHOT_SHA)

    def test_metadata_old_operation_counter_must_be_an_integer_not_bool(self):
        before, after, old_system, new_system = self.metadata()
        old_system['operation_count'] = True
        with self.assertRaisesRegex(ValueError, 'EXACT_OLD_OPERATION_COUNT'):
            lease_module.check_metadata(before, after, old_system, new_system, self.lease, OLD_SNAPSHOT_SHA)

    def new_import0_fixture(self):
        cfg = {**self.cfg, 'nativeTick': 991187, 'sequenceOffset': 56,
               'localSequence': 0, 'completedCycles': 0}
        card = {'physical': {'N': 67, 'tick': 991187}}
        view = {'metadata': {'retained_ancestral_metadata': 'unchanged'}}
        ready = {'physical_equal': True, 'causal_prefix_equal': True,
                 'new_native_ticks': 0, 'sourceProofSha256': '1' * 64}
        return [cfg, card, view, 0, ready, '1' * 64, '2' * 64, '2' * 64]

    def test_new_import0_accepts_original_unused_state_without_mutation(self):
        args = self.new_import0_fixture()
        before = copy.deepcopy(args)
        lease_module.require_new_import0(*args)
        self.assertEqual(args, before)

    def test_new_import0_rejects_advanced_tick_or_nonzero_local_state(self):
        for change in ('N', 'card_tick', 'cfg_tick', 'offset', 'sequence', 'completed', 'cycles'):
            args = self.new_import0_fixture()
            if change == 'N': args[1]['physical']['N'] = 68
            elif change == 'card_tick': args[1]['physical']['tick'] = 992751
            elif change == 'cfg_tick': args[0]['nativeTick'] = 992751
            elif change == 'offset': args[0]['sequenceOffset'] = 0
            elif change == 'sequence': args[0]['localSequence'] = 1
            elif change == 'completed': args[0]['completedCycles'] = 1
            else: args[3] = 1
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'NEW_ONLY_CLOSED_ORIGINAL_IMPORT0_NO_AGENT_WORLD'):
                lease_module.require_new_import0(*args)

    def test_new_import0_rejects_any_existing_sdk_actor_key(self):
        args = self.new_import0_fixture()
        args[2]['metadata'][lease_module.ACTOR_KEY] = lease_module.canonical(
            {'phase': 'IDLE', 'cycles': 0, 'pending': None})
        with self.assertRaisesRegex(ValueError, 'NEW_ONLY_CLOSED_ORIGINAL_IMPORT0_NO_AGENT_WORLD'):
            lease_module.require_new_import0(*args)

    def test_new_import0_rejects_bad_ready_proof_or_prefix_pin(self):
        for change in ('physical', 'causal', 'ticks', 'proof', 'prefix'):
            args = self.new_import0_fixture()
            if change == 'physical': args[4]['physical_equal'] = False
            elif change == 'causal': args[4]['causal_prefix_equal'] = False
            elif change == 'ticks': args[4]['new_native_ticks'] = 1
            elif change == 'proof': args[4]['sourceProofSha256'] = '3' * 64
            else: args[6] = '4' * 64
            with self.subTest(change=change), self.assertRaisesRegex(
                    ValueError, 'NEW_ONLY_CLOSED_ORIGINAL_IMPORT0_NO_AGENT_WORLD'):
                lease_module.require_new_import0(*args)

    def test_stage_false_rejects_before_paths_or_helpers(self):
        with mock.patch.object(lease_module, 'helpers', side_effect=AssertionError('helpers must not load')) as helpers:
            with mock.patch.object(lease_module, 'load', side_effect=AssertionError('loader must not run')) as loader:
                for flag in (False, None, 1):
                    with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'ROOT_ONLY_LEASE_STAGE'):
                        lease_module.stage(MustNotResolve(), object(), MustNotResolve(), execute_root_only=flag)
                helpers.assert_not_called(); loader.assert_not_called()

    def test_apply_false_rejects_before_paths_or_helpers(self):
        with mock.patch.object(lease_module, 'helpers', side_effect=AssertionError('helpers must not load')) as helpers:
            with mock.patch.object(lease_module, 'load', side_effect=AssertionError('loader must not run')) as loader:
                for flag in (False, None, 1):
                    with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'ROOT_ONLY_NATIVE_LEASE_COMMIT'):
                        lease_module.apply(MustNotResolve(), '0' * 64, MustNotResolve(), execute_root_only=flag)
                helpers.assert_not_called(); loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
