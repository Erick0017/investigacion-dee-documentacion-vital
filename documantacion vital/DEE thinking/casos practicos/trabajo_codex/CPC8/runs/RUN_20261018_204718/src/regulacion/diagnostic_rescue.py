"""Explicit actuator-rescue diagnostic forks; never a MAIN repair."""
import hashlib,json,sys,time
from array import array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.regulacion.native_feedback import record,neighborhood
from dee_thinking import _native as d
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot

out=ROOT/'resultados/regulacion/REG_V2_DIAGNOSTIC_ACTUATOR_R1';out.mkdir(parents=True,exist_ok=False)
observations=[]
for medium,case,label,key in ((1,'REG_V2_D21','P','1_0.P'),(-1,'REG_V2_D22','Q','1_1.Q')):
 config=json.loads((ROOT/'resultados/regulacion'/case/'CONFIG.json').read_text(encoding='utf-8'))
 g=config['geometry'];w,_=load_world_snapshot(ROOT/'resultados/regulacion'/case/'T9.deetsnap.gz')
 w.run_until(10);q=g['ports']['regulatory_action.'+key];before=record(w,q)
 parent_hash={'raw':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
 for sham in (False,True):
  e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q)
  e.raw=int(before['raw']) if sham else d.pack_record(1,114,*((0,0,1) if label=='P' else(-1,1,1)),1)
  e.label='Explicit prescribed actuator '+('SHAM' if sham else'RESCUE')+'; not acquired choice'
  child=w.diagnostic_fork([e],True);pre=neighborhood(child,q)
  child.run_until(12);contact=record(child,g['ports']['interception.'+key]);child.run_until(15)
  delivery=record(child,g['ports']['delivery.'+key])
  proof=save_world_snapshot(child,out/(case+('_sham' if sham else'_rescue')+'.deetsnap.gz'))
  observations.append({'parent':case,'medium':medium,'modality':'DIAGNOSTIC_FORK','intervention':'same RAW and preserved clock' if sham else'prescribed actuator RAW; clock preserved',
   'before':before,'edited_pre_neighborhood':pre,'parent_hash':parent_hash,'interception':contact,'delivery':delivery,'checkpoint':proof,
   'scope':'Tests availability of actuator/consequence path after return cut. A prescribed diagnostic action is not autonomous regulation.'})
  assert hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest()==parent_hash['raw']
  assert hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()==parent_hash['clock']
(out/'OBSERVACIONES.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'parent':r['parent'],'intervention':r['intervention'],'delivery':r['delivery']['s_reg']} for r in observations]))
