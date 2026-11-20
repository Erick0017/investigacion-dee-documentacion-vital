"""Two finite pre-Native general-environment plans; no target-aware actions."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    protocol=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R03.json';p=json.loads(protocol.read_text(encoding='utf8'))
    fixture=P/'codigo'/p['fixture']['file']
    if sha(fixture)!=p['fixture']['sha256']or p['fixture']['birth_count']!=61:raise ValueError('Frozen61source fixture required')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();paths=[]
    for condition in('nube','control'):
        def fi(label):return {'label':label,'literal':{'modo':'eci01-pi06-fiplus','condicion':'intacto',
            'izquierda':14,'derecha':3,'captura':'normal'},'max_native_ticks':208,'feedback':'omit','actuator':'closed'}
        plan={'schema':'DEE.PI06.fixed_phase_plan.v1','status':'SEALED','initial_tick':826449,
            'max_native_ticks':955,'registration_utc':stamp,
            'source_proof':{'protocol':str(protocol),'protocol_sha256':sha(protocol),
                'fixture':str(fixture),'fixture_sha256':sha(fixture),'source':p['source']},
            'description':'One exogenous material preparation in a general35,35,35box, not a correction aimed at the leftzero or a responsepolicy. Nube submits all61legalexperiences; expected58Applied/3RejectedOccupied from the fixedpreflight, preserving allactualreceipts. Control submits no newenvironmentalpacket. Both evolve268, perform originalintactFI14/3, evolve271 with the sameexternalRawSupportSafety67, and repeat originalFI14/3. All questions/readers are fixed, no newguard/cleaning/seedsearch/response-dependentchange. HostSafety stops both scientificinterpretation and latersteps if triggered; it is not regulation byDEE. If all originalFIwindows last198, q2−q1=469=7N; actual qnormalization is recorded. A cloud may form only transient activity, relax or leave no functionalbenefit.',
            'steps':[{'label':'AMBIENTE_'+condition.upper(),
                'literal':{'modo':'eci01-pi06-ambiente','condicion':condition,'captura':'global'},
                'max_native_ticks':268,'expected_new_ticks':268,'feedback':'omit','actuator':'closed'},
                fi('FI_COMUN_1'),
                {'label':'EVOLUCION_SEGURA271','literal':{'modo':'eci01-pi06-ambiente-evolucion','ticks':271,'captura':'global'},
                 'max_native_ticks':271,'expected_new_ticks':271,'feedback':'omit','actuator':'closed'},
                fi('FI_COMUN_2')]}
        out=P/'control'/('PLAN_AMBIENTE_'+condition.upper()+'_PI06_R03.json');write(out,plan)
        paths.append({'file':out.name,'sha256':sha(out)})
    value={'schema':'DEE.PI06.material_environment.finite_paired_plan_registration.R03',
        'registered_utc':stamp,'status':'SEALED_BEFORE_R03_NATIVE','plans':paths,
        'maximum_Native_ticks_both':1910,'fixed_worlds_requested':2,'new_Native_ticks_by_this_tool':0,
        'global_capture_budget_increment':{'characterization_frames_per_arm':15,'characterization_anchors_per_arm':2,
            'safe_evolution_frames_per_arm':16,'safe_evolution_anchors_per_arm':2,'total_pair_deltas':54,'total_pair_anchors':8},
        'admission_occupied_terminal_exception':'Only the61ambientinputs may resolveasRejectedOccupied without stopping. No unknown or nonterminal receipt is silently accepted.',
        'functional_queries_are_material':True,'same_complete_prefix_not_independent_replicas':True,
        'Root_must_approve_actual_remaining_storage_worldslots_ticks_and_time_before_material_start':True,
        'Native_executed':False}
    output=P/'control/PLANES_AMBIENTE_PAREADOS_PI06_R03.json';write(output,value)
    print(json.dumps({'proof':output.name,'sha256':sha(output),'plans':paths,'Native_executed':False}))
if __name__=='__main__':main()
