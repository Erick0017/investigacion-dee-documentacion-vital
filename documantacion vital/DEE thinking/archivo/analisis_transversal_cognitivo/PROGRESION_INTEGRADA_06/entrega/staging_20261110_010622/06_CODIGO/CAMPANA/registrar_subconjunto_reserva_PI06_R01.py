"""Prospective finite subset decision; never rewrites the original reserve."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    for wait in(11,13):
        for label in('IZQ7','INTACTO'):
            path=P/'control'/('PLAN_RESERVA_'+label+'_ESPERA'+str(wait)+'_PI06_R02.json')
            plan=json.loads(path.read_text(encoding='utf8'))
            if plan['status']!='SEALED'or plan['initial_tick']!=825849:raise ValueError('Preserve exact reserve plans')
            rows.append({'plan':path.name,'sha256':sha(path),'initial_wait':wait,
                         'status':'SELECTED_PROSPECTIVELY_FOR_EXECUTION'if wait==11 else'PREPARADO_NO_EJECUTADO'})
    output=P/'control/DECISION_SUBCONJUNTO_RESERVA_PI06_R01.json'
    value={'schema':'DEE.PI06.reserve.prospective_subset_decision.R01',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'decision_authority':'Root within the user-authorized finite PI06 campaign',
        'made_before_any_reserved_response_or_evaluation':True,
        'selected':'Only wait11: IZQ7 versus INTACTO from the same coherent825849prefix',
        'not_executed':'Both wait13plans remain intact, prepared and unexecuted. No replacement hidden condition.',
        'reason':'Reduce the factorial, preserve decisive comparison and leave the fixed world/storage/frame budget for an intervention on the formed carrier, a cold replay and continued same-world C2C use.',
        'plans':rows,'literal_steps_geometry_readers_decoder_unchanged':True,
        'reserved_changes_together':{'payload':{'development':0,'reserve':7},
            'public_operands':{'development':[14,3],'reserve':[20,7]},'pre_challenge_wait':11},
        'scope':'Local transfer of this predeclared compound variation. It does not isolate the three factors independently or test wait13/general phase robustness.',
        'capture_budget':{'baseline_delta_frames':23,'four_development_arms_delta_frames':792,
            'two_selected_reserve_arms_delta_frames':264,'planned_total_before_diagnostic_replay':1079,
            'fixed_delta_ceiling':1600,'planned_anchors_before_diagnostic_replay':50,'fixed_anchor_ceiling':100,
            'fixed_world_ceiling':12},
        'states_originals_or_preregistration_deleted':False,'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':output.name,'sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':main()
