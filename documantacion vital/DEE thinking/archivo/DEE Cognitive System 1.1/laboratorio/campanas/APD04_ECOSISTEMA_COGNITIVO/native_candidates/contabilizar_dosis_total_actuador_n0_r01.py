"""Separate ten-op Native dose from the subsequent material old-panel dose."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();base=args.evidence;index=json.loads((base/'INDICE.json').read_bytes());rows=[]
    for life,info in index['lives'].items():
        record=json.loads((base/info['record']).read_bytes());groups={'ten_opportunities':{},'old_panel':{},'other_preparations':{}}
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if'apd04_actuator_'not in relative:continue
            path=base/relative;encoded=path.read_bytes()
            if hashlib.sha256(encoded).hexdigest()!=operation['result_sha256']:raise ValueError('Primary hash differs')
            primary=json.loads(encoded);group=('old_panel'if'old16_MA6'in relative else
                'ten_opportunities'if any('rows'in block and block.get('kind','').startswith('APD04.shared_workshop')for block in primary['result'].get('rows',[]))else'other_preparations')
            for item in walk(primary['result']):
                if'id'in item and'port'in item and isinstance(item.get('receipt'),dict):
                    identifier=int(item['id']);previous=groups[group].get(identifier)
                    if previous and item['receipt']['status']in('scheduled','queued'):continue
                    groups[group][identifier]=item
        all_inputs={identifier:item for entries in groups.values()for identifier,item in entries.items()}
        rows.append({'life':life,'groups':{key:{'requested_unique':len(entries),
            'statuses_exact':dict(Counter(item['receipt']['status']for item in entries.values()))}for key,entries in groups.items()},
            'all_committed_operations_unique':len(all_inputs),'all_statuses_exact':dict(Counter(item['receipt']['status']for item in all_inputs.values()))})
    value={'schema':'APD04.actuator_R02.all_committed_doses.N0.r01','lives':rows,'new_native_ticks':0,
           'scope':'Only exact committed primary receipts. Host transport/result reads are not physical inputs. '
                   'The old16+6 panel is a separate material dose and must not disappear from overall input accounting.'}
    with args.out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(value,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
