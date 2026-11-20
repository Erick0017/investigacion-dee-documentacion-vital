"""Select two immutable CPC7 operational snapshots; never run old commands."""
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREFIX='CPC7/resultados/demo_live_u0_integrated_03/'
NAMES=('sesion_demo.deetsnap.gz','sesion_continuada.deetsnap.gz','INITIAL.json','CONTINUATION.json','OUTCOMES.json','VERIFICATION.json','INITIAL.COMMAND.json','CONTINUATION.COMMAND.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args()
    archive_sha=hashlib.sha256(a.archive.read_bytes()).hexdigest()
    assert archive_sha=='64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128'
    out=ROOT/'evidence/legacy_CPC7_demo03';out.mkdir(parents=True,exist_ok=True);rows=[]
    with zipfile.ZipFile(a.archive) as z:
        for name in NAMES:
            data=z.read(PREFIX+name);target=out/name
            if target.exists():assert target.read_bytes()==data
            else:target.write_bytes(data)
            rows.append({'member':PREFIX+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    (out/'PROVENANCE.json').write_text(json.dumps({'source_archive_sha256':archive_sha,'originals_unchanged':True,'members':rows},indent=2),encoding='utf-8')
    print(json.dumps({'selected':len(rows),'bytes':sum(r['bytes'] for r in rows)}))
if __name__=='__main__':main()
