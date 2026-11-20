"""PI04 C2C: recorded-data export, fixed20-slot yoke, central q+4 and hold q+6 and analytical references.

Standard library only. No DEE import, SQLite, Native execution or actor policy. C2C adaptation is PREPARED; no synthetic or Native validation is claimed by constructing this source.
Export reads only CLOSED summaries and their completed primaries plus immutable
resource/product files. Recalculation opens only relative exported members.
Reference policies and required answers are EVALUATION ONLY, never actor input.
"""
from __future__ import annotations
import argparse, base64, collections, gzip, hashlib, json, shutil, zlib
from pathlib import Path

VERSION = 'DEE.PI04.C2C.documentary_recalculation.R01'
E3_VERSION = 'PI04.E3.stratified_fixed_rotation.R01'
CAL_KEYS = ('query_tick','query_read_tick','outcome_injection_tick','contact_tick','delay_laps','reference_contact_phase')
FOLDER = 'PI04_C2C_COORDINACION_R01'

def need(ok, message):
    if not ok: raise ValueError(message)
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def sha(b): return hashlib.sha256(b).hexdigest()
def read_json(path):
    b=Path(path).read_bytes(); return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b.decode('utf-8-sig'))
def safe(root, name):
    p=Path(name); need(not p.is_absolute() and '..' not in p.parts,'Relative member only')
    result=root/p; need(result.resolve().is_relative_to(root.resolve()),'Escaping member')
    return result
def load(root,name): return read_json(safe(root,name))
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8'))
def fresh(path):
    need(not path.exists(),'Fresh destination required; no overwrite'); path.mkdir(parents=True)
def outer(value):
    need(value['status']=='completed','Only completed primary may be recalculated')
    v=json.loads(value['result'])if isinstance(value['result'],str)else value['result']
    need(len(v['result']['rows'])==1,'One material row required')
    return v,v['result']['rows'][0]
