"""N0 correction: count both port and channel receipt representations exactly.

R01 port-only counts are preserved; they were not the entire material dose.
No Native import, replay, altered criterion or scientific-state modification.
"""
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
        per_op=[]
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if'apd04_actuator_'not in relative:continue
            encoded=(base/relative).read_bytes()
            if hashlib.sha256(encoded).hexdigest()!=operation['result_sha256']:raise ValueError('Primary hash differs')
            primary=json.loads(encoded);group=('old_panel'if'old16_MA6'in relative else
                'ten_opportunities'if any('rows'in block and block.get('kind','').startswith('APD04.shared_workshop')for block in primary['result'].get('rows',[]))else'other_preparations')
            receipts={}
            for item in walk(primary['result']):
                if'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
                    identifier=int(item['id']);previous=receipts.get(identifier)
                    if previous and item['receipt']['status']in('scheduled','queued'):continue
                    normalized={'id':identifier,'channel':item.get('channel',item.get('port')),
                        'representation':'channel'if'channel'in item else'port','status':item['receipt']['status'],
                        'value':item.get('payload',item.get('value')),'tick':item['tick']}
                    if previous and previous['channel']!=normalized['channel']:raise ValueError('One Native id names different channels')
                    receipts[identifier]=normalized
            groups[group].update(receipts)
            per_op.append({'primary':relative,'group':group,'requested_unique':len(receipts),
                'statuses_exact':dict(Counter(item['status']for item in receipts.values())),
                'schema_forms':dict(Counter(item['representation']for item in receipts.values()))})
        all_inputs={identifier:item for entries in groups.values()for identifier,item in entries.items()}
        rows.append({'life':life,'groups':{key:{'requested_unique':len(entries),
            'statuses_exact':dict(Counter(item['status']for item in entries.values())),
            'schema_forms':dict(Counter(item['representation']for item in entries.values()))}for key,entries in groups.items()},
            'all_committed_operations_unique':len(all_inputs),'all_statuses_exact':dict(Counter(item['status']for item in all_inputs.values())),
            'per_operation':per_op})
    value={'schema':'APD04.actuator_R02.all_committed_doses.N0.r02','lives':rows,'new_native_ticks':0,
           'correction':'R01 required port and omitted channel records. Original bytes/results remain preserved. '
                        'R02 unifies both representations by exact Native ID. No changed actions, effects, reader or experiment.',
           'scope':'Committed primary receipts only. Host result reads are not material inputs. '
                   'The old16+6 panel is a separate material dose. Rejections remain exact named statuses.'}
    with args.out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps([{key:row[key]for key in('life','groups','all_committed_operations_unique','all_statuses_exact')}for row in rows],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
