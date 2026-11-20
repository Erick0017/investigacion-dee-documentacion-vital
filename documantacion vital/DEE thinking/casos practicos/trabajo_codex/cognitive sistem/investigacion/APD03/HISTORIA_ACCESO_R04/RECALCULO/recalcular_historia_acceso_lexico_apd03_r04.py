"""Exact archived R04 ROI/admission/reader recalculation, no Native imports."""
import argparse,collections,gzip,hashlib,importlib.util,json
from pathlib import Path


def read(path):
    path=Path(path);data=path.read_bytes();return json.loads(gzip.decompress(data)if path.suffix=='.gz'else data)


def fields(raw):
    def signed(shift):
        value=(raw>>shift)&15;return value-16 if value&8 else value
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,
        'direction':[signed(shift)for shift in(48,52,56)]}


def walk(value):
    if isinstance(value,dict):
        yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)


def calculate(evidence):
    evidence=Path(evidence);results=read(evidence/'RESULTADOS.json');checks=0;issues=[];arms=[]
    roi={tuple(r['site'])for r in results['plan']['ROI']}
    def check(condition,message):
        nonlocal checks
        checks+=1
        if not condition:issues.append(message)
    gate_map={}
    for row in results['plan']['ROI']:
        for role in row['roles']:
            if role.startswith('fixed32_'):gate_map[tuple(row['site'])]=int(role.rsplit('_',1)[1])
    check(len(gate_map)==32,'Fixed common reader must have32gates')
    check(results['sources_unchanged'],'Executed sources unchanged')
    for branch in results['results']:
        if 'failure'in branch:
            arms.append({'index':branch['index'],'failure':branch['failure'],'arm':branch['arm']});continue
        folder=evidence/Path(branch['primary']).parent;primary=read(folder/'PRIMARIO.json.gz')
        initial=read(folder/'IGUALDAD_INICIAL.json');check(initial['exact_encoded_and_decoded_snapshot'],folder.name+': initial source proof')
        for item in walk(primary):
            if 'raw'in item and all(key in item for key in('state','s_reg','semantic','direction')):
                raw=int(item['raw']);check(0<=raw<1<<64,folder.name+': uint64 RAW')
                for key,value in fields(raw).items():check(item[key]==value,folder.name+': RAW field '+key)
        frames={};trace=folder/'ROI_TICK_A_TICK.jsonl.gz'
        if trace.is_file():
            with gzip.open(trace,'rb')as stream:
                for line in stream:
                    frame=json.loads(line);tick=frame['tick'];actual={tuple(r['site']):r for r in frame['sites']}
                    check(set(actual)==roi and len(frame['sites'])==len(roi),folder.name+': ROI coverage at'+str(tick))
                    check(tick not in frames,folder.name+': duplicate tick')
                    for item in actual.values():
                        check(type(item['raw'])is str and 0<=int(item['raw'])<1<<64,folder.name+': exact RAW')
                        check(type(item['clock'])is str and 0<=int(item['clock'])<1<<64,folder.name+': exact clock')
                    frames[tick]=actual
            check(list(frames)==list(range(primary['start_tick'],primary['end_tick']+1)),folder.name+': contiguous owner-step coverage')
            check(len(frames)==branch['frames_recorded'],folder.name+': frame denominator')
        else:check(not branch['arm']['recording'],folder.name+': recording expected')
        queries=[]
        for item in walk(primary):
            if item.get('kind')!='APD03_common_lexical_query':continue
            panel={tuple(r['site']):r for r in item['reader']['panel']}
            check(set(panel)==set(gate_map)and len(item['reader']['panel'])==32,folder.name+': common-reader sites')
            candidates=[]
            for site,sign in gate_map.items():
                rawfields=fields(int(panel[site]['raw']))
                if rawfields['state']>0 and rawfields['semantic']==1 and rawfields['direction']==[0,0,sign]:candidates.append(sign)
                if frames:
                    actual=frames[item['read_tick']][site]
                    check(actual['raw']==str(panel[site]['raw'])and actual['clock']==str(panel[site]['clock']),folder.name+': passive gate agrees with material reader')
            formed=candidates[0]if len(candidates)==1 else None
            check(formed==item['reader']['formed_native_command'],folder.name+': output from fixed32RAW')
            check((len(candidates)>1)==item['reader']['ambiguous'],folder.name+': ambiguity')
            queries.append({'form':item['form'],'input_tick':item['input_tick'],'read_tick':item['read_tick'],'formed':formed})
        requests={}
        for item in walk(primary):
            if 'receipt'in item and 'id'in item:
                key=(item['channel'],int(item['id']))
                if key in requests:check(item==requests[key],folder.name+': repeated receipt agrees')
                requests[key]=item
        status=collections.Counter(item['receipt']['status']for item in requests.values())
        selected=[]
        for label in('A_lesson','B_lesson'):
            episode=primary[label];counts=collections.Counter(r['receipt']['status']for r in episode['requests'])
            selected.append({'episode':label,'teacher_mode':episode['teacher_mode'],'input_tick':episode['input_tick'],
                'teacher_tick':episode['teacher_tick'],'end_tick':episode['end_tick'],
                'requested':len(episode['requests']),'statuses':dict(counts),'requests':episode['requests']})
        boundaries=[]
        chosen={(r['channel'],int(r['id']))for label in('A_lesson','B_lesson')for r in primary[label]['requests']}
        for key,item in sorted(requests.items(),key=lambda row:(row[1]['tick'],row[1]['id'])):
            if key not in chosen and item['receipt']['status']=='applied':continue
            site=tuple(item['site']);tick=item['tick']
            boundary=[]
            for offset in(-1,0,1):
                entry=frames.get(tick+offset,{}).get(site)
                if entry is not None:boundary.append({'tick':tick+offset,'relative_to_requested_tick':offset,
                    'raw':entry['raw'],'clock':entry['clock'],'fields':fields(int(entry['raw']))})
            boundaries.append({'id':item['id'],'channel':item['channel'],'site':list(site),'requested_tick':tick,
                'receipt':item['receipt'],'observed_owner_boundaries':boundary,
                'scope':'State at tick counters t-1,t,t+1; receipt is authoritative admission. No invented within-tick lineage.'})
        pre={r['form']:r['result']['reader']['formed_native_command']for r in primary['old_before']}
        post={r['form']:r['result']['reader']['formed_native_command']for r in primary['old_after']}
        valid_same=sum(pre[f]in(-1,1)and post[f]==pre[f]for f in pre)
        boutputs=[r['reader']['formed_native_command']for r in primary['B_uses']]
        arms.append({'index':branch['index'],'arm':branch['arm'],'start_tick':primary['start_tick'],'end_tick':primary['end_tick'],
            'native_unique_requested':len(requests),'native_statuses':dict(status),'A_and_B_lessons':selected,
            'A_uses':[r['reader']['formed_native_command']for r in primary['A_uses']],
            'B_preteaching':primary['B_before_teaching']['reader']['formed_native_command'],'B_postlesson_uses':boutputs,
            'criterion_two_correct':all(sign==primary['B_sign_auditor']for sign in boutputs),
            'old4_before':pre,'old4_after':post,'old4_same_valid':valid_same,'queries_redecoded':queries,
            'trace_frames':len(frames),'source_boundaries':boundaries,'passivity_source_proof':branch.get('passivity')})
        if branch.get('passivity'):
            check(all(branch['passivity'][key]for key in('exact_encoded_final_snapshot','exact_decoded_final_snapshot','physical_equal')),
                folder.name+': complete passivity source proof')
        del frames
    return {'schema':'DEE.APD03.history_access_R04.archived_recalculation','checks':checks,'issues':issues,
        'arms':arms,'new_native_ticks':0,'new_material_queries':0,
        'limits':['Source proofs for complete-state/passivity equality do not replace omitted Native snapshots.',
            'Four branches share one prepared prefix; passivity repeat is instrumental, not independent learning.',
            'Nominal dose equality does not imply equal admission; read explicit receipt denominators.',
            'Teacher+11 can change age and phase; actual later query calendars must be compared.',
            'ROI63 is not the complete causal universe; no return/unique-lineage inference.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args();result=calculate(args.evidence)
    with args.out.open('x',encoding='utf8')as stream:json.dump(result,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'checks':result['checks'],'issues':len(result['issues']),'arms':len(result['arms'])}))


if __name__=='__main__':main()
