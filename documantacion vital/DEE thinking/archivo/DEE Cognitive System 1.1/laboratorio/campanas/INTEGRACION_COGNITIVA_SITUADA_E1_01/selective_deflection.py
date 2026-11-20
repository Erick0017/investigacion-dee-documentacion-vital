from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,ic_native_core as ic
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
prediction={'before_new_tests':'At3643 two observed opposite sources [19,19,50]XY140 and [21,21,50](-X,-Y)0 point to[20,20,50]. At3644 direction cancels, at3645 that carrier disappears. A generic Z0 at[22,22,50]3642 should divert the already formed zero contribution off plane without supplying choice/content. Sham equal dose is9Z away. All outcomes, including rejections, remain.', 'no_general_regulation_claim':True}
for name,mode in [('CAUSAL_ZERO_DIVERT_53','divert'),('CAUSAL_ZERO_SHAM_54','sham'),('CAUSAL_ZERO_NONE_55','none')]:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/E1_INTEGRADO_MAIN.T3639.322242165084.deetsnap.gz')
    def run(a):
        pre=physical(a.world,occupation=True);rr=[];frames=[]
        if mode!='none':
            target=[22,22,50]if mode=='divert'else[22,22,59];rr.append(ic.arrive(a,'IC01.'+name+'.counterflow',target,(0,0,1),3642,0))
        h=body.attach(a)
        try:
            for t in list(range(3639,3649))+[3650,3691]:
                a.run_until(t);sites={(20,20,50),(21,21,50),(22,22,50),(15,15,50),(23,23,50)}
                sites.update(tuple(ic.move([15,15,50],(1,1,0),t-3639))for _ in[0])
                frames.append({'tick':t,'sites':[ic.obs(a,p)for p in sorted(sites)],'collision_context':[ic.obs(a,ic.move([20,20,50],(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if t in(3642,3643,3644,3645)else[],'global':physical(a.world,occupation=True)})
        finally:h['detach']()
        return{'prediction_frozen':prediction,'mode':mode,'initial':pre,'frames':frames,'native_frames':h['frames'],'requests':ic.receipts(a,rr),'final_action':ic.obs(a,[15,15,50]),'final':physical(a.world,occupation=True)}
    r=s.mutate(life,'IC01_SELECTIVE_NATIVE_ZERO_DEFLECTION',run,{'source':digest_file(__file__),'prediction':prediction,'no_information_or_state_copy':True});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
