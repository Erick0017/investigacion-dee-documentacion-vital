"""Do not mistake equal-phase RAW samples for a tick-by-tick fixed point."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
from capacidades.integracion_situada_01 import ic_native_core as n
life='MI01_VARIACION_LIBRE_490';r=Store().record('E1_MI01_MAIN');fork('E1_MI01_MAIN',life)
atomic_json(E/'VARIACION_LIBRE_PROTOCOLO_490.json',{'parent_snapshot_sha256':r['snapshot_sha256'],'parent_tick':r['physical']['tick'],'ticks':67,'inputs':0,'purpose':'All previous endpoints25757/26762/27834 and free201 are separated by multiples67. Equal RAW there is not proof of constant RAW between ticks. Record every consecutive tick and original phase3 without any material query.','not_claimed':'A repeated array is not a toroidal packet lineage, complete causal-state return, memory or infinite stability.'})
def fn(a):
    initial=physical(a.world,occupation=True);start=a.tick;before=E/(life+'.INITIAL.deetsnap.gz');a.save(before);x=Snapshot(before);assert not x.pending;rows=[]
    sites=[('negative7',[31,59,26],[-1,0,0]),('positive7',[11,59,23],[1,0,0]),('lateral7',[11,48,29],[1,0,0]),('acquired145',[10,56,26],[1,0,0]),('selector40',[40,35,55],None)]
    for step in range(68):
        a.run_until(start+step);p=physical(a.world,occupation=True);obs=[]
        for label,site,vector in sites:
            v=n.obs(a,site);qualified=bool(vector is not None and v['state']==1 and v['semantic']==1 and v['s_reg']>0 and v['direction']==vector);obs.append({'label':label,'native':v,'qualified_original_direction':qualified})
        rows.append({'step':step,'physical':p,'ports':obs})
        if step in(1,11,41,67):a.save(E/(life+'.T'+str(a.tick)+'.deetsnap.gz'))
    after=E/(life+'.FINAL.deetsnap.gz');a.save(after);y=Snapshot(after);assert not y.pending
    return{'initial':initial,'rows':rows,'unique_RAW_hashes':len({q['physical']['RAW_sha256']for q in rows}),'same_RAW_at67':rows[0]['physical']['RAW_sha256']==rows[-1]['physical']['RAW_sha256'],'phase3_readings':[q for q in rows if q['physical']['tick']%67==3],'final':physical(a.world,occupation=True),'pending_before':x.pending,'pending_after':y.pending,'native_inputs_added':0}
v=run(life,'MI01_490_VARIACION_LIBRE',fn)['result'];print(json.dumps({'unique_RAW_hashes':v['unique_RAW_hashes'],'same_RAW_at67':v['same_RAW_at67'],'phase3':v['phase3_readings'],'final':v['final']},ensure_ascii=False))
