"""Read only the three closed C2B development cuts and their recorded journal.

No DEE imports, Native execution, live VIDA or SQLite access.  The parser is the
previously preserved stdlib DEETSNP1 reader.  This is an autopsy, not a replay.
"""
from pathlib import Path
import collections, datetime, hashlib, json, runpy

P4 = Path(__file__).resolve().parents[1]
S2 = P4 / 'estados/candidato_R02/sistema'
KEY = 'DEE.Cognitive.PI04.C2B.coordination.R01'
PORTS = [(57,53,63), (6,47,12)]
POINTS = {'FI_rejected_122307': PORTS[0], 'FI_rejected_122323': PORTS[1],
          'eligibility_hub': (19,53,3), 'A': (18,53,5), 'B': (20,53,5),
          'Q': (19,54,5), 'eligibility_seed': (19,53,2),
          'postread_guard': (19,57,5)}

def sha(b): return hashlib.sha256(b).hexdigest()
def witness(path):
    b=path.read_bytes()
    return {'path':str(path.resolve()),'bytes':len(b),'sha256':sha(b)}
def read_primary(path):
    d=json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(d.get('result'),str): d=json.loads(d['result'])
    return d
def compact_receipt(request):
    r=request['receipt']
    return {'id':int(r['id']),'status':r['status'],'requested_tick':int(r['requested_tick']),
            'effective_tick':r.get('effective_tick'),'reason':r.get('reason'),
            'channels':r['channels'],'site':request.get('site'),
            'payload':request.get('payload'),'direction':request.get('direction')}

