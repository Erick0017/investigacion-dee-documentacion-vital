"""Exact saved-neighbour analysis: normal template vs actual B context."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
src=json.loads((E/'MI01_B_OPERANDOS_306.json').read_bytes())['data']['result']['frames'];out=[]
for t in(23865,24200):
    pre=next(z for z in src if z['tick']==t);post=next(z for z in src if z['tick']==t+1);B=pre['center']['site'];alive=[z for z in pre['context125']if z['site']!=B and all(min((z['site'][j]-B[j])%67,(B[j]-z['site'][j])%67)<=1 for j in range(3))and z['state']>0 and z['semantic']!=5]
    grad=[0,0,0]
    for z in alive:
        off=[((z['site'][j]-B[j]+33)%67)-33 for j in range(3)]
        for j in range(3):grad[j]-=off[j]*z['s_reg']
    out.append({'pre_tick':t,'pre_native_B':pre['center'],'nonzero_neighbours':alive,'gradient_from_these_state_positive_neighbours':grad,'gradient_direction':[(x>0)-(x<0)for x in grad],'measured_post_B':post['center'],'source_snapshot':pre['snapshot'],'source_sha256':pre['sha256'],'note':'This reconstructs neighbour contributions, NOT a complete replacement of the official tick. Matter-survival conditions apply before direction use. The first response used a43 context at the old reference hub; the nominal reference site was empty.'})
atomic_json(E/'CONTEXTO_B_307_0TICKS.json',{'cases':out,'native_ticks':0,'interpretation':'Do not treat current B as an intact canonical quantity session merely from its interface names. The second arrival145 succeeds but lacks the former43 local context, while actual object57 is still present. No global erasure or toroidal cause is inferred from this alone.'});print(json.dumps(out,ensure_ascii=False),flush=True)
