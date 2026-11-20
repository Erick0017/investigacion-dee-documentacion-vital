"""Prospective diagnostic counterflow versus material sham, never a repair claim."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    proof=P/'control/DIFERENCIA_TERMINAL_IZQ_NONE_PI06_R01.json'
    source=json.loads(proof.read_text(encoding='utf8'))
    if source['tick']!=826449 or source['RAW_difference_count']!=1 or source['clock_difference_count']!=0:
        raise ValueError('Exact formed-state contrast required before intervention')
    difference=source['RAW_differences'][0]
    if difference['site']!=[52,48,47]or difference['izq']['state']!=1 or difference['izq']['s_reg']!=0 or difference['izq']['semantic']!=1 or difference['izq']['direction']!=[0,0,1]:
        raise ValueError('No substitution of the empirical formed source')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();plans=[]
    for condition in('contraflujo','sham'):
        plan={'schema':'DEE.PI06.fixed_phase_plan.v1','status':'SEALED','initial_tick':826449,
            'max_native_ticks':211,'registration_utc':stamp,
            'source_proof':{'file':str(proof),'sha256':sha(proof),'source_cut':source['sources']['izq'],
                'complete_frozen_source_required':True},
            'description':'Diagnostic intervention on the already formed state, not learned repair or an action of DEE. Both copies retain the exact original anatomy/history, age and clocks. One SEM1/state1/zero-load −Z birth atT+2; contraflow source52,48,51 versus off-path sham60,48,51. Advance3 then original intactFI14/3 at its unchanged q+4/q+6readers. With the old198tick calendar the whole sequence lasts201ticks and q826508; actual timing and outcome remain empirical. No response-dependent operation, newSEM4, clearing, RAW/clock edit or reinjection. The appearance, disappearance, stationary outcome or rerouting of the matched signature is measured; annihilation is not presumed.',
            'steps':[{'label':'INTERVENIR_'+condition.upper(),
                'literal':{'modo':'eci01-pi06-interrupcion','condicion':condition,'captura':'global'},
                'max_native_ticks':3,'expected_new_ticks':3,'feedback':'omit','actuator':'closed'},
                {'label':'FI_INTACTO','literal':{'modo':'eci01-pi06-fiplus','condicion':'intacto',
                    'izquierda':14,'derecha':3,'captura':'global'},'max_native_ticks':208,
                 'feedback':'omit','actuator':'closed'}]}
        path=P/'control'/('PLAN_INTERRUPCION_'+condition.upper()+'_PI06_R02.json')
        write(path,plan);plans.append({'file':path.name,'sha256':sha(path)})
    registration={'schema':'DEE.PI06.formed_state_interruption.preregistration.R02',
        'status':'SEALED_BEFORE_INTERVENTION_NATIVE','registration_utc':stamp,'plans':plans,
        'source_difference_proof':{'file':proof.name,'sha256':sha(proof)},
        'hypotheses':[
            'The formed +Z zero can be causally interrupted by a legal contrary −Z input before a phase-aligned original query; its material sham cannot act at that contact.',
            'A persistent adverse outcome after both arms would weaken this proposed intervention or show an inadequately isolated cause; it is preserved rather than followed by a new guard.',
            'An improvement only after the diagnostic intervention supports local causal contribution of the formed carrier/interaction. It does not show endogenous learned recovery, unique particle ancestry or absence of all other historical influences.'],
        'scores_and_denominators':'Two diagnostic lives, one extra material intervention and one original176inputFI in each. Both new births/readers are counted; zero and NULL remain distinct.',
        'paired_branches_not_independent_organisms':True,'changes_main':False,'changes_official_motor':False,
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    output=P/'control/PROTOCOLO_INTERRUPCION_FORMADA_PI06_R02.json';write(output,registration)
    print(json.dumps({'proof':output.name,'sha256':sha(output),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
