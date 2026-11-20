"""Portable explicit execution ledger. Actual JSON pointers, no recursive census."""
from pathlib import Path
from collections import defaultdict
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from auditoria_documental_PI08 import checked, digest, interval_union, local, pointer, read_json


def recalculate(root, name='04_EVIDENCIAS/CONTROL/INDICE_LEDGER_PI08.json'):
    root=Path(root).resolve(strict=True);ib=local(root,name).read_bytes();index=read_json(ib)
    if index.get('schema')!='DEE.PI08.execution_ledger_index.v1':raise ValueError('Exact ledger index schema required')
    evidence={}
    for alias,entry in index['evidence'].items():
        _,data=checked(root,entry);evidence[alias]=read_json(data)
    seen=set();records=[];windows=defaultdict(list);errors=[]
    for row in index['executions']:
        execution=row['execution_id']
        if execution in seen:raise ValueError('One actual execution was indexed twice')
        seen.add(execution);values={}
        for field,binding in row['fields'].items():
            values[field]=pointer(evidence[binding['evidence']],binding['pointer'])
        before,after,ticks=(values[k]for k in('before_tick','after_tick','Native_ticks'))
        if any(type(v)is not int for v in(before,after,ticks))or not 0<=before<=after or ticks!=after-before:
            raise ValueError('Actual Native tick fields do not form one exact advancement window')
        if values['life_id']!=row['life_id']:raise ValueError('Actual source life disagrees with ledger scope')
        if type(values.get('scope_closed'))is not bool:raise ValueError('Actual closure boolean required')
        if not values['scope_closed']:
            errors.append({'execution_id':execution,'error':'Actual proof does not close this execution scope'})
        windows[row['world_key']].append((before,after))
        records.append({'execution_id':execution,'world_key':row['world_key'],'life_id':row['life_id'],
                        'modality':row['modality'],'actual_fields':values,
                        'scope':'Index labels identify provenance; measured fields come only from hash-checked JSON pointers.'})
    intervals={world:interval_union(rows)for world,rows in windows.items()}
    for world,value in intervals.items():
        if value['overlap_not_counted_twice']:
            errors.append({'world_key':world,'error':'Overlapping actual execution windows; do not double count or silently discard one'})
    total=sum(r['actual_fields']['Native_ticks']for r in records)
    limits=index.get('prospective_limits',{})
    if 'Native_ticks'in limits and total>limits['Native_ticks']:
        errors.append({'error':'Recorded Native budget exceeded','actual':total,'limit':limits['Native_ticks']})
    if 'worlds'in limits and len(windows)>limits['worlds']:
        errors.append({'error':'Declared world-scope budget exceeded','actual':len(windows),'limit':limits['worlds']})
    return {'schema':'DEE.PI08.portable_execution_ledger_recalculation.v1',
            'all_ledger_checks_passed':not errors,'index_sha256':digest(ib),'executions':records,
            'actual_included_Native_ticks':total,'declared_world_scopes':len(windows),
            'interval_coverage':intervals,'errors':errors,
            'coverage_is_complete_campaign':index.get('coverage_is_complete_campaign')is True,
            'coverage_declaration':index.get('coverage_declaration'),
            'new_Native_ticks':0,'DEE_imports':0,
            'scope':'Documentary sum of explicitly identified actual executions. Not a new Native run, '
                    'not individuals/concepts and not a full campaign ledger unless the final index explicitly closes its coverage. '
                    'Zero-tick imports/technical actions remain zero; absent fields are not inferred.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--raiz',type=Path,required=True)
    ap.add_argument('--indice',default='04_EVIDENCIAS/CONTROL/INDICE_LEDGER_PI08.json')
    ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    if a.salida.exists():raise FileExistsError(a.salida)
    value=recalculate(a.raiz,a.indice)
    with a.salida.open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'schema':value['schema'],'all_ledger_checks_passed':value['all_ledger_checks_passed'],
                      'actual_included_Native_ticks':value['actual_included_Native_ticks'],
                      'worlds':value['declared_world_scopes'],'new_Native_ticks':0},ensure_ascii=False))
    return 0 if value['all_ledger_checks_passed']else 2


if __name__=='__main__':raise SystemExit(main())
