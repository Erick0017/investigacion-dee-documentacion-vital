"""Archive-only APD04 workshop recalculation, exact uint64; no Native import.

Call once per declared LIFE/trajectory; never combine divergent branch labels.
Inputs remain untouched. Every exported opportunity retains source SHA+locator.
This is not native replay and cannot establish omitted microscopic causes.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def walk(obj,path='$'):
    yield path,obj
    if isinstance(obj,dict):
        for key,value in obj.items():
            if key in('result','result_json')and isinstance(value,str)and value.lstrip().startswith(('{','[')):
                try:value=json.loads(value)
                except json.JSONDecodeError:pass
            yield from walk(value,path+'.'+str(key))
    elif isinstance(obj,list):
        for key,value in enumerate(obj):yield from walk(value,path+'['+str(key)+']')


def decode(obs):
    n=int(obs['raw'])
    if not 0<=n<2**64:raise ValueError('RAW outside exact uint64')
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
            'direction':[((n>>k)&15)-(16 if ((n>>k)&15)>=8 else 0)for k in(48,52,56)]}


def choice(reader,kind):
    obs=reader.get('observations',[]);candidates=[]
    expected={(25+2*x,15,53):(x,[x,1,0])for x in(-1,0,1)}if kind=='selection'else{
        (15+2*x,17,15+2*z):(x,[x,1,z])for x in(-1,0,1)for z in(0,-1)}
    if len(obs)!=len(expected)or{tuple(o['site'])for o in obs}!=set(expected):
        raise ValueError('Frozen reader gate coverage differs')
    for o in obs:
        d=decode(o);value,direction=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==direction:candidates.append(value)
    return candidates[0]if len(candidates)==1 else None


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--life',required=True)
    parser.add_argument('--input',action='append',required=True);parser.add_argument('--output')
    parser.add_argument('--preview-open',action='store_true')
    args=parser.parse_args()
    if not args.preview_open and not args.output:raise ValueError('Closed extraction requires explicit new output directory')
    output=Path(args.output)if args.output else None
    if output is not None:
        if output.exists():raise FileExistsError('Preserve prior recalculation; new revision required')
        output.mkdir(parents=True)
    rows=[];sources=[];seen={};issues=[];receipts={};checks=0
    for name in args.input:
        source=Path(name).resolve(strict=True);raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        decoded=gzip.decompress(raw)if source.name.endswith('.gz')else raw
        if source.name.endswith(('.jsonl','.jsonl.gz')):
            lines=decoded.splitlines();obj=[]
            for index,line in enumerate(lines):
                try:obj.append(json.loads(line))
                except json.JSONDecodeError:
                    if not(args.preview_open and index==len(lines)-1):raise
        else:obj=json.loads(decoded)
        sources.append({'source':str(source),'bytes':len(raw),'sha256_of_bytes_read':sha,'closed_claimed':not args.preview_open})
        for locator,node in walk(obj):
            if not isinstance(node,dict)or not set(('public_before','committed_effect','selection'))<=set(node):continue
            selector=node['selection'];selection_reader=selector.get('reader',selector.get('native_trial',{}).get('reader',{}))
            key=(args.life,selector.get('query_tick'),node.get('episode'),node['public_before'].get('source_id'))
            if key in seen:
                seen[key].append({'source_sha256':sha,'locator':locator});continue
            seen[key]=[{'source_sha256':sha,'locator':locator}]
            try:selected=choice(selection_reader,'selection')
            except(ValueError,KeyError,TypeError)as error:issues.append({'key':key,'error':str(error)});selected=None
            reported=selector.get('physical_choice',selector.get('native_trial',{}).get('physical_choice'))
            checks+=1
            if selected!=reported:issues.append({'key':key,'field':'selection','RAW':selected,'reported':reported})
            action={-1:'USE',0:'INSPECT',1:'INSPECT'}.get(selected)
            checks+=1
            if action!=node.get('physical_action'):issues.append({'key':key,'field':'action','RAW_action':action,'reported':node.get('physical_action')})
            primitive=node.get('native_operation');primitive_choice=None;primitive_observations=[]
            if primitive is not None:
                trial=primitive.get('native_trial',{});primitive_observations=trial.get('reader',{}).get('observations',[])
                try:primitive_choice=choice(trial.get('reader',{}),'primitive')
                except(ValueError,KeyError,TypeError)as error:issues.append({'key':key,'error':str(error)})
                checks+=1
                if primitive_choice!=primitive.get('physical_choice'):issues.append({'key':key,'field':'primitive','RAW':primitive_choice,'reported':primitive.get('physical_choice')})
            effect=node['committed_effect'];public=node['public_before'];useful=bool(effect.get('useful'))
            if 'loads_before'in effect and 'loads_after'in effect:
                before=effect['loads_before'];after=effect['loads_after'];gb=abs(before[0]-before[1]);ga=abs(after[0]-after[1]);checks+=3
                expected=(ga<gb or(primitive_choice==0 and gb==0))and public['tag']==public['goal_tag']
                if gb!=effect.get('gap_before')or ga!=effect.get('gap_after')or useful!=expected:
                    issues.append({'key':key,'field':'balance_effect','recalculated_useful':expected})
            if 'actual_bin'in effect:
                audit=node.get('auditor_only_after_effect')
                if audit is not None:
                    value=audit['actual_source_value'];criterion=audit['criterion']
                    expected_sign=(value>criterion)-(value<criterion)
                    correct=primitive_choice==expected_sign and audit['observed_version']==audit['source_version']
                    checks+=2
                    if effect.get('correct')!=correct:issues.append({'key':key,'field':'class_full_correctness','recalculated':correct})
                else:
                    correct=bool(effect.get('correct'))
                    if correct and primitive_choice!=node.get('expected_class_auditor_only_after_action'):issues.append({'key':key,'field':'class_direction'})
                expected=correct and public['tag']==public['goal_tag']and effect.get('previous_bin')!=primitive_choice
                checks+=2
                if useful!=expected:issues.append({'key':key,'field':'class_usefulness','recalculated':expected})
            for _,part in walk(node):
                if isinstance(part,dict)and isinstance(part.get('receipt'),dict)and'id'in part['receipt']:
                    receipt=part['receipt'];rid=str(receipt['id']);previous=receipts.get(rid)
                    waiting={'scheduled','pending','admitted'}
                    # JSON key order is not temporal order: a query's cached
                    # SCHEDULED receipt can occur after the final APPLIED copy.
                    if previous is None or previous.get('status')in waiting:
                        receipts[rid]=receipt
                    elif receipt.get('status')not in waiting and previous.get('status')!=receipt.get('status'):
                        issues.append({'key':key,'field':'conflicting_terminal_receipts','id':rid,
                                       'statuses':[previous.get('status'),receipt.get('status')]})
            rows.append({'life':args.life,'source_sha256':sha,'source_locator':locator,'episode':node.get('episode'),
                         'query_tick':selector.get('query_tick'),'read_tick':selection_reader.get('tick'),
                         'public_before':public,'raw_sensor_components':node.get('raw_sensor_components'),
                         'selector_RAW_observations':selection_reader.get('observations'),'RAW_selection':selected,
                         'action':action,'primitive_RAW_observations':primitive_observations,'RAW_primitive':primitive_choice,
                         'committed_effect':effect,'feedback':node.get('feedback'),
                         'actual_return_category':(node.get('native_return')or{}).get('category'),
                         'artifact_locator':node.get('artifact'),'expected_auditor_only':node.get('expected_class_auditor_only_after_action')})
    report={'schema':'APD04.workshop_archive_recalculation.N0.R01','life':args.life,'new_native_ticks':0,
            'checks':checks,'issues':issues,'unique_opportunities':len(rows),'rows':rows,'sources':sources,
            'action_counts':dict(Counter(r['action']for r in rows)),'useful':sum(bool(r['committed_effect'].get('useful'))for r in rows),
            'last_observation_exported_receipt_status':dict(Counter(r.get('status')for r in receipts.values())),
            'native_receipts_by_id':receipts,
            'scope':'Archived recalculation only. No Native replay, no microscopic causal reconstruction, no inference of independent learners from row counts.',
            'duplicate_record_locations':[{'key':k,'locations':v}for k,v in seen.items()if len(v)>1],
            'limitations':['Class freshness can only be independently recalculated when environmental object versions are exported.',
                           'Unique receipt counts cover exported IDs, not all historical pending queues.',
                           'Native snapshots and deep frames omitted from this compact extraction remain necessary for physical replay.']}
    if output is not None:(output/'RECALCULO_COMPACTO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'checks':checks,'issues':issues,'opportunities':len(rows),'useful':report['useful'],
                      'actions':report['action_counts'],'receipts':report['last_observation_exported_receipt_status'],
                      'preview_of_open_source':args.preview_open,'new_native_ticks':0,
                      'rows':[{'episode':r['episode'],'query_tick':r['query_tick'],'public':r['public_before'],
                               'selection':r['RAW_selection'],'action':r['action'],'primitive':r['RAW_primitive'],
                               'effect':r['committed_effect']}for r in rows]},ensure_ascii=False))


if __name__=='__main__':main()
