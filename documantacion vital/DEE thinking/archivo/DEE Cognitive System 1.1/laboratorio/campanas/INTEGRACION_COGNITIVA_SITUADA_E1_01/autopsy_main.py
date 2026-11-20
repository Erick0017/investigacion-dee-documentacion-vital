from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native_core as ic
protect_current();s=Store();name='AUTOPSY_MAIN_FIRST_LOSS_51';life='IC01_AUTOPSY_MAIN_51';out=EV/(name+'.json')
if out.exists():raise FileExistsError('No overwrite')
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
parent='estado/checkpoints/E1_INTEGRADO_MAIN.T3639.322242165084.deetsnap.gz'
s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint=parent)
def run(a):
    frames=[];snaps=[];S=[15,15,50]
    for t in range(3639,3651):
        a.run_until(t);raw=a.world.runtime.raw_copy();clock=a.world.runtime.clock_copy()
        sparse=[{'site':[i//(67*67),(i//67)%67,i%67],'raw':str(int(v)),'clock':str(int(clock[i])),'state':int(v&0xffffffff),'s_reg':int((v>>32)&65535),'direction':ic.obs(a,[i//4489,(i//67)%67,i%67])['direction']}for i,v in enumerate(raw)if int(v)!=0]
        k=t-3639;pred=ic.move(S,(1,1,0),k)
        frames.append({'tick':t,'predicted_unintervened_action_site':pred,'context':[ic.obs(a,ic.move(pred,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)],'all_nonzero_RAW':sparse,'global':physical(a.world,occupation=True)})
        if t in(3642,3643,3644,3645):
            path=EV/(name+'_T'+str(t)+'.deetsnap.gz');a.save(path);snaps.append({'path':str(path),'sha256':digest_file(path),'tick':t,'complete_owner_snapshot':True})
    return{'parent':parent,'frames':frames,'snapshots':snaps,'no_new_inputs':True,'coverage':'All nonzero RAW and their clocks globally at every recorded step; exact125-site local context. Full owner state at four decisive boundaries. Empty-site clocks outside local context remain in full snapshots, not all repeated in JSON.'}
r=s.mutate(life,'IC01_AUTOPSY_PASSIVE_REPLAY',run,{'source':digest_file(__file__),'scope':'Native replay from a real saved prefix, not a past inferred from final fields'});atomic_json(out,r);print(r['INSTRUMENTO'],flush=True)
