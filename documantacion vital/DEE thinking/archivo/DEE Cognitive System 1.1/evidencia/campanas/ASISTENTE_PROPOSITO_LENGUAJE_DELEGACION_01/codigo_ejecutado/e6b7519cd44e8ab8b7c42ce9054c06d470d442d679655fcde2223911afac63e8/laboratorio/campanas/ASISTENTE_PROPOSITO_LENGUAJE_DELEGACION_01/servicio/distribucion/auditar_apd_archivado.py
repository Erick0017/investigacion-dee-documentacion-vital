"""Independent APD result checks; standard library, no engine or actor calls.

This is an auditor, not a codec supplied to DEE. Arithmetic here checks the
already emitted operator against the archived physical result. It never feeds
an answer, route, repaired record or target back into a participant.
"""
import hashlib
from pathlib import Path


def unpack(raw):
    if isinstance(raw,str)and raw.isascii()and raw.isdecimal():raw=int(raw)
    if type(raw)is not int or not 0<=raw<2**64:raise ValueError('Exact uint64 RAW integer or lossless decimal string required; never float')
    return {'active':bool(raw&0xffffffff),'semantic':(raw>>60)&15,
            'direction':[((raw>>s)&15)-(16 if((raw>>s)&15)>=8 else 0)for s in(48,52,56)],
            'payload':(raw>>32)&65535}


def lexical(reader):
    vectors=((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1),(-1,0),(0,-1))
    expected={((33+4*x)%67,(33+4*y)%67,(33+sg)%67):sg for x,y in vectors for sg in(-1,1)}
    second={((47+4*x)%67,(47+4*y)%67,(47+sg)%67):sg for x,y in((-1,0),(0,-1))for sg in(-1,1)}
    panel=reader['panel']
    if len(panel)in(20,24):
        expected.update(second)
        if len(panel)==24:expected.update({((47+4*x)%67,(47+4*y)%67,(47+sg)%67):sg for x,y in((1,0),(0,1))for sg in(-1,1)})
    elif len(panel)==4:expected={site:sg for site,sg in expected.items()if site[:2]in((29,33),(33,29))}
    elif len(panel)!=16:raise ValueError('Undeclared fixed lexical gate count')
    if len(panel)!=len(expected)or{tuple(o['site'])for o in panel}!=set(expected):raise ValueError('Incomplete/duplicate/unexpected fixed lexical gates')
    candidates=[]
    for o in panel:
        n=unpack(o['raw']);sg=expected[tuple(o['site'])]
        if n['active']and n['semantic']==1 and n['direction']==[0,0,sg]:candidates.append(sg)
    command=candidates[0]if len(candidates)==1 else None
    return {'gate_count':len(panel),'candidates':candidates,'command':command,
            'agrees_with_archived_command':reader['formed_native_command']==command}


def selector(reader,origin):
    expected={((origin[0]+2*x)%67,(origin[1]+2)%67,(origin[2]+2*z)%67):(x,z)for x in(-1,0,1)for z in(0,-1)}
    observations=reader['observations']
    if len(observations)!=6 or{tuple(o['site'])for o in observations}!=set(expected):raise ValueError('Incomplete/duplicate/unexpected six-gate selector')
    candidates=[]
    for o in observations:
        n=unpack(o['raw']);x,z=expected[tuple(o['site'])]
        if n['active']and n['semantic']==1 and n['direction']==[x,1,z]:candidates.append(x)
    choice=candidates[0]if len(candidates)==1 else None
    return {'gate_count':6,'candidates':candidates,'choice':choice,
            'agrees_with_archived_choice':reader['choice']==choice}


def native_number(native,command):
    trial=native['native_trial'];at=int(trial['datum_tick'])-2
    frames=[f for f in trial['frames']if int(f['tick'])==at]
    if len(frames)!=1:raise ValueError('No unique archived native numeric gate frame')
    o=frames[0]['fields']['C'];n=unpack(o['raw'])
    valid=o['site']==[12,17,18]and int(o['tick'])==at and n['active']and n['semantic']==1 and n['direction']==[1,-1,-1]
    value=(n['payload']-(32 if command==-1 else 0))if valid else None
    return {'numeric_gate_valid':bool(valid),'value':value,
            'agrees_with_archived_numeric_reader':native['numeric_reader']['numeric_result']==value,
            'physical_fields_checked':{'tick':at,'site':o['site'],'raw':o['raw']}}


