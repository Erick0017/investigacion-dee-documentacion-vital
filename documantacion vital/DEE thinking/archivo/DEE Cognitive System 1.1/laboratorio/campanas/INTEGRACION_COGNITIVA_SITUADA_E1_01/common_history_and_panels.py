from pathlib import Path
import sys,json,time,importlib.util
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe,exact_receipt
from app.process_control import protect_current
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
sources=[('INTEGRATED_COST_SOCIAL_132','E1_INTEGRADO_COSTO_SOCIAL_01'),('INTEGRATED_NO_B_134','IC01_INTEGRATED_NO_B_134'),('INTEGRATED_RETURN_OMIT_137','IC01_INTEGRATED_RETURN_OMIT_137'),('INTEGRATED_NULL_138','IC01_INTEGRATED_NULL_138'),('INTEGRATED_SECOND_ENV_140','IC01_INTEGRATED_SECOND_ENV_140')]
spec={'frozen_before_new_tests':True,'common_raw_objects':[160,200,240,280],'one_material_probe_per_exact_fork':True,'content_reference_not_reintroduced':True,'scope':'Native magnitude opportunities outside the bounded Pendulum sin codec1..145. This is cross-context use of experience-modified reference, not demonstration of better Pendulum control. Histories are factual action/return/no-partner interventions. These are dependent branches, not independent learners.','criterion':'Same fixed direction decoder and physical input format for every history. Compute signs from physical outputs, not expected reference or scenario ID.'}
if not(EV/'COMMON_HISTORY_SPEC_154.json').exists():atomic_json(EV/'COMMON_HISTORY_SPEC_154.json',spec)
for key,source in sources:
    parent=json.loads((EV/(key+'.json')).read_text())['final_record']
    for value in spec['common_raw_objects']:
        if time.monotonic()>deadline:raise TimeoutError('Original deadline')
        name='COMMON_'+key+'_Q'+str(value)+'_154';life='IC01_'+name;out=EV/(name+'.json')
        if out.exists():continue
        s.fork(source,life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
        def common(a):
            initial=physical(a.world,occupation=True);t=70+67*max(0,(a.tick+8-70+66)//67);a.quantity.present_object(value,round_index=(t-70)//67);rr=[dict(r)for r in a.quantity.state['requests'][-2:]];a.run_until(t)
            return{'common_raw_object':value,'format_cue':5,'requests':[dict(r,receipt=exact_receipt(a.world.runtime.receipt(r['id'])))for r in rr],'quantity':observe(a.world,a.quantity.geometry['center']),'reference_hub':observe(a.world,a.quantity.geometry['reference_hub']),'initial':initial,'final':physical(a.world,occupation=True),'spec':spec}
        r=s.mutate(life,'IC01_COMMON_NATIVE_OPPORTUNITY_AFTER_DIFFERENT_ACTUAL_ENVIRONMENTAL_HISTORIES',common,{'source':digest_file(__file__),'factual_parent':parent['snapshot_sha256'],'no_future_returned_to_source':True});atomic_json(out,r)
    print('COMMON '+key,flush=True)

# Material old-function checks never consume protected parents. The unchanged
# panel implementation is reused, not a new invented capability definition.
sp=importlib.util.spec_from_file_location('_ic_existing_habitat_panel',ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/habitat.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
panels=[('PANEL_MAIN_REACHED_155','E1_INTEGRADO_MAIN'),('PANEL_INTEGRATED_STRESS_REACHED_156','E1_INTEGRADO_COSTO_SOCIAL_01'),('PANEL_CONSERVED_REACHED_157','IC01_STRESS_MATCHED_144'),('PANEL_DIRECT_REACHED_158','E1_SITUADO_DIRECTO_01')]
for name,source in panels:
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork(source,life,kind='DIAGNOSTIC_COPY')
    r=s.mutate(life,'IC01_AFFECTED_OLD_FUNCTIONS_MATERIAL_PANEL',lambda a:h.inherited_panel(a),{'reused_source':digest_file(h.__file__),'panel_material_not_passive':True,'no_parent_mutated':True,'implementation_unchanged':True});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
