"""Portable audit: stdlib only, zero DEE ticks, no engine/environment import.
Recompute from exact RAW, requests and physical observations, not PASS labels.
Usage: python recalcular.py --evidencia <analysis-root>/EVIDENCIA_CAUSAL/PRIMARIOS --salida CALCULOS.json
"""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def input_ledger(path):
    """Recount raw archived transitions, never infer inputs from repeated references."""
    d=json.loads(gzip.decompress(Path(path).read_bytes()));out={}
    assert d['native_ticks']==0 and d['passive_observation_before']==d['passive_observation_after']
    for id,v in d['operations'].items():
        if 'before'not in v:
            out[id]={'new_requests':v['new_requests'],'scope':v['scope']};continue
        start,stop=v['new_id_range_half_open'];assert start==v['before']['next_event_id']and stop==v['after']['next_event_id']
        assert stop-start==v['new_requests']
        transitions=v['transitions'];assert len({q['id']for q in transitions})==len(transitions)
        applied=sum(q['status_name']=='applied'for q in transitions)
        rejected=sum(q['status_name'].startswith('rejected')for q in transitions)
        new=[q for q in transitions if start<=q['id']<stop]
        counts=dict(sorted(Counter(q['status_name']for q in new).items()))
        assert len(new)==v['new_requests']and counts==dict(sorted(v['new_request_status_at_operation_end'].items()))
        assert applied==v['applied_during_operation']and rejected==v['rejected_during_operation']
        out[id]={'new_requests':len(new),'new_request_status_at_close':counts,'applied_in_window_including_prior_queue':applied,
                 'rejected_in_window_including_prior_queue':rejected,'pending_at_close':v['after']['pending_count'],
                 'before_tick':v['before']['tick'],'after_tick':v['after']['tick']}
    return {'operations':out,'unresolved':d['unresolved_operations'],'complete_snapshots_read_by_original_zero_tick_audit':d['unique_complete_snapshots_read'],
            'scope':'Recounts exported receipt transitions and header counters, not a native rerun or an independent reparse of omitted complete original snapshots.'}
def fields(raw):
    n=int(raw)
    def signed(k):v=(n>>k)&15;return v-16 if v&8 else v
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[signed(k)for k in(48,52,56)]}
def walk(x):
    yield x
    if isinstance(x,dict):
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def qsocial(read,bank):
    f=fields(read['raw']);return f['state']==1 and f['semantic']==1 and f['s_reg']>0 and f['direction']==[bank,0,0]
def external(e):
    if not isinstance(e,dict)or'rows'not in e:return None
    rows=[]
    for r in e['rows']:
        if 'social_reads'not in r:continue
        reads=[]
        for z in r['social_reads']:
            f=fields(z['native']['raw']);qual=qsocial(z['native'],z['bank'])
            assert qual==z['qualified'],('social decoding',r['tick'],z)
            reads.append({'bank':z['bank'],'site':z['target'],'fields':f,'qualified':qual})
        rows.append({'index':r['index'],'tick':r['tick'],'native_quantity':fields(r['native']['raw']),
          'social':reads,'qualified_social_count':sum(z['qualified']for z in reads),
          'torque':r['executed_torque'],'environment_response':r['response'],
          'sensor_reader':r['sensor_reader'],'sensor_input_tick':r['sensor_input_tick']})
    return {'steps':len(rows),'rows':rows}
def receipts(payload):
    by={};conflicts=[]
    for v in walk(payload):
        if not isinstance(v,dict)or'status'not in v or'id'not in v:continue
        k=str(v['id']);old=by.get(k)
        if old and old['status']!=v['status']:
            if 'pending'not in(old['status'],v['status']):conflicts.append({'id':k,'statuses':[old['status'],v['status']]})
            if v['status']=='pending':continue
        by[k]=v
    c=Counter(v['status']for v in by.values())
    return {'unique_request_ids':len(by),'statuses':dict(sorted(c.items())),
      'applied':c['applied'],'rejected':sum(n for k,n in c.items()if k.startswith('rejected')),
      'pending':c['pending']+c['scheduled'],'terminal_conflicts':conflicts,
      'scope':'Per-case IDs; shared prefix/fork IDs are never summed as independent material events or independent learners.'}
