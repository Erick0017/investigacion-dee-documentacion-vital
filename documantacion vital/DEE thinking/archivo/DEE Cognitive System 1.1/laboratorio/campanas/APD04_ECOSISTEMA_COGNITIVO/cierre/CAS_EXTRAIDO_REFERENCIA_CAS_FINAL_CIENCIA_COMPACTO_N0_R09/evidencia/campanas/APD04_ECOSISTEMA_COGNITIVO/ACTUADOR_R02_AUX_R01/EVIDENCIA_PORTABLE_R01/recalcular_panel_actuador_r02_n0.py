"""Recalculate completed old16/MA6 RAW readers and compare archived baseline.

External N0 tool only: not a reader supplied to a DEE participant. No engine.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json


def read(path):return json.loads(path.read_bytes())
def sha(data):return hashlib.sha256(data).hexdigest()


def panel_rows(panel):
    rows=[]
    for family,key in(('forms','form'),('memories','context')):
        for item in panel[family]:
            reader=item['result']['reader'];candidates=[]
            for observation in reader['panel']:
                raw=int(observation['raw']);semantic=raw&0xffffffff;state=(raw>>60)&15
                vector=[((raw>>shift)&15)-(16 if((raw>>shift)&15)>=8 else 0)for shift in(48,52,56)]
                if state>0 and semantic==1 and vector in([0,0,-1],[0,0,1]):
                    candidates.append({'sign':vector[2],'site':observation['site'],'raw':observation['raw'],'clock':observation['clock']})
            sign=candidates[0]['sign']if len(candidates)==1 else None
            if sign!=reader['formed_native_command']:raise ValueError('RAW exact decoder differs from fixed common reader')
            rows.append({'family':family,'name':item[key],'sign':sign,'candidates':candidates,
                         'reader_uses_target_or_token':reader['reader_uses_target_or_token']})
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();base=args.index.parent;index=read(args.index)
    old=base/index['old_panel_baseline']['directory'];bi=read(old/'INDICE_LINEA_ORIGINAL.json')
    encoded=(old/bi['exported_line']).read_bytes();decoded=gzip.decompress(encoded)
    if sha(encoded)!=bi['export_sha256']or sha(decoded)!=bi['original_line_sha256']:raise ValueError('Baseline primary line SHA mismatch')
    original=json.loads(decoded)['result']['request']['result']
    if isinstance(original,str):original=json.loads(original)
    reference=panel_rows(original['result']['rows'][0]);expected={(row['family'],row['name']):row['sign']for row in reference}
    results=[]
    for life,info in index['lives'].items():
        record=read(base/info['record'])
        operations=[row for row in record['operations']if 'apd04_actuator_'in row.get('result_file','')and'old16_MA6'in row.get('result_file','')]
        if not operations:
            results.append({'life':life,'panel_executed':False,'not_a_retention_failure':True});continue
        if len(operations)!=1:raise ValueError('Expected one explicitly requested material panel per AUX')
        operation=operations[0];path=base/operation['result_file'];encoded=path.read_bytes()
        if sha(encoded)!=operation['result_sha256']:raise ValueError('New panel primary hash differs')
        primary=json.loads(encoded);rows=panel_rows(primary['result']['rows'][0])
        for row in rows:row['same_sign_as_archived_prior_panel']=row['sign']==expected[(row['family'],row['name'])]
        results.append({'life':life,'panel_executed':True,'primary':operation['result_file'],
            'primary_sha256':sha(encoded),'rows':rows,'forms_requested':sum(row['family']=='forms'for row in rows),
            'memories_requested':sum(row['family']=='memories'for row in rows),
            'unique_formed_forms':sum(row['family']=='forms'and row['sign']is not None for row in rows),
            'unique_formed_memories':sum(row['family']=='memories'and row['sign']is not None for row in rows),
            'matches_prior_forms':sum(row['family']=='forms'and row['same_sign_as_archived_prior_panel']for row in rows),
            'matches_prior_memories':sum(row['family']=='memories'and row['same_sign_as_archived_prior_panel']for row in rows)})
    value={'schema':'APD04.actuator_R02.old_panel_RAW.N0.r01','lives':results,'prior_rows':reference,
        'new_native_ticks':0,'scope':'Consecutive material queries after the10opportunities, not passive observation, '
        'independent learners or proof that all functions remained accessible at all intermediate times. '
        'A matched sign is compared with the exact earlier archived common-prefix ancestor panel, not a new target.'}
    with args.out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps([{key:row[key]for key in row if key not in('rows',)}for row in results],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
