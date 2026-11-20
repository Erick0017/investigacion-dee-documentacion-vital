from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native as ic
protect_current();store=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('STREAM_R7_21','trained','intact',True),('CUT_POSTFORMED_22','trained','cut_action',True),('SHAM_POSTFORMED_23','trained','sham_action',True),('OPPOSITE_HISTORY_24','opposite','intact',True),('NO_CONSEQUENCE_TRAIN_25','omitted','intact',True),('PASSIVITY_R6_26','trained','intact',False)]
for name,history,mode,stream in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():print('ALREADY_DONE '+name,flush=True);continue
    if history=='trained':store.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz')
    else:
        store.fork('E1_SOCIAL_11',life,kind='DIAGNOSTIC_COPY')
        result=store.mutate(life,'IC01_MATCHED_HISTORY',lambda a:ic.train(a,episode=name+'_H',contexts=(-1,1)if history=='opposite'else(1,-1),feedback='paired'if history=='opposite'else'omit'),{'history':history,'source_sha256':digest_file(LAB/'ic_native.py')})
        atomic_json(EV/(name+'_H.json'),result)
    def run(a):
        pre=physical(a.world,occupation=True);rows=ic.situated(a,name=name,availability=(1,1,-1,-1,1,1),mode=mode,trace=False,compact=True,gap=0,stream=stream)
        return{'initial':pre,'native':rows,'final':physical(a.world,occupation=True)}
    result=store.mutate(life,'IC01_CONTROL_EXPANDED',run,{'history':history,'mode':mode,'stream':stream,'source_sha256':digest_file(LAB/'ic_native.py'),'shared_prefix_not_independent_replicates':True})
    atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
