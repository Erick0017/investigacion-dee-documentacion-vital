"""Recover a complete JSONL prefix from an unfinished instrument gzip, N0.

Never changes the original, invents an end event, imports Native or restores life.
The derived file is a new gzip of the exact already-recorded JSONL bytes.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import zlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    original = args.source.read_bytes()
    stream = zlib.decompressobj(16 + zlib.MAX_WBITS)
    recovered = stream.decompress(original)
    if not recovered.endswith(b'\n'):
        raise ValueError('The recorded prefix ends inside a JSONL row; do not silently trim it.')
    rows = [json.loads(line) for line in recovered.decode('utf8').splitlines() if line.strip()]
    frames = [row for row in rows if row.get('event') == 'passive_frame']
    archived = args.out / args.source.name
    if archived.exists():
        if archived.read_bytes() != original:
            raise ValueError('Refusing to replace a different preserved original.')
    else:
        shutil.copyfile(args.source, archived)
    output = args.out / 'REPLAY_PREFIJO_PARCIAL_060123_A_065619.jsonl.gz'
    packed = gzip.compress(recovered, compresslevel=9, mtime=0)
    if output.exists() and output.read_bytes() != packed:
        raise ValueError('Refusing to overwrite a different derived replay.')
    output.write_bytes(packed)
    assert gzip.decompress(output.read_bytes()) == recovered
    report = {
        'schema': 'APD05.GUI_partial_recorder_prefix.N0.R01',
        'scope': 'Instrument recording only, not video, not complete60min, not Native reproduction.',
        'native_ticks_added': 0,
        'original': {'path': str(args.source), 'preserved_copy': str(archived),
                     'bytes': len(original), 'sha256': digest(original),
                     'gzip_end_of_stream_present': stream.eof},
        'derived': {'path': str(output), 'bytes': len(packed), 'sha256': digest(packed),
                    'exact_decompressed_prefix_sha256': digest(recovered),
                    'exact_decompressed_prefix_bytes': len(recovered),
                    'complete_json_rows': len(rows), 'passive_frames': len(frames),
                    'first_wall_utc': rows[0]['wall_utc'], 'last_wall_utc': rows[-1]['wall_utc'],
                    'first_tick': frames[0]['frame']['tick'], 'last_tick': frames[-1]['frame']['tick'],
                    'recompressed_jsonl_bytes_unchanged': True, 'invented_end_event': False},
        'limitation': 'Original compressor was not cleanly closed. No trailer/CRC validation is possible for the original. Every recovered JSON row parsed; no later unrecorded events are reconstructed. The replay ends at the recorded partial boundary, not at the final scientific tick. Host browser tool delay was not a new live scientific observation.'
    }
    report_file = args.out / 'RECUPERACION_GRABACION_PARCIAL_N0.json'
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
