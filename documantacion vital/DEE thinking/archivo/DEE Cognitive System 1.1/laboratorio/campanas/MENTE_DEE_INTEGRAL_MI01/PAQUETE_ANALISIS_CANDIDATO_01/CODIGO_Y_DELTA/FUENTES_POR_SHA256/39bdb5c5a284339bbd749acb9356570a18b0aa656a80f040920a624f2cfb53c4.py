"""First negative-reply path mismatch; complete fixed future retained."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.integracion_situada_01 import ic_native_core as n
source=E/'MI01_RETORNO_181.ANTES_RESPUESTA.deetsnap.gz';life='MI01_RETORNO_DIAG_185'
def execute():
    Store().import_state(source,life,'cpc9_integral_n67',sha(source))
    def fn(a):
        a.run_until(23930);site=[15,40,43];v=[1,0,0];rows=[]
        previous=E/(life+'.T23930.deetsnap.gz');a.save(previous)
        initial=n.obs(a,site)
        for k in range(1,26):
            a.run_until(23930+k);target=n.move(site,v,k);z=n.obs(a,target);good=z['state']==1 and z['semantic']==1 and z['s_reg']==145 and z['direction']==v
            row={'tick':a.tick,'site':target,'native':z,'signature_continues':good};rows.append(row)
            if not good:
                row['context125']=[n.obs(a,n.move(target,(dx,dy,dz)))for dx in(-2,-1,0,1,2)for dy in(-2,-1,0,1,2)for dz in(-2,-1,0,1,2)]
                pre=E/(life+'.PRIMER_FALLO_PREVIO.deetsnap.gz');shutil.copy2(previous,pre);post=E/(life+'.PRIMER_FALLO.deetsnap.gz');a.save(post);row['pre']=str(pre.relative_to(R));row['post']=str(post.relative_to(R));break
            previous=E/(life+'.T'+str(a.tick)+'.deetsnap.gz');a.save(previous)
        return{'initial':initial,'rows':rows,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'initial':v['initial'],'last':{k:v['rows'][-1][k]for k in('tick','site','native')},'nonzero_context':[z for z in v['rows'][-1].get('context125',[])if z['raw']!='0']},ensure_ascii=False),flush=True)
if __name__=='__main__':execute()
