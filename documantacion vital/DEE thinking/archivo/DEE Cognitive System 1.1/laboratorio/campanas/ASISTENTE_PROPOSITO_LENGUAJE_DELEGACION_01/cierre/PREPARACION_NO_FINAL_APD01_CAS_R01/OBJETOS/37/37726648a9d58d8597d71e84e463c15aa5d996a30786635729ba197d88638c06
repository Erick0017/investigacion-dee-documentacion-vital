"""Portable offline APD audit from supervisor primaries; no DEE imports/ticks.

The evaluator computes expected arithmetic here, never in the participant.
Issued native operator signs, not literal Spanish words, select the audited
operation. External calculator results are counted separately from native ones.
"""
import argparse,collections,gzip,hashlib,json
from pathlib import Path

def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(value):
    n=int(value)
    if not 0<=n<2**64:raise ValueError('Not an exact uint64')
    def signed(k):
        x=(n>>k)&15;return x-16 if x&8 else x
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
            'direction':[signed(k)for k in(48,52,56)]}
def walk(node,path='$'):
    if isinstance(node,dict):
        yield path,node
        for k,v in node.items():
            if k not in('parent','operations','historical_parent','source_life_record','initial_record','final_record'):
                yield from walk(v,path+'.'+k)
    elif isinstance(node,list):
        for i,v in enumerate(node):yield from walk(v,path+'['+str(i)+']')
def formed_word(q):
    found=[];panel=q['reader']['panel']
    old6=[(1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1)]
    if len(panel)==4:vectors=[(33,33,-1,0),(33,33,0,-1)]
    elif len(panel)in(12,16,20,24):
        vectors=[(33,33,x,y)for x,y in old6]
        if len(panel)>=16:vectors.extend((33,33,x,y)for x,y in[(-1,0),(0,-1)])
        if len(panel)>=20:vectors.extend((47,47,x,y)for x,y in[(-1,0),(0,-1)])
        if len(panel)>=24:vectors.extend((47,47,x,y)for x,y in[(1,0),(0,1)])
    else:raise ValueError('Undeclared fixed lexical gate count')
    expected={((ox+4*x)%67,(oy+4*y)%67,(33 if ox==33 else 47)+sg):sg
              for ox,oy,x,y in vectors for sg in(-1,1)}
    if len(panel)!=len(expected)or{tuple(o['site'])for o in panel}!=set(expected):
        raise ValueError('Incomplete, duplicated or unexpected fixed lexical gates')
    for o in panel:
        d=decode(o['raw'])
        sg=expected[tuple(o['site'])]
        if d['state']>0 and d['semantic']==1 and d['direction']==[0,0,sg]:found.append(sg)
    return found[0]if len(found)==1 else None
def formed_route(q):
    found=[];origin=tuple(q['reader'].get('origin',[15,15,15]))
    if origin not in((15,15,15),(15,45,15)):raise ValueError('Undeclared fixed reader origin')
    count=len(q['reader']['observations'])
    if count==3 and origin==(15,15,15):zs=(0,)  # Original P09/P11 selection reader, frozen before the later six-gate revision.
    elif count==6:zs=(0,-1)
    else:raise ValueError('Undeclared fixed selector gate count')
    expected={(origin[0]+2*x,origin[1]+2,origin[2]+2*z)for x in(-1,0,1)for z in zs}
    if {tuple(o['site'])for o in q['reader']['observations']}!=expected:
        raise ValueError('Incomplete, duplicated or unexpected fixed selector gates')
    for o in q['reader']['observations']:
        x=(o['site'][0]-origin[0])//2;z=(o['site'][2]-origin[2])//2;d=decode(o['raw'])
        if o['site']in[[origin[0]+2*xx,origin[1]+2,origin[2]+2*zz]for xx in(-1,0,1)for zz in(0,-1)]and d['state']>0 and d['semantic']==1 and d['direction']==[x,1,z]:found.append(x)
    return found[0]if len(found)==1 else None
