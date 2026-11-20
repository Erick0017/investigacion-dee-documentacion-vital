"""Frozen independent references, never controllers for an evaluated DEE world.

Policy functions receive current raw observations and their own past actions /
observed consequences only. Hidden capacity credit and transaction state live
solely in Environment, which produces consequences AFTER a chosen action.
Each reference owns its own environment and transaction future.
"""
from dataclasses import dataclass
import random

REVISION='EO02.external_references.frozen.v1'
RANDOM_SEEDS=(1001,1002,1003,1004,1005,1006,1007,1008)
INITIAL_ESTIMATE=12

@dataclass
class Consequence:
    action:int
    contact:bool
    completed_step:bool
    completed_transaction:bool
    received:bool=True
    visible_phase:int|None=None

class Policy:
    def __init__(self,name,seed=None):
        self.name=name;self.rng=random.Random(seed);self.estimate=INITIAL_ESTIMATE
        self.n=0;self.prepared_action=None
    def choose(self,observations,*,phase_visible=False):
        """No environment, desired action, calibration or future parameter."""
        obs=list(observations)
        if self.name=='fixed_left':return 1
        if self.name=='fixed_right':return -1
        if self.name=='alternating':return 1 if self.n%2==0 else -1
        if self.name=='random':return self.rng.choice((-1,1))
        if self.name=='adaptive_phase'and phase_visible and obs[-1]==1 and self.prepared_action is not None:
            return -self.prepared_action
        left=sum(obs[::2]);right=sum(obs[1::2])
        # In the phase-aware reference the last public bit describes stage,
        # not workload; its interpretation is explicit prepared protocol.
        if self.name=='adaptive_phase'and phase_visible:
            left,right=obs[0],obs[1]
        return 1 if left+self.estimate>=right else -1
    def observe(self,result):
        self.n+=1
        if not result.received:return
        if self.name not in('adaptive_threshold','adaptive_phase'):return
        if result.contact and not(self.name=='adaptive_phase'and result.visible_phase==1):
            self.estimate=max(-64,min(64,self.estimate-result.action))
        if self.name=='adaptive_phase'and result.visible_phase is not None and result.completed_step:
            self.prepared_action=result.action if result.visible_phase==0 else None

class Environment:
    """Bounded task model only. It never selects a policy action."""
    def __init__(self,domain,credit,*,phase_visible=False):
        if domain not in('puertas','trabajadores','transaccion','transaccion_visible'):raise ValueError(domain)
        self.domain=domain;self.credit=int(credit);self.prepared_by=None
        self.phase_visible=bool(phase_visible);self.attempts=0;self.completed_steps=0;self.transactions=0
    def observations(self,exogenous):
        result=list(exogenous)
        if self.phase_visible:
            # Current phase belongs to THIS reference's evolving environment,
            # never copied from the archived DEE transaction future.
            if len(result)!=4:raise ValueError('Visible phase codec requires four explicit channels')
            result[-1]=int(self.prepared_by is not None)
        return result
    def execute(self,action,observations,*,actuator='closed',feedback='real'):
        self.attempts+=1;phase=int(self.prepared_by is not None)
        moved=action in(-1,1)and actuator=='closed'
        transaction=self.domain.startswith('transaccion')
        if transaction and phase:
            accepted=bool(moved and action!=self.prepared_by)
        else:
            left,right=observations[:2]
            eligible=1 if left+self.credit>=right else -1
            accepted=bool(moved and action==eligible)
        commit=bool(transaction and phase and accepted)
        if transaction and accepted:self.prepared_by=None if phase else action
        self.completed_steps+=int(accepted);self.transactions+=int(commit)
        contact=bool(moved and not accepted)
        received=feedback!='omit'
        # The explicit decoupled arm inverts the sensed posture, not the
        # service result. No correct action is reconstructed for the policy.
        sensed_action=-action if feedback=='decoupled'and contact else action
        return Consequence(action=sensed_action,contact=contact,completed_step=accepted,
            completed_transaction=commit,received=received,
            visible_phase=phase if self.phase_visible else None)

def policy_specs():
    return [('fixed_left',None),('fixed_right',None),('alternating',None),
        *[('random',seed)for seed in RANDOM_SEEDS],('adaptive_threshold',None),('adaptive_phase',None)]

def evaluate(events):
    """Observational task replay; each policy has an independent task future.

    Exogenous raw measurements and resets are shared. Internal pending states
    are NOT forced equal after actions differ. No disk files are written here.
    This is archived benchmark arithmetic, not native or service execution.
    """
    results=[]
    for name,seed in policy_specs():
        policy=Policy(name,seed);envs={};rows=[]
        for event in events:
            domain=event['domain'];key=event['environment_identity']
            old=envs.get(domain)
            if old is None or old[0]!=key:
                environment=Environment(domain,event['external_credit'],phase_visible=event.get('phase_visible',False))
                envs[domain]=(key,environment)
            else:environment=old[1]
            obs=environment.observations(event['observations'])
            action=policy.choose(obs,phase_visible=environment.phase_visible)
            before=policy.estimate
            outcome=environment.execute(action,obs,actuator=event.get('actuator','closed'),feedback=event.get('feedback','real'))
            policy.observe(outcome)
            rows.append({'case':event['case'],'ordinal':event['ordinal'],'domain':domain,'observations':obs,
                'action':action,'completed_step':outcome.completed_step,'completed_transaction':outcome.completed_transaction,
                'contact':outcome.contact,'feedback_received':outcome.received,'estimate_before':before,'estimate_after':policy.estimate,
                'independent_environment_phase_after':int(environment.prepared_by is not None)})
        results.append({'policy':name,'seed':seed,'attempts':len(rows),'completed_steps':sum(r['completed_step']for r in rows),
            'completed_transactions':sum(r['completed_transaction']for r in rows),'rows':rows})
    return {'revision':REVISION,'initial_estimate':INITIAL_ESTIMATE,'random_seeds':list(RANDOM_SEEDS),
        'policy_count':len(results),'results':results,
        'scope':'Independent task-model reference calculation, never controlling DEE; not a CPU/intelligence benchmark. Adaptive phase uses a prepared public stage protocol only when that sensor is actually present.'}
