"""Reconcile archived A/B/C port+channel receipts with their exact committed FULLs.

Does not read current live VIDAs, rerun a query or touch interrupted futures.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
BASE=EV/'ATENCION_CONSECUENCIAS_AUX_R02_BC/EVIDENCIA_PORTABLE_R02'
OUT=EV/'ATENCION_ABC_DOSIS_COMPLETA_N0_R02'


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def main():
    if OUT.exists():raise FileExistsError('Closed ABC dose correction exists; no overwrite')
    OUT.mkdir()
    observer_path=EV/'ACTUADOR_R02_AUX_R01/CORRECCION_Y_DOSSIER_N0_R02/observador_causal_retrospectivo_01.py'
    spec=importlib.util.spec_from_file_location('archived_exact_parser_N0',observer_path)
    observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    parent_path=ROOT/'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01/VIDA.deetsnap.gz'
    parent=observer.Snapshot(parent_path,verify_checksum=False)
    if parent.encoded_sha256!='771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8':raise ValueError('Common FULL differs')
    before={row['id']:row for row in parent.receipts};del parent
    rows=[];all_inputs={}
    index=read(BASE/'INDICE.json')
    for label,info in index['branches'].items():
        record=read(BASE/info['record']);inputs={};sources=[];work=[]
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if relative not in info['primaries']:continue
            path=BASE/info['primaries'][relative];encoded=path.read_bytes()
            if hashlib.sha256(encoded).hexdigest()!=operation['result_sha256']:raise ValueError('Committed primary changed')
            primary=json.loads(encoded);sources.append({'file':info['primaries'][relative],'sha256':operation['result_sha256']})
            for item in walk(primary['result']):
                if'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
                    identifier=int(item['id']);receipt=item['receipt']
                    if int(receipt['id'])!=identifier:raise ValueError('Outer and receipt Native ids differ')
                    if identifier in inputs and receipt['status']in('queued','scheduled'):continue
                    channel=item.get('channel',item.get('port'))
                    if identifier in inputs and inputs[identifier]['channel']!=channel:raise ValueError('One Native id names different channels')
                    inputs[identifier]={'id':identifier,'channel':channel,'tick':item['tick'],
                        'value':item.get('payload',item.get('value')),'receipt':receipt,
                        'representation':'channel'if'channel'in item else'port'}
            for block in primary['result'].get('rows',[]):
                for row in block.get('rows',[]):
                    if isinstance(row,dict)and'selection'in row:work.append(row)
        path=ROOT/'sistema'/record['snapshot'];snapshot=observer.Snapshot(path,verify_checksum=False)
        if snapshot.encoded_sha256!=record['snapshot_sha256']:raise ValueError('Archived old FULL differs')
        after={row['id']:row for row in snapshot.receipts};new={key:value for key,value in after.items()if key not in before}
        missing=sorted(set(new)-set(inputs));extra=sorted(set(inputs)-set(new))
        changed=[key for key,value in before.items()if after.get(key)!=value]
        if missing or extra or changed:raise ValueError('FULL/primary receipt coverage differs: '+label+' / '+repr((missing[:6],extra[:6],changed[:6])))
        statuses=Counter(row['receipt']['status']for row in inputs.values())
        row={'branch':label,'life':info['life'],'tick':snapshot.tick,'old_FULL':path.relative_to(ROOT).as_posix(),
            'snapshot_sha256':snapshot.encoded_sha256,'completed_work_opportunities':len(work),
            'all_unique_native_inputs':len(inputs),'statuses_exact':dict(statuses),
            'applied':statuses['applied'],'rejected':sum(v for k,v in statuses.items()if k.startswith('rejected')),
            'schema_forms':dict(Counter(row['representation']for row in inputs.values())),
            'new_FULL_receipt_count':len(new),'new_FULL_status_enum':dict(Counter(str(r['status'])for r in new.values())),
            'parent_receipts_unchanged':not changed,'Native_pending_at_committed_FULL':snapshot.pending,
            'sources':sources,'exact_new_FULL_receipts':[new[key]for key in sorted(new)]}
        rows.append(row);all_inputs[label]=inputs;del snapshot
    # The earlier A/C six-op port-only comparison can be widened without Native.
    first6={}
    for label in('A','C'):
        inputs={}
        for block in('2_goal0_first4','3_goal0_next2'):
            path=BASE/label/'PRIMARIOS'/('apd04_attention_'+label+'_'+block+'.json')
            primary=read(path)
            for item in walk(primary['result']['rows'][0]):
                if'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
                    identifier=int(item['id'])
                    if identifier in inputs and item['receipt']['status']in('queued','scheduled'):continue
                    inputs[identifier]={'channel':item.get('channel',item.get('port')),'tick':item['tick'],
                        'value':item.get('payload',item.get('value')),'status':item['receipt']['status']}
        first6[label]=inputs
    differences=[]
    for identifier in sorted(first6['A'].keys()|first6['C'].keys()):
        a,c=first6['A'].get(identifier),first6['C'].get(identifier)
        if a is None or c is None or any(a[key]!=c[key]for key in('channel','tick','value')):
            differences.append({'id':identifier,'A':a,'C':c})
    value={'schema':'APD04.ABC.all_native_receipts.port_channel.N0.r02','branches':rows,
        'old_port_only_counts':{'A':204,'B':186,'C':102},
        'first6_AC_all_schema_input_counts':{key:len(rows)for key,rows in first6.items()},
        'first6_AC_all_schema_spec_differences':differences,
        'new_native_ticks':0,'scope':'Only old archived committed cuts and exact primaries; interrupted futures remain unexamined/uncleared. '
        'FULL encoded SHA checked against archived record, FNV not repeated. Native receipt totals, not query-count or independent-learner claims. '
        'Port-only R01/R02 results preserved as partial schema coverage, not silently rewritten.'}
    with(OUT/'RECALCULO_ABC_Y_CONCILIACION_FULL_R02.json').open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    shutil.copy2(Path(__file__),OUT/Path(__file__).name);shutil.copy2(observer_path,OUT/observer_path.name)
    print(json.dumps({'branches':[{key:row[key]for key in('branch','completed_work_opportunities','all_unique_native_inputs','applied','rejected','schema_forms')}for row in rows],
        'first6_AC_all_schema_input_counts':value['first6_AC_all_schema_input_counts'],'first6_AC_spec_differences':len(differences),'new_native_ticks':0},indent=2))


if __name__=='__main__':main()
