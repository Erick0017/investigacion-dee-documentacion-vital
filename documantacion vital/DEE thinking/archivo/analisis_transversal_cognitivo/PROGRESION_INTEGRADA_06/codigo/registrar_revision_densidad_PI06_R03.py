"""Record pre-Native exogenous design revision without replacing prior files."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=P/'codigo/FIXTURE_PI06_AMBIENTE_R03.json';new=P/'codigo/FIXTURE_PI06_AMBIENTE_R03_R02.json'
    a=json.loads(old.read_text(encoding='utf8'));b=json.loads(new.read_text(encoding='utf8'))
    if a['Bernoulli_probability']!=0.2 or b['Bernoulli_probability']!=0.4 or a['seed']!=b['seed']or b['birth_count']>64:raise ValueError('Literal independent design revision only')
    output=P/'control/REVISION_PROSPECTIVA_DENSIDAD_PI06_R03.json'
    value={'schema':'DEE.PI06.cloud_density.pre_Native_design_revision.R03',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'old':{'file':old.name,'sha256':sha(old),'Bernoulli_probability':0.2,'selected_sources':a['birth_count'],
            'status':'SUPERADO_NO_EJECUTADO','Native_ticks':0},
        'new':{'file':new.name,'sha256':sha(new),'Bernoulli_probability':0.4,'selected_sources':b['birth_count'],
            'status':'GEOMETRY_SEALED_ROOT_EXECUTION_GATE_PENDING','Native_ticks':0},
        'revision_requested_by_Root_before_any_R03_Native':True,
        'reason':'Offer a denser general material neighborhood given the frozen matter support threshold n_active>=6, without guaranteeing persistence. Density0.2 offers an expected5.2Moore-neighbors;0.4offers10.4in a full interior. This is a structural P0preparation choice, not a favorablefunctionalresult.',
        'same_seed_no_resampling':True,'same_box_center':[35,35,35],'same_side':5,
        'unchanged_state_semantic_load':[1,1,7],
        'observed_preflight_RAW_nonzero_selected':b['preflight_selected_nonzero_RAW_sites'],
        'admission_policy_requires_Root_clarification_before_Native':'Three selectedsources contain inheritedSEM4/state0RAW4<<60. No source/seed is changed to avoid them; their omission/rejection must be explicit and must not erase the oldsupport or be counted as appliedNativeinputs.',
        'no_final_functional_outcome_inspected':True,'Native_executed_by_this_tool':False,
        'limits':'Initial support opportunities are not a guarantee of subsequentselforganization or learning; direction, encounters, phase and inheritedanatomy remain relevant.'}
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':output.name,'sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':main()
