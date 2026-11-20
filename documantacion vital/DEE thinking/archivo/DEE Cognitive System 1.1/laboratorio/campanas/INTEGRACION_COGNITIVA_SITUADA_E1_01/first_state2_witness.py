"""Minimal native replay of the already bracketed6367..6385 interval."""
from pathlib import Path
import sys,json,time,shutil
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical
from app.process_control import protect_current
import ic_native_core as ic
protect_current();s=Store();name='STRESS_FIRST_STATE2_WITNESS_159';life='IC01_'+name
if(EV/(name+'.json')).exists():raise FileExistsError('No overwrite')
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
source=EV/'STRESS_REPLAY_ALL_148_T6367.deetsnap.gz';cp=s.root/'estado/checkpoints'/source.name
if not cp.exists():shutil.copyfile(source,cp)
s.fork('IC01_STRESS_REPLAY_ALL_148',life,kind='DIAGNOSTIC_COPY',checkpoint=str(cp.relative_to(s.root)))
def run(a):
    rows=[];snaps=[];first=None
    for at in range(6368,6386):
        pre=a.world.runtime.raw_copy();preclock=a.world.runtime.clock_copy();a.run_until(at);raw=a.world.runtime.raw_copy();clock=a.world.runtime.clock_copy();indices=[i for i,v in enumerate(raw)if v&0xffffffff==2];row={'tick':at,'state2_count':len(indices),'occupied':sum(bool(v&0xffffffff)for v in raw),'quantity':ic.obs(a,a.quantity.geometry['center']),'reference':ic.obs(a,a.quantity.geometry['reference_hub'])}
        if indices and first is None:
            first=at;context=[]
            for idx in indices[:3]:
                p=[idx//4489,(idx//67)%67,idx%67];cells=[]
                for x in range(-3,4):
                    for y in range(-3,4):
                        for z in range(-3,4):
                            q=ic.move(p,(x,y,z));i=(q[0]*67+q[1])*67+q[2];cells.append({'site':q,'pre_raw':str(pre[i]),'pre_clock':str(preclock[i]),'post_raw':str(raw[i]),'post_clock':str(clock[i])})
                context.append({'site':p,'context7cubed':cells})
            row['first_new_state2_context']=context
        if at in(6383,6384):
            path=EV/(name+'_T'+str(at)+'.deetsnap.gz');a.save(path);snaps.append({'path':str(path),'sha256':digest_file(path),'tick':at})
        rows.append(row)
    return{'rows':rows,'first_state2_tick':first,'snapshots':snaps,'no_new_inputs':True,'final':physical(a.world,occupation=True),'scope':'Native-only diagnostic interval. All needed inputs before6385 were already queued; next original external cost would enter6432, outside this interval. Mid-motor diagnostic snapshots are not offered as ready-to-resume external lives. Existing inherited prepared states4/3000/etc were incorrectly bracketed by the earlier observer first_other_state field; this witness explicitly measures state2, not any non1 state. First local state2 is not asserted to be the sole cause of global expansion.'}
r=s.mutate(life,'IC01_MINIMAL_NATIVE_BRACKET_STATE2',run,{'source':digest_file(__file__),'saved_source_sha256':digest_file(source),'new_diagnostic_not_archived_recalculation':True});atomic_json(EV/(name+'.json'),r);print(r['INSTRUMENTO'],flush=True)