def gate(v):
    mode=v.get('mode','intact');rows=[]
    for r in v.get('rows',[]):
        if 'force_sensor'not in r:continue
        f=fields(r['native_response']['raw']);valid=f['state']==1 and f['semantic']==1 and f['s_reg']==7 and f['direction']in([1,0,0],[-1,0,0])
        native=-f['direction'][0]if valid else 0;action=0 if mode=='null_action'else native
        q=r['force_sensor'];env=r['environment'];before=env['resistance_before'];after=before+(r['wear_available']if action==1 else 0)
        opened=action==1 and q>before;jam=action==1 and not opened;useful=opened or(action==-1 and q<=before)
        assert native==r['native_action'] and action==r['executed_action']
        assert after==env['resistance_after']and opened==env['opened']and jam==env['jam']
        assert valid==r['valid']and bool(useful)==r['useful_auditor_only']
        native_useful=(native==1 and q>before)or(native==-1 and q<=before)
        rows.append({'index':r['index'],'tick':r['tick'],'force':q,'wear_available':r['wear_available'],'resistance_before':before,'resistance_after':after,
          'reference_load':fields(r['native_pre']['reference']['raw'])['s_reg'],
          'native_raw':str(r['native_response']['raw']),'native_clock':str(r['native_response']['clock']),
          'native_fields':f,'valid':valid,'native_action':native,'executed_action':action,'native_choice_useful':bool(native_useful),
          'outside_actuator_codec_material':not valid and f['state']!=0,'abstention_empty':not valid and int(r['native_response']['raw'])==0,
          'opened':opened,'jam':jam,'useful':bool(useful),'utility':int(opened)-int(jam)})
    return {'mode':mode,'opportunities':len(rows),'valid':sum(r['valid']for r in rows),'native_choice_useful':sum(r['native_choice_useful']for r in rows),'useful':sum(r['useful']for r in rows),'utility':sum(r['utility']for r in rows),'rows':rows}