def native_numeric(q,errors,where):
    op=q['operation'];left,right=q['operands'];trial=q['native_trial'];reader=q['numeric_reader']
    expected=left+right if op=='suma'else left-right
    bias=0 if op=='suma' else 32
    tick=int(trial['datum_tick'])-2
    frames=[f for f in trial['frames']if int(f['tick'])==tick]
    if len(frames)!=1 or 'C'not in frames[0]['fields']:
        errors.append([where,'NO_UNIQUE_NUMERIC_GATE']);return {'valid':False,'correct':False,'expected_evaluator_only':expected,'actual':None}
    o=frames[0]['fields']['C'];d=decode(o['raw'])
    valid=o['site']==[12,17,18]and int(o['tick'])==tick and d['state']>0 and d['semantic']==1 and d['direction']==[1,-1,-1]
    actual=d['s_reg']-bias if valid else None
    if actual!=reader['numeric_result']or valid!=reader['fixed_site_direction_valid']or o!=reader['observation']:
        errors.append([where,'CACHED_NUMERIC_READER_DISAGREES'])
    vector=[0]*128;vector[0]=left;vector[1]=right if op=='suma' else 32-right
    same_vector=trial['raw_components']==vector
    if not same_vector:errors.append([where,'DECLARED_INDEPENDENT_OPERAND_CODEC_DISAGREES'])
    return {'operation':op,'operands':[left,right],'fixed_gate_tick':tick,'fixed_gate_RAW':o['raw'],
            'native_payload':d['s_reg'],'representation_bias':bias,'valid':valid,'actual':actual,
            'expected_evaluator_only':expected,'correct':actual==expected,'independent_operand_vector_matches':same_vector,
            'scope':'Prepared native tree with fixed operand/output transduction, not learned arithmetic rule'}
def native_count(q,errors,where):
    samples=q['presence_samples'];trial=q['native_trial'];reader=q['numeric_reader'];tick=int(trial['datum_tick'])-2
    frames=[f for f in trial['frames']if int(f['tick'])==tick]
    if len(frames)!=1 or 'C'not in frames[0]['fields']:
        errors.append([where,'NO_UNIQUE_COUNT_GATE']);return {'valid':False,'correct':False,'actual':None}
    o=frames[0]['fields']['C'];d=decode(o['raw'])
    valid=o['site']==[12,17,18]and int(o['tick'])==tick and d['state']>0 and d['semantic']==1 and d['direction']==[1,-1,-1]
    actual=d['s_reg']if valid else None;expected=sum(samples)
    if actual!=reader['numeric_result']or valid!=reader['fixed_site_direction_valid']or o!=reader['observation']:
        errors.append([where,'CACHED_COUNT_READER_DISAGREES'])
    vector=[*samples,*([0]*(128-len(samples)))];same_vector=trial['raw_components']==vector
    if not same_vector:errors.append([where,'INDEPENDENT_PRESENCE_CODEC_DISAGREES'])
    return {'samples':samples,'fixed_gate_tick':tick,'fixed_gate_RAW':o['raw'],'valid':valid,'actual':actual,
            'expected_evaluator_only':expected,'correct':actual==expected,'independent_input_vector_matches':same_vector,
            'scope':'Prepared physical presence sampling and native aggregation, not acquired cardinality'}
