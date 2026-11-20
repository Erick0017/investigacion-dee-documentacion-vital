"""Technical continuation of two saved unit-count states, no added experiences."""
import argparse,hashlib,json,os
from array import array
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot
from dee_thinking.consolidated import exact_receipt

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def physical(w):
 r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();rows=[]
 for name in('CARD_F41_A_ONLY','CARD_F43_AB'):
  parent=ROOT/'resultados/semantica/contact_cardinality_f3'/name;m=json.loads((parent/'MEASUREMENTS.json').read_text(encoding='utf8'));snap=parent/'T77.deetsnap.gz'
  w,_=load_world_snapshot(snap,max_bytes=64*1024**2);before=physical(w);w.run_until(170)
  physical_equal=physical(w)==m['final_physical'];receipts=[exact_receipt(w.runtime.receipt(x['id']))for x in m['requests']]
  rows.append({'case_id':name,'parent':str(snap.relative_to(ROOT)),'parent_sha256':sha(snap),'from_tick':77,'to_tick':170,'preparations':0,'diagnostic_forks':0,'continuations':0,'technical_continuations':1,'before':before,'final':physical(w),'checks':{'physical_final_equal':physical_equal,'receipts_by_id_equal':receipts==[x['receipt']for x in m['requests']]}})
 out={'schema':'CPC8R.contact_cardinality.technical_restore.v1','cases':rows,'status':'PASS'if all(all(r['checks'].values())for r in rows)else'FAIL'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out))
