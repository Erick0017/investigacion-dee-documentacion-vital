"""Locate the first mismatch, preserving local context and full predecessor."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
path=E/'MI01_EXTENSION_DIAG_136.T23768.deetsnap.gz';life='MI01_CORREDOR_139'
fork('MI01_CORREDOR_138',life)
def fn(a):
    start=a.tick;initial_site=[43,59,55];v=[1,0,0];rows=[];mismatch=False
    before=E/(life+'.T'+str(a.tick)+'.deetsnap.gz');a.save(before)
    for j in range(1,46):
        target=n.move(initial_site,v,j)
        a.run_until(start+j);z=n.obs(a,target)
        ok=z['state']==1 and z['semantic']==1 and z['s_reg']==145 and z['direction']==v
        rows.append({'tick':a.tick,'expected_site':target,'native':z,'signature_continues':ok,'context125':[n.obs(a,n.move(target,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if not ok else[]})
        if not ok:
            mismatch=True;pre=E/(life+'.PRIMER_FALLO_PREVIO.deetsnap.gz');shutil.copy2(before,pre);post=E/(life+'.PRIMER_FALLO.deetsnap.gz');a.save(post);break
        before=E/(life+'.T'+str(a.tick)+'.deetsnap.gz');a.save(before)
    return{'start_source':str(path.relative_to(R)),'rows':rows,'mismatch':mismatch,'final':physical(a.world,occupation=True),'scope':'First loss of this declared signature, not by itself unique carrier genealogy or global information erasure.'}
v=run(life,life,fn)['result'];print(json.dumps({'last':v['rows'][-1],'steps':len(v['rows'])},ensure_ascii=False),flush=True)
