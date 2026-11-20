from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file,observe
from app.process_control import protect_current
import ic_external as ext
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
expected=json.loads((EV/'MAIN_OWN_ACQUISITION_37.json').read_text())['INSTRUMENTO']['snapshot_sha256'];parent=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
cases=[('COST_NATIVE_73','cost','closed','omit',81017),('COST_RETURN_OMIT_74','omit','closed','omit',81017),('COST_ACTION_NULL_75','cost','nulled','omit',81017),('COST_DELAY_76','cost','delay1','omit',81017),('COST_SEED_RESERVE_77','cost','closed','omit',81031),('COST_READER_PROBE_78','cost','closed','probe',81017)]
for name,feedback,mode,reader,seed in cases:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    life='IC01_'+name;out=EV/(name+'.json')
    if out.exists():continue
    s.fork('E1_INTEGRADO_MAIN',life,kind='CANDIDATE'if name=='COST_NATIVE_73'else'DIAGNOSTIC_COPY',checkpoint=str(parent.relative_to(s.root)))
    def trial(a,steps):return ext.run(a,steps=steps,seed=seed,mode=mode,readout='magnitude',feedback=feedback,reader=reader,codec=2,stop_invalid=3)
    prefix=s.mutate(life,'IC01_COST_EXTERNAL_FIRST3',lambda a:trial(a,3),{'before':'Fixed sin codec, native prepared magnitude comparator, raw actual cost via fixed acquisition channels. This does not predeclare learning or competent control. Stop after3 invalid outputs or24 total steps. Common cue73 after the3-step prefix in a diagnostic copy, no new reference.', 'sources':{p.name:digest_file(p)for p in[LAB/'ic_external.py',Path(__file__)]},'condition':{'feedback':feedback,'mode':mode,'reader':reader,'seed':seed}});atomic_json(EV/(name+'_PREFIX3.json'),prefix)
    prefix_rec=s.record(life);probe_id=life+'_COMMON'
    s.fork(life,probe_id,kind='DIAGNOSTIC_COPY')
    def common(a):
        pre=physical(a.world,occupation=True);t=70+67*max(0,(a.tick+6-70+66)//67);k=(t-70)//67;a.quantity.present_object(73,round_index=k);requests=[dict(r)for r in a.quantity.state['requests'][-2:]];a.run_until(t)
        return{'initial':pre,'current_object_raw':73,'same_format_cue':5,'future_reference_not_reintroduced':True,'native':observe(a.world,a.quantity.geometry['center']),'reference_hub':observe(a.world,a.quantity.geometry['reference_hub']),'reference_site':observe(a.world,a.quantity.geometry['reference_site']),'context':[observe(a.world,[(a.quantity.geometry['center'][i]+v[i])%67 for i in range(3)])for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)for v in[(x,y,z)]],'requests':[dict(r,receipt=ext.exact_receipt(a.world.runtime.receipt(r['id'])))for r in requests],'final':physical(a.world,occupation=True)}
    probe=s.mutate(probe_id,'IC01_COMMON_NATIVE_OPPORTUNITY_AFTER_ACTUAL_COST_HISTORY',common,{'shared_three_step_prefix':prefix_rec['snapshot_sha256'],'not_an_external_replay_or_a_future_returned_to_parent':True});atomic_json(EV/(name+'_COMMON.json'),probe)
    if prefix['result']['final_environment'].get('stop_reason'):continuation=None
    else:continuation=s.mutate(life,'IC01_COST_EXTERNAL_CONTINUE21',lambda a:trial(a,21),{'same_life_no_environment_reset':True,'source':digest_file(LAB/'ic_external.py')})
    if continuation:atomic_json(EV/(name+'_CONTINUATION.json'),continuation)
    atomic_json(out,{'name':name,'life':life,'prefix3':prefix,'common_probe_separate_branch':probe,'continuation_same_parent':continuation,'prefix_record':prefix_rec,'scope':'Consequence-dependent native scalar acquisition attempt, not an externally trained control policy. Probes are material and remain in their own diagnostic futures.'});print(name+' '+str(s.record(life)['physical']['tick']),flush=True)
