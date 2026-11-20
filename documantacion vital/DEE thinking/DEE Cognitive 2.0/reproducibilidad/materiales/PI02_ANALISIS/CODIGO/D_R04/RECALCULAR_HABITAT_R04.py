"""Passive R04 journal/RAW/actuator/resource verifier; no DEE imports or ticks.

--journal may contain a longer continuation: the exact historical prefix is
selected by the summary's committed log_count, never by favorable outcomes.
--bank optionally verifies the actual64-byte collected/spent artifacts.
"""
from pathlib import Path
import argparse,collections,datetime,gzip,hashlib,json,sys
N=67
def sha(b):return hashlib.sha256(b).hexdigest()
def load(path):
    b=Path(path).read_bytes();return gzip.decompress(b)if Path(path).suffix=='.gz'else b
def raw(o):
    if isinstance(o['raw'],(float,bool)):raise ValueError('Inexact RAW')
    v=int(o['raw'])
    if not 0<=v<2**64:raise ValueError('RAW outsideuint64')
    def d(k):
        x=(v>>k)&15;return x-16 if x&8 else x
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':[d(48),d(52),d(56)]}
def route(o):
    x=raw(o)
    if x['state']>0 and x['semantic']==1:
        if x['direction']==[1,0,0]:return 0
        if x['direction']==[0,1,0]:return 1
    return None
def close(o):
    x=raw(o);return x['state']>0 and x['semantic']==1 and x['direction']==[-1,1,0]
def fi(o):
    x=raw(o);dx,dy,dz=x['direction']
    return dx if x['state']>0 and x['semantic']==1 and dx in(-1,0,1)and dy==1 and dz in(0,-1)else None
