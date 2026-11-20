"""Exact frozen-source device RAW/clock preflight; stdlib, no DEE execution."""
from pathlib import Path
from datetime import datetime, timezone
import gzip, hashlib, importlib.util, itertools, json, struct

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
PAIR = P / 'pares/PRINCIPAL_D_T922371'
OUT = P / 'control/PREFLIGHT_DISPOSITIVO_PI10_R01.json'
def need(ok, msg):
    if not ok: raise ValueError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
need(not OUT.exists(), 'Do not overwrite prior static preflight')
mf = json.loads((PAIR / 'EXPORTACION_SERVICIO.json').read_text('utf-8-sig'))
snap = PAIR / mf['native_snapshot']
need(sha(snap) == mf['snapshot_sha256'] == '72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331', 'Exact source snapshot')
spec = importlib.util.spec_from_file_location('pi10_frozen_safe_reader', C / 'reproducibilidad/observador_pasivo.py')
reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
data = snap.read_bytes(); data = gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data
r = reader.Reader(data[:-8])
need(r.take(8) == b'DEETSNP1' and r.u32() == 2, 'Exact snapshot format')
n = r.u32(); tick = r.u64(); r.u8(); r.u64(); r.u64(); phase = r.text(); total = r.u64()
need(n == 67 and tick == 922371 and total == n ** 3, 'Exact main source physical cut')
raw = r.take(8 * total); clocks = r.take(8 * total)
need(hashlib.sha256(raw).hexdigest() == mf['physical']['RAW_sha256'] and hashlib.sha256(clocks).hexdigest() == mf['physical']['clocks_sha256'], 'Exact physical arrays')
def signed4(v): return v - 16 if v & 8 else v
def lookup(site):
    x, y, z = site; i = (x * n + y) * n + z
    v = struct.unpack_from('<Q', raw, 8 * i)[0]
    return {'site': list(site), 'raw': v, 'clock': struct.unpack_from('<Q', clocks, 8 * i)[0], 'state': v & 0xffffffff, 's_reg': (v >> 32) & 0xffff, 'direction': [signed4((v >> s) & 15) for s in (48, 52, 56)], 'semantic': (v >> 60) & 15}
sites = {'sample': (30,40,30), 'source_Z': (30,40,29), 'source_X': (29,40,30), 'question_source': (33,40,30), 'question_reader': (34,40,30), 'new_sink_preview_X': (32,40,30), 'new_sink_preview_Z': (30,40,32), 'new_sink_question': (35,40,30)}
frame = set(sites.values())
halo = {tuple((s[k] + d[k]) % n for k in range(3)) for s in frame for d in itertools.product((-1,0,1), repeat=3)}
rows = [lookup(s) for s in sorted(halo)]
conflicts = [v for v in rows if v['raw'] != 0]
report = {'schema': 'DEE.PI10.static_exact_device_preflight.R01', 'utc': datetime.now(timezone.utc).isoformat(), 'Native_imported': False, 'new_ticks': 0, 'source_manifest': str(PAIR/'EXPORTACION_SERVICIO.json'), 'snapshot_sha256': sha(snap), 'physical': mf['physical'], 'declared_sites': sites, 'site_observations': {k: lookup(v) for k,v in sites.items()}, 'raw0_halo1_requested': True, 'halo_sites': len(rows), 'eligible_strict_RAW0': not conflicts, 'conflicts': conflicts, 'observations': rows, 'scope': 'Frozen source only. No future clearance, Native stepping, or attribution.'}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'report':str(OUT),'sha256':sha(OUT),'eligible':not conflicts,'sites':report['site_observations'],'conflicts':conflicts},ensure_ascii=False))
