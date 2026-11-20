"""Offline exact-frame compatibility proof for R05 editorial revisions.

Two fresh processes import the old/new pure model sources separately. No DEE,
browser, encoder, simulation, retagging or register mutation is performed.
The root owner approves the emitted evidence in the sole production register.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def emit_models(source):
    # sys.path precedence is explicit; no module from the other source is cached.
    sys.path.insert(0, str(source))
    import pipeline_r05 as pipeline
    rows = {}
    for number, seconds in enumerate(pipeline.SCENE_SECONDS, 1):
        scene = f'S{number:02d}'
        frames = []
        sequence = hashlib.sha256()
        for index in range(seconds*30):
            encoded = json.dumps(pipeline.model(scene, index), sort_keys=True,
                                 ensure_ascii=False, separators=(',', ':'),
                                 allow_nan=False).encode('utf-8')
            frame_digest = hashlib.sha256(encoded).hexdigest()
            frames.append(frame_digest)
            sequence.update(index.to_bytes(4, 'big'))
            sequence.update(bytes.fromhex(frame_digest))
        rows[scene] = {'frame_hashes': frames, 'sequence_sha256': sequence.hexdigest()}
    return {'source': str(source), 'fingerprint': pipeline.visual_fingerprint(),
            'scene_seconds': list(pipeline.SCENE_SECONDS), 'scenes': rows,
            'common_files': {name: digest(source/name)
                             for name in ('renderer_r05.py', 'render_common.cjs')}}


def child(source):
    result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                             '--emit-models', str(source)], check=True,
                            capture_output=True, text=True, encoding='utf-8', timeout=180,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    return json.loads(result.stdout)


def compare(old_source, new_source, expected_old):
    old, new = child(old_source), child(new_source)
    if old['fingerprint'] != expected_old:
        raise ValueError('Frozen reference fingerprint does not match the declared candidate')
    if old['scene_seconds'] != new['scene_seconds']:
        raise ValueError('Timeline changed; scene reuse requires a separate protocol')
    common = {name: {'old_sha256': old['common_files'][name],
                     'new_sha256': new['common_files'][name],
                     'equal': old['common_files'][name] == new['common_files'][name]}
              for name in old['common_files']}
    sys.path.insert(0, str(new_source))
    import pipeline_r05 as pipeline
    scenes = {}
    for scene in old['scenes']:
        a, b = old['scenes'][scene], new['scenes'][scene]
        if len(a['frame_hashes']) != len(b['frame_hashes']):
            raise ValueError('Frame count changed: '+scene)
        different = [i for i, (left, right) in enumerate(zip(a['frame_hashes'], b['frame_hashes']))
                     if left != right]
        segment = new_source/'escenas'/(scene+'.mp4')
        info = pipeline.probe(segment, False)
        comment = info['format'].get('tags', {}).get('comment', '')
        prefix = 'R05 visual_source_sha256='
        if not comment.startswith(prefix):
            raise ValueError('Segment lacks source provenance: '+scene)
        scenes[scene] = {
            'frames': len(a['frame_hashes']), 'frames_individually_compared': len(a['frame_hashes']),
            'all_frames_equal': not different, 'different_frame_indices': different,
            'old_models_sequence_sha256': a['sequence_sha256'],
            'new_models_sequence_sha256': b['sequence_sha256'],
            'segment_path': str(segment), 'segment_sha256': digest(segment),
            'segment_source_fingerprint': comment[len(prefix):],
            'approved': False,
        }
    return {
        'operation': 'exact_offline_model_comparison', 'approved': False,
        'approval_authority': 'Root owner must record approval in REGISTRO_PRODUCCION_R05.json',
        'reference_fingerprint': old['fingerprint'], 'new_fingerprint': new['fingerprint'],
        'old_source': str(old_source), 'new_source': str(new_source),
        'common_files': common, 'common_files_unchanged': all(x['equal'] for x in common.values()),
        'total_frames_individually_compared': sum(x['frames'] for x in scenes.values()),
        'equal_scenes': [s for s, x in scenes.items() if x['all_frames_equal']],
        'changed_scenes': [s for s, x in scenes.items() if not x['all_frames_equal']],
        'hash_rule': 'sha256(UTF8 canonical JSON sort_keys separators=(comma,colon)); sequence hashes big-endian4-byte frame index followed by32-byte frame digest',
        'scenes': scenes, 'files_retagged': 0, 'native_ticks': 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-models', type=Path)
    parser.add_argument('--old', type=Path)
    parser.add_argument('--new', type=Path, default=HERE)
    parser.add_argument('--expected-old', default='a610b45d1b2defc5f51f26935cfda199a5e6cee509a7416fcbdebb0587ecf106')
    args = parser.parse_args()
    if args.emit_models:
        result = emit_models(args.emit_models.resolve())
    else:
        if not args.old:
            parser.error('--old frozen-source directory is required')
        result = compare(args.old.resolve(), args.new.resolve(), args.expected_old)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
