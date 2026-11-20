from pathlib import Path
import sys,time,json,random
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native_core as ic
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
# Entire reserve fixed before any response. Seed is auditor-only.
contexts=(-1,-1,-1,1,1,-1,1,1,1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,1,1,-1,-1,-1,1,-1,1,1,-1,-1)
cases=[('RESERVED_SHUNT_46','trained','a_only','intact'),('RESERVED_SHAM_47','trained','sham','intact'),('RESERVED_OPPOSITE_48','opposite','a_only','intact'),('RESERVED_RETURN_OMIT_49','trained','a_only','omit_return'),('RESERVED_NO_TEACH_50','omitted','a_only','intact')]
for name,history,shunt,mode in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    if history=='trained':s.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz')
    else:
        s.fork('E1_SOCIAL_11',life,kind='DIAGNOSTIC_COPY');r=s.mutate(life,'IC01_RESERVED_HISTORY',lambda a:ic.train(a,episode=name+'_H',contexts=(-1,1)if history=='opposite'else(1,-1),feedback='paired'if history=='opposite'else'omit'),{'source_sha256':digest_file(LAB/'ic_native_core.py'),'history':history});atomic_json(EV/(name+'_H.json'),r)
    def run(a):
        pre=physical(a.world,occupation=True);rows=ic.situated(a,name=name,availability=contexts,mode=mode,trace=False,compact=True,gap=0,stream=True,shunt=shunt)
        return{'initial':pre,'contexts_frozen':list(contexts),'native':rows,'final':physical(a.world,occupation=True)}
    r=s.mutate(life,'IC01_RESERVED_SHUNT',run,{'shunt':shunt,'history':history,'mode':mode,'source_sha256':digest_file(LAB/'ic_native_core.py'),'reserve_before_results':list(contexts),'shared_prefix':True});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
