"""Passive exact local reducer candidates; never advances or feeds E1.
The full saved state and pending agenda remain the causal source, not a target.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
cases=[('CORREDOR139',E/'MI01_CORREDOR_139.PRIMER_FALLO_PREVIO.deetsnap.gz',E/'MI01_CORREDOR_139.PRIMER_FALLO.deetsnap.gz',[66,59,55]),('RETORNO185',E/'MI01_RETORNO_DIAG_185.PRIMER_FALLO_PREVIO.deetsnap.gz',E/'MI01_RETORNO_DIAG_185.PRIMER_FALLO.deetsnap.gz',[37,40,43])]
out=[]
for name,pre,post,target in cases:
    a=Snapshot(pre);b=Snapshot(post);incoming=[];context=[]
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                if (dx,dy,dz)==(0,0,0):continue
                p=[(target[0]+dx)%a.N,(target[1]+dy)%a.N,(target[2]+dz)%a.N];q=a.observation(p)
                if q['raw']!='0':context.append(q)
                if q['direction']!=[0,0,0]and[(p[j]+q['direction'][j])%a.N for j in range(3)]==target:incoming.append(q)
    sums=[sum(z['direction'][j]for z in incoming)for j in range(3)];direction=[(x>0)-(x<0)for x in sums];load=min(19664,sum(z['s_reg']for z in incoming))
    out.append({'id':name,'pre_path':str(pre.relative_to(R)),'pre_sha256':sha(pre),'post_path':str(post.relative_to(R)),'post_sha256':sha(post),'pre_target':a.observation(target),'post_target':b.observation(target),'incoming_by_frozen_directional_source_test':incoming,'nonzero_neighbour_context':context,'reducer_if_empty_branch':{'source_count':len(incoming),'sum_vector':sums,'direction':direction,'s_reg':load},'scope':'Exact candidate source relation from the frozen helper. Only attributes the empty-site reducer when its earlier branches do not supersede it. No unique carrier IDs or whole-kernel reversibility inferred.'})
atomic_json(E/'RECONSTRUCCION_LOCAL_187_0TICKS.json',{'cases':out,'source_kernel_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31','native_ticks':0})
print(json.dumps(out,ensure_ascii=False),flush=True)
