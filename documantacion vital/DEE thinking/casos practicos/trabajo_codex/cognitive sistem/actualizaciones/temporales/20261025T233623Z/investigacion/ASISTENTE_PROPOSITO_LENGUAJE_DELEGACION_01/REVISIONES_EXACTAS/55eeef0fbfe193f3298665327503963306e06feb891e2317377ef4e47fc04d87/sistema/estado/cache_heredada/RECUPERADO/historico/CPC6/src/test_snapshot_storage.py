"""Finite lossless-codec checks; synthetic fixtures are not DEE experiments."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, put, digest
from integrated import Session
from package_cpc6 import selected
from snapshot_storage import stage_states, mapped_files, verify_tree, logical_sha, materialized, materialize_all, sha


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--native-snapshot', type=Path, required=True); a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False); started = time.monotonic(); checks = {}; parent = ROOT / '_distribution_tests'; parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='snapshot_storage_', dir=parent) as temporary:
        base = Path(temporary); root = base / 'CPC6'; stage = base / 'encodings'; root.mkdir()
        state = root / 'resultados/example/STATE.deetsnap'; state.parent.mkdir(parents=True)
        data = bytes(range(256)) * 8192 + b'SYNTHETIC_STORAGE_FIXTURE_NOT_NATIVE_WORLD'; state.write_bytes(data)
        fixture = root / 'genealogia/fixture.deetsnap'; fixture.parent.mkdir(); fixture.write_bytes(b'PLAIN_REFERENCE_FIXTURE')
        original_hash = sha(state); original_bytes = state.read_bytes()
        mapped = stage_states(root, stage); mapped_again = stage_states(root, stage)
        checks['one_results_state_encoded_genealogy_left_plain'] = mapped['states_count'] == 1 and fixture.read_bytes() == b'PLAIN_REFERENCE_FIXTURE'
        checks['incremental_reuse_reverified'] = mapped_again['reused_encodings_verified_again'] == 1
        checks['workspace_original_byte_exact_and_not_deleted'] = state.read_bytes() == original_bytes
        extracted = base / 'extracted'; extracted.mkdir()
        for source, rel in mapped_files(root, stage, list(selected(root))):
            target = extracted / rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
        logical = extracted / 'resultados/example/STATE.deetsnap'; encoded = Path(str(logical) + '.gz')
        checks['archive_shape_omits_raw_duplicate'] = not logical.exists() and encoded.exists()
        tree_check = verify_tree(extracted); checks['all_gzip_CRC_and_logical_SHA'] = tree_check['verified']
        checks['logical_fallback_hash_original'] = logical_sha(logical) == original_hash
        checks['explicit_logical_gzip_hash_original'] = logical_sha(encoded) == original_hash
        checks['encoded_file_identity_separate'] = sha(encoded) == mapped['states'][0]['encoded_sha256'] and sha(encoded) != original_hash
        with materialized(logical) as decoded:
            short_path = decoded; checks['owned_temporary_exact'] = decoded.read_bytes() == data
        checks['temporary_cleaned_after_reader'] = not short_path.exists()
        with materialized(state) as existing:
            checks['plain_original_returned_inert'] = existing == state
        try:
            with materialized(logical, max_bytes=16): pass
        except ValueError: checks['explicit_decode_size_bound_rejected'] = True
        else: checks['explicit_decode_size_bound_rejected'] = False
        bad = base / 'corrupt.gz'; encoded_bytes = encoded.read_bytes(); bad.write_bytes(encoded_bytes[:-1] + bytes([encoded_bytes[-1] ^ 0xff]))
        try:
            with materialized(bad): pass
        except (OSError, EOFError): checks['corrupt_gzip_rejected_before_native_reader'] = True
        else: checks['corrupt_gzip_rejected_before_native_reader'] = False
        restore = materialize_all(extracted); again = materialize_all(extracted)
        checks['explicit_restore_byte_exact'] = restore['restored'] == 1 and logical.read_bytes() == data
        checks['existing_same_state_preserved'] = again['already_present_and_byte_identity_verified'] == 1
        logical.write_bytes(b'EXISTING_FOREIGN_FILE')
        try: materialize_all(extracted)
        except AssertionError: checks['existing_different_state_never_overwritten'] = logical.read_bytes() == b'EXISTING_FOREIGN_FILE'
        else: checks['existing_different_state_never_overwritten'] = False
        # Codec only: load a real finished snapshot after exact decompression;
        # no evolution, re-preparation, target, response table or RAW edit.
        native_plain = a.native_snapshot.resolve(); native_encoded = base / 'NATIVE.deetsnap.gz'
        with native_plain.open('rb') as source, native_encoded.open('xb') as sink:
            with gzip.GzipFile(filename='', mode='wb', fileobj=sink, mtime=0) as output: shutil.copyfileobj(source, output)
        original = Session.load(native_plain)
        with materialized(native_encoded) as native_path:
            restored = Session.load(native_path)
            checks['real_native_snapshot_RAW_clock_tick_after_decode'] = digest(original.world) == digest(restored.world)
            checks['real_native_session_geometry_and_requests'] = original.geometry == restored.geometry and original.requests == restored.requests
        native_identity = {'plain_sha256': sha(native_plain), 'decoded_sha256': logical_sha(native_encoded),
                           'tick': int(original.world.runtime.current_tick), 'native_ticks_evolved': 0}
        checks['real_native_snapshot_bytes_exact'] = native_identity['plain_sha256'] == native_identity['decoded_sha256']
    report = {'schema': 'CPC6.snapshot-storage-technical.v1', 'classification': 'LOSSLESS_ENCODING_TECHNICAL_TEST',
              'verified': all(checks.values()), 'checks': checks, 'synthetic_fixture_bytes': len(data),
              'native_codec_check': native_identity, 'elapsed_seconds': time.monotonic() - started}
    put(a.output / 'TECHNICAL.json', report); print(json.dumps({'verified': report['verified'], 'checks': len(checks)}))
    assert report['verified']


if __name__ == '__main__': main()
