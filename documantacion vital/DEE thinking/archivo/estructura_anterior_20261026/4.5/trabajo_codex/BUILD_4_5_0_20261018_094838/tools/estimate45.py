"""Measure raw-deflate size without creating or publishing a release ZIP."""
import argparse
from collections import Counter
from pathlib import Path
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from package45 import ARCHIVE_ROOT, BLOCK, put, selection


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--product-root', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args(); started = time.monotonic()
    files, omitted = selection(a.product_root)
    raw = Counter(); compressed = Counter(); count = 0; headers = 0
    for name, row in sorted(files.items()):
        compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
        encoded = 0; size = 0
        with row['source'].open('rb') as stream:
            for block in iter(lambda: stream.read(BLOCK), b''):
                size += len(block); encoded += len(compressor.compress(block))
        encoded += len(compressor.flush())
        category = name.split('/')[0]
        raw[category] += size; compressed[category] += encoded
        # Exact filename headers plus conservative ZIP64/data-descriptor room.
        length = len((ARCHIVE_ROOT + '/' + name).encode('utf-8'))
        headers += 30 + 46 + length * 2 + 64
        count += 1
        if count % 500 == 0:
            print(f'{count}/{len(files)} files measured', flush=True)
    result = {'schema': 'DEE45.preseal-compression-estimate.v1', 'files_measured': count,
              'expanded_selected_bytes': sum(raw.values()), 'measured_deflate_payload_bytes': sum(compressed.values()),
              'estimated_zip_bytes': sum(compressed.values()) + headers + 1024 * 1024,
              'reserved_headers_bytes': headers, 'reserved_virtual_manifests_bytes': 1024 * 1024,
              'expanded_by_category': dict(raw), 'deflate_by_category': dict(compressed), 'omitted': len(omitted),
              'elapsed_seconds': time.monotonic() - started,
              'scope': 'Raw deflate level 6 measured over selected inputs; no ZIP created. Conservative header/manifest allowance; final compressed bytes decide transport splitting.'}
    put(a.report, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