def calculate(folder):
    data={};observations=0
    for p in sorted(Path(folder).glob('*.json.gz')):
        d=json.loads(gzip.decompress(p.read_bytes()));v=d['payload'];data[d['id']]=d
        for a in walk(v):
            if isinstance(a,dict)and'raw'in a and all(k in a for k in('state','s_reg','semantic','direction')):
                f=fields(a['raw'])
                assert all(a[k]==f[k]for k in f),('RAW mismatch',d['id'],a)
                assert 0<=int(a['raw'])<2**64
                if 'clock'in a:assert 0<=int(a['clock'])<2**64
                observations+=1
    cases={};gates={};externals={};social={};recovery={};selectors={};panels={};detours={};laterals={};separations={};diagnostics={}
    for id,d in data.items():
        v=d['payload'];r=receipts(v);g=gate(v)
        if g['opportunities']:gates[id]=g
        if isinstance(v,dict)and'gate'in v:
            gg=gate(v['gate'])
            if gg['opportunities']:gates[id]=gg
        ex=external(v)
        if ex and ex['steps']:externals[id]=ex
        if isinstance(v,dict)and'external'in v:
            ex=external(v['external'])
            if ex and ex['steps']:
                externals[id]=ex
                positive=sum(any(z['qualified']and z['bank']==1 for z in row['social'])for row in ex['rows'])
                negative=sum(any(z['qualified']and z['bank']==-1 for z in row['social'])for row in ex['rows'])
                recovery[id]={'uses':ex['steps'],'positive_usable':positive,'negative_usable':negative,'rows':ex['rows']}
        if isinstance(v,dict)and'private_value'in v:
            frames=[]
            for f in v.get('frames',[]):
                if'ports'not in f:continue
                codes=[z['sign']for z in f['ports']if qsocial(z['read'],z['sign'])]
                frames.append({'tick':f['tick'],'codes':codes,'raw_ports':f['ports']})
            expected=None if v.get('mode')=='no_partner'or type(v['private_value'])is not int else(1 if v['private_value']+5<36 else-1)
            functional=[f for f in frames if f['tick']%67==3]
            social[id]={'private_object':v['private_value'],'B_expected_auditor_only':expected,
                        'frames':frames,'record_requests':receipts(v.get('legacy_record_requests',v.get('record_requests',[]))),
                        'correct_phase_samples':len(functional),'correct_phase_native_valid':sum(len(f['codes'])==1 for f in functional),
                        'correct_phase_matches_private':sum(f['codes']==[expected]for f in functional)if expected is not None else None,
                        'cuts':v.get('cuts',[]),'occupation':v.get('samples',[f.get('global')for f in v.get('frames',[])if f.get('global')])}
        if isinstance(v,dict)and id.startswith('C02_REUSO_'):
            rows=[]
            for row in v['rows']:
                end=row['frames'][-1];codes=[z['sign']for z in end['received']if qsocial(z['read'],z['sign'])]
                expected=1 if row['private_object']+5<36 else-1
                assert codes==row['received_codes']
                rows.append({'index':row['index'],'private_object':row['private_object'],'tick':end['tick'],'codes':codes,'valid':len(codes)==1,'correct':codes==[expected],
                             'record_requests':receipts(row['record_requests']),'protection_requests':receipts(row['protection_requests']),
                             'after':row['after'],'contributions':end.get('record_contributions',[])})
            social[id]={'episodes':len(rows),'correct':sum(x['correct']for x in rows),'valid':sum(x['valid']for x in rows),'rows':rows,'terminal_variant':v['termination_variant']}
        if isinstance(v,dict)and id.startswith(('C02_ACT_','C02_SELECTOR_154')):
            rows=[]
            for row in v.get('rows',v.get('native_frames',[])):
                if'action'in row:
                    f=fields(row['action']['raw']);valid=f['state']==1 and f['semantic']==1 and f['s_reg']>0 and f['direction'][0]==1 and abs(f['direction'][1])==1 and f['direction'][2]==0
                    rows.append({'index':row['index'],'tick':row['query_tick'],'fields':f,'availability':row['availability'],'valid':valid,'useful':valid and f['direction'][1]==row['availability']})
            if rows:selectors[id]={'opportunities':len(rows),'valid':sum(z['valid']for z in rows),'useful':sum(z['useful']for z in rows),'rows':rows}
        if isinstance(v,dict)and'frames'in v and any(isinstance(f,dict)and f.get('kind')in('quantity','two_memory')for f in v['frames']):
            panels[id]=[{'kind':f['kind'],'tick':f['tick'],'fields':fields(f['read']['raw'])}for f in v['frames']if f.get('kind')in('quantity','two_memory')and'read'in f]
        if isinstance(v,dict)and id.startswith('C02_DETOUR_'):
            episodes=[]
            if 'episodes'in v:
                uses=[(z['private_object'],z['use'])for z in v['episodes']]
            else:uses=[(v['first_plan']['value_private_B'],v['uses'][0]),(v['second_plan']['value_private_B'],v['uses'][1])]
            for value,use in uses:
                ex=external(use)
                for row in ex['rows']:
                    old=any(z['qualified']and z['bank']==1 and z['site'][2]==23 and z['fields']['s_reg']==7 for z in row['social'])
                    expected=1 if value+5<36 else-1
                    new=any(z['qualified']and z['bank']==expected and z['site'][2]==29 for z in row['social'])
                    episodes.append({'private_object':value,'tick':row['tick'],'old_positive_fixed_port':old,'new_private_sign_fixed_port':new,
                                     'both':old and new,'social':row['social'],'torque':row['torque']})
            last=external(v['final_use']if'final_use'in v else v['uses'][-1])
            detours[id]={'episodes':episodes,'both_count':sum(z['both']for z in episodes),'opportunities':len(episodes),'final_use':last,
                          'scope':'Fixed-port content and actual motor contributions. Saturated/cancelled torque is not a separate proof of the utility of each contribution.'}
        if isinstance(v,dict)and id.startswith('C02_LATERAL_')and'episodes'in v:
            ee=[]
            for e in v['episodes']:
                use=external(e['use']);expected=1 if e['private_object']+5<36 else-1
                for row in use['rows']:
                    old=any(z['qualified']and z['bank']==1 and z['site']==[11,59,23]for z in row['social'])
                    new=any(z['qualified']and z['bank']==expected and z['site'][1:]==[48,29]for z in row['social'])
                    original=any(z['qualified']and z['bank']==expected and z['site'][1:]==[59,29]for z in row['social'])
                    ee.append({'index':e['index'],'tick':row['tick'],'private_object':e['private_object'],'old_positive_available':old,
                      'new_lateral_available':new,'original_channel_available':original,'both':old and new,'social':row['social'],'torque':row['torque'],'occupied':e['after']['occupied']})
            laterals[id]={'episodes':ee,'completed':len(ee),'new_lateral':sum(e['new_lateral_available']for e in ee),
              'old_positive':sum(e['old_positive_available']for e in ee),'both':sum(e['both']for e in ee),
              'final_occupation':v['final']['occupied'],'mode':v.get('mode','full'),'sham':v['sham'],
              'scope':'No-B/cut controls do not have an expected newly taught lateral message; their absence is not a mistaken classification. Original/lateral/old roles are separated by the frozen physical interfaces.'}
        if isinstance(v,dict)and id.startswith('C02_SEPARA_')and'first_uses'in v:
            stages=[]
            for label,raw in(('first',v['first_uses']),('new_private',v['new_use']),('after_scalar',v['last_use'])):
                for row in external(raw)['rows']:
                    roles={label2:any(z['qualified']and z['bank']==bank and z['site']==site for z in row['social'])
                      for label2,bank,site in(('old_positive',1,[11,59,23]),('prior_negative',-1,[31,59,26]),('initial_lateral',1,[11,48,29]),('new_private',-1,[31,48,29]))}
                    stages.append({'stage':label,'tick':row['tick'],'roles':roles,'social':row['social'],'torque':row['torque']})
            separations[id]={'mode':v['mode'],'stages':stages,'requests':receipts(v['requests']),
                'three_codes_first_uses':sum(r['stage']=='first'and all(r['roles'][x]for x in('old_positive','prior_negative','initial_lateral'))for r in stages),
                'scope':'Restores use of a transformed prior negative contribution and retains old+before their directional coalescence; not reconstruction after whole-state information erasure. New private52 is scored only at its lateral interface, never inferred from the old negative port.'}
        if isinstance(v,dict)and'first_departure'in v:
            f=v['first_departure'];diagnostics[id]={'mode':v.get('mode'),'first_departure':f,
                'new_inputs':v.get('new_inputs'),'scope':v.get('scope',v.get('attribution'))}
        init=v.get('initial',v.get('initial_native',{}))if isinstance(v,dict)else{}
        final=v.get('final',v.get('final_native',{}))if isinstance(v,dict)else{}
        if not init:init=d.get('initial_life',{}).get('physical',{})
        if not final:final=d.get('final_life',{}).get('physical',d.get('instrument_context',{}))
        cases[id]={'life':d.get('life'),'requested_receipts':r,'initial_tick':init.get('tick'),'final_tick':final.get('tick'),
          'initial_occupied':init.get('occupied'),'final_occupied':final.get('occupied'),'returncode':d.get('returncode'),
          'original':d['original'],'error':d.get('error')}
    names=['C02_MAIN_061_PUERTA','C02_MAIN_106_RESERVA','C02_MAIN_108_RETENCION','C02_MAIN_125_PUERTA','C02_MAIN_174_PUERTA']
    # Discover names by exact life identity when a command ID uses another
    # descriptive suffix; each stored index occurs only once in MAIN.
    main=[]
    for id,g in gates.items():
        if id.startswith('C02_MAIN_')and any(x in id for x in('_061','_106','_108','_125','_174')):
            main.extend({'experiment':id,**r}for r in g['rows'])
    main.sort(key=lambda x:x['index'])
    if main:
        assert [r['index']for r in main]==list(range(len(main)))
        for a,b in zip(main,main[1:]):assert a['resistance_after']==b['resistance_before']
    return {'schema':'DCS.C02.recalculated.v1','method':'RAW decoding + declared fixed transduction + actual action/environment/wear. No automatic verdict accepted as primary truth.',
      'native_ticks':0,'exported_primaries':len(data),'exact_raw_observations_verified':observations,
      'gate_cases':gates,'main_gate':{'opportunities':len(main),'valid':sum(z['valid']for z in main),'useful':sum(z['useful']for z in main),'utility':sum(z['utility']for z in main),'rows':main},
      'social_cases':social,'recovery_cases':recovery,'selector_cases':selectors,'old_panels':panels,'detour_cases':detours,
      'lateral_cases':laterals,'separation_cases':separations,'diagnostic_cases':diagnostics,'external_cases':externals,'case_inventory':cases,
      'inference_limits':['Deterministic forks share past and are not independent learners.','Prepared comparison/actuator law is not learned policy-law discovery.','P0/P1 access and operator query initiative do not establish P2/R2.','Missing fixed-port access does not by itself prove whole-state erasure.','No competence claim for Pendulum from emitting torque.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--recibos',type=Path);a=p.parse_args()
    result=calculate(a.evidencia)
    if a.recibos:result['exact_input_ledger']=input_ledger(a.recibos)
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_bytes(canon(result))
    print(json.dumps({'primaries':result['exported_primaries'],'raw_checked':result['exact_raw_observations_verified'],'main_gate':{k:v for k,v in result['main_gate'].items()if k!='rows'},
      'social_reuse':{k:{z:v[z]for z in('episodes','correct','valid')if z in v}for k,v in result['social_cases'].items()if k.startswith('C02_REUSO')},
      'recovery':{k:{z:v[z]for z in('uses','positive_usable','negative_usable')}for k,v in result['recovery_cases'].items()if k.startswith(('C02_REPET','C02_LATE','C02_PRE'))}},ensure_ascii=False))
