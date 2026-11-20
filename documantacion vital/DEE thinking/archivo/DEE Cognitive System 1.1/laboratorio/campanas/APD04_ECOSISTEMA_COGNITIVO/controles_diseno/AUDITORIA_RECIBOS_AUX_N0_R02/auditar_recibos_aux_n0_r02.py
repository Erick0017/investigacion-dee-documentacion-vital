"""Read-only complete Native receipt coverage audit. No engine, SQLite or ticks."""
from pathlib import Path
import collections, csv, gzip, hashlib, importlib.util, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXPORT = HERE.parent / 'EVIDENCIA_CONTROLES_CERRADOS_R01'
PARSER = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'

def sha(b): return hashlib.sha256(b).hexdigest()
def load(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
def walk(v, loc='$'):
    if isinstance(v, dict):
        yield loc, v
        for k, x in v.items():
            if isinstance(x, str) and k in ('result', 'result_json'):
                try: x = json.loads(x)
                except json.JSONDecodeError: pass
            yield from walk(x, loc+'.'+k)
    elif isinstance(v, list):
        for j, x in enumerate(v): yield from walk(x, loc+'['+str(j)+']')
def numeric_id(v):
    if isinstance(v, bool): return None
    if isinstance(v, int): return v
    if isinstance(v, str) and v.isdecimal(): return int(v)
    return None
def dump(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')

def main():
    index = load(EXPORT/'INDICE.json'); recalc = load(EXPORT/'RECALCULO.json')
    spec = importlib.util.spec_from_file_location('native_snapshot_read_only', PARSER)
    observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
    prefix_path = ROOT/'sistema/estado/fuentes_emparejadas/APD04_LEX_P0_R02_T605516_R01/VIDA.deetsnap.gz'
    prefix = observer.Snapshot(prefix_path, verify_checksum=False)
    assert prefix.encoded_sha256 == 'f8081af0e79d9091009b4a0f14e16d51dd00eeca561666735f6727265a1c30d0'
    initial = {r['id']: r for r in prefix.receipts}
    branches=[]; rows=[]; evidence=[]
    for branch in index['branches']:
        label=branch['label']; p=Path(branch['paired']['directory'])/'VIDA.deetsnap.gz'
        final=observer.Snapshot(p, verify_checksum=False)
        assert final.encoded_sha256 == branch['snapshot_sha256']
        after={r['id']:r for r in final.receipts}
        new={i:r for i,r in after.items() if i not in initial}
        changed_old={i:{'before':initial[i],'after':r}for i,r in after.items() if i in initial and r != initial[i]}
        export_any={}; legacy={}; parent_markers=collections.Counter(); primary_sources=[]
        for item in index['primaries']:
            if item['branch'] != label: continue
            ep=EXPORT/item['export']; z=ep.read_bytes(); b=gzip.decompress(z)
            assert sha(z)==item['export_sha256'] and sha(b)==item['original_sha256']
            primary_sources.append({'file':item['export'],'original_sha256':sha(b),'gzip_sha256':sha(z)})
            for loc,n in walk(json.loads(b)):
                if isinstance(n.get('receipt'),dict):
                    ri=numeric_id(n['receipt'].get('id'))
                    if ri is not None:
                        key='port' if 'port'in n else 'channel' if 'channel'in n else 'neither'
                        parent_markers[key]+=1
                ri=numeric_id(n.get('id'))
                if ri is not None and 'status'in n:
                    export_any.setdefault(ri,[]).append({'status':n['status'],'file':item['export'],'locator':loc,'receipt':n})
        for event in recalc['events']:
            if event['branch']!=label:continue
            for q in event['metrics']['receipts']:
                ri=numeric_id(q['receipt'].get('id'))
                if ri is not None:legacy.setdefault(ri,[]).append(q['receipt'])
        missing_any=sorted(set(new)-set(export_any)); missing_legacy=sorted(set(new)-set(legacy))
        extra_any=sorted(set(export_any)-set(after)); prior_referenced=sorted(set(export_any)&set(initial))
        states=collections.Counter(str(r['status'])for r in new.values())
        api_states=collections.Counter()
        status_mapping=collections.defaultdict(set)
        for i,r in new.items():
            terminal=[q for q in export_any.get(i,[])if q['status']not in('scheduled','pending','admitted')]
            api = terminal[-1]['status']if terminal else None
            api_states[str(api)]+=1
            if api is not None: status_mapping[str(r['status'])].add(str(api))
            rows.append({'branch':label,'life':branch['life'],'native_id':i,'native_kind':r['kind'],'native_status':r['status'],
                         'requested_tick':r['requested_tick'],'effective_tick':r['effective_tick'],'channels':'|'.join(r['channels']),
                         'reason':r['reason'],'legacy_scan_present':i in legacy,'any_export_present':i in export_any,
                         'api_terminal_status':api,'api_occurrence_count':len(export_any.get(i,[]))})
        item={'label':label,'life':branch['life'],'prefix_tick':prefix.tick,'final_tick':final.tick,'prefix_receipts':len(initial),
              'full_final_receipts':len(after),'new_receipt_ids':len(new),'new_native_status_counts':dict(states),
              'new_api_terminal_status_counts':dict(api_states),'native_to_API_status_mapping':{k:sorted(v)for k,v in status_mapping.items()},
              'legacy_export_unique_ids':len(legacy),'any_export_unique_ids':len(export_any),'old_summed_event_statuses':next(b['receipt_statuses']for b in recalc['branches']if b['label']==label),
              'missing_from_any_export':missing_any,'missing_from_legacy_scan':missing_legacy,'export_IDs_absent_full_final':extra_any,
              'referenced_prefix_ids':prior_referenced,'changed_prefix_receipts':changed_old,'prefix_IDs_absent_final':sorted(set(initial)-set(after)),
              'receipt_wrapper_parent_markers_occurrences_not_unique':dict(parent_markers),'final_pending':final.pending,
              'final_snapshot':str(p),'final_encoded_sha256':final.encoded_sha256,'final_decoded_sha256':final.decoded_sha256,
              'full_delta_receipts':list(new.values()),'primary_sources':primary_sources}
        branches.append(item)
        evidence.append({'branch':label,'receipts_by_native_ID':{str(i):export_any.get(i,[])for i in sorted(new)}})
    assert not any(k.startswith('dee_thinking')for k in sys.modules)
    result={'schema':'APD04.full_receipt_coverage.N0.R02','new_native_ticks':0,
            'prefix':{'path':str(prefix_path),'tick':prefix.tick,'encoded_sha256':prefix.encoded_sha256,'receipts':len(initial),'pending':prefix.pending},
            'branches':branches,'summary':{'new_receipt_ids':sum(b['new_receipt_ids']for b in branches),
                 'missing_any':sum(len(b['missing_from_any_export'])for b in branches),'missing_legacy':sum(len(b['missing_from_legacy_scan'])for b in branches),
                 'new_API_terminal_status_counts':dict(sum((collections.Counter(b['new_api_terminal_status_counts'])for b in branches),collections.Counter()))},
            'method':{'no_SQLite_opened':True,'no_native_import':True,'snapshot_checksum_FNV_recalculated':False,
                 'identity_verification':'Exact gzip SHA256 equals sealed branch identity; parser reads complete snapshot format with full receipts. FNV skipped explicitly to avoid costly repetition.',
                 'no_source_modifications':True,'no_reexecutions':True,'scope':'Eight dependent AUX prefixes, not independent learners; final complete Native receipt table minus exact shared prefix IDs, preserving changed old statuses separately. Export and full native counts deduplicated by per-life Native ID; polling copies are not new inputs.'},
            'sources':{'index_sha256':sha((EXPORT/'INDICE.json').read_bytes()),'recalc_R01_sha256':sha((EXPORT/'RECALCULO.json').read_bytes()),
                       'read_only_parser_sha256':sha(PARSER.read_bytes()),'this_code_sha256':sha(Path(__file__).read_bytes())}}
    dump(HERE/'AUDITORIA_RECIBOS.json',result)
    compressed=gzip.compress(json.dumps(evidence,ensure_ascii=False,separators=(',',':')).encode('utf8'),compresslevel=9,mtime=0)
    with(HERE/'LOCALIZADORES_Y_RECIBOS_EXPORTADOS.json.gz').open('xb')as f:f.write(compressed)
    with(HERE/'RECIBOS_NUEVOS_POR_ID.csv').open('x',encoding='utf-8-sig',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({'summary':result['summary'],'branches':[{k:b[k]for k in('label','new_receipt_ids','new_api_terminal_status_counts','legacy_export_unique_ids','any_export_unique_ids','missing_from_any_export','missing_from_legacy_scan','receipt_wrapper_parent_markers_occurrences_not_unique')}for b in branches]},ensure_ascii=False))

if __name__=='__main__':main()
