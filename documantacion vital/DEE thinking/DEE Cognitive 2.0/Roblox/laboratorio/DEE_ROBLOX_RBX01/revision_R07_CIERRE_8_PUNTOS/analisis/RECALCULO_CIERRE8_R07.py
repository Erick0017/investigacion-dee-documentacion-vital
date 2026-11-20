"""Passive, portable R07 analysis. Reads frozen files; never imports DEE or SDK.

Inputs JSON: {parent_world:path, arms:[{name,participant,sensor_arm,blocks:
[{events:path,result:path,world:path,source_world:path(optional)}]}]}.
Default source root is explicit. Package mode resolves historical source paths
only through CONTROL/MANIFIESTO_SHA256.json, never through the original drive.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics

VERSION='DEE.R07.passive_recalculation.R01'
COUNTERS=('permissionStock','queries','skips','moves','waits','collisions','resourceCount',
          'delivered','tollSpent','querySpent','functionCalls','functionNoResult','codeRejected')
PHASES=('decision','query_sensor','function','feedback')

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(v):return hashlib.sha256(v).hexdigest()
def integer(v):return type(v)is int
def number(v):return type(v)in(int,float)
def ensure(ok,msg):
    if not ok:raise ValueError(msg)

class Sources:
    def __init__(self,root,package_root=None):
        self.root=Path(root).resolve();self.package=Path(package_root).resolve()if package_root else None
        self.by_source={};self.records={}
        if self.package:
            p=self.package/'CONTROL/MANIFIESTO_SHA256.json'
            ensure(p.is_file(),'Package content manifest is required')
            m=json.loads(p.read_text('utf-8-sig'))
            rows=m.get('members',m.get('files',[]))
            ensure(isinstance(rows,list),'Manifest member array')
            for row in rows:
                if not isinstance(row,dict):continue
                source=row.get('source');archive=row.get('archive',row.get('path'))
                if not source:continue # Generated controls are not primary source aliases.
                ensure(isinstance(source,str)and isinstance(archive,str),'Manifest source/archive strings')
                expected=row.get('sha256')
                ensure(isinstance(expected,str)and len(expected)==64 and all(c in'0123456789abcdef'for c in expected),
                       'Primary package member requires its actual SHA-256')
                target=(self.package/archive).resolve()
                ensure(target.is_relative_to(self.package)and not target.is_symlink(),'Unsafe archive path')
                self.by_source[source]=(target,expected)
    def resolve(self,key):
        ensure(isinstance(key,str),'Explicit source path string')
        if self.package:
            if key in self.by_source:return self.by_source[key]
            p=(self.package/key).resolve()
            ensure(p.is_relative_to(self.package)and not p.is_symlink(),'Unmapped original path refused')
            ensure(p.is_file(),'Missing package member: '+key)
            return p,None
        p=Path(key)
        if not p.is_absolute():p=self.root/p
        p=p.resolve();ensure(p.is_relative_to(self.root)and not p.is_symlink(),'Source outside declared project root')
        ensure(p.is_file(),'Missing source: '+str(p))
        return p,None
    def raw(self,key):
        p,expected=self.resolve(key);raw=p.read_bytes();h=digest(raw)
        ensure(not expected or h==expected,'Manifest SHA mismatch: '+key)
        old=self.records.get(key)
        ensure(old is None or old['sha256']==h,'Source changed between reads: '+key)
        self.records[key]={'source':key,'resolved':str(p),'bytes':len(raw),'sha256':h}
        return raw
    def json(self,key):return json.loads(self.raw(key).decode('utf-8-sig'))
    def jsonl(self,key):
        rows=[]
        for line_no,line in enumerate(self.raw(key).decode('utf-8-sig').splitlines(),1):
            if line.strip():rows.append((line_no,json.loads(line)))
        return rows
    def verify_unchanged(self):
        for key,record in list(self.records.items()):
            p,_=self.resolve(key)
            ensure(digest(p.read_bytes())==record['sha256'],'Source changed during analysis: '+key)

def first_stat(values):
    clean=[float(x)for x in values if number(x)]
    return {'n':len(clean),'p50_seconds':statistics.median(clean)if clean else None,
            'sum_seconds':sum(clean)if clean else None}

def counters_delta(before,after):
    return{k:after[k]-before[k]if number(before.get(k))and number(after.get(k))else None for k in COUNTERS}

def read_block(source,block):
    result=source.json(block['result'])
    ensure(result.get('owner_closed')is True,'Only closed blocks may be recalculated: '+block['result'])
    world=source.json(block['world'])
    ensure(world.get('boundary',{}).get('phase')=='BOUNDARY','Frozen World must be at boundary')
    events=source.jsonl(block['events'])
    return result,world,events

def analyze_arm(source,spec,parent):
    name=spec['name'];participant=spec['participant'];sensor_arm=spec.get('sensor_arm','local_tag')
    ensure(participant in('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI'),'Known arm type')
    ensure(sensor_arm in('local_tag','constant_tag2'),'Known fixed sensor arm')
    issues=[];notes=[];operations={};intents={};opportunities={};feedback_by_cycle={};tool_application={}
    blocks=[];world_events={};previous_world=parent;previous_world_key=None
    previous_source_tick=parent.get('native_tick');current_cycle=None
    for bidx,block in enumerate(spec['blocks'],1):
        result,world,events=read_block(source,block)
        ensure(world['S']['completedCycles']>=previous_world['S']['completedCycles'],'World cursor regressed')
        prefix=previous_world.get('events',[]);actual_events=world.get('events',[])
        prefix_equal=isinstance(prefix,list)and isinstance(actual_events,list)and actual_events[:len(prefix)]==prefix
        if not prefix_equal:issues.append({'code':'WORLD_EVENT_PREFIX_DIFFERENCE','block':bidx})
        for index,event in enumerate(actual_events):
            world_events.setdefault(digest(canonical(event).encode()),{'event':event,'source':block['world'],'json_pointer':'/events/'+str(index)})
        beforeS=previous_world['S'];afterS=world['S']
        source_match=None
        if block.get('source_world'):
            src_world=source.json(block['source_world'])
            source_match=canonical(src_world)==canonical(previous_world)
            if not source_match:issues.append({'code':'RESTORED_SOURCE_DIFFERS_PREVIOUS_CHECKPOINT','block':bidx})
        first_event_line=None;last_event_line=None
        for line,event in events:
            ensure(isinstance(event,dict),'Event JSON object')
            kind=event.get('kind');cycle=event.get('cycle',current_cycle)
            if integer(cycle):current_cycle=cycle
            locator={'source':block['events'],'line':line}
            if kind in('NATIVE_INTENT','BACKEND_INTENT'):
                context=event.get('context',{});op=context.get('operation_id')
                if not op:issues.append({'code':'INTENT_WITHOUT_ID','locator':locator});continue
                normalized={'cycle':event.get('cycle'),'phase':event.get('phase'),'payload':event.get('payload'),'context':context}
                if op in intents and intents[op]['value']!=normalized:issues.append({'code':'CONFLICTING_INTENT_ID','operation_id':op})
                else:intents.setdefault(op,{'value':normalized,'locator':locator})
            elif kind in('NATIVE_COMPLETED','BACKEND_COMPLETED'):
                op=event.get('operation_id');ensure(isinstance(op,str),'Completed operation ID')
                normalized={'cycle':event.get('cycle'),'phase':event.get('phase'),'result':event.get('result')}
                if op in operations:
                    if operations[op]['value']!=normalized:issues.append({'code':'CONFLICTING_COMPLETED_ID','operation_id':op})
                    operations[op]['duplicate_localizers'].append(locator)
                else:operations[op]={'value':normalized,'locator':locator,'wall_seconds':event.get('wall_seconds'),'duplicate_localizers':[],'event_kind':kind}
                first_event_line=first_event_line or line;last_event_line=line
            elif kind=='MCP_COMPLETED':
                out=event.get('result');label=event.get('label')
                if isinstance(out,dict):
                    c=out.get('S',{}).get('cycle',current_cycle)
                    if label=='feedback_fields'and integer(c):feedback_by_cycle[c]={'value':out.get('feedback',{}),'locator':locator}
                    if label=='tool'and integer(c):tool_application[c]={'value':out.get('result',{}),'locator':locator}
            elif kind=='OPPORTUNITY_COMPLETED':
                c=event.get('cycle');ensure(integer(c),'Opportunity has cycle')
                row={k:v for k,v in event.items()if k not in('utc','kind')}
                if c in opportunities and opportunities[c]['value']!=row:issues.append({'code':'CONFLICTING_OPPORTUNITY_CYCLE','cycle':c})
                else:opportunities.setdefault(c,{'value':row,'locator':locator})
        # Result rows are cross-checks, not extra experiences or duplicate phases.
        for index,row in enumerate(result.get('rows',[])):
            c=row.get('cycle')
            if c in opportunities:
                if canonical(row)!=canonical(opportunities[c]['value']):notes.append({'code':'RESULT_ROW_DIFFERS_EVENT_ROW','cycle':c,'source':block['result'],'json_pointer':'/rows/'+str(index)})
            else:opportunities[c]={'value':row,'locator':{'source':block['result'],'json_pointer':'/rows/'+str(index)}}
        blocks.append({'block':bidx,'result':block['result'],'world':block['world'],
            'reported_source_tick':result.get('source_tick'), 'reported_final_tick':result.get('final_tick'),
            'world_native_tick':world.get('native_tick'),'world_completed':afterS['completedCycles'],
            'parent_event_prefix_equal':prefix_equal,'restored_source_equals_previous_checkpoint':source_match,
            'same_life_as_previous':world.get('native_life_id')==previous_world.get('native_life_id'),
            'same_session_as_previous':afterS.get('sessionId')==beforeS.get('sessionId'),
            'delta':counters_delta(beforeS,afterS),'owner_closed_reported':True,
            'material_reopen_of_final_cut_proved_by_this_block':False})
        previous_world=world;previous_world_key=block['world']
    final=previous_world
    completed=sorted(c for c in opportunities if 29<=c<=46)
    offered=sorted({v['value']['cycle']for v in intents.values()if integer(v['value'].get('cycle'))and 29<=v['value']['cycle']<=46})
    outside=sorted(c for c in opportunities if not 29<=c<=46)
    if outside:notes.append({'code':'OPPORTUNITIES_OUTSIDE_DECLARED_R07_HORIZON_NOT_SCORED','cycles':outside})
    if completed and completed!=list(range(29,max(completed)+1)):issues.append({'code':'COMPLETED_CURSOR_GAP','cycles':completed})
    phase_order=[];by_cycle={};ticks_total=0;last_tick=parent.get('native_tick');native_delta_checks=[]
    for op,record in operations.items():
        v=record['value'];cycle=v.get('cycle');phase=v.get('phase');out=v.get('result',{})
        if not integer(cycle)or not 29<=cycle<=46:continue
        ensure(phase in PHASES,'Known completed phase')
        if not isinstance(out,dict):issues.append({'code':'NONOBJECT_PHASE_RESULT','operation_id':op});continue
        by_cycle.setdefault(cycle,{})
        if phase in by_cycle[cycle]:issues.append({'code':'MULTIPLE_UNIQUE_PHASE_IDS_FOR_CYCLE','cycle':cycle,'phase':phase})
        by_cycle[cycle][phase]={'operation_id':op,'output':out,'intent':intents.get(op),'locator':record['locator']}
        phase_order.append({'operation_id':op,'cycle':cycle,'phase':phase,'result':out,'locator':record['locator'],'wall_seconds':record['wall_seconds']})
        if participant=='LIVE_NATIVE':
            tick=out.get('nativeTick');delta=out.get('nativeTicks')
            if integer(tick)and integer(delta):
                before=tick-delta
                if last_tick is not None and before!=last_tick:issues.append({'code':'NATIVE_TICK_GAP','operation_id':op,'expected_before':last_tick,'observed_before':before})
                ticks_total+=delta;last_tick=tick
                native_delta_checks.append({'operation_id':op,'before':before,'after':tick,'delta':delta})
            else:issues.append({'code':'MISSING_NATIVE_TICK_DELTA','operation_id':op})
        elif out.get('nativeTicks',0)!=0 or out.get('nativeTick',0)!=0:issues.append({'code':'REFERENCE_CLAIMS_NATIVE_TICKS','operation_id':op})
    if participant=='LIVE_NATIVE'and integer(final.get('native_tick')):
        if ticks_total!=final['native_tick']-parent['native_tick']:issues.append({'code':'NATIVE_TOTAL_MISMATCH','dedup_phase_sum':ticks_total,'world_delta':final['native_tick']-parent['native_tick']})
    rows=[];numeric=[];lessons=[];memory=[];latencies={p:[]for p in PHASES};previousS=parent['S'];loops=0
    phase_choice_counts={'material_null':0,'voluntary_wait':0,'invalid_policy_output':0,'material_zero_memory':0}
    for entry in phase_order:latencies[entry['phase']].append(entry['wall_seconds'])
    for cycle in completed:
        raw=opportunities[cycle]['value'];after=raw['state_after'];phase=by_cycle.get(cycle,{})
        q1=phase.get('decision',{}).get('output',raw.get('Native_Q1')or{})
        q2=phase.get('query_sensor',{}).get('output',raw.get('Native_Q2')or{})
        wr=dict(raw.get('world_result')or{});wr_locator=opportunities[cycle]['locator']
        if cycle in tool_application:wr.update(tool_application[cycle]['value']);wr_locator=tool_application[cycle]['locator']
        fb=feedback_by_cycle.get(cycle)
        if fb:
            for k in('outcome','collision','resourceCollected','resourceDelivered','permissionSpent','materialConsequence'):
                if k in fb['value']:wr[k]=fb['value'][k]
            wr_locator=fb['locator']
        elif'feedback'in phase:
            intent=phase['feedback']['intent']
            if intent:
                f=intent['value'].get('payload')or{}
                for k in('outcome','collision','resourceCollected','resourceDelivered','permissionSpent','materialConsequence'):
                    if k in f:wr[k]=f[k]
                wr_locator=intent['locator']
        for out in(q1,q2):
            if not out:continue
            if out.get('null')is True:phase_choice_counts['material_null']+=1
            if out.get('voluntary_wait')is True and out.get('null')is False:phase_choice_counts['voluntary_wait']+=1
            if out.get('invalid')is True:phase_choice_counts['invalid_policy_output']+=1
        origin=previousS.get('station');destination=after.get('station')
        moved=after.get('moves',0)>previousS.get('moves',0)
        loop_transition=bool(moved and(origin,destination)in((2,3),(3,2)))
        loops+=int(loop_transition)
        selected=q2.get('action')if q2 else None;executed=raw.get('executed_route')
        actual_override=selected is not None and executed is not None and selected!=executed
        delta=counters_delta(previousS,after)
        q2_intent=(phase.get('query_sensor',{}).get('intent')or{}).get('value',{})
        q2_sensors=(q2_intent.get('payload')or{}).get('observation',{}).get('sensors',{})
        raw_price=q2_sensors.get('stationSignal');actual_tag=q2_sensors.get('publicContactCode')
        submitted_tag=2 if sensor_arm=='constant_tag2'else actual_tag
        recalculated_datum=(raw_price+3*submitted_tag)if integer(raw_price)and raw_price>=0 and integer(submitted_tag)else None
        row={'arm':name,'participant':participant,'cycle':cycle,'new_opportunity':cycle-28,
             'period':'FIRST6'if cycle<=34 else'CONTINUATION_BEFORE_CHANGE'if cycle<=40 else'CHANGED_RESERVE',
             'origin':origin,'destination':destination,'q1':q1.get('action'),'q1_null':q1.get('null'),
             'selected_route':selected,'executed_route':executed,'route_null':q2.get('null')if q2 else None,
             'voluntary_wait':bool((q1.get('voluntary_wait')is True and q1.get('null')is False)or(q2.get('voluntary_wait')is True and q2.get('null')is False)),
             'material_move':moved,'loop_2_3_transition':loop_transition,'effective_override':actual_override,
             'motor_status':(wr.get('motor')or{}).get('status',wr.get('motorStatus')),
             'outcome':wr.get('outcome'),'world_result_locator':wr_locator,
             'A_present':after.get('numberAPresent'),'actual_A':after.get('numberA'),
             'A_version':after.get('numberAVersion'),'B_present':after.get('codeBPresent'),'actual_B':after.get('finalCode'),
             'B_current':bool(after.get('codeBPresent')and after.get('codeBFromAVersion')==after.get('numberAVersion')),
             'round':after.get('round'),'tuple':after.get('roundOperands'),
             'new_resources':delta.get('resourceCount'),'new_deliveries':delta.get('delivered'),
             'query_cost':delta.get('queries'),'toll_cost':delta.get('tollSpent'),
             'stock_after':after.get('permissionStock'),'source':opportunities[cycle]['locator']}
        row.update(raw_paid_price=raw_price,actual_contact_tag=actual_tag,submitted_contact_tag=submitted_tag,
            q2_datum_recalculated_from_frozen_contract=recalculated_datum,
            input_recalculation_scope='Recorded public observation + fixed encoder; not a new material consultation or an independently measured input receipt')
        fn=phase.get('function')
        if fn:
            tool=(fn.get('intent')or{}).get('value',{}).get('payload',{}).get('tool',{})
            out=fn['output'];tr=out.get('toolResult',raw.get('tool_result')or{})
            if not isinstance(tr,dict):tr={}
            if tool.get('kind')=='CALCULATE':
                value=tr.get('numeric_result');formed=tr.get('formed')is not False and integer(value)
                opcode=tr.get('operation');left=tool.get('left');right=tool.get('right')
                reference=(left+right if opcode=='suma'else left-right if opcode=='diferencia'else None)if integer(left)and integer(right)else None
                correct=(value==reference)if formed and reference is not None else None
                mem=tr.get('memory_value');phase_choice_counts['material_zero_memory']+=int(type(mem)is int and mem==0)
                n={'cycle':cycle,'operation_id':fn['operation_id'],'slot':tool.get('slot'),'form':tool.get('form'),
                   'left':left,'right':right,'memory_value':mem,'actual_operation':opcode,'numeric_result':value,
                   'formed_integer':formed,'correct_given_actual_opcode':correct,'offline_reference':reference,
                   'actual_B_input_matches_previous_A':left==previousS.get('numberA')if tool.get('slot')=='B'and previousS.get('numberAPresent')else None,
                   'request_accepted':out.get('accepted'),'capability_execution_admitted':tr.get('capability_execution_admitted'),
                   'reason':tr.get('reason'),'compact_evidence_locator':out.get('compactEvidence'),
                   'locator':fn['locator']}
                numeric.append(n);memory.append({'cycle':cycle,'form':tool.get('form'),'value':mem,'locator':fn['locator']})
                row.update(numeric_result=value,numeric_formed=formed,numeric_correct=correct,operation=opcode,memory_value=mem,form=tool.get('form'))
            elif tool.get('kind')=='LESSON':
                lessons.append({'cycle':cycle,'operation_id':fn['operation_id'],'visible_items':tool.get('items'),
                    'request_accepted':out.get('accepted'),'capability_execution_admitted':tr.get('capability_execution_admitted'),
                    'reason':tr.get('reason'),'receipt_input_counts':None,
                    'compact_updates_reported':tr.get('updates'),'compact_evidence_locator':out.get('compactEvidence'),
                    'receipt_note':'No per-input admission denominator is inferred from a compact tool flag. Read the linked primary when needed.',
                    'locator':fn['locator']})
        rows.append(row);previousS=after
    first6=[r for r in rows if r['cycle']<=34];last3=first6[-3:]
    exits=sum(1 for r in last3 if r['material_move']and r['destination']not in(2,3))
    summary={'name':name,'participant':participant,'sensor_arm':sensor_arm,'offered_cycles':offered,
      'completed_cycles':completed,'completed_new':len(completed),'uncompleted_offered':sorted(set(offered)-set(completed)),
      'parent_inventory_resource':parent['S'].get('inventoryResource'),'inherited_delivery_credit':0 if parent['S'].get('inventoryResource')is False else None,
      'parent_counters':{k:parent['S'].get(k)for k in COUNTERS},'final_counters':{k:final['S'].get(k)for k in COUNTERS},
      'delta':counters_delta(parent['S'],final['S']),'final_native_tick':final.get('native_tick'),
      'deduplicated_completed_operations':len(phase_order),'duplicate_operation_localizers':sum(len(v['duplicate_localizers'])for v in operations.values()),
      'native_ticks_from_unique_phases':ticks_total if participant=='LIVE_NATIVE'else 0,
      'native_tick_checks':native_delta_checks,'blocks':blocks,
      'calculation_opportunities':len(numeric),'formed_integer_outputs':sum(n['formed_integer']for n in numeric),
      'correct_given_actual_opcode':sum(n['correct_given_actual_opcode']is True for n in numeric),
      'wrong_given_actual_opcode':sum(n['correct_given_actual_opcode']is False for n in numeric),
      'numeric_no_integer':sum(not n['formed_integer']for n in numeric),
      'lesson_calls':len(lessons),'numeric':numeric,'lessons':lessons,'memory_reads':memory,
      'loop_2_3_transitions':loops,'effective_host_overrides':sum(r['effective_override']for r in rows),
      'first6_P02':{'completed':len(first6),'outside_2_3_in_last3':exits,
        'sustained_exit_criterion_met':len(first6)==6 and exits>=2,
        'learning_not_inferred_from_new_encoder':True},
      'phase_choice_counts':phase_choice_counts,'latencies':{p:first_stat(v)for p,v in latencies.items()},
      'last_final_cut_materially_reopened':False,'rows':rows,'issues':issues,'notes':notes,
      'limits':['Arithmetic correctness is evaluated against the chosen actual opcode, separately from the World objective.',
       'New sensor fields/ABI do not establish semantic decoding or acquired navigation.',
       'Teaching admission is not functional recall. Nara must be actually queried after its lesson before credit.',
       'No full historical retention panel is inferred from these episodes.',
       'Source file availability/hashes are not a material Native reopen.',
       'World.S.latency is inherited; only phase wall_seconds is used.']}
    return summary

def run(spec,source):
    ensure(spec.get('schema')=='DEE.R07.recalculation.inputs.v1','Explicit input schema')
    parent=source.json(spec['parent_world'])
    ensure(parent['native_tick']==991187 and parent['S']['completedCycles']==28,'Exact PAR28 baseline')
    arms=[analyze_arm(source,a,parent)for a in spec['arms']]
    wanted=[a for a in arms if a['participant']in('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')and a.get('sensor_arm')!='constant_tag2']
    common=set.intersection(*[set(a['completed_cycles'])for a in wanted])if wanted else set()
    comparison=[]
    for arm in arms:
        for scope,cycles in [('FULL_OBSERVED',set(arm['completed_cycles'])),('COMMON_OBSERVED_PREFIX',common)]:
            rs=[r for r in arm['rows']if r['cycle']in cycles]
            comparison.append({'arm':arm['name'],'participant':arm['participant'],'scope':scope,
              'completed':len(rs),'new_resources':sum(r['new_resources']or 0 for r in rs),
              'new_deliveries':sum(r['new_deliveries']or 0 for r in rs),
              'queries':sum(r['query_cost']or 0 for r in rs),'toll_cost':sum(r['toll_cost']or 0 for r in rs),
              'numeric_calls':sum('numeric_formed'in r for r in rs),'integers':sum(r.get('numeric_formed')is True for r in rs),
              'correct_chosen_opcode':sum(r.get('numeric_correct')is True for r in rs),
              'no_integer':sum(r.get('numeric_formed')is False for r in rs),
              'loop_2_3':sum(r['loop_2_3_transition']for r in rs),
              'effective_overrides':sum(r['effective_override']for r in rs)})
    source.verify_unchanged()
    main_arms=[a for a in arms if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='local_tag']
    control_arms=[a for a in arms if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='constant_tag2']
    paired=[]
    for main in main_arms:
        for control in control_arms:
            m=main['rows'][:6];c=control['rows'][:6]
            paired.append({'main':main['name'],'control':control['name'],
                'main_completed_first6':len(m),'control_completed_first6':len(c),
                'same_offered_global_cycles':[r['cycle']for r in m]==[r['cycle']for r in c],
                'first_contract_datum_equal':m[0]['q2_datum_recalculated_from_frozen_contract']==c[0]['q2_datum_recalculated_from_frozen_contract']if m and c else None,
                'main_fixed_criterion':main['first6_P02'],'control_fixed_criterion':control['first6_P02'],
                'baseline_world_shared':True,'Native_physical_prefix_equality_requires_import0_proof':True,
                'dose_note':'Actions, queries and consequences after the sensor intervention can differ endogenously; do not assume all admitted dose matched.',
                'interpretation':'An encoder-dependent functional difference is not by itself acquired contextual navigation.'})
    return{'schema':VERSION,'mode':'PASSIVE_FROZEN_FILES_NOT_NATIVE_REPRODUCTION',
      'parent':{'path':spec['parent_world'],'native_tick':991187,'world_completed':28,
        'inventory_resource':parent['S'].get('inventoryResource'),'resourceCount':parent['S'].get('resourceCount'),'delivered':parent['S'].get('delivered')},
      'target_new_per_main_reference':18,'main_global_horizon':[29,46],
      'arms':arms,'comparison':comparison,'common_observed_cycles':sorted(common),
      'comparison_group_arms':[a['name']for a in wanted],
      'has_all_three_configurations':{'LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI'}.issubset({a['participant']for a in wanted}),
      'P02_paired_comparisons':paired,
      'sources':list(source.records.values()),'issues_total':sum(len(a['issues'])for a in arms),
      'interpretation_limits':['One history per arm; shared Native prefix is not independent replication.',
       'Reference symbolic prior and pretrained model differ from Native physical history.',
       'Missing/unoffered episodes are not failures and are not projected to the full horizon.',
       'Control constant_tag2 is an information intervention, not an equal strategic intelligence benchmark.',
       'No Native, model, SDK, World, queue, database or source state was modified.']}

def save_outputs(out,facts):
    out=Path(out);ensure(not out.exists(),'Fresh analysis output required');out.mkdir(parents=True)
    (out/'HECHOS_CIERRE8_R07.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=[r for arm in facts['arms']for r in arm['rows']]
    def csv_file(name,values):
        if not values:return
        fields=list(dict.fromkeys(k for row in values for k in row))
        with(out/name).open('w',encoding='utf-8',newline='')as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for row in values:writer.writerow({k:canonical(v)if isinstance(v,(dict,list))else v for k,v in row.items()})
    csv_file('TODAS_OPORTUNIDADES_R07.csv',rows);csv_file('COMPARACION_R07.csv',facts['comparison'])
    lines=['Recálculo pasivo R07. No reproduce DEE.','',f"Incidencias: {facts['issues_total']}",
      'Los costes y resultados se restan del World PAR28; no se cuenta la historia anterior como nueva.',
      'No se imputa fallo aritmético a una salida sin entero ni capacidad a un episodio no ofrecido.','']
    for arm in facts['arms']:
        lines.append(f"{arm['name']}: {arm['completed_new']} oportunidades completas; "
          f"enteros correctos {arm['correct_given_actual_opcode']}/{arm['formed_integer_outputs']} formados "
          f"({arm['calculation_opportunities']} invocaciones), sin entero {arm['numeric_no_integer']}; "
          f"nuevos recursos {arm['delta'].get('resourceCount')}; nuevas entregas {arm['delta'].get('delivered')}; "
          f"transiciones2/3 {arm['loop_2_3_transitions']}; overrides efectivos {arm['effective_host_overrides']}.")
    lines.extend(['','Aprendizaje, revisión causal, reapertura material y tres propietarios simultáneos requieren sus primarios propios; este resumen no los certifica automáticamente.'])
    (out/'LEER_RECALCULO_R07.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source-root',type=Path)
    p.add_argument('--package-root',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();spec=json.loads(a.inputs.read_text('utf-8-sig'))
    source=Sources(a.source_root or a.inputs.parent,a.package_root)
    facts=run(spec,source);save_outputs(a.output,facts)
    print(json.dumps({'output':str(a.output),'issues':facts['issues_total'],
       'arms':[{k:arm[k]for k in('name','completed_new','formed_integer_outputs','correct_given_actual_opcode','numeric_no_integer')}for arm in facts['arms']],
       'Native_executed':False,'model_called':False},ensure_ascii=False))
