"""Pure reusable audit of one archived goal opportunity. No DEE imports."""
def decode(raw):
    if type(raw)is not int and not(type(raw)is str and raw.isdecimal()):raise ValueError('Exact integer RAW required')
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('uint64 RAW required')
    return {'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,
        'direction':[((n>>s)&15)-(16 if((n>>s)&15)>=8 else 0)for s in(48,52,56)]}
def physical_action(reader):
    expected={(23,15,53):-1,(25,15,53):0,(27,15,53):1};rows=reader['observations'];values=[]
    if len(rows)!=3 or{tuple(o['site'])for o in rows}!=set(expected):raise ValueError('R04 fixed three gates differ')
    for o in rows:
        f=decode(o['raw']);x=expected[tuple(o['site'])]
        if f['state']and f['semantic']==1 and f['direction']==[x,1,0]:values.append(x)
    return values[0]if len(values)==1 else None
def physical_word(reader):
    rows=reader['panel'];values=[]
    I=(33,33,33);J=(47,47,47);H=(47,17,47)
    core=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0)]
    codec=[(I,v)for v in core]+[(J,v)for v in((-1,0,0),(0,-1,0),(1,0,0),(0,1,0))]+[(H,v)for v in((1,0,0),(0,1,0))]
    expected={tuple((origin[i]+4*v[i]+(sg if i==2 else 0))%67 for i in range(3)):sg for origin,v in codec for sg in(-1,1)}
    if len(rows)!=28 or{tuple(o['site'])for o in rows}!=set(expected):raise ValueError('Exact fixed common28 lexical gate set differs')
    for o in rows:
        f=decode(o['raw']);sg=expected[tuple(o['site'])]
        if f['state']and f['semantic']==1 and f['direction']==[0,0,sg]:values.append(sg)
    return values[0]if len(values)==1 else None
def physical_number(record):
    trial=record['native_trial'];tick=int(trial['datum_tick'])-2;rows=[f['fields']['C']for f in trial['frames']if int(f['tick'])==tick]
    if len(rows)!=1:raise ValueError('Unique fixed C numeric frame required')
    o=rows[0];f=decode(o['raw']);valid=o['site']==[12,17,18]and int(o['tick'])==tick and f['state']and f['semantic']==1 and f['direction']==[1,-1,-1]
    return f['s_reg']-(32 if record['operation']=='diferencia'else 0)if valid else None
def audit_goal_opportunity(opportunity,*,artifact_directory=None,quality_module=None,expected_second=None):
    """Post-action audit; private references never feed an actor.

    `opportunity` is the exact dict from row.result.opportunities (word,
    native_selection, environment_effect, native_numeric, common_return).
    artifact_directory contains this effect's real exported file, not a
    target-generated replacement. `expected_second` is auditor-only actual
    environmental b, if known; None means no historical reference supplied.
    """
    o=opportunity;e=o['environment_effect'];issues=[]
    action_sign=physical_action(o['native_selection']['reader']);word_sign=physical_word(o['word']['reader'])
    action=None if action_sign is None else'ACT'if action_sign==-1 else'QUERY'
    if action_sign!=e['physical_action_sign']or action_sign!=o['native_selection']['reader']['choice']:issues.append('action_not_from_physical_reader')
    if word_sign!=e['physical_operation_sign']or word_sign!=o['word']['reader']['formed_native_command']:issues.append('operation_not_from_physical_word')
    if action!=e['selected_action']:issues.append('fixed_action_codec_changed')
    before=e['public_before'];after=e['public_after'];number=None;correct=None;category=None;report=None
    if before!=o['public_observation']:issues.append('public_observation_changed_before_effect')
    if action=='QUERY':
        if e['native_provider_called']or o['native_numeric']or e['committed_effect']is not None:issues.append('query_used_arithmetic_or_file_provider')
        if after['second']is None or(expected_second is not None and after['second']!=expected_second):issues.append('query_did_not_reveal_actual_raw_operand')
        if e['feedback']!={'category':'FAILURE'}:issues.append('incomplete_goal_return_changed')
    elif action=='ACT'and before['second']is not None and word_sign is not None:
        if len(o['native_numeric'])!=1:issues.append('act_not_one_native_provider')
        else:
            record=o['native_numeric'][0];number=physical_number(record);receipt=e['committed_effect']
            if record['operands']!=[before['left'],before['second']]:issues.append('native_operands_not_observed_values')
            if receipt['selected_procedure']!='native'or receipt['selected_operation']!=('add'if word_sign==1 else'sub'):issues.append('provider_not_selected_native_operation')
            if receipt.get('provider_calls')!={'native':1,'external':0}:issues.append('dual_or_external_provider_call')
            if receipt['state']=='uncertain':
                if e['feedback']is not None or e['quality']is not None:issues.append('uncertain_effect_was_evaluated_or_returned')
            else:
                if number!=receipt['raw_provider_response']['value']or number!=receipt['used_value']:issues.append('artifact_value_not_actual_native_numeric')
                if artifact_directory is None or quality_module is None:raise ValueError('Actual exported artifact directory and pure post-commit evaluator required')
                public={'task_id':receipt['task_id'],'text':before['text'],'operands':[before['left'],before['second']]}
                report=quality_module.evaluate_literal_committed(public,receipt,sandbox_root=artifact_directory,
                    policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True})
                if {k:v for k,v in report.items()if k!='evaluation_resources'}!={k:v for k,v in e['quality'].items()if k!='evaluation_resources'}:issues.append('real_file_quality_mismatch')
                if e['feedback']!=quality_module.actor_feedback(report,binary=True):issues.append('actor_return_not_only_projected_category')
                correct=report['task_success'];category=report['feedback']['category']
    elif e['native_provider_called']or o['native_numeric']or e['committed_effect']is not None:issues.append('missing_or_silent_action_substituted_operand_or_provider')
    if action!='QUERY'and before['second']is None and after['second']is not None:issues.append('private_b_revealed_without_query')
    if o['common_return']is not None:
        ret=o['common_return']
        if e['feedback']is None or ret['category']!=e['feedback']['category']or ret['mode']!=o['mode']:issues.append('native_consequence_not_common_category_and_mode')
        if any(r['payload']!=0 for r in ret['requests']):issues.append('consequence_contains_more_than_generic_zero_resource')
        if not ret.get('no_action_or_correct_route_argument'):issues.append('native_return_assistance_marker_missing')
    if e['feedback']is not None and set(e['feedback'])!={'category'}:issues.append('feedback_contains_answer_operator_or_preferred_route')
    return {'opportunity':o['opportunity'],'action_sign':action_sign,'word_sign':word_sign,'action':action,
        'public_before':before,'public_after':after,'effect':e['environment_effect'],'native_number':number,
        'file_quality_category':category,'file_goal_success':correct,'feedback':e['feedback'],'mode':o['mode'],
        'query_tick':o['native_selection']['query_tick'],'issues':issues,
        'scope':'Archived physical/actual-file audit only. Prepared action codec, generic external goal consequence and assisted stopping; no missing-data semantics or general planner.'}