def physical(o):
    r=int(o['raw']); need(0<=r<2**64,'uint64 RAW required')
    def nib(n):
        k=(r>>n)&15; return k-16 if k>=8 else k
    v={'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[nib(48),nib(52),nib(56)]}
    need(all(v[k]==o[k]for k in v),'Recorded physical fields differ from RAW')
    return v
def six_reader(reader,origin):
    candidates=[]; expected=set()
    for x in(-1,0,1):
        for z in(0,-1): expected.add(((origin[0]+2*x)%67,(origin[1]+2)%67,(origin[2]+2*z)%67))
    observed=set()
    for item in reader['observations']:
        o=item.get('physical',item); v=physical(o); site=tuple(item.get('site',o['site'])); observed.add(site)
        for x in(-1,0,1):
            for z in(0,-1):
                target=((origin[0]+2*x)%67,(origin[1]+2)%67,(origin[2]+2*z)%67)
                if site==target and v['state']>0 and v['semantic']==1 and v['direction']==[x,1,z]: candidates.append(x)
    need(observed==expected and len(reader['observations'])==6,'Exact six frozen reader sites required')
    choice=candidates[0]if len(candidates)==1 else None
    need(choice==reader['choice'],'Recorded choice differs from fixed six-site signature')
    return choice
def central_reader(reader,query_tick):
    # Exact sensor pi04_sensor_central_C2C_R01.py; no six-site/window search.
    o=reader['observation'];v=physical(o);direction=v['direction']
    need(tuple(o['site'])==(19,54,5),'Single frozen central Q site required')
    need(reader['tick']==reader['physical_read_tick']==query_tick+4,'Actual first read must be q+4')
    need(reader['available_for_actuation_tick']==query_tick+6,'Two-tick prepared hold must preserve q+6 availability')
    valid=v['state']>0 and v['semantic']==1 and direction[0]in(-1,0,1)and direction[1]==1 and direction[2]in(-1,0)
    choice=direction[0]if valid else None
    need(reader['choice']==choice,'Central fixed signature differs; no favourable later read')
    return choice

def motor(choice): return -1 if choice==0 else choice
def operation(choice): return 'suma'if choice==1 else 'diferencia'if choice in(-1,0)else None
def calendar(c):
    need(set(c)==set(CAL_KEYS)and all(type(c[k])is int for k in c),'Exact calendar fields')
    need(c['delay_laps']==4 and c['reference_contact_phase']==391,'Predeclared L4/phase391 required')
    need(c['query_read_tick']==c['query_tick']+6,'Unchanged q+6 only')
    need(c['outcome_injection_tick']==c['contact_tick']-2 and c['contact_tick']-c['query_read_tick']==67*4+2,'Frozen generic-return/efference timing')
    return c
def verify_row(row,spec,env):
    need(row['spec']==spec,'Primary does not match sealed public fixture')
    c=row['calendar']; n=calendar(row['normalized_calendar'])
    need(all(c[k]==n[k]for k in CAL_KEYS[:-1]),'Normalized/physical calendar mismatch')
    need(row['after_tick']==c['contact_tick']+2 and 0<row['after_tick']-row['before_tick']<=1500,'Finite original settled boundary')
    for b in row['bank_before']+row['bank_after']: physical(b)
    phases=[(int(b['clock'])+c['contact_tick']-row['before_tick'])%782 for b in row['bank_before']]
    need(phases==[391,391],'Both bank contact phases required')
    first=central_reader(row['first_reader'],c['query_tick'])
    need(row['physical_read_tick']==c['query_tick']+4 and row['actuation_availability_tick']==c['query_read_tick'],'Original first read/hold metadata required')
    op=operation(first); need(op==row['selected_operation'] and motor(first)==row['first_motor'],'First fixed codec changed')
    num=row['actual_numeric_result']; arithmetic=row['native_arithmetic']; arith_correct=None
    if op is not None:
        need(arithmetic is not None,'Selected operation lacks actual Native trial')
        request=arithmetic['literal_operator_request']
        need(request['operacion']==op and request['izquierda']==spec['left']and request['derecha']==spec['right'],'Operands or actual function replaced')
        reader=arithmetic['numeric_reader'];o=reader['observation'];physical(o)
        if reader['fixed_site_direction_valid']:
            need(num==arithmetic['numeric_result']==reader['numeric_result']==o['s_reg']-reader['representation_bias'],'Actual integer not derived from fixed RAW reader')
        else:need(num is None,'Invalid numeric reader must not receive expected fallback')
        expected=spec['left']+spec['right']if op=='suma'else spec['left']-spec['right']
        arith_correct=type(num)is int and num==expected
    else:need(arithmetic is None and num is None,'NULL must not invoke an invented function')
    second=row['second_native_use']; second_choice=None
    if second is not None and second.get('reader')is not None:
        second_choice=six_reader(second['reader'],(15,15,15))
        need(second['read_tick']==second['query_tick']+6,'MU reader must retain q+6')
        need(second['raw_sensor_value']==num,'MU must receive actual upstream Native integer')
    need(row['second_motor']==motor(second_choice),'Second motor differs from actual signature')
    route=None if row['arm']=='actuator_null'else motor(second_choice)
    need(row['applied_route']==route,'External actuator did not apply fixed Native route')
    wanted=env['low_operation']if spec['context']<=env['context_cut']else env['high_operation']
    valid=type(num)is int and 0<=num<=65535
    target=(env['low_route']if num<=env['numeric_cut']else env['high_route'])if valid else None
    success=valid and op==wanted and route is not None and route==target
    effect=row['actual_effect'];need(type(row['actual_failed'])is bool and type(row['returned_failed'])is bool,'No NULL/zero coercion to consequence')
    need(effect['actual_operation']==op and effect['actual_value']==num and effect['actual_route']==route,'Device did not receive actual output')
    need(effect['failed']==row['actual_failed']==(not success)and row['useful_product']==success,'Actual device law/product mismatch')
    need(effect['actual_deadline']==c['outcome_injection_tick']-1,'Actual effect precedes generic return by one fixed tick')
    need(effect['private_evaluator_only']=={'required_operation':wanted,'connected_route':target},'Evaluator metadata inconsistent')
    groups={'outer':row['requests']}
    if arithmetic is not None:groups['arithmetic']=arithmetic['native_operation']['native_trial']['requests']
    if second is not None and 'requests'in second:groups['MU']=second['requests']
    unique={};aliases=0;outside=0
    for label,requests in groups.items():
        for req in requests:
            receipt=req['receipt']; tick=receipt['requested_tick']; identifier=int(req['id'])
            # Some old function evidence repeats historical requests as context.
            if not row['before_tick']<tick<=row['after_tick']:outside+=1;continue
            need(identifier==int(receipt['id']),'Native receipt ID mismatch')
            status=receipt['status']
            need(status=='applied'or status.startswith('rejected'),'Pending/unknown receipt is not a closed input')
            need(receipt['effective_tick']==tick if status=='applied'else receipt['effective_tick']is None,'Applied/rejected boundary differs')
            if identifier in unique:
                need(unique[identifier]==receipt,'Conflicting receipt alias'); aliases+=1
            else:unique[identifier]=receipt
    context_count=0 if row['arm']=='context_cut'else 1
    need(row['context_input_supplied']==(context_count==1),'Context intervention differs')
    need(len(row['requests'])==3+context_count+int(first is not None)+1,'Outer physical dose differs')
    query={r['channel']:r for r in row['requests']if r['channel'].startswith('PI03.TC.R01.')}
    for name in('query','support.plus','support.minus'):
        r=query['PI03.TC.R01.'+name];need(r['payload']==0 and r['requested_tick']==c['query_tick'],'Prepared query/support changed')
    data=[r for r in row['requests']if 'datum'in r['channel']]
    need(len(data)==context_count and all(r['payload']==spec['context']and r['requested_tick']==c['query_tick']+3 for r in data),'Single current datum is not fixed public context')
    ret=[r for r in row['requests']if '.outcome.'in r['channel']];need(len(ret)==1,'Exactly one generic consequence')
    need(ret[0]['channel']=='PI03.TC.R01.outcome.'+('failure'if row['returned_failed']else'nonfailure')and ret[0]['requested_tick']==c['outcome_injection_tick'],'Return type/timing differs')
    need(row['reconciliation']['finished']and row['reconciliation']['actual_receipt']['id']==ret[0]['id'],'Feedback not reconciled')
    if row['arm']in('real','context_cut','link_cut','actuator_null'):need(row['returned_failed']==row['actual_failed'],'Real arm has noncontingent feedback')
    if row['arm']=='none':need(row['returned_failed']is False,'None arm must use declared nonfailure material return')
    quality=row['native_input_summary'];counts=collections.Counter(r['status']for r in unique.values())
    need(quality['unique_requested']==len(unique)and quality['applied']==counts.get('applied',0),'Native primary counter differs from direct deduplicated receipts')
    need(quality['rejected']==sum(v for k,v in counts.items()if k.startswith('rejected'))and quality['pending_or_other']==0 and quality['all_terminal'],'Terminal rejections/uncertainty mismatch')
    return {'ordinal':row['ordinal'],'stage':spec['stage'],'context':spec['context'],'left':spec['left'],'right':spec['right'],
        'before_tick':row['before_tick'],'after_tick':row['after_tick'],'calendar':n,'first_choice':first,'operation':op,
        'first_operation_correct':op==wanted,'actual_numeric_result':num,'arithmetic_correct':arith_correct,
        'second_choice':second_choice,'actual_route':route,'route_correct_given_actual_result':route is not None and route==target,
        'actual_failed':row['actual_failed'],'returned_failed':row['returned_failed'],'useful_product':success,
        'first_NULL_preserved':row['first_NULL_preserved'],'unique_inputs':len(unique),'aliases':aliases,'out_of_window_receipts':outside,
        'native_ids':sorted(unique),'receipt_statuses':dict(collections.Counter(r['status']for r in unique.values())),
        'rejected_inputs':[{'id':i,**r}for i,r in unique.items()if r['status']!='applied'],
        'bank_before':[b['s_reg']for b in row['bank_before']],'bank_after':[b['s_reg']for b in row['bank_after']]}

def fixed_plan(rows,identity):
    need([r['ordinal']for r in rows]==list(range(20)),'Plan requires exactly twenty observed real effects0..19')
    records=[{'ordinal':r['ordinal'],'calendar':calendar(r['calendar']),'failed':r['actual_failed']}for r in rows]
    slots=[{'ordinal':i,'calendar':r['calendar'],'source_ordinal':(i+1)%20,'returned_failed':records[(i+1)%20]['failed']}for i,r in enumerate(records)]
    counts=collections.Counter(r['failed']for r in records);changed=sum(r['failed']!=s['returned_failed']for r,s in zip(records,slots))
    body={'schema':'DEE.PI04.E3.frozen_signal_plan.v1','version':E3_VERSION,'frozen_rule':'rotate_plus_one_within_delay_phase',
        'source_identity':identity,'source_records':records,'source_records_sha256':sha(canon(records)),'slots':slots,
        'strata':[{'delay_laps':4,'reference_contact_phase':391,'slots':list(range(20)),'failure':counts[True],
                   'nonfailure':counts[False],'changed_signal_slots':changed}],
        'source_signal_changes':changed,'attribution':'Experimental control schedule only. Not cognitive memory, a learned policy or Native agency.'}
    envelope={'plan':body,'sha256':sha(canon(body))};raw=canon(envelope)
    need(len(raw)<=32768,'Expanded plan exceeds fixed32KB limit')
    packed='E3Z1:'+base64.urlsafe_b64encode(zlib.compress(raw,9)).decode('ascii');need(len(packed)<=6144,'Encoded plan exceeds fixed6144chars')
    return envelope,packed

def references(rows,env):
    """Analytical counterfactuals; no Native result is invented or fed to actor.

    Each reference sees the public context, operands and its own prior generic
    consequence. A declared fixed numeric comparator maps its analytical result
    to a route, OR a fixed route is used. Neither is a new Native execution.
    """
    refs=[]
    for strategy in('fixed','WSLS_global','WSLS_exact_context'):
        for initial in(-1,1):
            for route_policy in(-1,1,'fixed_numeric_comparator'):
                state={};events=[]
                for r in rows:
                    key=r['context']if strategy=='WSLS_exact_context'else'global'
                    choice=state.get(key,initial); op=operation(choice)
                    num=r['left']+r['right']if op=='suma'else r['left']-r['right']
                    route=(-1 if num<=20 else 1)if route_policy=='fixed_numeric_comparator'else route_policy
                    wanted=env['low_operation']if r['context']<=env['context_cut']else env['high_operation']
                    needed=-1 if num<=20 else 1
                    good=0<=num<=65535 and op==wanted and route==needed
                    events.append({'ordinal':r['ordinal'],'stage':r['stage'],'choice':choice,'operation':op,
                        'analytical_number':num,'route':route,'analytical_product':good,
                        'matches_observed_first_choice':choice==r['first_choice'],
                        'matches_observed_selected_operation':op==r['operation'],
                        'first_operation_correct':op==wanted})
                    if strategy!='fixed':state[key]=choice if good else-choice
                def score(indices):return {'included':len(indices),'analytical_products':sum(events[i]['analytical_product']for i in indices),
                    'exact_physical_first_choice_matches':sum(events[i]['matches_observed_first_choice']for i in indices),
                    'selected_operation_matches':sum(events[i]['matches_observed_selected_operation']for i in indices),
                    'first_operation_correct':sum(events[i]['first_operation_correct']for i in indices)}
                refs.append({'name':strategy+'_initial'+str(initial)+'_route'+str(route_policy),'strategy':strategy,
                    'second_route_policy':route_policy,'all':score(range(len(rows))),
                    'reserve8':score([i for i,r in enumerate(rows)if 12<=r['ordinal']<20]),
                    'crossed22_23':score([i for i,r in enumerate(rows)if r['ordinal']in(22,23)]),
                    'rows':events,'mode':'ANALYTICAL_COUNTERFACTUAL_NOT_NATIVE',
                    'information':'Public context/operands and OWN previous analytical action/consequence; second fixed comparator explicitly assisted.'})
    matched=[]
    for contextual in(False,True):
        for initial in(-1,1):
            state={};events=[]
            for r in rows:
                key=r['context']if contextual else'global';a=state.get(key,initial)
                events.append({'ordinal':r['ordinal'],'predicted_first_choice':a,'observed':r['first_choice'],
                    'match':a==r['first_choice'],'selected_operation_match':operation(a)==r['operation']})
                state[key]=-a if r['returned_failed']else a
            matched.append({'contextual':contextual,'initial':initial,'first_choice_matches':sum(e['match']for e in events),
                'selected_operation_matches':sum(e['selected_operation_match']for e in events),
                'zero_and_minus_are_same_prepared_function_not_same_material_signature':True,
                'rows':events,'mode':'POSTHOC_RECEIVED_SIGNAL_DESCRIPTION_ONLY','products_not_imputed':True})
    return {'counterfactual_references':refs,'received_signal_first_choice_descriptions':matched}

def export(args):
    need(args.summary,'At least one closed summary required')
    summaries=[(p.resolve(strict=True),read_json(p))for p in args.summary]
    for p,s in summaries:need(s.get('owner_closed')is True and s['schema']=='DEE.PI04.C2C.actual_batch.R01','Only actually closed C2C batches may export')
    protocol=read_json(args.protocol);need(protocol['schema']=='DEE.PI04.C2C.protocol.R01'and protocol['status']=='SEALED_FOR_EVALUATION','Actual sealed C2C evaluation protocol required, not the source draft')
    fresh(args.out);(args.out/'protocol.json').write_bytes(args.protocol.read_bytes());arms={};sources=[]
    for sp,s in summaries:
        arm=s['arm'];item=arms.setdefault(arm,{'life':s['life'],'summaries':[],'primaries':{},'files':{}})
        need(item['life']==s['life'],'Cannot merge different lives into one arm')
        name=arm+'/summaries/'+sp.name+'.gz';safe(args.out,name).parent.mkdir(parents=True,exist_ok=True)
        safe(args.out,name).write_bytes(gzip.compress(sp.read_bytes(),mtime=0));item['summaries'].append(name)
        for row in s['rows']:
            i=row['ordinal'];need(str(i)not in item['primaries'],'Repeated ordinal is not a new experience')
            pp=Path(row['primary']).resolve(strict=True);o=read_json(pp);_,r=outer(o)
            need(r['ordinal']==i and r['arm']==arm,'Primary arm/ordinal differs from summary')
            target=arm+'/primaries/%02d.json.gz'%i;safe(args.out,target).parent.mkdir(parents=True,exist_ok=True)
            safe(args.out,target).write_bytes(gzip.compress(pp.read_bytes(),mtime=0));item['primaries'][str(i)]=target
            # Owner transport/SQLite lives in servicios_persistentes, whereas
            # complete environment/capability artifacts live in servicios_locales.
            home=args.system_root.resolve(strict=True)/'estado/servicios_locales'/s['life']/FOLDER/'dispositivo'
            resource='%04d.resource'%i;matches=[home/d/resource for d in('reservoir','inflight_minus','inflight_plus','inflight_silence','consumed','rejected')if(home/d/resource).is_file()]
            need(len(matches)==1,'Exactly one actual immutable resource file required')
            def blob(f):
                b=f.read_bytes();dest='blobs/'+sha(b)+'.bin';d=safe(args.out,dest);d.parent.mkdir(exist_ok=True)
                if d.exists():need(d.read_bytes()==b,'Content address collision')
                else:d.write_bytes(b)
                return {'member':dest,'bytes':len(b),'sha256':sha(b)}
            entry={'resource':blob(matches[0]),'product':None}
            product=r['actual_effect']['product']
            if product is not None:entry['product']=blob(safe(home,product['path']))
            item['files'][str(i)]=entry
        sources.append({'summary':str(sp),'bytes':sp.stat().st_size,'sha256':sha(sp.read_bytes())})
    dump(args.out/'INDEX.json',{'schema':VERSION,'arms':arms,'sources_reference_only':sources,'source_paths_opened_during_recalculation':False})
    shutil.copyfile(Path(__file__).resolve(),args.out/'RECALCULAR_C2C_R01.py')
    files=[]
    for f in sorted(args.out.rglob('*')):
        if f.is_file():b=f.read_bytes();files.append({'file':f.relative_to(args.out).as_posix(),'bytes':len(b),'sha256':sha(b)})
    dump(args.out/'MANIFEST.json',{'schema':VERSION,'files':files,'self_hash_excluded':True})
    result=analyze(args.out)
    if args.plan20:
        real=result['arms'].get('real');need(real is not None,'Actual real history required')
        first=[r for r in real['rows']if r['ordinal']<20]
        need(len(first)==20,'No control plan is fabricated before twenty actual effects')
        need(all(r['first_choice']is not None and r['receipt_statuses'].get('applied',0)==r['unique_inputs']for r in first),'Twenty closed fully-admitted cases required for matched20 plan; preserve rejected/NULL history without fabrication')
        identity={'life':real['life'],'first_tick':first[0]['before_tick'],'last_tick':first[-1]['after_tick'],
                  'source_export_manifest_sha256':sha((args.out/'MANIFEST.json').read_bytes()),'scope':'Actual first20effects only; no retention/cross/future supply signals'}
        envelope,packed=fixed_plan(first,identity)
        dump(args.out/'PLAN_C2C_YOKED20_E3.json',envelope);dump(args.out/'PLAN_C2C_YOKED20_ENCODED.json',packed)
        dump(args.out/'PLAN_C2C_YOKED20_AUDITORIA.json',{'Native_ticks':0,'rule':'rotate_plus_one_within_delay_phase','signals':20,
            'failure':sum(r['actual_failed']for r in first),'nonfailure':sum(not r['actual_failed']for r in first),
            'changed_source_slots':envelope['plan']['source_signal_changes'],
            'potential_false_failures_against_REAL_effect_only':sum(not r['actual_failed']and s['returned_failed']for r,s in zip(first,envelope['plan']['slots'])),
            'actual_control_false_failures':'UNKNOWN_UNTIL_CONTROL_EXECUTED','encoded_chars':len(packed),
            'scope':'Fixed rotation, never selected for favourable score. The signal can remain predictive; dose equality is not independence.'})
    dump(args.out/'RECALCULO_C2C.json',result)
    return result

def analyze(root):
    root=root.resolve(strict=True);manifest=load(root,'MANIFEST.json')
    for entry in manifest['files']:
        b=safe(root,entry['file']).read_bytes();need(len(b)==entry['bytes']and sha(b)==entry['sha256'],'Manifest mismatch '+entry['file'])
    index=load(root,'INDEX.json');p=load(root,'protocol.json');arms={}
    for arm,case in index['arms'].items():
        rows=[];allids=set();last_tick=None;summaries={}
        for name in case['summaries']:
            summary=load(root,name);need(summary['owner_closed']is True,'Open owner is not coherent evidence')
            final=summary['final'];need(final['before_tick']==final['after_tick'],'Final administrative view advanced the world')
            state=final['result']['rows'][0];progress=state['progress']
            need(progress['protocol_sha256']==sha(safe(root,'protocol.json').read_bytes()),'Exported literal protocol differs from Native-bound evaluated protocol')
            need(progress['arm']==arm and not progress.get('pending')and not progress.get('uncertain'),'Final task is not closed/coherent')
            observed_end=summary['start_ordinal']+len(summary['rows'])
            need(summary['completed']==len(summary['rows'])and progress['ordinal']==observed_end,'Final ordinal differs from actually executed opportunities')
            need(observed_end<=summary['stop_exclusive'],'Observed history exceeds requested horizon')
            if observed_end<summary['stop_exclusive']:
                need(summary.get('status')=='STOPPED_FIRST_FAILURE_PRESERVED'and summary.get('stop_reason')is not None,'An unexecuted requested suffix must have its preserved stop reason, not be silently omitted')
            if 'device'in state:
                device=state['device']
                need(device['ordinal']==progress['ordinal']and not device['pending']and not device['feedback_pending']and not device['uncertain'],'External device final state is pending/uncertain')
            for s in summary['rows']:
                need(s['ordinal']not in summaries,'Duplicate summary ordinal');summaries[s['ordinal']]=s
        for k,name in sorted(case['primaries'].items(),key=lambda e:int(e[0])):
            i=int(k);outer_primary=load(root,name);v,r=outer(outer_primary)
            need(r['ordinal']==i and r['arm']==arm and v['before_tick']==r['before_tick']and v['after_tick']==r['after_tick'],'Primary boundary/arm mismatch')
            if last_tick is not None:need(r['before_tick']==last_tick,'History gap: do not merge nonconsecutive material lives')
            last_tick=r['after_tick'];entry=verify_row(r,p['schedule'][i],p['environment']);summary=summaries[i]
            need(summary['operation']==entry['operation']and summary['actual_number']==entry['actual_numeric_result']and summary['useful_product']==entry['useful_product'],'Summary contradicts primary')
            need(not(allids&set(entry['native_ids'])),'Native ID reused across opportunities');allids.update(entry['native_ids'])
            files=case['files'][k];resource=safe(root,files['resource']['member']).read_bytes()
            expected_resource=hashlib.sha256(('PI04.C2.resource.'+str(i)).encode('ascii')).digest()*2
            need(resource==expected_resource and len(resource)==64,'Actual external resource corrupt')
            if entry['useful_product']:
                need(files['product']is not None,'Counter without actual product file')
                product=safe(root,files['product']['member']).read_bytes();recorded=r['actual_effect']['product']
                expected=entry['actual_numeric_result'].to_bytes(2,'little')+resource[2:]
                need(product==expected and len(product)==recorded['bytes']==64 and sha(product)==recorded['sha256'],'Actual product does not contain actual Native integer')
            else:need(files['product']is None and r['actual_effect']['product']is None,'Failure presented as useful product')
            rows.append(entry)
        applied=sum(r['receipt_statuses'].get('applied',0)for r in rows)
        arms[arm]={'life':case['life'],'included':len(rows),'rows':rows,'products':sum(r['useful_product']for r in rows),
            'Native_inputs_unique':len(allids),'applied':applied,'rejected':len(allids)-applied,'pending':0,
            'formed_first':sum(r['first_choice']is not None for r in rows),'NULL_first':sum(r['first_choice']is None for r in rows),
            'arithmetic_correct':sum(r['arithmetic_correct']is True for r in rows),
            'reserve8':{'included':sum(12<=r['ordinal']<20 for r in rows),'products':sum(r['useful_product']for r in rows if 12<=r['ordinal']<20)},
            'crossed22_23':{'included':sum(r['ordinal']in(22,23)for r in rows),'products':sum(r['useful_product']for r in rows if r['ordinal']in(22,23))},
            'analytical_references':references(rows,p['environment'])}
    comparisons={}
    if 'real'in arms:
        real_by={r['ordinal']:r for r in arms['real']['rows']}
        for arm,case in arms.items():
            if arm=='real':continue
            common=[r for r in case['rows']if r['ordinal']in real_by]
            calendars=all(r['calendar']==real_by[r['ordinal']]['calendar']for r in common)
            counts_equal=all(r['unique_inputs']==real_by[r['ordinal']]['unique_inputs']for r in common)
            comparison={'paired_ordinals':[r['ordinal']for r in common],'same_calendars':calendars,'same_native_input_count_each':counts_equal,
                'products_real':sum(real_by[r['ordinal']]['useful_product']for r in common),'products_control':sum(r['useful_product']for r in common),
                'shared_prefix_not_independent_replicates':True}
            if arm=='yoked':
                first=[real_by[i]for i in range(20)];env,packed=fixed_plan(first,{'only_comparison':True})
                need(len(common)==20 and calendars,'Yoked comparison requires all20 fixed calendars')
                need(all(r['returned_failed']==env['plan']['slots'][r['ordinal']]['returned_failed']for r in common),'Not the fixed rotate+1 of real20')
                need(collections.Counter(r['returned_failed']for r in common)==collections.Counter(r['actual_failed']for r in first),'Type dose differs')
                comparison.update({'source_signal_changes':env['plan']['source_signal_changes'],
                    'actual_control_effect_return_mismatches':sum(r['actual_failed']!=r['returned_failed']for r in common),
                    'false_failure_signals':sum(not r['actual_failed']and r['returned_failed']for r in common),
                    'real_failures_without_failure_signal':sum(r['actual_failed']and not r['returned_failed']for r in common)})
            comparisons[arm]=comparison
    return {'schema':VERSION,'mode':'DOCUMENTARY_RECALCULATION_NOT_NATIVE','Native_ticks':0,'source_path_fields_opened':False,
        'manifest_sha256':sha((root/'MANIFEST.json').read_bytes()),'arms':arms,'comparisons':comparisons,
        'limits':['Host initiates and sequences query→FI→MU→device. Native selects operation and route, not the global algorithm or its initiation.',
        'Analytical reference products are counterfactual calculations, not recorded Native executions or participant input.',
        'NULL differs from material zero. Dose/phase comparisons do not establish statistical independence or autonomous anticipation.',
        'A frozen inherited state and matched branches are not independent individuals. Full operative states remain local.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='mode',required=True)
    e=sub.add_parser('export');e.add_argument('--summary',type=Path,action='append',required=True);e.add_argument('--protocol',type=Path,required=True);e.add_argument('--system-root',type=Path,required=True);e.add_argument('--out',type=Path,required=True);e.add_argument('--plan20',action='store_true')
    r=sub.add_parser('recalculate');r.add_argument('--evidence',type=Path,required=True);r.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='export':result=export(args)
    elif args.mode=='recalculate':
        result=analyze(args.evidence);fresh(args.out);dump(args.out/'RECALCULO_C2C.json',result)
    print(json.dumps({'mode':result['mode'],'Native_ticks':0,'arms':{k:{n:v[n]for n in('included','products','Native_inputs_unique','reserve8','crossed22_23')}for k,v in result['arms'].items()},'comparisons':result['comparisons']},ensure_ascii=False))
if __name__=='__main__':main()