def admissions(value):
    """Unique receipt IDs in one already-executed result, not new trials."""
    found={};conflicts=[]
    def walk(v):
        if isinstance(v,dict):
            if type(v.get('id'))is int and isinstance(v.get('receipt'),dict):
                receipt=v['receipt'];key=v['id']
                fingerprint=(receipt.get('status'),receipt.get('applied_tick'),receipt.get('rejection_reason'))
                if key in found and found[key]!=fingerprint:conflicts.append(key)
                found[key]=fingerprint
            for child in v.values():walk(child)
        elif isinstance(v,list):
            for child in v:walk(child)
    walk(value)
    counts={}
    for status,_,_ in found.values():counts[status]=counts.get(status,0)+1
    return {'requested_unique':len(found),'by_status':counts,'conflicting_receipt_ids':sorted(set(conflicts))}


def audit(row,artifact_root=None):
    if row.get('kind')=='APD01_assisted_composition':return composition(row,artifact_root)
    if row.get('kind')=='APD01_prepared_count':
        n=native_number(row,1);actual=n['value'];wanted=sum(row['presence_samples'])
        return {'kind':'prepared_native_count','numeric':n,'public_samples':row['presence_samples'],
                'correct_when_responded':None if actual is None else actual==wanted,
                'abstention':actual is None,'admissions':admissions(row),
                'issues':[]if n['agrees_with_archived_numeric_reader']else['numeric_decoder_disagrees']}
    if row.get('kind')!='APD01_integrated_request':raise ValueError('No APD result; do not substitute a transport verdict')
    issues=[];word=lexical(row['word']['reader']);command=word['command']
    if not word['agrees_with_archived_command']or row['native_operator_command']!=command:issues.append('word_decoder_disagrees')
    route=selector(row['route']['reader'],(15,45,15))if row.get('route')else None
    choice=route['choice']if route else None
    if route and not route['agrees_with_archived_choice']or row['native_route_command']!=choice:issues.append('route_decoder_disagrees')
    expected_procedure='native'if choice==-1 else('external'if choice==1 else('material_help_external'if choice==0 else None))
    if row['procedure']!=expected_procedure:issues.append('procedure_not_from_native_route')
    native=row.get('native_numeric');external=row.get('external_tool');numeric=row.get('numeric_result');checked_number=None
    if native is not None and external is not None:issues.append('both_implementations_ran')
    if native is not None:
        checked_number=native_number(native,command)
        if choice!=-1 or not checked_number['agrees_with_archived_numeric_reader']or numeric!=checked_number['value']:issues.append('native_numeric_or_route_disagrees')
    if external is not None:
        if choice not in(0,1)or not external.get('not_a_DEE_operation')or numeric!=external['value']:issues.append('external_tool_or_route_disagrees')
    operands=row['raw_operands'];expected=operands[0]+operands[1]if command==1 else(operands[0]-operands[1]if command==-1 else None)
    correct=None if numeric is None or expected is None else numeric==expected
    material=selector(row['result_material_use']['reader'],(15,15,15))if row.get('result_material_use')else None
    if material and not material['agrees_with_archived_choice']:issues.append('material_actuator_decoder_disagrees')
    artifact=row.get('artifact');artifact_info=None
    if artifact:
        emission=material['choice']if material else None
        if emission not in(-1,0,1)or numeric is None:issues.append('artifact_without_formed_material_result')
        else:
            payload=bytes([165 if emission==1 else(90 if emission==-1 else 0)])*(numeric+32);digest=hashlib.sha256(payload).hexdigest()
            artifact_info={'name':artifact['name'],'bytes':len(payload),'expected_sha256_from_actual_emission':digest,'actual_bytes_found':None}
            if artifact['bytes']!=len(payload)or artifact['sha256']!=digest or artifact['native_actuator']!=emission:issues.append('artifact_conversion_disagrees')
            if artifact_root is not None:
                matches=[p for p in Path(artifact_root).rglob(artifact['name'])if p.is_file()and p.stat().st_size==len(payload)and hashlib.sha256(p.read_bytes()).hexdigest()==digest]
                artifact_info['actual_bytes_found']=bool(matches)
                if not matches:issues.append('declared_artifact_bytes_not_exported_or_different')
    if bool(row['completed'])!=bool(artifact):issues.append('completion_not_artifact_based')
    returns=[]
    for ret in row.get('outcome_returns',[]):
        returns.append({'cost':ret.get('cost'),'mode':ret.get('mode'),'fixed_budget':ret.get('fixed_budget'),
                        'before':ret.get('before'),'after':ret.get('after'),
                        'reader':selector(ret['reader'],(15,45,15))})
        if ret.get('cost')!=row.get('consequence_cost')or not returns[-1]['reader']['agrees_with_archived_choice']:issues.append('common_cost_or_return_decoder_disagrees')
    admitted=admissions(row)
    if admitted['conflicting_receipt_ids']:issues.append('conflicting_receipts')
    return {'kind':'integrated_APD','literal_form':row['literal_form'],'operands':operands,
            'word':word,'route':route,'native_numeric':checked_number,'external_tool_ran':external is not None,
            'numeric_result':numeric,'auditor_operation_result':expected,'correct_when_responded':correct,
            'abstention':numeric is None,'material_result':material,'artifact':artifact_info,
            'completed':bool(artifact),'modeled_price':row.get('modeled_price'),'common_returns':returns,
            'admissions':admitted,'issues':issues,
            'attribution':'Auditor checks archived emissions; not an actor parser, calculator, route selector or memory.'}