def main():
    out=P4/'control/C2B_DEV_STOP_AUTOPSIA_PASIVA_R01.json'
    if out.exists(): raise FileExistsError('Preserve the first closed autopsy')
    parser_path=P4/'codigo/contrastar_finales_E3_pasivo.py'
    tools=runpy.run_path(str(parser_path),run_name='pure_snapshot_parser')
    journal=S2/'estado/servicios_locales/ECI02_PI03_REPRO_PI04_MAIN_02/PI04_C2B_COORDINACION_R01/eventos.jsonl'
    journal_bytes=journal.read_bytes(); lines=journal_bytes.splitlines(keepends=True)
    events=[json.loads(line) for line in lines]
    assert [x['index']for x in events]==list(range(len(events)))
    chain='00'*32; chain_by_count={0:chain}
    for i,line in enumerate(lines,1):
        chain=sha(bytes.fromhex(chain)+line);chain_by_count[i]=chain
    observations=[]; all_requests={}; total_groups=collections.Counter()
    cuts=[]; views=[]; final_receipts={}
    for ordinal in range(3):
        source=P4/f'ensayos/PI04_C2B_REAL_DEV_R01_OP_{ordinal}.json'
        d=read_primary(source); row=d['result']['rows'][0]; cut=d['committed_snapshot']
        parsed=tools['parse'](S2/cut['snapshot'],cut['snapshot_sha256'])
        public,raw,clocks,channels,pending,receipts,metadata=parsed[:7]
        assert public['physical']=={k:cut['physical'][k] for k in ('N','tick','RAW_sha256','clocks_sha256')}
        m=json.loads(metadata[KEY]); assert m['log_chain_sha256']==chain_by_count[m['log_count']]
        assert m['pending'] is None and m['plan'] is None and m['uncertain'] is False
        assert not pending
        sites={}
        for name,site in POINTS.items():
            index=(site[0]*67+site[1])*67+site[2]
            sites[name]={'site':list(site),'clock':int(clocks[index]),**tools['decode'](raw[index])}
        local=[]
        for x in range(17,22):
            for y in range(51,58):
                for z in range(1,8):
                    index=(x*67+y)*67+z
                    if raw[index]:local.append({'site':[x,y,z],'clock':int(clocks[index]),**tools['decode'](raw[index])})
        arith=row['native_arithmetic']['native_operation']['native_trial']
        second=row['second_native_use']
        groups={'outer_query_context_copy_return':row['requests'], 'FI_arithmetic':arith['requests'],
                'second_MU_actual_result':second['requests']}
        statuses={}; rejected=[]
        for name,requests in groups.items():
            statuses[name]=dict(collections.Counter(x['receipt']['status'] for x in requests))
            total_groups[name]+=len(requests)
            for req in requests:
                item=compact_receipt(req);identifier=item['id']
                if identifier in all_requests and all_requests[identifier]!=item:
                    raise ValueError('Conflicting aliases of one Native receipt')
                all_requests[identifier]=item
                if item['status']!='applied': rejected.append(item)
        op_events=[x for x in events if row['before_tick']<=x['tick']<=row['after_tick']
                   and not(x['kind']=='C2_OPPORTUNITY_INTENT'and x['tick']==row['after_tick'])]
        frames=[x for x in op_events if x['kind']=='C2_CAUSAL_FRAME']
        receipt_index={x['id']:x for x in receipts}
        for reqs in groups.values():
            for req in reqs:
                receipt=receipt_index[req['id']]
                assert receipt['status']==(2 if req['receipt']['status']=='applied' else 5)
                assert receipt['requested_tick']==req['receipt']['requested_tick']
        v={'ordinal':ordinal,'source':witness(source),'cut':public,'state_points':sites,
           'local_nonzero_RAW_ROI':{'bounds_inclusive':[[17,21],[51,57],[1,7]],'sites':local},
           'B_metadata_closure':{k:m[k]for k in ('ready','admitted','pending','plan','uncertain','ordinal','log_count','log_chain_sha256','halted_reason')},
           'journal_prefix_matches_snapshot_metadata':True,'Native_pending_empty':not pending,
           'context':row['spec']['context'],'first_reader_choice':row['first_reader']['choice'],
           'first_reader_not_missing_first_choice_field':True,'first_motor':row['first_motor'],
           'operation':row['selected_operation'],'numeric_result':row['actual_numeric_result'],
           'second_reader_choice':second['reader']['choice'],'second_motor':row['second_motor'],
           'useful_product':row['useful_product'],'actual_failed':row['actual_failed'],
           'returned_failed':row['returned_failed'],'bank_before':row['bank_before'],'bank_after':row['bank_after'],
           'bank_delta_before':row['bank_before'][0]['s_reg']-row['bank_before'][1]['s_reg'],
           'bank_delta_after':row['bank_after'][0]['s_reg']-row['bank_after'][1]['s_reg'],
           'request_group_status_counts':statuses,'rejections':rejected,
           'arithmetic_timing':{k:arith[k] for k in ('input_tick','query_tick','datum_tick','read_tick')},
           'arith_recorded_frames':arith['frames'],'causal_frames':frames,
           'outcome_actual_receipt':row['requests'][-1]['receipt']}
        views.append(v);cuts.append(public)
        final_receipts=receipt_index
        del parsed,raw,clocks,channels,pending,receipts,metadata
    unique_statuses=dict(collections.Counter(x['status']for x in all_requests.values()))
    # Search actual recorded point fields, never interpolate absent port data.
    target_samples=[]
    def visit(value,where):
        if isinstance(value,dict):
            if 'site'in value and isinstance(value['site'],list)and tuple(value['site'])in PORTS and ('raw'in value or 'RAW'in value):
                target_samples.append({'locator':where,'sample':value})
            for k,v in value.items():visit(v,where+'/'+str(k))
        elif isinstance(value,list):
            for i,v in enumerate(value):visit(v,where+'/'+str(i))
    for ordinal in range(3):
        visit(read_primary(P4/f'ensayos/PI04_C2B_REAL_DEV_R01_OP_{ordinal}.json'),f'OP_{ordinal}')
    final=views[-1]
    proof={'schema':'PI04.C2B.closed_development.passive_autopsy.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),
           'mode':'Read exact frozen snapshots and historical records only; no Native, owner, GUI, live SQLite or VIDA',
           'sources':{'parser':witness(parser_path),'journal':witness(journal),
                      'instrument':witness(S2/'capacidades/pi04_coordinacion_simetrica_C2B.py')},
           'journal':{'lines':len(events),'chain_sha256':chain,'metadata_prefix_checks':3},
           'opportunities':views,'deduplicated_Native_requests':{'by_group':dict(total_groups),'unique':len(all_requests),'statuses':unique_statuses,
             'every_ID_terminal_in_final_snapshot':all(final_receipts[k]['status']in(2,5)for k in all_requests),
             'IDs_min':min(all_requests),'IDs_max':max(all_requests)},
           'FI_target_recorded_samples_inside_primaries':target_samples,
           'scientific_conclusions':[
             'The three first sensor outputs are real +1, all three arithmetic outputs are real 25, and all three second outputs are +1. Missing field first_choice is not Native NULL: read first_reader.choice.',
             'FI requests 122307 and122323 are terminal rejected_occupied: at their own admission boundaries the target RAW was not zero. Both target sites are RAW0 at all three closed final cuts. Later emptiness does not invalidate the historical rejection.',
             'No point sample at those two admission boundaries was recorded by these arithmetic frames. These data do not identify the blocker RAW, trajectory or historical parent. Sparse final states cannot by themselves attribute the rejections to the additional symmetric datum.',
             'The op2 return was admitted. Its eligibility hub already contained a moving SEM1 zero-charge +Z record at the pre-event outcome boundary800375; at800376 and800377 the hub is RAW0, while the bank delta remains-5. This is an observed obstruction/changed hub state, not a proved absence of content or learning throughout the organization.',
             'The generic-return contact and arithmetic admission are distinct failed links. Their common cause is unresolved. A q+4 first reader revision alone does not establish repair of FI admission or eligibility routing.',
             'The B closed metadata uncertainty flag reconciles seven outer requests only. It does not include nested FI admission. Thus uncertain=false is compatible with terminal nested rejections; the external development runner correctly stopped rather than opening reserved evaluation.',
             'For safe diagnostic cloning only: finalT800379 has empty Native agenda, all561 included IDs have terminal receipts, coherent34-line B journal and pending/plan null. Terminal rejections are scientific evidence, not unresolved transport. No strict incomplete-operation blocker was found in the inspected closed checkpoint; the complete export still must carry environment, SQLite and other contract resources.'
           ],
           'not_proven':['Native acquisition of a useful C2B operation policy','a causal origin for the pre-existing+Z hub carrier','a causal identity between the FI blockers and that carrier','repair by reading q+4','current MAIN adoption or capability of a different branch'],
           'new_Native_ticks':0,'operational_files_modified':False,'scope':'Three development opportunities, no C2B reserved evaluation; no experimental replication performed.'}
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
                      'requests':proof['deduplicated_Native_requests'],'sample_count':len(target_samples),
                      'final_sites':final['state_points'],'new_Native_ticks':0},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
