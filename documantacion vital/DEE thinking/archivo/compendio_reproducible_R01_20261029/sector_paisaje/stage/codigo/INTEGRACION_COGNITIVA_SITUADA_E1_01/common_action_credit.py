"""Refined held-current-input causal test, fixed native reader, no answer fed."""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe
from app.process_control import protect_current
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
histories=[('INTEGRATED_COST_SOCIAL_132','E1_INTEGRADO_COSTO_SOCIAL_01'),('INTEGRATED_NULL_138','IC01_INTEGRATED_NULL_138'),('INTEGRATED_RETURN_OMIT_137','IC01_INTEGRATED_RETURN_OMIT_137')]
spec={'before_new_cases':True,'histories':histories,'common_actual_object':230,'additional_whole_period_delays':[0,67,134],'current_input_identical_except_generic_interface_ID':True,'no_new_reference_or_strategy':True,'exploratory_hypothesis':'The coarse154 grid separated return histories but not action-null histories. Post-hub value and value available at the gradient event may differ within a full tick. Refine one common current magnitude and vary whole periods, without changing the fixed reader or decoder. These are mechanism follow-ups, not independent confirmatory replicas.','criterion':'Observe native+X/-X/neutral and raw/clock pre/post fields. A physical parameter difference alone is not counted as a changed decision.'}
if not(EV/'ACTION_CREDIT_SPEC_160.json').exists():atomic_json(EV/'ACTION_CREDIT_SPEC_160.json',spec)
for key,source in histories:
    parent=json.loads((EV/(key+'.json')).read_text())['final_record']
    for delay in(0,67,134):
        if time.monotonic()>deadline:raise TimeoutError('Original deadline')
        name='COMMON_ACTION_'+key+'_D'+str(delay)+'_160';life='IC01_'+name;out=EV/(name+'.json')
        if out.exists():continue
        s.fork(source,life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
        def trial(a):
            initial=physical(a.world,occupation=True);t=70+67*max(0,(a.tick+8-70+66)//67)+delay;a.quantity.present_object(230,round_index=(t-70)//67);requests=[dict(r)for r in a.quantity.state['requests'][-2:]];frames=[]
            sites={k:a.quantity.geometry[k]for k in('center','reference_hub','reference_site','object_site','object_hub')if k in a.quantity.geometry}
            for when in range(t-6,t+1):
                a.run_until(when);frames.append({'tick':when,'sites':{k:observe(a.world,p)for k,p in sites.items()},'context':[observe(a.world,[(a.quantity.geometry['center'][i]+v[i])%67 for i in range(3)])for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)for v in[(x,y,z)]]})
            return{'spec':spec,'initial':initial,'common_actual_object':230,'whole_period_delay':delay,'frames':frames,'quantity':observe(a.world,a.quantity.geometry['center']),'reference_hub':observe(a.world,a.quantity.geometry['reference_hub']),'requests':requests,'final':physical(a.world,occupation=True),'no_future_transferred_back':True}
        r=s.mutate(life,'IC01_ACTION_ENVIRONMENT_RETURN_COMMON_FUTURE_OPPORTUNITY',trial,{'source':digest_file(__file__),'parent':parent['snapshot_sha256'],'scope':spec});atomic_json(out,r)
    print('ACTION_CREDIT '+key,flush=True)
