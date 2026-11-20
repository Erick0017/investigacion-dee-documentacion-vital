"""Read selected immutable Native snapshot records; stdlib, no DEE imports."""
from pathlib import Path
import argparse, gzip, hashlib, json, struct


def inspect(path):
    encoded = Path(path).read_bytes()
    b = gzip.decompress(encoded) if encoded[:2] == b'\x1f\x8b' else encoded
    if b[:8] != b'DEETSNP1' or struct.unpack_from('<I', b, 8)[0] != 2:
        raise ValueError('Known DEETSNP1/v2 only')
    n = struct.unpack_from('<I', b, 12)[0]
    tick = struct.unpack_from('<Q', b, 16)[0]
    offset = 24 + 1 + 8 + 8
    text_n = struct.unpack_from('<I', b, offset)[0]; offset += 4 + text_n
    total = struct.unpack_from('<Q', b, offset)[0]; offset += 8
    if n != 67 or total != n**3:
        raise ValueError('Inherited N67 snapshot required')
    raw = b[offset:offset+8*total]; offset += 8*total
    clocks = b[offset:offset+8*total]
    origins = {'PI03_Q': (19,54,5), 'MU': (15,15,15)}
    roles = {'A': (-1,-1,0), 'B': (1,-1,0), 'datum': (-1,0,1), 'center': (0,0,0),
             'tail_stop': (0,3,0)}
    for x in (-1,0,1):
        for z in (0,-1):
            roles['output_%d_%d' % (x,z)] = (2*x,2,2*z)
            roles['stop_%d_%d' % (x,z)] = (3*x,3,3*z)
    rows = []
    for name, q in origins.items():
        for role, p in roles.items():
            xyz = tuple((q[k]+p[k]) % n for k in range(3))
            i = (xyz[0]*n+xyz[1])*n+xyz[2]
            v = struct.unpack_from('<Q', raw, 8*i)[0]
            direction = [((v >> s)&15)-(16 if ((v >> s)&15)>=8 else 0) for s in (48,52,56)]
            rows.append({'organization': name, 'role': role, 'site': list(xyz), 'raw': str(v),
                         'state': v & 0xffffffff, 's_reg': (v>>32)&65535, 'semantic': (v>>60)&15,
                         'direction': direction, 'clock': str(struct.unpack_from('<Q',clocks,8*i)[0])})
    return {'schema':'PI04.passive_selected_supports.R01','source':str(Path(path).resolve()),
            'source_bytes':len(encoded),'source_sha256':hashlib.sha256(encoded).hexdigest(),
            'N':n,'tick':tick,'coordinate_index':'(x*N+y)*N+z',
            'RAW_sha256':hashlib.sha256(raw).hexdigest(),'clocks_sha256':hashlib.sha256(clocks).hexdigest(),
            'records':rows,'Native_imports':False,'Native_ticks':0,
            'scope':'Binary snapshot records only; no inferred functional threshold or new experiment. GzipCRC checked, internalFNV not recalculated.'}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',required=True);p.add_argument('--salida',required=True)
    a=p.parse_args();out=Path(a.salida)
    if out.exists():raise ValueError('Refuse overwrite')
    value=inspect(a.snapshot)
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(value,ensure_ascii=False,indent=2))