def run(journal,summary,bank=None):
    summary_bytes=load(summary);s=json.loads(summary_bytes.decode('utf-8-sig'));errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    final_view=s['requests'][-1]['result']['result']['rows'][0]['habitat']
    expected_count=int(final_view['log_count']);available=load(journal);lines=available.splitlines(keepends=True)
    check(len(lines)>=expected_count,'Journal shorter than its committed log_count')
    selected=b''.join(lines[:expected_count]);events=[json.loads(x.decode('utf-8'))for x in lines[:expected_count]]
    check(sha(selected)==s['journal_sha256'],'Exact historical journal prefix SHA')
    chain=bytes(32)
    for index,(line,event)in enumerate(zip(lines,events)):
        check(line.endswith(b'\n'),'Partial journal line')
        check(event['index']==index,'Journal event index')
        chain=hashlib.sha256(chain+line).digest()
    check(chain.hex()==final_view['log_chain_sha256'],'Journal chained SHA')
    check([x['tick']for x in events]==sorted(x['tick']for x in events),'Nonmonotonic journal ticks')
    bykind=collections.defaultdict(list)
    for x in events:bykind[x['kind']].append(x)
    native_receipts={};receipt_aliases=0;obs_count=0
    def walk(x,label):
        nonlocal receipt_aliases,obs_count
        if isinstance(x,dict):
            if {'raw','clock','site','state','s_reg','semantic','direction'}<=set(x):
                decoded=raw(x)
                for k,v in decoded.items():check(x[k]==v,label+': inconsistent RAW/'+k)
                check(not isinstance(x['clock'],(float,bool))and int(x['clock'])>=0,label+': exact clock')
                obs_count+=1
            if {'id','channels','status'}<=set(x):
                i=int(x['id']);status=str(x['status']).lower()
                if i in native_receipts:
                    receipt_aliases+=1;check(native_receipts[i]==x,label+': inconsistent aliases of one Native receipt')
                else:native_receipts[i]=x
            for k,v in x.items():walk(v,label+'/'+str(k))
        elif isinstance(x,list):
            for i,v in enumerate(x):walk(v,label+'/'+str(i))
    for x in events:walk(x,str(x['index']))
    admitted=bykind['NATIVE_RETURN_ADMITTED'];done=bykind['OPPORTUNITY_COMPLETED']
    check([x['episode']for x in admitted]==list(range(len(admitted))),'Admitted episode sequence')
    check([x['episode']for x in done]==list(range(len(done))),'Completed episode sequence')
    counters={'returns':0,'busy_returns':0,'exhausted_returns':0,'close_signatures':0,'false_close_signatures':0}
    previous_tick=None;previous_o=False;previous_h=False;active=None;next_episode=0
    fixture_count=6 if s['series']=='development' else 12
    for x in events:
        if x['kind']=='NATIVE_RETURN_ADMITTED':active=x['episode']
        elif x['kind']=='OPPORTUNITY_COMPLETED':active=None;next_episode=x['episode']+1
        elif x['kind']=='FIXED_PORT_OBSERVATIONS':
            tick=x['tick'];r=route(x['O']);oc=r is not None;hc=close(x['H'])
            contiguous=previous_tick is not None and tick==previous_tick+1
            if oc and not(previous_o and contiguous):
                counters['returns']+=1
                if active is not None:counters['busy_returns']+=1
                elif next_episode>=fixture_count:counters['exhausted_returns']+=1
            if hc and not(previous_h and contiguous):counters['close_signatures']+=1
            previous_tick=tick;previous_o=oc;previous_h=hc
    # The observation precedes its NATIVE_RETURN_ADMITTED in the same tick.
    # Six/twelve free returns are therefore neither busy nor exhausted.
    check(counters['returns']==final_view['returns'],'Native return count')
    check(counters['close_signatures']==final_view['close_signatures'],'CLOSE rising-edge count')
    # Per-return transaction capacity is also witnessed directly by committed totals.
    observed_busy=counters['returns']-len(admitted)-final_view['exhausted_returns']
    check(observed_busy==final_view['busy_returns'],'Busy/capacity return reconciliation')
    check(counters['busy_returns']==final_view['busy_returns'],'Busy count from event timeline')
    check(counters['exhausted_returns']==final_view['exhausted_returns'],'Exhausted count from event timeline')
    check(len(bykind['LEARNED_WARNING_SIGNATURE'])==counters['close_signatures'],'Recorded CLOSE/event detector disagreement')
    false_close=sum(x['active_episode']is None or not next(y for y in admitted if y['episode']==x['active_episode'])['fixture_environment_only']['peripheral_active']for x in bykind['LEARNED_WARNING_SIGNATURE'])
    check(false_close==final_view['false_close_signatures'],'False CLOSE condition counter')
    check(len(done)==final_view['episode'],'Completed opportunity total')
    device=bykind['DEVICE_COMMAND'];spent=[x for x in device if x['applied']]
    check(len({x['actual_control_packet']['index']for x in spent})==len(spent),'Duplicated device packet')
    resource_count=0;op_rows=[];artifacts=[]
    for op in done:
        start=next(x for x in admitted if x['episode']==op['episode']);r=route(start['origin_observation'])
        check(r==op['route']==start['route'],'Route not derived from origin RAW')
        check(start['origin_observation']['tick']==start['q'],'Origin reader time')
        check(op['tick']==start['busy_until']==start['q']+10*N+40,'Frozen completion/backpressure')
        effect=op['effect'];warnings=op['warning_receipts'];work=None
        if r==0:
            emission=next(x for x in bykind['FI_EMISSION_AND_EFFECT']if x['episode']==op['episode'])
            frame=next(x for x in bykind['FI_FRAME_FINISHED']if x['episode']==op['episode'])
            e=emission['emission'];choice=fi(e['observation'])
            check(choice==e['physical_choice']==effect['physical_choice'],'Work command not derived from FI RAW')
            check(e['tick']==e['query_tick']+4==e['observation']['tick'],'Fixed FIq+4 reader')
            check(frame['trial']['early_observation']['raw']==e['observation']['raw'],'FI event/frame observation disagreement')
            command=choice if s['arm']!='actuator_null'else None
            l,rr=effect['loads_before'];nl,nr=l,rr;blocked=False
            if command==1:
                if l>0 and rr<32:nl-=1;nr+=1
                else:blocked=True
            elif command==-1:
                if rr>0 and l<32:nr-=1;nl+=1
                else:blocked=True
            useful=command is not None and not blocked and(abs(nl-nr)<abs(l-rr)or(l==rr and command==0))
            check(effect['applied_command']==command and effect['loads_after']==[nl,nr]and effect['useful']==useful,'External work consequence mismatch')
            if useful:
                resource_count+=1;item=effect['resource'];check(item is not None and item['bytes']==64,'Missing actual resource record');artifacts.append(('collected',item))
            else:check(effect['resource']is None,'Unhelpful work released a resource')
            work={'physical_choice':choice,'applied_command':command,'useful':useful,'loads_before':[l,rr],'loads_after':[nl,nr],
                  'input_gate':frame['gate'],'raw0_status':frame['trial']['requests'][0]['receipt']['status'],
                  'FI_requests':len(frame['trial']['requests']),'FI_statuses':dict(collections.Counter(x['receipt']['status']for x in frame['trial']['requests'])),
                  'noise_receipt':frame['noise_receipt'],'early_observation':e['observation']}
        else:check(effect['kind']=='DEVICE_COST_OPPORTUNITY'and effect['useful']is False,'Device opportunity was scored as work')
        check(op['resources_total']==resource_count,'Cumulative resource count')
        op_rows.append({'episode':op['episode'],'q':op['q'],'completed_tick':op['tick'],'route':r,'configured_warning_offered':start['fixture_environment_only']['warning_offered'],
                        'actual_W_requested':sum(x['channel']=='PI02.R03.warning'for x in warnings),
                        'actual_W_applied':sum(x['channel']=='PI02.R03.warning'and x['receipt']['status']=='applied'for x in warnings),
                        'is_training':start['is_training'],'warning_receipts':warnings,'work':work,'device':effect.get('device'),'feedback':op['feedback'],'resources_total':resource_count})
    check(resource_count==final_view['resources'],'Final resource total')
    for x in spent:artifacts.append(('control_spent',x['actual_control_packet']))
    artifact_checks=[]
    for folder,item in artifacts:
        entry={'folder':folder,**item,'bytes_checked':False}
        if bank is not None:
            name=item['file']
            if '/'in name or'\\'in name or':'in name or'..'in name:raise ValueError('Unsafe artifact filename')
            p=Path(bank)/folder/name;b=p.read_bytes();check(len(b)==item['bytes']and sha(b)==item['sha256'],'Actual artifact bytes/hash:'+str(p));entry['bytes_checked']=True
        artifact_checks.append(entry)
    check(s['opportunities']==done,'Summary opportunity projection differs from journal')
    check(s['device_commands']==device,'Summary device projection differs from journal')
    check(s['warning_signatures']==bykind['LEARNED_WARNING_SIGNATURE'],'Summary warning projection differs from journal')
    positive_H=[x for x in bykind['FIXED_PORT_OBSERVATIONS']if x['H']['state']>0]
    native_status=collections.Counter(x['status']for x in native_receipts.values())
    return {'schema':'PI02.R04.passive_journal_recalculation.v1','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life':s['life'],'series':s['series'],'history':s['history'],'arm':s['arm'],'new_ticks':0,'DEE_imports':0,
            'source_summary':{'file':Path(summary).name,'bytes':len(summary_bytes),'sha256':sha(summary_bytes)},
            'source_journal':{'file':Path(journal).name,'available_decoded_bytes':len(available),'used_prefix_bytes':len(selected),'used_events':len(events),'sha256':sha(selected),'chained_sha256':chain.hex(),'trailing_events_outside_this_historical_cut':len(lines)-len(events)},
            'reported_native_interval':s['ticks'],'before_tick':s['requests'][1]['result']['before_tick'],'after_tick':s['requests'][1]['result']['after_tick'],
            'global_before_after_reported':{'before':s['requests'][0]['result']['committed_snapshot']['physical'],'after':s['requests'][-1]['result']['committed_snapshot']['physical']},
            'event_kinds':{k:len(v)for k,v in bykind.items()},'Native_receipts_unique':len(native_receipts),'receipt_aliases_not_recounted':receipt_aliases,'Native_receipt_statuses':dict(native_status),'observation_serializations_RAW_checked_not_independent_events':obs_count,
            'returns':counters['returns'],'busy_returns_reconciled':observed_busy,'busy_returns_from_event_timeline':counters['busy_returns'],'exhausted_returns_reported':final_view['exhausted_returns'],'exhausted_returns_from_event_timeline':counters['exhausted_returns'],'false_CLOSE_conditions_from_events':false_close,'completed_opportunities':len(done),'actual_work_frames':len(bykind['FI_FRAME_FINISHED']),'actual_resources':resource_count,
            'actual_device_commands':len(device),'actual_applied_device_commands':len(spent),'device_cost_bytes':sum(x['resource_cost_bytes']for x in spent),'CLOSE_signatures':counters['close_signatures'],
            'training_report_events':bykind['ACTUAL_INPUT_FAILURE_SENSOR'],'first_recorded_positive_H':positive_H[:1],
            'opportunities':op_rows,'device_commands':device,'warning_signatures':bykind['LEARNED_WARNING_SIGNATURE'],'artifacts':artifact_checks,
            'inconsistencies':errors,'limits':['Recalculation of stored evidence, not Native reproduction or a full backup','Configured warning slots and actual W inputs are different denominators; routeB can leave the configured warning unpresented','A raw0 rejection can coexist with a useful FI action; do not make it a universal failure definition','A prepared recurring return and fixed transducer do not prove learned timing or unrestricted autonomy','Useful regulation or anticipation requires paired controls and actual effects, not the CLOSE label alone']}
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--journal',type=Path,required=True);a.add_argument('--summary',type=Path,required=True);a.add_argument('--bank',type=Path);a.add_argument('--output',type=Path,required=True);a.add_argument('--strict',action='store_true');args=a.parse_args();r=run(args.journal,args.summary,args.bank);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k]for k in('life','completed_opportunities','actual_work_frames','actual_resources','actual_applied_device_commands','device_cost_bytes','CLOSE_signatures','Native_receipts_unique','Native_receipt_statuses','returns','busy_returns_reconciled','inconsistencies')},ensure_ascii=False,indent=2));return 2 if args.strict and r['inconsistencies']else 0
if __name__=='__main__':sys.exit(main())
