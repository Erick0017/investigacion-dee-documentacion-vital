"""Predeclared common protocol; every branch starts at the reached24-step state.

The external mixed actuator is prepared gain1+gain1 wiring, not a claim of
native composition. All native social access opportunities are symmetrical.
"""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,observe,physical
from app.process_control import protect_current
import ic_external as ext
import delayed_social as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('INTEGRATED_COST_SOCIAL_132','E1_INTEGRADO_COSTO_SOCIAL_01',18,'full','closed','cost',False,False),('INTEGRATED_OPPOSITE_133','IC01_INTEGRATED_OPPOSITE_133',45,'full','closed','cost',False,False),('INTEGRATED_NO_B_134','IC01_INTEGRATED_NO_B_134',18,'no_partner','closed','cost',False,False),('INTEGRATED_CUT_135','IC01_INTEGRATED_CUT_135',18,'cut','closed','cost',False,False),('INTEGRATED_SHAM_136','IC01_INTEGRATED_SHAM_136',18,'sham','closed','cost',False,False),('INTEGRATED_RETURN_OMIT_137','IC01_INTEGRATED_RETURN_OMIT_137',18,'full','closed','omit',False,False),('INTEGRATED_NULL_138','IC01_INTEGRATED_NULL_138',18,'full','nulled','cost',False,False),('INTEGRATED_SENSOR_CLAMP_139','IC01_INTEGRATED_SENSOR_CLAMP_139',18,'full','closed','cost',True,False),('INTEGRATED_SECOND_ENV_140','IC01_INTEGRATED_SECOND_ENV_140',18,'full','closed','cost',False,True)]
spec={'schema':'IC01.integrated.cost.social.reserve.v1','frozen_cases':cases,'parent_life':'IC01_COST_NATIVE_73','parent_tick_required':4894,'horizon_steps':12,'stop_rule':'3 consecutive out-of-domain magnitude readings, not neutral active outputs','social_query':'Fixed56-tick retention then zero-load readers on both branches; private B contents never enter E1 through Python','motor':'Native quantity sign gain1 + both physically qualified social signs gain1, clipped2; all read simultaneously. Prepared external wiring, not native learned composition.','future_cost':'Actual rounded/clipped environmental cost delivered unchanged through native acquisition interface','no_promised_success':True,'sources':{p.name:digest_file(p)for p in[Path(__file__),LAB/'delayed_social.py',LAB/'ic_external.py']}}
if not(EV/'INTEGRATED_RESERVE_SPEC_132.json').exists():atomic_json(EV/'INTEGRATED_RESERVE_SPEC_132.json',spec)
for name,life,value,smode,mode,feedback,clamp,reset in cases:
    if time.monotonic()>deadline:raise TimeoutError('Fixed campaign deadline')
    out=EV/(name+'.json')
    if out.exists():continue
    if not(s.root/'estado/vidas'/life/'VIDA.json').exists():
        if s.record('IC01_COST_NATIVE_73')['physical']['tick']!=4894:raise ValueError('Parent changed; no silent alternate snapshot')
        s.fork('IC01_COST_NATIVE_73',life,kind='CANDIDATE'if name=='INTEGRATED_COST_SOCIAL_132'else'DIAGNOSTIC_COPY')
    def run(a,steps,initial):
        before=physical(a.world,occupation=True)
        if initial:p=social.begin(a,name=name,value=value,mode=smode)
        else:p=social.get(a)['plan']
        original=a.run_until;frames=[]
        def advance(t):frames.extend(social.advance_until(a,t,original,record=True))
        a.run_until=advance
        try:r=ext.run(a,steps=steps,seed=81031 if reset else 81017,mode=mode,readout='magnitude',feedback=feedback,reader='omit',reset=reset and initial,codec=2,stop_invalid=3,social_ports=p['banks'],clamp_sensor=clamp)
        finally:a.run_until=original
        r.update({'social_plan':p,'social_progress':social.get(a),'social_frames':frames,'reference_after':observe(a.world,a.quantity.geometry['reference_hub']),'initial_native_before_setup':before,'requests_social':[dict(q,receipt=ext.exact_receipt(a.world.runtime.receipt(q['id'])))for q in social.get(a)['plan']['requests']]})
        return r
    first=EV/(name+'_FIRST3.json')
    if not first.exists():atomic_json(first,s.mutate(life,'IC01_INTEGRATED_ACTUAL_EXTERNAL_AND_NATIVE_SOCIAL_FIRST3',lambda a:run(a,3,True),spec))
    r0=json.loads(first.read_text());record=s.record(life)
    last=s.mutate(life,'IC01_INTEGRATED_CONTINUATION_SEPARATE_RESTORE',lambda a:run(a,9,False),{'same_world_and_environment':True,'first3_snapshot':record['snapshot_sha256'],'source':spec['sources']})
    atomic_json(EV/(name+'_CONTINUE9.json'),last)
    atomic_json(out,{'name':name,'life':life,'first3_file':first.name,'continuation_file':name+'_CONTINUE9.json','first3_snapshot':record,'final_record':s.record(life),'scope':'One native history uses an acquired mutable magnitude reference, current external observations, a privately produced received relation and fixed retrieval after56ticks. Mixed motor is a declared external apparatus, not learned native compositionality.'})
    print(name+' '+str(last['INSTRUMENTO']['tick']),flush=True)
