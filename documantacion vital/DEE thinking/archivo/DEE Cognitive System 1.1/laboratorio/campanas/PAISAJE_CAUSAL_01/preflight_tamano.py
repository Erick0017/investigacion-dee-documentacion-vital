"""Size the real primary corpus before choosing a justified thin extraction."""
from pathlib import Path
import argparse,json,zlib
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();rows=[]
for path in sorted(a.evidence.glob('*/*/PRIMARIOS.json')):
    b=path.read_bytes();rows.append({'source':path.relative_to(a.evidence).as_posix(),'bytes':len(b),'compressed_deflate9_bytes':len(zlib.compress(b,9))})
traces=[{'source':p.relative_to(a.evidence).as_posix(),'bytes':p.stat().st_size}for p in sorted(a.evidence.rglob('*.jsonl.gz'))]
out={'primaries':rows,'traces':traces,'totals':{'primary_cases':len(rows),'primary_expanded_bytes':sum(r['bytes']for r in rows),'all_primary_deflate9_bytes':sum(r['compressed_deflate9_bytes']for r in rows),'all_jsonl_gzip_bytes':sum(r['bytes']for r in traces)},'not_final_zip_size':True};(a.evidence/'PREFLIGHT_TAMANOS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out['totals']))
