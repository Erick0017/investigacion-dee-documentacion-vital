"""Two disclosed actuator effects, not a planner or DEE action selector.

The private second operand is an environment fact. It enters the public
observation only after an already selected QUERY action. No host decision
uses availability to select an action. Quality arithmetic is post-commit
external evaluation, not an actor policy. No engine imports occur here.
"""
from pathlib import Path
import hashlib,json,re

VERSION='APD02.goal_clarification_environment.prospective.R01'
MAX_OPPORTUNITIES=4
TOKEN=re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]{0,95}$')
ACTION_CODEC={-1:'ACT',0:'QUERY',1:'QUERY'}
POLICY={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True}

def exact_operand(x):return type(x)is int and 0<=x<=32
def projection(sign):
    if sign is None:return None
    if type(sign)is not int or sign not in ACTION_CODEC:raise ValueError('Admitted physical direction or explicit absence only')
    return ACTION_CODEC[sign]

class GoalEnvironment:
    def __init__(self,*,task_id,text,left,second,second_initially_public,directory,quality,effects):
        if not isinstance(task_id,str)or not TOKEN.fullmatch(task_id):raise ValueError('Bounded synthetic goal ID required')
        if not isinstance(text,str)or not 1<=len(text)<=96:raise ValueError('Bounded literal cue required')
        if not exact_operand(left)or not exact_operand(second)or type(second_initially_public)is not bool:raise ValueError('Exact raw operands0..32 and explicit visibility required')
        self._directory=Path(directory).resolve();self._directory.mkdir(parents=True,exist_ok=False)
        self._quality=quality;self._effects=effects;self._private_second=second
        self._public={'task_id':task_id,'text':text,'left':left,'second':second if second_initially_public else None}
        self._opportunities=0;self._completed=False;self._uncertain=None;self._events=[]
    def observation(self):
        # No private value, reference operation, correct route, history table,
        # future seed or expected result is projected into this observation.
        return dict(self._public)
    def progress(self):
        return {'opportunities_used':self._opportunities,'max_opportunities':MAX_OPPORTUNITIES,
            'second_observed':self._public['second']is not None,'verified_file_goal_completed':self._completed,
            'uncertain_effect':self._uncertain,'filesystem_artifacts':[x.name for x in sorted(self._directory.glob('*.json'))],
            'not_a_plan_or_recommended_next_action':True}
    def terminal(self):return self._completed or self._opportunities>=MAX_OPPORTUNITIES or self._uncertain is not None
    def commit_selected(self,physical_action_sign,physical_operation_sign,*,native_value_reader,synthetic_fixture=False):
        if self.terminal():raise ValueError('Terminated/bounded/uncertain goal; no automatic retry')
        if type(synthetic_fixture)is not bool:raise ValueError('Explicit factual fixture scope required')
        if physical_operation_sign is not None and(type(physical_operation_sign)is not int or physical_operation_sign not in(-1,1)):raise ValueError('Physical acquired operation sign or absence required')
        action=projection(physical_action_sign);before=self.observation();self._opportunities+=1
        row={'version':VERSION,'opportunity':self._opportunities,'public_before':before,
            'physical_action_sign':physical_action_sign,'physical_operation_sign':physical_operation_sign,
            'selected_action':action,'native_provider_called':False,'committed_effect':None,'quality':None,
            'private_value_sent_to_participant':False,'actuator_initiative':'Only the supplied physical sign selects ACT/QUERY; operator schedules the opportunity'}
        if action is None:
            row['environment_effect']='NO_ACTION';row['feedback']={'category':'FAILURE'}
        elif action=='QUERY':
            self._public['second']=self._private_second
            row['environment_effect']='SECOND_OPERAND_OBSERVED';row['revealed_observation']={'second':self._public['second']}
            row['private_value_sent_to_participant']=True
            row['feedback']={'category':'FAILURE'}
            row['consequence_reason_private_auditor']='INCOMPLETE: querying reveals an actual raw operand but produces no verified goal file. This is not a correction or an ACT instruction.'
        elif self._public['second']is None:
            # Resource/precondition enforcement AFTER ACT was selected. It
            # does not substitute QUERY or manufacture a neutral operand.
            row['environment_effect']='ACT_FAILED_MISSING_OBSERVATION';row['feedback']={'category':'FAILURE'}
        elif physical_operation_sign is None:
            row['environment_effect']='ACT_FAILED_NO_OPERATION_EMISSION';row['feedback']={'category':'FAILURE'}
        else:
            operation='add'if physical_operation_sign==1 else'sub'
            effect_id=self._public['task_id']+'_attempt'+str(self._opportunities)
            public={'task_id':effect_id,'text':self._public['text'],'operands':[self._public['left'],self._public['second']]}
            def native(op,values):
                row['native_provider_called']=True
                return native_value_reader(op,values)
            def forbidden_external(*_):raise AssertionError('No external calculator is an admitted ACT provider in this apparatus')
            committed=self._effects.execute_selected(public,{'operation':operation,'procedure':'native'},sandbox_root=self._directory,
                native_value_reader=native,external_calculator=forbidden_external,
                law={'price':1,'delay_ticks':0,'available':True},synthetic_fixture=synthetic_fixture)
            row['committed_effect']=committed
            if committed['state']=='uncertain':
                self._uncertain={'attempt':self._opportunities,'effect':committed};row['environment_effect']='UNCERTAIN_FILE_EFFECT'
                row['feedback']=None;row['no_feedback_or_retry_on_uncertain_effect']=True
            else:
                # Only after the selected effect has a terminal receipt may
                # the verifier privately resolve conventional semantics.
                report=self._quality.evaluate_literal_committed(public,committed,sandbox_root=self._directory,policy=POLICY)
                row['quality']=report;row['feedback']=self._quality.actor_feedback(report,binary=True)
                self._completed=bool(report['task_success'])
                row['environment_effect']='VERIFIED_GOAL_FILE'if self._completed else'ACT_TERMINAL_GOAL_NOT_VERIFIED'
        row['public_after']=self.observation();row['progress_after']=self.progress()
        self._events.append(row);return row
    def checkpoint(self,path):
        """External world state, never installed in DEE metadata as memory."""
        body={'version':VERSION,'public':self.observation(),'private_environment':{'second':self._private_second},
            'progress':self.progress(),'events':self._events,'directory':str(self._directory),
            'actor_access':'Only observation() and projected feedback; private_environment/events belong to environment and auditor'}
        data=(json.dumps(body,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        with Path(path).open('xb')as f:f.write(data)
        return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
