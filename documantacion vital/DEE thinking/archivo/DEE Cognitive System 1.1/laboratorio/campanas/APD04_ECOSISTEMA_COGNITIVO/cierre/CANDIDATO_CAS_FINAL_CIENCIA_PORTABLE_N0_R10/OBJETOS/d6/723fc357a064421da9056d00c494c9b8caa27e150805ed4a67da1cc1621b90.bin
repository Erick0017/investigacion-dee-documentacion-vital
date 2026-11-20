"""Read only committed actuator primaries; exact RAW decoder and denominators.

No DEE imports/ticks. Effects are recorded environmental outcomes, not a second
Native decision. Run --index for a future portable copy; otherwise reads local
committed VIDA references. Does not consume or repair a pending operation.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json

ROOT=Path(__file__).resolve().parents[4]
LIVES=('APD04_ACTUADOR_REAL_R02','APD04_ACTUADOR_OMIT_R02')
CODEC={-1:'INSPECT',0:'INSPECT',1:'USE'}


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def raw_choice(observations):
    candidates=[]
    for row in observations:
        raw=int(row['raw']);state=(raw>>60)&15;semantic=raw&0xffffffff
        direction=[((raw>>shift)&15)-(16 if((raw>>shift)&15)>=8 else 0)for shift in(48,52,56)]
        for sign in(-1,0,1):
            if row['site']==[(25+2*sign)%67,15,53] and state>0 and semantic==1 and direction==[sign,1,0]:
                candidates.append(sign)
    return candidates[0]if len(candidates)==1 else None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    portable=json.loads(args.index.read_text(encoding='utf8'))if args.index else None
    results=[];discrepancies=[]
    for life in LIVES:
        if portable:
            info=portable['lives'].get(life)
            if not info:continue
            home=args.index.parent
            record=json.loads((home/info['record']).read_text(encoding='utf8'))
        else:
            record_path=ROOT/'sistema/estado/vidas'/life/'VIDA.json'
            if not record_path.is_file():continue
            record=json.loads(record_path.read_text(encoding='utf8'))
            home=ROOT/'sistema/estado/servicios_persistentes'/life
        rows=[];sources=[];receipts={};panels=[];lastphysical=None
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if 'apd04_actuator_'not in relative:continue
            path=home/relative
            encoded=path.read_bytes();digest=hashlib.sha256(encoded).hexdigest()
            if digest!=operation['result_sha256']:raise ValueError('Committed primary SHA differs: '+str(path))
            primary=json.loads(encoded)
            sources.append({'file':relative,'sha256':digest,'bytes':len(encoded)})
            result=primary.get('result',{})
            lastphysical=result.get('final',{}).get('memory_contract',{}).get('INSTRUMENTO',{}).get('physical',lastphysical)
            for block in result.get('rows',[]):
                if block.get('kind')=='APD03_explicit_material_panel':
                    panels.append({'source':relative,'forms_requested':block['forms_requested'],
                                   'memory_queries_requested':block['memory_queries_requested']})
                for row in block.get('rows',[]):
                    if not isinstance(row,dict)or'selection'not in row:continue
                    selection=row['selection'];choice=raw_choice(selection['reader']['observations'])
                    action=CODEC.get(choice);effect=row['committed_effect']
                    if choice!=selection['physical_choice']or action!=row['physical_action']:
                        discrepancies.append({'life':life,'episode':row['episode'],'check':'fixed Native reader and R02 action codec'})
                    per={}
                    for entry in walk(row):
                        if'id'in entry and'port'in entry and isinstance(entry.get('receipt'),dict):
                            key=int(entry['id'])
                            if key in per and entry['receipt']['status']in('scheduled','queued'):continue
                            per[key]=entry
                    receipts.update(per)
                    statuses=Counter(entry['receipt']['status']for entry in per.values())
                    rows.append({'source':relative,'episode':row['episode'],'components':row['raw_sensor_components'],
                        'query_tick':selection['query_tick'],'reader_tick':selection['reader']['tick'],
                        'choice_from_exact_RAW':choice,'action_from_fixed_R02':action,
                        'prepared_codec':effect.get('prepared_action_codec'),
                        'environmental_effect':effect,'feedback':row['feedback'],
                        'references_before':selection['references'],
                        'references_after':row['native_return'].get('after'),
                        'requested_unique':len(per),'statuses_exact':dict(statuses)})
        statuses=Counter(entry['receipt']['status']for entry in receipts.values())
        results.append({'life':life,'parent':record['parent'],'snapshot_sha256':record['snapshot_sha256'],
            'final_committed_tick':record['physical']['tick'],'sources':sources,'rows':rows,'panels':panels,
            'opportunities_completed':len(rows),'valid_native_responses':sum(row['choice_from_exact_RAW']is not None for row in rows),
            'NULL_responses':sum(row['choice_from_exact_RAW']is None for row in rows),
            'useful_environmental_effects':sum(bool(row['environmental_effect']['useful'])for row in rows),
            'new_facts':sum(bool(row['environmental_effect']['new_fact'])for row in rows),
            'requested_unique_native_inputs':len(receipts),'statuses_exact':dict(statuses),
            'rejected':sum(count for status,count in statuses.items()if status.startswith('rejected')),
            'last_completed_primary_physical':lastphysical,
            'scope':'Completed primary rows only; a pending request is not counted as wrong or individually admitted. '
                    'RAW choice and fixed action are recalculated. Environment usefulness/new_fact are archived measured effects, '
                    'not an independently reconstructed unseen cache history.'})
    value={'schema':'APD04.actuator_R02.committed_primary_summary.N0.r01','lives':results,
           'discrepancies':discrepancies,'new_native_ticks':0,'same_prefix_not_independent_learners':True}
    if args.out:
        with args.out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    compact=[{key:life[key]for key in('life','final_committed_tick','opportunities_completed','valid_native_responses',
              'NULL_responses','useful_environmental_effects','new_facts','requested_unique_native_inputs','statuses_exact')}for life in results]
    print(json.dumps({'lives':compact,'discrepancies':discrepancies},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
