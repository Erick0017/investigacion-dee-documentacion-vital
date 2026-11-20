"""Stdlib-only recomputation of the eight EO01 social auxiliary trials.

No engine, Runtime, external targets or native ticks. Verifies raw decoding,
receipts, frozen two-sample reader and the limited causal recipient effect.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, json


def decoded(q):
    v = int(q['raw'])
    def signed(shift):
        x = (v >> shift) & 15
        return x - 16 if x & 8 else x
    fields = {'state':v & 0xffffffff, 's_reg':(v >> 32) & 65535,
              'semantic':(v >> 60) & 15, 'direction':[signed(k) for k in (48,52,56)]}
    for key, value in fields.items():
        if q[key] != value:
            raise AssertionError(('RAW field mismatch',key,q))
    if str(int(q['clock'])) != q['clock']:
        raise AssertionError('Clock not an exact integer string')
    return fields


def walk(v):
    if isinstance(v, dict):
        if all(k in v for k in ('raw','clock','state','s_reg','semantic','direction')):
            yield v
        for x in v.values():
            yield from walk(x)
    elif isinstance(v, list):
        for x in v:
            yield from walk(x)


def reader(action):
    critical = action['row']['critical_tick']
    samples = []
    for tick in (critical-16, critical-15):
        frame = next(f for f in action['frames'] if f['tick'] == tick)
        roles = []
        for r in (-1,0,1):
            q = decoded(frame['contacts'][str(r)])
            if q['state'] > 0 and q['semantic'] == 1 and q['direction'] in ([r,-1,-1],[r,-1,0]):
                roles.append(r)
        samples.append({'tick':tick,'material_roles':roles,
                        'command':(1 if roles[0]>=0 else -1)if len(roles)==1 else None,
                        'simultaneous_conflict':len(roles)>1})
    if samples[-1]['simultaneous_conflict']:
        command, source = None, None
    else:
        chosen = next((s for s in reversed(samples)if s['command']is not None),None)
        command, source = (None,None)if chosen is None else(chosen['command'],chosen['tick'])
    return {'samples':samples,'command':command,'source_tick':source}


def changes(frames, key):
    out = []
    previous = None
    for frame in frames:
        values = frame[key] if isinstance(frame[key],list) else [frame[key]]
        signature = [q['raw'] for q in values]
        if signature != previous:
            out.append({'tick':frame['tick'],'values':[{k:q[k]for k in ('site','raw','clock','state','s_reg','semantic','direction')}for q in values]})
        previous = signature
    return out


def analyze(path):
    data = json.loads(gzip.decompress(path.read_bytes()))
    observations = sum(1 for q in walk(data) if decoded(q) is not None)
    blocks = []
    receipts = []
    all_receipts = []
    for b in data['blocks']:
        native = b.get('private_input',b.get('native_query_calibration'))
        requests = b.get('private_requests',native.get('requests',[]))
        receipts.extend(requests)
        all_requests = {q['id']:q for q in native.get('requests',[])}
        all_requests.update({q['id']:q for q in b.get('private_requests',[])})
        all_requests.update({q['id']:q for q in b.get('common_action',{}).get('requests',[])})
        all_receipts.extend(all_requests.values())
        fs = native['frames']
        row = {'index':b['index'],'start_tick':native.get('before',{})['tick'],
               'end_tick':native['after']['tick'],
               'B_RAW_changes':changes(fs,'B'),
               'context_RAW_changes':changes(fs,'context_A'),
               'context_before':[q['s_reg']for q in native['before']['context_A']],
               'context_after':[q['s_reg']for q in native['after']['context_A']],
               'own_before':[q['s_reg']for q in native['before']['own']],
               'own_after':[q['s_reg']for q in native['after']['own']],
               'private_B_before':[q['s_reg']for q in native['before']['private_B']],
               'private_B_after':[q['s_reg']for q in native['after']['private_B']],
               'B_qualified_output_ticks':[{'tick':f['tick'],'direction':f['B']['direction']}for f in fs if decoded(f['B'])['state']>0 and f['B']['semantic']==1 and f['B']['direction']in([-1,-1,-1],[1,-1,-1])],
               'requests':requests}
        row['all_requests'] = list(all_requests.values())
        if 'common_action' in b:
            r = reader(b['common_action'])
            if r['command'] != b['fixed_reader']['command'] or r['source_tick'] != b['fixed_reader']['source_tick']:
                raise AssertionError('Fixed reader differs from primary')
            row['common_action'] = {'public':b['common_action']['row']['public_raw'],
                                    'critical':b['common_action']['row']['critical_tick'],
                                    'own_after':[q['s_reg']for q in b['common_action']['after']['own']],**r}
        blocks.append(row)
    return {'case':data['case'],'source_file':path.name,
            'source_bytes':path.stat().st_size,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'fork':data['fork_record']['parent'],'final_life':data['final_record']['life_id'],
            'final_tick':data['final_record']['physical']['tick'],
            'snapshot':data['final_record']['snapshot'],'snapshot_sha256':data['final_record']['snapshot_sha256'],
            'observations_RAW_checked':observations,'source_unchanged_during_run':data['source_unchanged'],
            'tracked_input_receipts_by_status':dict(collections.Counter(q['receipt']['status']for q in receipts)),
            'all_episode_receipts_by_status':dict(collections.Counter(q['receipt']['status']for q in all_receipts)),
            'all_episode_requested':len(all_receipts),
            'blocks':blocks}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('evidence_directory',type=Path)
    p.add_argument('--output',type=Path)
    args = p.parse_args()
    paths = sorted(args.evidence_directory.glob('EO01_SOC_AUX_*.json.gz'))
    rows = [analyze(q)for q in paths]
    if len(rows) != 8:
        raise AssertionError(('Expected bounded eight auxiliary trials',len(rows)))
    by = {q['case']:q for q in rows}
    # First same-prefix negative message: exact localized direction-only effect.
    target_tick = 68462
    contexts = {}
    for arm in ('INTACT','CUT','SHAM'):
        d = json.loads(gzip.decompress((args.evidence_directory/('EO01_SOC_AUX_'+arm+'.json.gz')).read_bytes()))
        frame = next(f for f in d['blocks'][0]['private_input']['frames']if f['tick']==target_tick)
        contexts[arm] = {'context_A':frame['context_A'],'A':frame['A']}
    assert contexts['INTACT']['context_A'][0]['raw'] == contexts['SHAM']['context_A'][0]['raw']
    assert contexts['INTACT']['context_A'][0]['raw'] != contexts['CUT']['context_A'][0]['raw']
    assert contexts['INTACT']['A']['raw'] == contexts['CUT']['A']['raw'] == contexts['SHAM']['A']['raw']
    assert all([q['s_reg']for q in value['context_A']]==[7,5]for value in contexts.values())
    repeated = json.loads(gzip.decompress((args.evidence_directory/'EO01_SOC_AUX_REPEAT.json.gz').read_bytes()))
    transport = []
    for i,b in enumerate(repeated['blocks']):
        critical = b['private_input']['row']['critical_tick']
        sign = 'minus' if i == 0 else 'plus'
        frames = {f['tick']:f for f in b['private_input']['frames']}
        points = {f['tick']:f['message_waypoints']for f in b['passive_waypoints']}
        route = [{'relative_tick':15,'kind':'B_output','observation':frames[critical+15]['B']}]
        for offset,index in ((16,0),(17,1),(18,2),(30,6),(33,7),(34,8),(35,9),(36,10)):
            route.append({'relative_tick':offset,'kind':sign+'_waypoint_'+str(index),
                          'observation':points[critical+offset][sign][index]})
        transport.append({'block':i,'critical':critical,'private_value':b['private_requests'][0]['payload'],
                          'route_witnesses_not_unique_lineage':route,
                          'recipient_and_A_window':[{'tick':t,'A':frames[t]['A'],'context_A':frames[t]['context_A']}for t in range(critical+35,critical+43)],
                          'A_RAW_constant_in_window':len({frames[t]['A']['raw']for t in range(critical+35,critical+43)})==1})
    result = {'schema':'EO01.social.recalculation.v1','no_native_ticks':True,
              'auxiliary_trials':len(rows),'not_independent_lives':'Exact shared historical prefix; not eight independent acquisitions',
              'cases':rows,'postformed_cut_local_effect':{'tick':target_tick,'arms':contexts,
                  'demonstrates':'New formed material transmission has a one-tick recipient-direction effect, selectively blocked by the minus-bus intervention and preserved by opposite-bus sham.',
                  'does_not_demonstrate':'New persistent context content, improved later action, learned autonomous consultation or new B reference.'},
              'repeated_transport_exact':transport,
              'total_observations_RAW_checked':sum(q['observations_RAW_checked']for q in rows)}
    text = json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
    if args.output:
        args.output.write_text(text,encoding='utf8')
    print(json.dumps({'auxiliary_trials':len(rows),'raw_observations_checked':result['total_observations_RAW_checked'],
                      'localized_cut_effect':True,'repeat_B_directions':[b['B_qualified_output_ticks']for b in by['EO01_SOC_AUX_REPEAT']['blocks']],
                      'repeat_later_commands':[b['common_action']['command']for b in by['EO01_SOC_AUX_REPEAT']['blocks']]},ensure_ascii=False))


if __name__ == '__main__':
    main()
