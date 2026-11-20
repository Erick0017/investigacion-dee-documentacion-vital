"""Candidate same-world wiring; importing creates no Runtime and no ticks.

Preparation, lexical cue, route query, ACT/QUERY conversion, environmental
consequence and stopping rule are explicit external assistance. Only the
route emission and its acquired changes may be attributed to native DEE.
"""
VERSION='APD02.goal_clarification_apparatus.prospective.R01'

def run_goal(adapter,environment,learner,*,words,arithmetic,feedback_mode='real',detailed=True):
    if feedback_mode not in('real','omit','sham','desync'):raise ValueError('Prospectively selected common-return modality')
    rows=[]
    for opportunity in range(4):
        if environment.terminal():break
        public=environment.observation()
        word=words.query(adapter,public['text'],detailed=detailed)
        operation_sign=word['reader']['formed_native_command']
        selection=learner.use(adapter);action_sign=selection['reader']['choice']
        native_records=[]
        def native_value(op,values):
            result=arithmetic.native_pair(adapter,'suma'if op=='add'else'diferencia',*values,detailed=detailed)
            native_records.append(result)
            return result['numeric_reader']['numeric_result']
        effect=environment.commit_selected(action_sign,operation_sign,native_value_reader=native_value,synthetic_fixture=False)
        # The learner receives one generic category, never the action sign,
        # missing-data flag, private second operand or a recommended route.
        projected=effect['feedback'];returned=None
        if projected is not None:returned=learner.consequence(adapter,projected['category'],mode=feedback_mode)
        rows.append({'opportunity':opportunity+1,'public_observation':public,'word':word,'native_selection':selection,
            'environment_effect':effect,'native_numeric':native_records,'common_return':returned,'mode':feedback_mode,
            'actor_received_private_audit':False,'no_next_action_computed_from_progress':True})
        if projected is None:break
    return {'kind':VERSION,'opportunities':rows,'progress':environment.progress(),
        'scope':'At most four operator-scheduled opportunities. Native selected QUERY can reveal an operand; native selected ACT can use it. Arithmetic is prepared; generic feedback is external; termination on a verified file is assisted. No missing-data semantic input or autonomous goal invention is claimed.'}
