"""¿Los recursos comunes de dos accesos interfieren cuando falta su cue?
Copias de control; no se interpreta silencio como NO ni se repara MAIN.
"""
import sys,json,gzip,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];SYS=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
sys.path.insert(0,str(SYS));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import mente_acumulativa_r02 as ma
from acumulacion_A05 import run,ses
def main():
    p=HERE/'PROTOCOLO_RECURSOS_A25.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps({'purpose':'Before native selector wiring, test same generic resources at both epsilon/zeta routes, without any token cue; compare exact-prefix no-resource arm, then original6first-use panel. Nohostselectionofbank.','arms':['MU_GENERIC_BOTH','MU_GENERIC_NONE'],'parent':'MU_MAIN currentown6learned afterA24','fixed_resources':'Both6resourcepatterns from existing MA02query, value7, select/back/restore fixed atphase+4/+5/+6','reader':'Same12gate prospectivereader','horizon':'endphase+7 then six queries, no correctingteacher'},ensure_ascii=False,indent=2),encoding='utf8')
    for life in['MU_GENERIC_BOTH','MU_GENERIC_NONE']:run('A25_FORK_'+life,'bifurcar','MU_MAIN',life,'--modalidad','DIAGNOSTIC_COPY')
    st=Store(SYS)
    def block(a,material):
        t=ma.phase(a.tick);rs=[];rows=[]
        if material:
            for token in ['epsilon','zeta']:
                v=ma.TOKENS[token]
                for sg in(-1,1):
                    for stage,k,z,di,arrival in [('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)]:
                        dv=(di*v[0],di*v[1],0);dest=ma.pos(v,k,z*sg)
                        ma.submit(a,'MU.resource.only.'+token+'.'+stage+'.'+str(sg),ma.add(dest,dv,-2),dv,7,t+arrival-2,rs)
        for tt in range(t,t+8):
            a.run_until(tt);rows.append({'tick':a.tick,'reader':ma.fixed_read(a)})
        return {'material_resources':material,'no_token_cue':True,'requests':ma.receipts(a,rs),'rows':rows}
    for life,material in [('MU_GENERIC_BOTH',True),('MU_GENERIC_NONE',False)]:
        r=st.mutate(life,'MU_GENERIC_RESOURCES_WITHOUT_CUE',lambda a:block(a,material))
        out=EV/(life+'.resource_primary.json.gz')
        if out.exists():raise FileExistsError(out)
        out.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
        print(json.dumps({'life':life,'tick':r['INSTRUMENTO']['tick']}),flush=True)
        ses('A26_PANEL_'+life,life,[{'contexto':k}for k in['zeta','epsilon','alfa','beta','gamma','delta']])
if __name__=='__main__':main()
