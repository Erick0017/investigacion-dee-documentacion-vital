"""Append an actual PI08 scientific milestone. Stdlib; no DEE or world writes."""
from pathlib import Path
import argparse,datetime,hashlib,json,os
P=Path(__file__).resolve().parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('--fuente',required=True);a.add_argument('--hecho',required=True);v=a.parse_args()
 f=Path(v.fuente).resolve(strict=True)
 if not f.is_relative_to(P.resolve()):raise ValueError('An actual campaign primary/proof is required')
 row={'kind':'SCIENTIFIC_MILESTONE','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fact':v.hecho,'source':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'not_an_actor_input':True}
 with(P/'ENSAYOS.jsonl').open('a',encoding='utf8')as out:out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush();os.fsync(out.fileno())
 print(json.dumps(row,ensure_ascii=False))
if __name__=='__main__':main()
