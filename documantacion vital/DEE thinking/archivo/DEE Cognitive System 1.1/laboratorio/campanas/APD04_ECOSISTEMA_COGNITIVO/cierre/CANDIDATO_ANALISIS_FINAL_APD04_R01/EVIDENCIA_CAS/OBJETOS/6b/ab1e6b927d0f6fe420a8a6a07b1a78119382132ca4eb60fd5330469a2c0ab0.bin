"""Reconcile NEW Native receipt IDs in twelve Full UI requests. No engine.

Full snapshots are read by the already shipped pure parser, no Runtime/ticks.
Every port/channel alias is accepted; repeated JSON/poll entries dedup by ID.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))


def requests_from_journal(events,walker):
    phases=['BASELINE','DOCENCIA_NUEVA','PENDIENTE','REAPERTURA_MISMO_ID']
    phase_index=-1;rows={};global_ids={};duplicates=[]
    for event in events:
        if event.get('event')=='owned_start_paused':phase_index+=1
        if event.get('event')=='literal_material_submission':
            key=event['id']
            if key in rows:raise ValueError('Duplicate material put; not new Native acquisition')
            rows[key]={'id':key,'phase':phases[phase_index] if 0<=phase_index<len(phases) else 'UNKNOWN',
                       'situations':event['payload']['situaciones'],'native':{}}
        if event.get('event') not in ('literal_material_result','same_id_read_only_result'):continue
        key=event['id']
        if key not in rows:raise ValueError('Unsubmitted UI result ID')
        for locator,item in walker(event.get('result',{})):
            if not isinstance(item,dict) or 'id' not in item or not isinstance(item.get('receipt'),dict) or not ('port' in item or 'channel' in item):continue
            native_id=str(item['id']);receipt=dict(item['receipt'])
            row={'id':native_id,'interface':item.get('port',item.get('channel')),'receipt':receipt}
            prior=rows[key]['native'].get(native_id)
            if prior and prior!=row:raise ValueError('Same Native ID has incompatible primary receipts')
            if prior:duplicates.append({'UI_ID':key,'Native_ID':native_id,'locator':locator})
            rows[key]['native'][native_id]=row
            if native_id in global_ids and global_ids[native_id]['UI_ID']!=key:
                raise ValueError('Same Native ID attributed to two material UI requests')
            global_ids[native_id]={'UI_ID':key,**row}
    return rows,global_ids,duplicates,phase_index+1


def run(extraction,root,out):
    package=extraction/'cognitive sistem';result=package/'trabajo_personal/resultados/APD04_FULL_PERSONAL_R01'
    journal=result/'SESIONES_ORIGINALES.jsonl'
    events=[json.loads(line) for line in journal.read_bytes().splitlines() if line.strip()]
    mod=load(root/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/distribucion/recalcular_full_apd04_sesiones_n0_r01.py','pure_full_calculation')
    rows,ids,dups,starts=requests_from_journal(events,mod.walk)
    if starts!=4 or len(rows)!=12:raise ValueError('Actual four-owner/twelve-request sequence differs; no assumed denominator')
    catalogue=json.loads((package/'entes/CATALOGO.json').read_bytes())
    source=next(x for x in catalogue['cuts'] if x['alias']=='APD04_ECOSISTEMA')
    final=json.loads((result/'RESULTADOS_FULL_APD04.json').read_bytes())['continuity']['final_record']
    before=package/source['snapshot'];after=(package/'sistema'/final['snapshot']).resolve()
    if sha(before)!=source['snapshot_sha256'] or sha(after)!=final['snapshot_sha256']:raise ValueError('Exact snapshot hash differs')
    parser=load(package/'sistema/capacidades/observador_causal_retrospectivo_01.py','pure_full_snapshot_parser')
    b=parser.Snapshot(before,verify_checksum=False);a=parser.Snapshot(after,verify_checksum=False)
    bp={str(x['id']):x for x in b.receipts};ap={str(x['id']):x for x in a.receipts}
    inherited_equal=all(ap.get(key)==value for key,value in bp.items())
    delta={key:value for key,value in ap.items() if key not in bp}
    if not inherited_equal or set(delta)!=set(ids):raise ValueError('New Native delta and unique twelve-request union differ')
    phase_counts=Counter();status=Counter();breakdown=[]
    for row in rows.values():
        primary_status=Counter(x['receipt']['status'] for x in row['native'].values())
        phase_counts[row['phase']]+=len(row['native']);status.update(primary_status)
        breakdown.append({'UI_ID':row['id'],'phase':row['phase'],'situations':row['situations'],
                          'native_unique_requested':len(row['native']),'statuses':dict(primary_status),
                          'native_IDs':sorted(map(int,row['native']))})
    for key in delta:
        receipt=ids[key]['receipt'];native=delta[key]
        if receipt['requested_tick']!=native['requested_tick'] or receipt.get('effective_tick')!=native['effective_tick'] or receipt.get('channels')!=native['channels']:
            raise ValueError('New Native and primary exact receipt context differ')
    report={'schema':'APD04.Full.NEW_native_ID_reconciliation.N0.R01','Native_ticks_executed':0,
        'source_snapshot':{'file':str(before),'sha256':sha(before),'tick':b.tick,'receipts':len(bp)},
        'final_snapshot':{'file':str(after),'sha256':sha(after),'tick':a.tick,'receipts':len(ap)},
        'UI_requests':len(rows),'owner_starts':starts,'new_native_union':len(ids),'native_delta_count':len(delta),
        'native_delta_ID_set_equals_UI_primary_union':True,'inherited_receipts_unchanged':True,
        'old_inherited_IDs_NOT_counted':len(bp),'phase_counts':dict(phase_counts),'statuses_from_primary':dict(status),
        'native_serialized_statuses':dict(Counter(str(x['status']) for x in delta.values())),
        'per_UI_request':breakdown,'new_native_receipts':delta,'deduplicated_JSON_poll_occurrences':len(dups),
        'exact_journal_sha256':sha(journal),'parser_source_sha256':sha(package/'sistema/capacidades/observador_causal_retrospectivo_01.py'),
        'scope':'691 (if actually obtained) is a union of NEW Native receipt IDs, not inherited history or independent learning trials.',
        'parser_scope':'Exact encoded SHA and gzip CRC verified; optional expensive internal FNV not recomputed in this N0 parse.',
        'portable_limit':'Full source/final snapshots stay local. Exported delta can be compared with primary union; full inherited equality needs those exact local snapshots.'}
    with out.open('x',encoding='utf8',newline='\n') as f:json.dump(report,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('UI_requests','new_native_union','native_delta_count','old_inherited_IDs_NOT_counted','phase_counts','statuses_from_primary','inherited_receipts_unchanged')},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--extraction',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.extraction.resolve(),a.root.resolve(),a.out.resolve())