def composition(row,artifact_root=None):
    parts=[audit(r,artifact_root)for r in row['rows']];issues=[]
    for i,(native,part)in enumerate(zip(row['rows'],parts)):
        issues.extend('stage_'+str(i)+':'+s for s in part['issues'])
        if i and native['raw_operands'][0]!=row['rows'][i-1]['numeric_result']:issues.append('intermediate_result_not_transported_at_'+str(i))
    for i,instruction in enumerate(row.get('program',[])):
        native=row['rows'][i];opcode='ADD'if native['native_operator_command']==1 else'DIFF'
        if instruction.get('opcode')!=opcode or instruction.get('procedure')!=native['procedure']or instruction.get('operand_source')!='previous_actual_output_and_next_public_operand':issues.append('DSL_not_from_emissions_at_'+str(i))
    forms=row.get('literal_forms')
    if forms is not None and [r['literal_form']for r in row['rows']]!=forms[:len(parts)]:issues.append('DSL_literal_order_disagrees')
    if 'raw_data'in row:
        for i,native in enumerate(row['rows']):
            if native['raw_operands'][1]!=row['raw_data'][i+1]or i==0 and native['raw_operands'][0]!=row['raw_data'][0]:issues.append('public_composition_operand_disagrees_at_'+str(i))
    final=parts[-1]['numeric_result']if parts and len(row.get('program',[]))==len(row.get('literal_forms',[]))else None
    if row.get('result')!=final:issues.append('composition_final_value_disagrees')
    artifact_info=None
    if row.get('artifact'):
        import json
        payload=(json.dumps({'language':'APD01.bounded.operator_sequence.R1','instructions':row['program'],'arbitrary_code_execution':False},sort_keys=True)+'\n').encode('utf8');digest=hashlib.sha256(payload).hexdigest();declared=row['artifact']
        artifact_info={'name':declared['name'],'bytes':len(payload),'sha256_from_emitted_program':digest,'actual_bytes_found':None}
        if declared['bytes']!=len(payload)or declared['sha256']!=digest:issues.append('DSL_artifact_conversion_disagrees')
        if artifact_root is not None:
            matches=[p for p in Path(artifact_root).rglob(declared['name'])if p.is_file()and p.stat().st_size==len(payload)and hashlib.sha256(p.read_bytes()).hexdigest()==digest];artifact_info['actual_bytes_found']=bool(matches)
            if not matches:issues.append('DSL_actual_bytes_not_exported_or_different')
    return {'kind':'assisted_operator_order_composition','parts':parts,'program':row.get('program'),
            'result':row.get('result'),'out_of_domain':row.get('out_of_domain',False),'artifact':artifact_info,'issues':issues,
            'not_claimed':'Learned order, native planner, general syntax or autonomous tool invention.'}
