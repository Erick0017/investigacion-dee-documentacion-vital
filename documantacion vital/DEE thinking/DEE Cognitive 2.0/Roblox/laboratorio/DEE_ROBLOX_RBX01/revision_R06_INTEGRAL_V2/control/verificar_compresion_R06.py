"""Passive byte-exact Zstd transport check, no DEE, Studio or Native imports."""
from pathlib import Path
import base64,hashlib,json,zstandard
ROOT=Path(__file__).resolve().parents[1]
def main():
 proof=json.loads((ROOT/'control/COMPRESION_TRANSPORTE_FIJO_R06.json').read_text('utf8'))
 source=json.loads((ROOT/'native/MAIN/WORLD_PADRE_DEV4.json').read_text('utf8'))
 canonical=json.dumps(source,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
 packed=base64.b64decode(proof['b64'],validate=True)
 raw=zstandard.ZstdDecompressor().decompress(packed,max_output_size=5_000_000)
 sha=hashlib.sha256(raw).hexdigest()
 assert raw==canonical and len(raw)==proof['raw_bytes'] and len(packed)==proof['compressed_bytes'] and sha==proof['sha256_hex']
 report={'schema':'DEE.RBX01.R06.frozen_transport_verification.R01','raw_bytes':len(raw),'compressed_bytes':len(packed),
 'sha256':sha,'byte_exact_roundtrip':True,'source_JSON_semantically_identical':json.loads(raw)==source,
 'source_file_raw_sha256':hashlib.sha256((ROOT/'native/MAIN/WORLD_PADRE_DEV4.json').read_bytes()).hexdigest(),
 'Native_loaded':False,'new_ticks':0,'instrument_scope':'frozen transport packet only; Native may progress independently during server instrumentation',
 'zstandard_version':zstandard.__version__}
 out=ROOT/'control/VERIFICACION_COMPRESION_TRANSPORTE_R06.json'
 with out.open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
 print(json.dumps(report))
if __name__=='__main__':main()
