"""APD03 common local consequence, derived from exact APD02 GoalEnvironment.

The base supplies real raw facts, single selected file effects, post-commit
quality and portable state. This wrapper distinguishes the usefulness of an
information action from final goal completion. It never selects an action.
No Native import occurs. Read-only audit rows are not participant memory.
"""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path

VERSION='APD03.shared_goal_environment.prospective.R01'
FEEDBACK_MODES=('local_useful','file_only')
_BASE=None


def _base_module():
    global _BASE
    if _BASE is None:
        # Operational path adapter only. The unchanged official Cognitive
        # capability is in sistema/, never a laboratory/vendor dependency.
        from capacidades import entorno_objetivo_apd02
        _BASE=entorno_objetivo_apd02
    return _BASE


class SharedGoalEnvironment:
    def __init__(self,*,task_id,text,left,second,second_initially_public,directory,
                 quality,effects,context=0,feedback_mode='local_useful'):
        if feedback_mode not in FEEDBACK_MODES:raise ValueError('Frozen feedback mode required')
        if type(context)is not int or context not in(0,1):raise ValueError('Raw public context bit0/1 required')
        self._base=_base_module().GoalEnvironment(task_id=task_id,text=text,left=left,
            second=second,second_initially_public=second_initially_public,directory=directory,
            quality=quality,effects=effects)
        self._context=context;self._feedback_mode=feedback_mode

    def observation(self):
        return {**self._base.observation(),'context':self._context,
            'public_resources':{'allowed_procedures':['native'],
                'native_price':1,'native_delay_ticks':0,'query_price':0,
                'max_opportunities':_base_module().MAX_OPPORTUNITIES}}

    def progress(self):
        return self._base.progress()

    def terminal(self):
        return self._base.terminal()

    def commit_selected(self,physical_action_sign,physical_operation_sign,*,native_value_reader,synthetic_fixture=False):
        before=self.observation()
        row=self._base.commit_selected(physical_action_sign,physical_operation_sign,
            native_value_reader=native_value_reader,synthetic_fixture=synthetic_fixture)
        after=self.observation()
        selected=row['selected_action']
        revealed_new_fact=(selected=='QUERY' and before['second'] is None and after['second'] is not None)
        final_completed=bool(row['progress_after']['verified_file_goal_completed'])
        local_useful=revealed_new_fact or final_completed
        # Only this common binary post-commit projection can return. It does
        # not carry the reason, right operation, target value or next action.
        if row['feedback'] is not None:
            success=local_useful if self._feedback_mode=='local_useful' else final_completed
            row['feedback']={'category':'SUCCESS'if success else'FAILURE'}
        row.update(version=VERSION,base_version=_base_module().VERSION,
            public_before=before,public_after=after,
            feedback_mode=self._feedback_mode,
            local_action_useful=local_useful,
            new_public_fact_revealed=revealed_new_fact,
            final_goal_file_completed=final_completed,
            assistance_scope='Prepared codec and opportunities; supplied physical sign selects ACT/QUERY. Environment evaluates only after the committed action.',
            reason_auditor_only=('new_actual_operand_observed'if revealed_new_fact else
                'verified_goal_file'if final_completed else'no_new_fact_or_completed_file'))
        return row

    def operational_state(self):
        return {'schema':VERSION,'feedback_mode':self._feedback_mode,
            'context':self._context,'base_state':self._base.operational_state()}

    @classmethod
    def restore_operational(cls,state,*,directory,quality,effects):
        if not isinstance(state,dict)or set(state)!={'schema','feedback_mode','context','base_state'}:
            raise ValueError('Exact complete APD03 environment state required')
        if state['schema']!=VERSION or state['feedback_mode']not in FEEDBACK_MODES:
            raise ValueError('Environment version or frozen feedback mode differs')
        if type(state['context'])is not int or state['context']not in(0,1):
            raise ValueError('Raw context bit required')
        obj=cls.__new__(cls)
        obj._base=_base_module().GoalEnvironment.restore_operational(copy.deepcopy(state['base_state']),
            directory=directory,quality=quality,effects=effects)
        obj._feedback_mode=state['feedback_mode'];obj._context=state['context']
        return obj


def restore_operational(state,*,directory,quality,effects):
    return SharedGoalEnvironment.restore_operational(state,directory=directory,quality=quality,effects=effects)
