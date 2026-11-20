"""One archived APD02 effect, independently bound to the original public input.

No engine imports, provider calls or target projection to a participant.
"""
def audit_effect(row,public,folder,*,quality,raw_util,route_util,origin):
    checks={};receipt=row['committed_effect'];env=row['environment'];word,_=raw_util.pure_z(row['word']['reader'],raw_util.FORM_CODEC)
    route=route_util.choice3(row['route']['reader'],origin)[0]if row['route']else None
    operation='add'if word==1 else'sub'if word==-1 else None;procedure='native'if route==-1 else'external'if route in(0,1)else None
    checks['original_public_binding']=row['literal_form']==public['text']and row['raw_operands']==public['operands']and receipt['task_id']==public['task_id']
    checks['operator_from_fixed_RAW']=operation==row['selected_operation']==receipt['selected_operation']and word==row['native_operator_command']
    checks['route_from_fixed_RAW']=procedure==row['selected_procedure']==receipt['selected_procedure']and route==row['native_route_command']
    available=bool(procedure is not None and env['disponibilidad'][0 if procedure=='native'else 1]);expected={'native':int(procedure=='native'and available),'external':int(procedure=='external'and available)}
    checks['sole_selected_provider_or_unavailable']=receipt['provider_calls']==expected
    numeric_from_RAW=None;before_fault=(receipt.get('raw_provider_response')or{}).get('value')
    if procedure is None:checks['no_silent_replacement']=receipt['state']=='no_output'and row['native_numeric']is None and row['external_tool']is None and receipt['artifact']is None
    else:
        checks['real_callback_not_synthetic_fixture']=receipt['fixture_does_not_advance_DEE']is False
        index=0 if procedure=='native'else 1
        checks['chosen_environment_resource_law']=receipt['price']==env['precios'][index]and receipt['delay_ticks']==env['demora'][index]
        if not available:checks['unavailable_no_alternate_callback']=row['native_numeric']is None and row['external_tool']is None and receipt['state']=='failed'and receipt['failure_class']=='selected_provider_unavailable'
        elif procedure=='native':
            trial=row['native_numeric'];numeric_from_RAW=raw_util.numeric(trial);checks['native_numeric_from_frozen_RAW']=numeric_from_RAW==before_fault==trial['numeric_reader']['numeric_result']
            checks['native_no_external_solver']=row['external_tool']is None
            checks['independent_fixed_operand_codec']=trial['operation']==('suma'if operation=='add'else'diferencia')and trial['operands']==public['operands']and trial['native_trial']['raw_components']==[public['operands'][0],public['operands'][1]if operation=='add'else 32-public['operands'][1]]+[0]*126
        else:checks['explicit_external_only']=row['native_numeric']is None and row['external_tool']is not None and row['external_tool']['value']==before_fault
        if'used_value'in receipt:checks['no_hidden_value_correction']=receipt['used_value']==before_fault+(1 if env['fallos'][index]=='wrong_value'else 0)
        if receipt.get('effect_phase'):
            checks['unknown_FS_effect_not_mislabeled_terminal']=receipt['state']!='uncertain'and not receipt['requires_explicit_reconciliation']
            if receipt['state']=='committed':checks['complete_FS_phases_before_commit']=receipt['effect_phases']==['planned','before_compute','computed','opened','written','fsynced','readback']
    policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':env['presupuesto'],'max_delay_ticks':env['demora_maxima'],'resource_limits_required_for_success':True}
    verified=quality.evaluate_literal_committed(public,receipt,sandbox_root=folder,policy=policy)
    checks['actual_artifact_and_original_request_quality']=raw_util.content(verified)==raw_util.content(row['quality'])
    checks['only_binary_category_return']=row['feedback_to_participant']==quality.actor_feedback(verified,binary=True)
    checks['effect_precedes_verification_and_return']=row['before']['tick']<=row['commit_before_verification']['tick']<=row['after']['tick']
    native_return=row['native_consequence']
    if native_return:
        checks['native_common_category_only']=native_return['category']==row['feedback_to_participant']['category']and native_return['no_action_or_correct_route_argument']is True
        expected_ports={-1,0,1}if native_return['category']=='FAILURE'and native_return['mode']=='real'else set()
        checks['all_or_no_generic_ports_not_chosen_side']={int(r['port'].rsplit('.',1)[1])for r in native_return['requests']}==expected_ports and all(r['payload']==0 for r in native_return['requests'])
        checks['trace_not_reinjected_from_reader']=row['route']['trace_not_reinjected_from_reader']is True
    value=verified['private_audit']['observed_artifact']['value']if verified['private_audit']['observed_artifact']else None
    reference=verified['private_audit']['reference_value']
    return{'checks':checks,'issues':[k for k,v in checks.items()if not v],'public_original':public,'word_sign':word,'route_choice':route,'selected_operation':operation,'selected_procedure':procedure,'native_number_from_RAW':numeric_from_RAW,'provider_value_before_declared_fault':before_fault,'reported_used_value':receipt.get('used_value'),'actual_artifact_value':value,'private_reference_value':reference,'numeric_provider_correct_for_original_request':type(before_fault)is int and before_fault==reference,'semantic_correct':verified['axes']['operation_corresponds_to_original_request'],'numeric_artifact_correct_for_original_request':verified['axes']['numeric_correct_for_original_request'],'real_artifact_valid':verified['axes']['artifact_valid'],'valid_completed_task':verified['completed_task'],'resource_acceptable':verified['resource_acceptable'],'task_success_under_limits':verified['task_success'],'category':verified['feedback']['category'],'provider_calls':receipt['provider_calls'],'effect_state':receipt['state'],'effect_phase':receipt.get('effect_phase'),'reported_number_is_not_a_file_effect':verified['private_audit']['reported_value_correct_is_not_a_file_effect'],'private_audit_not_actor_input':True,'scope':'Separate intended operation, correct number, real authorized file and resource compliance. A provider/external value and a native-RAW value retain their attribution; reference arithmetic is external post-action audit.'}
