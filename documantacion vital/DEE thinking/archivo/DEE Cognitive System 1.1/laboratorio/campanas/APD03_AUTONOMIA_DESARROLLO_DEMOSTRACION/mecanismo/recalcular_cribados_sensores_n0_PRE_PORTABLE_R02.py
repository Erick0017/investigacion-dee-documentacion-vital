"""Portable stdlib-only recomputation of archived APD03 sensor link screens.

No dee_thinking import, snapshot restoration or new native tick is possible.
The primary results retain raw integers as decimal strings where required.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def fingerprint(path):
    data = Path(path).read_bytes()
    return {'path':str(path), 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def nibble(value, shift):
    value = (value >> shift) & 15
    return value - 16 if value & 8 else value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    result=read(args.evidence/'RESULTADOS.json')
    issues=[]
    checks=0
    observations=0
    family_rows=[]
    causal_windows=[]
    input_counts=Counter()
    native_counts=Counter()
    sources=[]
    for family in result['families']:
        events=[]
        by_bit={0:[],1:[]}
        for arm in family['arms']:
            world_tag=family['family']+'/ARM'+str(arm['arm'])
            requests={}
            for event in arm.get('events',[]):
                index=event['index']
                path=args.evidence/family['family']/('ARM'+str(arm['arm']))/('EVENTO_'+str(index)+'.json.gz')
                original=read(path)
                checks+=1
                if original!=event:
                    issues.append(world_tag+': aggregate differs from original event'+str(index))
                sources.append(fingerprint(path))
                selection=event['selection']
                bit=selection['raw_observed_fact']
                reader=selection['reader']
                candidates=[]
                for row in reader['observations']:
                    if row['state']>0 and row['semantic']==1 and row['direction'][1:]==[1,0] and row['direction'][0] in(-1,0,1):
                        # A gate is additionally checked against the exact fixed
                        # site for this sign, never against the expected answer.
                        sign=row['direction'][0]
                        if row['site']==[(25+2*sign)%67,15,53]:
                            candidates.append(sign)
                actual=candidates[0] if len(candidates)==1 else None
                checks+=1
                if actual!=reader['choice']:
                    issues.append(world_tag+': fixed reader mismatch'+str(index))
                by_bit[bit].append(actual)
                sensors=selection.get('sensory_requests',[selection['sensory_request']] if 'sensory_request' in selection else [])
                for row in sensors:
                    input_counts[row['receipt']['status']]+=1
                    checks+=1
                    if row['payload']!=bit or row['tick']!=selection['query_tick']+3:
                        issues.append(world_tag+': raw fact changed or context-specific phase')
                for row in walk(event):
                    if {'raw','clock','site','direction','state','s_reg','semantic'}<=set(row):
                        observations+=1
                        raw=int(row['raw']);clock=int(row['clock'])
                        checks+=1
                        decoded=(raw&0xffffffff,(raw>>32)&0xffff,[nibble(raw,48),nibble(raw,52),nibble(raw,56)],(raw>>60)&15)
                        if decoded!=(row['state'],row['s_reg'],row['direction'],row['semantic']) or not 0<=clock<2**64:
                            issues.append(world_tag+': exact raw/clock decode mismatch')
                    if isinstance(row.get('receipt'),dict) and type(row.get('id')) is int:
                        receipt=row['receipt'];status=receipt.get('status')
                        old=requests.get(row['id'])
                        if old is None or old=='scheduled':
                            requests[row['id']]=status
                        elif status!='scheduled' and old!=status:
                            issues.append(world_tag+': inconsistent terminal receipt')
                after=event.get('sources_after_window',[event['source_after_window']] if 'source_after_window' in event else [])
                before=selection.get('sources_before',[selection['source_before']] if 'source_before' in selection else [])
                # The owner observes current_tick q+3 BEFORE inputs scheduled
                # at q+3 are applied during q+3 -> q+4. Reconstruct ONLY those
                # actually admitted public inputs, not a hidden prior state.
                frames={frame['offset']:frame for frame in selection['frames']}
                center=(25,13,53)
                pre_grid={tuple(row['site']):dict(row) for row in frames[3]['passive_capture']}
                post_grid={tuple(row['site']):row for row in frames[4]['passive_capture']}
                offsets=[(x,y,z) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1) if (x,y,z)!=(0,0,0)]
                required={tuple((center[i]+offset[i])%67 for i in range(3)) for offset in offsets}
                checks+=1
                if not required<=set(pre_grid):
                    issues.append(world_tag+': incomplete center Moore context for declared gradient')
                else:
                    def gradient(grid):
                        result=[0,0,0]
                        for offset in offsets:
                            row=grid[tuple((center[i]+offset[i])%67 for i in range(3))]
                            if row['state']>0:
                                for axis in range(3):result[axis]-=offset[axis]*row['s_reg']
                        return result
                    pre_gradient=gradient(pre_grid)
                    for source_row,request_row in zip(before,sensors):
                        if request_row['receipt']['status']=='applied':
                            coordinate=tuple(source_row['site'])
                            if coordinate in pre_grid:
                                pre_grid[coordinate]={'state':1,'s_reg':request_row['payload']}
                    admitted_gradient=gradient(pre_grid)
                    expected_direction=[(value>0)-(value<0) for value in admitted_gradient]
                    checks+=1
                    if post_grid[center]['direction']!=expected_direction:
                        issues.append(world_tag+': center direction differs from admitted-input gradient')
                    causal_windows.append({'world':world_tag,'event':index,'bit':bit,
                        'observed_current_tick_before_input':frames[3]['tick'],
                        'actual_requested_input_tick':selection['query_tick']+3,
                        'post_complete_tick':frames[4]['tick'],
                        'gradient_from_passive_preinput_ROI':pre_gradient,
                        'gradient_with_exact_admitted_inputs':admitted_gradient,
                        'observed_center_direction_after_tick':post_grid[center]['direction'],
                        'coverage':'Complete Moore26 of central encounter plus exact admitted sensor inputs. Does not claim unique lineage or complete neighboring tick-dependency closure.'})
                events.append({'arm':arm['arm'],'index':index,'bit':bit,'choice':actual,
                    'sensor_statuses':[row['receipt']['status'] for row in sensors],
                    'source_RAW_before':[str(row['raw']) for row in before],
                    'source_RAW_after':[str(row['raw']) for row in after],
                    'continued_same_arm':index>0})
            native_counts.update(requests.values())
        criterion=family['native_link_criterion']
        checks+=1
        if by_bit!={int(k):v for k,v in criterion['choices_by_raw_bit'].items()}:
            issues.append(family['family']+': bit-choice table differs')
        family_rows.append({'family':family['family'],'events':events,'choices_by_raw_bit':by_bit,
            'reusable_prepared_link':criterion['reusable_prepared_link'],
            'nonzero_final_sources':sum(any(int(raw) for raw in event['source_RAW_after']) for event in events)})
    checks+=1
    if sum(len(row['events']) for row in family_rows)!=result['material_queries']:
        issues.append('Material query denominator differs')
    body={'schema':'APD03.sensor_screens.stdlib_recalculation.v1',
        'primary':fingerprint(args.evidence/'RESULTADOS.json'),'checks':checks,
        'exact_RAW_observation_occurrences':observations,'issues':issues,
        'material_queries':result['material_queries'],'sensor_inputs_requested':sum(input_counts.values()),
        'sensor_statuses':dict(input_counts),'unique_native_requests_by_world_terminal_status':dict(native_counts),
        'winning_family':result['winning_family'],'families':family_rows,'primary_event_files':sources,
        'central_causal_windows':causal_windows,
        'scope':'Prepared perceptual link only. Repeated copies of a shared prefix are not independent learners. No Native execution or new result.'}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf8') as stream:
        json.dump(body,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'checks':checks,'issues':len(issues),'material_queries':body['material_queries'],'sensor_statuses':body['sensor_statuses'],'native_unique_terminal':dict(native_counts)}))
    return 1 if issues else 0


if __name__=='__main__':
    raise SystemExit(main())
