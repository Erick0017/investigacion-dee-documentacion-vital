"""Prepare R03 report: technical parser compatibility plus explicit chain view.

The criterion remains actual Native change after its own failed experience,
later useful behavior, and material controls. The old second-stage same-bit
descriptor is retained; shared-bank first-query changes are separately named.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];src=P/'fuentes/EVALUAR_D_PI09_R02.py';dst=P/'fuentes/EVALUAR_D_PI09_R03.py'
needhash='8ef28ca0b554d3b936f3bc014bdd89cb1ad93e90fce4ecd2069f7bd265ff608d';assert hashlib.sha256(src.read_bytes()).hexdigest()==needhash
text=src.read_text('utf8')
helper='''def first_chain_descriptors(rr):
    changes=[]
    for fail in rr:
        if not(fail['second']['actual_failed']and fail['second']['returned_failed']and fail['first']['Native_valid']):continue
        later=[r for r in rr if r['ordinal']>fail['ordinal']and r['first']['Native_valid']and r['first']['actual_STATE']==fail['first']['actual_STATE']and r['first']['actual_query_motor']!=fail['first']['actual_query_motor']]
        for changed in later:
            useful=[r['ordinal']for r in rr if r['ordinal']>=changed['ordinal']and r['joint_useful']and r['first']['actual_STATE']==fail['first']['actual_STATE']and r['first']['actual_query_motor']==changed['first']['actual_query_motor']]
            changes.append({'own_actual_failed_ordinal':fail['ordinal'],'generic_second_failed_return_actually_sent':True,'same_actual_STATE_input_to_first_TC':fail['first']['actual_STATE'],'failed_first_Native_choice':fail['first']['Native_choice'],'failed_first_actual_query_motor':fail['first']['actual_query_motor'],'later_changed_ordinal':changed['ordinal'],'later_first_Native_choice':changed['first']['Native_choice'],'later_first_actual_query_motor':changed['first']['actual_query_motor'],'same_observed_preview_direction':changed['first']['actual_direction']==fail['first']['actual_direction'],'changed_case_useful':changed['joint_useful'],'later_useful_same_STATE_ordinals':useful,'at_least_two_later_actual_useful':len(useful)>=2,'shared_bank_chain_revision_not_query_specific_credit':True})
    return changes
'''
changes=[
("def evaluate(r):",helper+'def evaluate(r):'),
("r.get('schema')=='DEE.PI09.D.recalculated_persistent_environment.R02'", "r.get('schema')in('DEE.PI09.D.recalculated_persistent_environment.R02','DEE.PI09.D.recalculated_persistent_environment.R03')"),
("    timing={}\n", "    shared_first_all=first_chain_descriptors(evalrows['real']);shared_first=[x for x in shared_first_all if x['changed_case_useful']and x['at_least_two_later_actual_useful']]\n    timing={}\n"),
("'schema':'DEE.PI09.D.fixed_actual_comparison.R02'", "'schema':'DEE.PI09.D.fixed_actual_comparison.R03'"),
("'revision_after_own_returned_failure_descriptors':own_revision", "'revision_after_own_returned_failure_descriptors':own_revision,'first_query_changes_after_shared_return_descriptors':shared_first_all"),
("'Native_changed_after_own_returned_failure_with_later_useful_cases':bool(own_revision),'all_fixed_descriptive_conditions_present':allclosed and greater and bool(own_revision)", "'strict_same_bit_second_stage_revision':bool(own_revision),'first_query_shared_return_chain_revision':bool(shared_first),'Native_chain_changed_after_own_shared_failed_return_with_later_useful_cases':bool(own_revision or shared_first),'all_fixed_descriptive_conditions_present':allclosed and greater and bool(own_revision or shared_first)"),
]
for old,new in changes:
    assert text.count(old)==1,old[:100]
    text=text.replace(old,new)
ast.parse(text)
with dst.open('x',encoding='utf8',newline='\n')as f:f.write(text)
print(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native_executed':False,'old_evaluator_and_criteria_unchanged':True,'actual_output_written':False}))