def run(primaries,artifact_dir=None):
    paths=sorted(primaries.glob('P[0-9][0-9]_*.json.gz'));files=[];errors=[];nobs=0;learning={}
    artifact_index={}
    if artifact_dir and artifact_dir.exists():
        for p in artifact_dir.rglob('*.bin'):artifact_index.setdefault(digest(p),[]).append(p)
    for path in paths:
        primary=read(path);body=primary.get('result');instrument={}
        if isinstance(body,dict)and 'INSTRUMENTO'in body:instrument=body['INSTRUMENTO'];body=body.get('result',body)
        z={'primary':path.name,'primary_sha256':digest(path),'case':primary.get('case'),'returncode':primary.get('returncode'),
           'timed_out':primary.get('timed_out'),'life_id':instrument.get('life_id'),'committed_tick':instrument.get('tick'),
           'snapshot_sha256':instrument.get('snapshot_sha256'),'native_numeric':[],'prepared_counts':[],'integrated_requests':[],
           'lexical_uses':[],'route_reads':[],'calendar_records':[],'affine_lessons':[],'bounded_accumulations':[],
           'separate_route_uses':[],'common_cost_returns':[],'explicit_reference_experiences':[]}
        if primary.get('returncode')!=0:
            z['unexecuted_or_instrumental_failure']=primary.get('stderr','')[-3000:]
        unique_requests={}
        for where,node in walk(body):
            if 'raw'in node and all(k in node for k in('state','s_reg','semantic','direction')):
                d=decode(node['raw']);nobs+=1
                if any(node[k]!=d[k]for k in d):errors.append([path.name,where,'RAW_FIELDS_DISAGREE'])
                if 'active'in node and node['active']!=bool(d['state']):errors.append([path.name,where,'ACTIVE_FLAG_DISAGREES'])
            if 'requests'in node and isinstance(node['requests'],list):
                for req in node['requests']:
                    if not isinstance(req,dict)or'receipt'not in req:continue
                    receipt=req['receipt'];rid=req.get('id',receipt.get('id'));key=str(rid)
                    if rid is None:key=json.dumps(req,sort_keys=True)
                    if key in unique_requests and unique_requests[key]!=receipt:errors.append([path.name,where,'REQUEST_ID_RECEIPT_CONFLICT',rid])
                    unique_requests[key]=receipt
            if isinstance(node.get('receipt'),dict)and'status'in node['receipt']and'id'in node['receipt']:
                receipt=node['receipt'];key=str(node.get('id',receipt['id']))
                if key in unique_requests and unique_requests[key]!=receipt:errors.append([path.name,where,'SINGULAR_RECEIPT_CONFLICT',key])
                unique_requests[key]=receipt
            if node.get('kind')=='APD01_candidate_numeric_operation':z['native_numeric'].append({'path':where,**native_numeric(node,errors,path.name+where)})
            if node.get('kind')=='APD01_prepared_count':z['prepared_counts'].append({'path':where,**native_count(node,errors,path.name+where)})
            if node.get('kind')=='explicit_affine_training':
                gate=node['frames'][-1]['junction'];d=decode(gate['raw'])
                valid=gate['site']==[20,15,30]and int(gate['tick'])==int(node['arrival'])and d['state']>0 and d['semantic']==1 and d['direction']==[0,1,0]
                acquired=d['s_reg']-4096 if valid else None
                x,y=node['teaching_pair'];paired=node['teacher']=='paired'and node['intervention']!='cut'
                lesson={'path':where,'arrival':node['arrival'],'teaching_pair':[x,y],'teacher':node['teacher'],'intervention':node['intervention'],
                    'post_junction_RAW':gate['raw'],'physical_direction':d['direction'],'qualified_acquired_offset':acquired,
                    'teacher_difference_evaluator_only':y-x if paired else None,
                    'matches_paired_teacher_difference':acquired==y-x if paired else None,
                    'scope':'A separately supplied external lesson can establish a physical offset; not autonomous tool use or a general binary rule'}
                z['affine_lessons'].append(lesson)
                if z['life_id'] is not None:learning[z['life_id']]={'offset':acquired,'cumulative':acquired,'arrival':int(node['arrival']),'last_step':-1}
            if node.get('kind')=='native_bounded_accumulation':
                step=int(node['step']);gate=node['frames'][-1]['reader_site'];d=decode(gate['raw']);expected_site=[(21+step)%67,(25+8*step)%67,30]
                valid=step in range(5)and gate['site']==expected_site and int(gate['tick'])==int(node['arrival'])+2 and d['state']>0 and d['semantic']==1 and d['direction']==[0,1,0]
                actual=d['s_reg']-4096 if valid else None
                if actual!=node['numeric_result']or valid==node['abstention']:errors.append([path.name,where,'ACCUMULATION_READER_DISAGREES'])
                history=learning.get(z['life_id']);expected=None
                if history is not None:
                    if history['last_step']+1!=step:errors.append([path.name,where,'ACCUMULATOR_STEP_SEQUENCE_DISAGREES'])
                    if int(node['arrival'])!=history['arrival']+8*(step+1):errors.append([path.name,where,'ACCUMULATOR_PREPARED_CALENDAR_DISAGREES'])
                    expected=history['cumulative']+node['current_increment']if history['cumulative']is not None else None
                    history['cumulative']=expected;history['last_step']=step
                z['bounded_accumulations'].append({'path':where,'step':step,'increment':node['current_increment'],'read_tick':node['read_tick'],
                    'fixed_gate_site':gate['site'],'fixed_gate_RAW':gate['raw'],'valid':valid,'actual':actual,
                    'initial_physical_offset':history['offset']if history is not None else None,'expected_cumulative_evaluator_only':expected,
                    'matches_cumulative_prediction':actual==expected if expected is not None else None,
                    'scope':'Learned offset plus cumulative increments in five prepared opportunities, not independent repeated n+offset or general addition'} )
            if node.get('kind')in('explicit_context_experience','explicit_B_seed','explicit_route_teacher_revision'):
                before=node.get('before',[]);after=node.get('after',[])
                if not isinstance(before,list)and node.get('frames'):before=node['frames'][0].get('references',[])
                if not isinstance(after,list)and node.get('frames'):after=node['frames'][-1].get('references',[])
                z['explicit_reference_experiences'].append({'path':where,'kind':node['kind'],
                    'side':node.get('side_declared_by_teacher',node.get('side_supplied_by_teacher','B'if node['kind']=='explicit_B_seed'else None)),
                    'before_D':before[0]['s_reg']-before[1]['s_reg']if len(before)==2 else None,
                    'after_D':after[0]['s_reg']-after[1]['s_reg']if len(after)==2 else None,
                    'reference_before_tick':before[0]['tick']if len(before)==2 else None,
                    'reference_after_tick':after[0]['tick']if len(after)==2 else None,
                    'scope':'Explicit external reference preparation/re-teaching, never counted as autonomous strategy change'})
            if node.get('kind')=='separate_native_route_use':
                before=node['references_before'];after=node['references_after']
                z['separate_route_uses'].append({'path':where,'query_tick':node['query_tick'],'read_tick':node['read_tick'],
                    'native_choice':formed_route(node),'before_D':before[0]['s_reg']-before[1]['s_reg'],
                    'after_D':after[0]['s_reg']-after[1]['s_reg'],'origin':[15,45,15]})
            if node.get('kind')=='separate_route_common_cost':
                before=node['before'];after=node['after'];requests=node['requests']
                cost_inputs=[q for q in requests if q.get('port')in('APD.route.cost','APD.route.cost_sham')]
                z['common_cost_returns'].append({'path':where,'cost':node['cost'],'mode':node['mode'],'fixed_budget':node['fixed_budget'],
                    'query_tick':node['query_tick'],'datum_tick':node['datum_tick'],'boundary_multiplier':node['boundary_multiplier'],
                    'before_D':before[0]['s_reg']-before[1]['s_reg'],'after_D':after[0]['s_reg']-after[1]['s_reg'],
                    'native_output_during_return':formed_route(node),'actual_cost_input_count':len(cost_inputs),
                    'cost_input_ports':[q['port']for q in cost_inputs],
                    'scope':'Common literal-cost transduction and prepared excess/cadence; utility or learned policy requires matched controls'})
            if isinstance(node.get('reader'),dict)and'formed_native_command'in node['reader']and'panel'in node['reader']:
                actual=formed_word(node)
                if actual!=node['reader']['formed_native_command']:errors.append([path.name,where,'WORD_READER_DISAGREES'])
                z['lexical_uses'].append({'path':where,'form':node.get('form',node.get('context_signal')),'command':actual,
                    'input_tick':node.get('input_tick'),'read_tick':node.get('read_tick'),'fixed_gates':len(node['reader']['panel'])})
            if isinstance(node.get('reader'),dict)and'choice'in node['reader']and'observations'in node['reader']:
                actual=formed_route(node)
                if actual!=node['reader']['choice']:errors.append([path.name,where,'MATERIAL_ROUTE_READER_DISAGREES'])
                z['route_reads'].append({'path':where,'choice':actual,'read_tick':node.get('read_tick',node['reader'].get('tick')),
                    'origin':node['reader'].get('origin',[15,15,15]),'gates':len(node['reader']['observations'])})
            timing=node.get('timing')
            if isinstance(timing,dict)and'effective_query_tick'in timing:
                requested=int(timing['requested_query_tick']);effective=int(timing['effective_query_tick']);wait=int(timing['wait_ticks'])
                valid=effective-requested==wait and 0<=wait<=10
                if timing.get('enabled'):valid=valid and (effective-2)//391==(effective+8)//391
                if not valid:errors.append([path.name,where,'P0_CALENDAR_DISAGREES'])
                z['calendar_records'].append({'path':where,'requested':requested,'effective':effective,'wait':wait,'protected':timing.get('enabled'),'valid':valid})
            if node.get('kind')=='APD01_integrated_request':
                word=formed_word(node['word']);route=formed_route(node['route'])if node.get('route')else None
                if word!=node['native_operator_command']or route!=node['native_route_command']:errors.append([path.name,where,'CACHED_NATIVE_COMMAND_DISAGREES'])
                op='suma'if word==1 else('diferencia'if word==-1 else None);left,right=node['raw_operands']
                expected=(left+right if word==1 else left-right)if op else None
                actual=node['numeric_result'];procedure=node['procedure'];native=node.get('native_numeric');tool=node.get('external_tool')
                if native is not None and native['operation']!=op:errors.append([path.name,where,'WORD_SIGN_NOT_SELECTING_ISSUED_OPERATION'])
                if procedure=='native'and tool is not None:errors.append([path.name,where,'EXTERNAL_TOOL_USED_ON_NATIVE_ROUTE'])
                if procedure in('external','material_help_external')and native is not None:errors.append([path.name,where,'NATIVE_TREE_PRESENT_ON_EXTERNAL_ROUTE'])
                artifact=node.get('artifact');artifact_check=None
                if artifact:
                    emission=formed_route(node['result_material_use']);length=actual+32 if actual is not None else None
                    byte=165 if emission==1 else(90 if emission==-1 else 0)
                    predicted=bytes([byte])*length if type(length)is int and length>=0 else None
                    predicted_sha=hashlib.sha256(predicted).hexdigest()if predicted is not None else None
                    files_with_hash=artifact_index.get(artifact['sha256'],[])
                    artifact_check={'recorded_bytes':artifact['bytes'],'actual_result_plus32':length,'matches_length':artifact['bytes']==length,
                        'native_actuator':emission,'recorded_native_actuator':artifact['native_actuator'],'matches_native_actuator':emission==artifact['native_actuator'],
                        'sha_matches_fixed_transduction':predicted_sha==artifact['sha256'],'actual_bytes_available':bool(files_with_hash),
                        'actual_files_matching':len(files_with_hash),'actual_file_sizes_match':all(p.stat().st_size==artifact['bytes']for p in files_with_hash)if files_with_hash else None}
                    if not artifact_check['matches_length']or not artifact_check['matches_native_actuator']or not artifact_check['sha_matches_fixed_transduction']:
                        errors.append([path.name,where,'FILE_ACTUATION_RECORD_DISAGREES'])
                z['integrated_requests'].append({'path':where,'literal_form':node['literal_form'],'raw_operands':node['raw_operands'],
                    'native_operator':word,'issued_operation_from_native_sign':op,'native_route':route,'procedure':procedure,
                    'expected_evaluator_only':expected,'actual_result':actual,'arithmetic_correct':actual==expected and expected is not None,
                    'completed':node['completed'],'actuator_mode':node['actuator_mode'],'feedback_mode':node['feedback_mode'],
                    'environment':node['environment'],'modeled_price':node['modeled_price'],'costly':node['costly'],
                    'outcome_return_episodes':len(node['outcome_returns']),'artifact':artifact_check})
        counts=collections.Counter(receipt['status']for receipt in unique_requests.values())
        z['request_denominators']={'unique_requested':len(unique_requests),'applied':counts.get('applied',0),
            'rejected':sum(v for k,v in counts.items()if k.startswith('rejected')),'pending':counts.get('pending',0),'status_counts':dict(sorted(counts.items()))}
        z['native_numeric_counts']={'valid':sum(q['valid']for q in z['native_numeric']),'correct':sum(q['correct']for q in z['native_numeric']),'denominator':len(z['native_numeric'])}
        z['prepared_count_counts']={'valid':sum(q['valid']for q in z['prepared_counts']),'correct':sum(q['correct']for q in z['prepared_counts']),'denominator':len(z['prepared_counts'])}
        z['bounded_accumulation_counts']={'valid':sum(q['valid']for q in z['bounded_accumulations']),
            'correct_cumulative':sum(q['matches_cumulative_prediction']is True for q in z['bounded_accumulations']),
            'expected_unknown':sum(q['expected_cumulative_evaluator_only']is None for q in z['bounded_accumulations']),
            'denominator':len(z['bounded_accumulations'])}
        z['integrated_counts']={'completed':sum(q['completed']for q in z['integrated_requests']),
            'arithmetic_correct':sum(q['arithmetic_correct']for q in z['integrated_requests']),
            'native_route':sum(q['procedure']=='native'for q in z['integrated_requests']),
            'external_route':sum(q['procedure']in('external','material_help_external')for q in z['integrated_requests']),
            'denominator':len(z['integrated_requests'])}
        files.append(z)
    return {'schema':'APD01.root_primary_recalculation.R05','files':files,'RAW_observations_decoded':nobs,'discrepancies':errors,
            'native_ticks_executed':0,'scope':'Offline audit only. Mathematics in the evaluator and external tool is not attributed to native learning. Requests within one life are not independent biographies; no global P2/R2 inference.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--artefactos',type=Path);p.add_argument('--salida',type=Path,required=True)
    args=p.parse_args();r=run(args.primarios,args.artefactos);b=(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with args.salida.open('xb')as f:f.write(b)
    print(json.dumps({'files':len(r['files']),'RAW_observations_decoded':r['RAW_observations_decoded'],'discrepancies':r['discrepancies'],
                      'sha256':hashlib.sha256(b).hexdigest(),'native_ticks_executed':0}))
    raise SystemExit(bool(r['discrepancies']))
