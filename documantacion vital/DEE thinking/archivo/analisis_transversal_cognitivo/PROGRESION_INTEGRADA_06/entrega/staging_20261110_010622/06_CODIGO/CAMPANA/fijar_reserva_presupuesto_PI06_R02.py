"""Prospective reserve capture subset within fixed1600delta/100anchor budget."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    old=P/'control/RESERVA_FI_PI06_R01.json';oldvalue=json.loads(old.read_text(encoding='utf8'))
    baseline=P/'control/BASELINE_global_PI06_R01.json';source=json.loads(baseline.read_text(encoding='utf8'))
    if source['status']!='COMPLETED'or source['closed_card']['physical']['tick']!=825849:raise ValueError('Closed parent only')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();plans=[]
    for wait in (11,13):
        for label,condition in [('IZQ7','izq7'),('INTACTO','intacto')]:
            def fi(name,c,capture):return {'label':name,'literal':{'modo':'eci01-pi06-fiplus',
                'condicion':c,'izquierda':20,'derecha':7,'captura':capture},
                'max_native_ticks':208,'feedback':'omit','actuator':'closed'}
            plan={'schema':'DEE.PI06.fixed_phase_plan.v1','status':'SEALED','initial_tick':825849,
                'max_native_ticks':630+wait,'registration_utc':stamp,
                'source_proof':{'path':str(baseline),'sha256':sha(baseline),
                    'snapshot':source['closed_card']['snapshot'],'snapshot_sha256':source['closed_card']['snapshot_sha256'],
                    'reserve_R01_sha256':sha(old)},
                'description':'Heldout public operands20/7, dose7orintact and fixed initial wait'+str(wait)+'. Capture subset fixed prospectively for budget: first and third FIglobal, second FInormal with exactly the same q+4/q+6readers and all176oldinputs. No dose7matched sham exists in the sealed apparatus. The original phase normalizer may realign query windows; record real q rather than asserting independent phases. No valid outcome changes these steps. NULL/rejected/uncertain stops preserve the future.',
                'steps':[{'label':'ESPERA_PREVIA'+str(wait),'literal':{'modo':'eci01-pi06-evolucion','ticks':wait,'captura':'normal'},
                          'max_native_ticks':wait,'expected_new_ticks':wait,'feedback':'omit','actuator':'closed'},
                    fi('FI1_'+label,condition,'global'),fi('FI2_INTACTO','intacto','normal'),
                    {'label':'EVOLUCION6','literal':{'modo':'eci01-pi06-evolucion','ticks':6,'captura':'normal'},
                     'max_native_ticks':6,'expected_new_ticks':6,'feedback':'omit','actuator':'closed'},
                    fi('FI3_INTACTO','intacto','global')]}
            path=P/'control'/('PLAN_RESERVA_'+label+'_ESPERA'+str(wait)+'_PI06_R02.json')
            write(path,plan);plans.append({'file':path.name,'sha256':sha(path)})
    proof={'schema':'DEE.PI06.reserve.capture_budget.R02','status':'SEALED_BEFORE_RESERVED_NATIVE',
        'registration_utc':stamp,'prior_reserve_R01':{'file':old.name,'sha256':sha(old)},
        'scientific_conditions_unchanged':True,'prospective_capture_subset':'FI1global,FI2normal,FI3global for all4reservearms',
        'fixed_limits':{'delta_frames':1600,'anchors':100},
        'budget_after_baseline_development_reserve':{'baseline':{'deltas':23,'anchors':2},
            'development4arms_x3FIglobal':{'deltas':792,'anchors':36},
            'reserve4arms_x2FIglobal':{'deltas':528,'anchors':24},
            'total_deltas':1343,'total_anchors':62,'remaining_deltas':257,'remaining_anchors':38},
        'capture_mode_changes_no_public_operand_or_material_reader':True,
        'not_new_Native_experiment':True,'Native_executed':False,'plans':plans}
    output=P/'control/RESERVA_CAPTURA_PRESUPUESTO_PI06_R02.json';write(output,proof)
    print(json.dumps({'proof':output.name,'sha256':sha(output),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
