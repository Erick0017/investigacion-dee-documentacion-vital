"""Two disclosed actuator effects, not a planner or DEE action selector.

The private second operand is an environment fact. It enters the public
observation only after an already selected QUERY action. No host decision
uses availability to select an action. Quality arithmetic is post-commit
external evaluation, not an actor policy. No engine imports occur here.
"""
from pathlib import Path
import base64,hashlib,json,re

VERSION='APD02.goal_clarification_environment.prospective.R02'
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
                self._uncertain={'attempt':self._opportunities,'state':'uncertain','requires_explicit_reconciliation':True,
                    'possible_artifact':committed.get('possible_artifact'),'effect_phase':committed.get('effect_phase')}
                row['environment_effect']='UNCERTAIN_FILE_EFFECT'
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
        """Portable world facts, never installed in DEE metadata as memory."""
        body=self.operational_state()
        data=(json.dumps(body,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        with Path(path).open('xb')as f:f.write(data)
        return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

    def operational_state(self):
        """Portable environment facts, not a target/plan lookup for DEE.

        The audit event history is deliberately absent. Private b is a fact
        of the external world and is only exposed by commit_selected QUERY.
        Embedded small artifact bytes make a stopped environment independent
        of its former directory without reconstructing a native individual.
        """
        artifacts=[]
        for p in sorted(self._directory.iterdir()):
            if not p.is_file()or p.is_symlink():raise ValueError('Only flat existing regular goal artifacts are portable')
            allowed={self._public['task_id']+'_attempt'+str(i)+'.json'for i in range(1,self._opportunities+1)}
            if p.name not in allowed:raise ValueError('Unexpected file is not silently included as cognitive memory')
            data=p.read_bytes()
            if len(data)>4096:raise ValueError('Goal artifact exceeds the declared limit')
            artifacts.append({'relative_path':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                'content_base64':base64.b64encode(data).decode('ascii')})
        return {'schema':VERSION,'public':self.observation(),'private_environment':{'second':self._private_second},
            'progress':{'opportunities_used':self._opportunities,'verified_file_goal_completed':self._completed,'uncertain_effect':self._uncertain},
            'artifacts':artifacts}

    @classmethod
    def restore_operational(cls,state,*,directory,quality,effects):
        """Validate a stopped external state into a NEW directory, zero ticks.

        This does not load/advance DEE or close its epoch. Its owner must
        separately restore the exact paired complete native state. No history
        is replayed, no action is chosen, and uncertain work remains blocked.
        """
        if not isinstance(state,dict)or set(state)!={'schema','public','private_environment','progress','artifacts'}or state['schema']!=VERSION:raise ValueError('Exact R02 environment state required')
        public=state['public'];private=state['private_environment'];progress=state['progress']
        if not isinstance(public,dict)or set(public)!={'task_id','text','left','second'}or not isinstance(public['task_id'],str)or not TOKEN.fullmatch(public['task_id']):raise ValueError('Portable public goal fields invalid')
        if not isinstance(public['text'],str)or not 1<=len(public['text'])<=96 or not exact_operand(public['left']):raise ValueError('Portable public request invalid')
        if not isinstance(private,dict)or set(private)!={'second'}or not exact_operand(private['second']):raise ValueError('Private environmental fact required')
        if public['second']is not None and(not exact_operand(public['second'])or public['second']!=private['second']):raise ValueError('Observed datum must match the actual environment fact')
        if not isinstance(progress,dict)or set(progress)!={'opportunities_used','verified_file_goal_completed','uncertain_effect'}:raise ValueError('Exact operational progress facts required')
        n=progress['opportunities_used'];done=progress['verified_file_goal_completed'];uncertain=progress['uncertain_effect']
        if type(n)is not int or not 0<=n<=MAX_OPPORTUNITIES or type(done)is not bool:raise ValueError('Counter cannot be reset or replaced with a plan')
        if uncertain is not None:
            keys={'attempt','state','requires_explicit_reconciliation','possible_artifact','effect_phase'}
            if not isinstance(uncertain,dict)or set(uncertain)!=keys or uncertain['attempt']!=n or uncertain['state']!='uncertain'or uncertain['requires_explicit_reconciliation']is not True or done:raise ValueError('Uncertain effect must remain unresolved, not completed')
            possible=uncertain['possible_artifact']
            expected=public['task_id']+'_attempt'+str(n)+'.json'
            if not isinstance(possible,dict)or set(possible)!={'relative_path','effect_may_exist','no_confirmed_bytes_or_hash'}or possible['relative_path']!=expected or possible['effect_may_exist']is not True or possible['no_confirmed_bytes_or_hash']is not True:raise ValueError('Relative uncertain artifact fact required')
            if uncertain['effect_phase']not in('opened','written','fsynced','readback'):raise ValueError('Unknown uncertain effect phase')
        artifacts=state['artifacts']
        if not isinstance(artifacts,list)or len(artifacts)>n:raise ValueError('Bounded real artifact list required')
        decoded=[];seen=set();allowed={public['task_id']+'_attempt'+str(i)+'.json'for i in range(1,n+1)}
        for artifact in artifacts:
            if not isinstance(artifact,dict)or set(artifact)!={'relative_path','bytes','sha256','content_base64'}:raise ValueError('Exact relative artifact with bytes/hash required')
            name=artifact['relative_path']
            if name not in allowed or name in seen:raise ValueError('Artifact path is outside this goal or duplicated')
            if type(artifact['bytes'])is not int or not 0<=artifact['bytes']<=4096 or not isinstance(artifact['sha256'],str)or not re.fullmatch(r'[0-9a-f]{64}',artifact['sha256']):raise ValueError('Bounded exact artifact receipt required')
            if not isinstance(artifact['content_base64'],str)or len(artifact['content_base64'])>5464:raise ValueError('Bounded Base64 artifact bytes required')
            try:data=base64.b64decode(artifact['content_base64'],validate=True)
            except (ValueError,TypeError)as e:raise ValueError('Invalid artifact bytes')from e
            if len(data)!=artifact['bytes']or hashlib.sha256(data).hexdigest()!=artifact['sha256']:raise ValueError('Portable artifact integrity mismatch')
            seen.add(name);decoded.append((name,data))
        if done and(n==0 or public['second']is None or public['task_id']+'_attempt'+str(n)+'.json'not in seen):raise ValueError('Completed goal needs its actual final artifact and observed inputs')
        obj=cls.__new__(cls);obj._directory=Path(directory).resolve();obj._directory.mkdir(parents=True,exist_ok=False)
        obj._quality=quality;obj._effects=effects;obj._private_second=private['second'];obj._public=dict(public)
        obj._opportunities=n;obj._completed=done;obj._uncertain=json.loads(json.dumps(uncertain));obj._events=[]
        for name,data in decoded:
            with(obj._directory/name).open('xb')as f:f.write(data)
        if done:
            # A restoration integrity check of an already terminal artifact,
            # not a new response, teaching event, action or native tick.
            name=public['task_id']+'_attempt'+str(n)+'.json';body=json.loads((obj._directory/name).read_bytes())
            receipt={'task_id':Path(name).stem,'state':'committed','selected_operation':body.get('operation'),
                'selected_procedure':'native','artifact':{'relative_path':name,'bytes':(obj._directory/name).stat().st_size,'sha256':hashlib.sha256((obj._directory/name).read_bytes()).hexdigest()},'price':1,'delay_ticks':0}
            request={'task_id':Path(name).stem,'text':public['text'],'operands':[public['left'],public['second']]}
            if not quality.evaluate_literal_committed(request,receipt,sandbox_root=obj._directory,policy=POLICY)['task_success']:raise ValueError('Completed fact does not match its real artifact; failed restoration is preserved')
        return obj

def restore_operational(state,*,directory,quality,effects):
    return GoalEnvironment.restore_operational(state,directory=directory,quality=quality,effects=effects)
