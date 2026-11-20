"""Bounded causal reconstruction of the unplanned zero-load premature join."""
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.regulacion.native_feedback import prepare,record,neighborhood
from dee_thinking.persistence import save_world_snapshot
from dee_thinking import _native as d
out=ROOT/'resultados/regulacion/NR_PREMATURE_ZERO_JOIN';out.mkdir(parents=True,exist_ok=False)
target=(31,35,27)
(out/'PREDICTION_BEFORE.json').write_text(json.dumps({'target_tick':1,'target_site':target,
 'prediction':'V1 gate1 lane-1/c+ and gate1 lane+1/c- both point into the empty target atT1. Their zero loads conceal their interaction from a scalar mass observer; direction reduction should produce(0,-1,+1). V2 lacks the first participant.',
 'scope':'Causal reconstruction from fixed source geometry, not an organism prediction or a new independent learning trial.'},indent=2),encoding='utf-8')
frames=[]
for family,lanes in(('v1',(-1,1)),('v2',(1,))):
 w,g=prepare(medium=-1,n=67,lanes=lanes)
 pre=neighborhood(w,target);contributors=[]
 for row in pre:
  q=row['site'];delta=[(target[i]-q[i]+33)%67-33 for i in range(3)]
  if row['state']>0 and row['semantic']!=5 and delta==row['direction'] and delta!=[0,0,0]:contributors.append(row)
 sums=[sum(r['direction'][i] for r in contributors) for i in range(3)]
 reduction=[(v>0)-(v<0) for v in sums]
 cp0=save_world_snapshot(w,out/(family+'_T0.deetsnap.gz'));w.run_until(1)
 post=record(w,target);cp1=save_world_snapshot(w,out/(family+'_T1.deetsnap.gz'))
 frames.append({'family':family,'kind':'TECHNICAL_RECONSTRUCTION_OF_PRIOR_PREPARATION','initial_records':len(w.recipe.placements),
  'pre_target':next(r for r in pre if r['site']==list(target)),'pre_Moore27':pre,'incoming_records':contributors,
  'calculated_sum_load':sum(r['s_reg'] for r in contributors),'calculated_sum_direction':sums,'calculated_sign_direction':reduction,
  'post_target':post,'post_Moore27':neighborhood(w,target),'storage':[cp0,cp1],
  'covered_segment':'ExactlyT0→T1 at a declared empty destination. No unique identity is inferred after this segment.'})
(out/'OBSERVACIONES.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'family':r['family'],'contributors':len(r['incoming_records']),'sum_load':r['calculated_sum_load'],'post':r['post_target']} for r in frames]))
