"""Small pure arithmetic checks of the auditor, not DEE experiments."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from referencias_eo02 import Policy,Environment,Consequence
from recalcular_eo02 import events_for,evaluate

def main():
    checks=[];root=Path(__file__).resolve().parent
    seal=json.loads((root/'SELLO_REFERENCIAS.json').read_bytes())
    digest=hashlib.sha256((root/'referencias_eo02.py').read_bytes()).hexdigest()
    assert digest==seal['code_sha256'];checks.append('frozen_policy_bytes_unchanged')
    p=Policy('adaptive_threshold');before=p.choose([0,13]);p.observe(Consequence(-1,True,False,False))
    assert before==-1 and p.estimate==13 and p.choose([0,13])==1
    checks.append('update_only_after_own_observed_contact')
    p=Policy('adaptive_threshold');p.observe(Consequence(-1,True,False,False,received=False));assert p.estimate==12
    e=Environment('puertas',14);p.observe(e.execute(-1,[0,14],actuator='nulled'));assert p.estimate==12
    checks.append('omission_and_null_actuator_do_not_teach_hidden_target')
    a,b=Environment('transaccion_visible',14,phase_visible=True),Environment('transaccion_visible',14,phase_visible=True)
    assert a.observations([0,14,0,1])[-1]==0
    a.execute(1,[0,14,0,0]);b.execute(-1,[0,14,0,0])
    assert a.observations([0,14,0,1])[-1]==1 and b.observations([0,14,0,1])[-1]==0
    checks.append('different_actions_have_independent_transaction_futures')
    def ep(start,end,raw):return{'ordinal':0,'domain':'puertas','start_tick':start,'end_tick':end,'environment_before':{'law':'test','created_at_tick':0},'external_credit_auditor_only':14,'raw_observations':raw,'actuator_mode':'closed','feedback':'real','phase_visible':False}
    cases=[{'life':'MAIN','file':'source','fork_parent':{'life_id':'external','tick':0},'episodes':[ep(0,10,[0,14])]},
        {'life':'AUX','file':'target','fork_parent':{'life_id':'MAIN','tick':10},'episodes':[ep(10,20,[0,13])]}]
    event=events_for(cases)['AUX'];result=next(x for x in evaluate(event)['results']if x['policy']=='adaptive_threshold')
    assert result['prefix_attempts']==1 and result['attempts']==1
    assert result['rows'][0]['inherited_reference_prefix']and result['rows'][0]['action']==-1
    assert not result['rows'][1]['inherited_reference_prefix']and result['rows'][1]['action']==1
    checks.append('fork_reference_inherits_its_exact_experience_prefix_without_counting_it_as_new')
    print(json.dumps({'checks':checks,'issues':[],'new_DEE_ticks':0,'new_worker_executions':0},ensure_ascii=False))
if __name__=='__main__':main()
