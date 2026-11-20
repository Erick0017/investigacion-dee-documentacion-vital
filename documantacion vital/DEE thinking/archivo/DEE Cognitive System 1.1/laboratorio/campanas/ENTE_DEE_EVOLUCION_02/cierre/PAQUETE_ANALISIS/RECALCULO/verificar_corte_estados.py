"""Read complete official snapshots and committed records, never advance/save them."""
from pathlib import Path
import argparse,collections,gzip,hashlib,json,sys

def read(p):
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf8')as f:return json.load(f)
    return json.loads(p.read_bytes())
def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for c in iter(lambda:f.read(1048576),b''):h.update(c)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--primarios',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.exists():raise FileExistsError('Prior state evidence protected')
    sys.path.insert(0,str(a.sistema))
    from app.native_tools import physical
    from dee_thinking.persistence import load_world_snapshot
    from dee_thinking.consolidated import exact_receipt
    initial=read(a.primarios/'00_ESTADO_PROTEGIDO_INICIAL.json');issues=[];protected=[]
    active=a.sistema/'estado/ACTIVO.json'
    active_ok=digest(active)==initial['active_sha256']
    if not active_ok:issues.append('Protected active pointer changed')
    for life,old in initial['protected'].items():
        record=a.sistema/'estado/vidas'/life/'VIDA.json';current=read(record);snapshot=a.sistema/current['snapshot']
        row={'life':life,'record_sha256':digest(record),'record_bytes_unchanged':digest(record)==old['record_sha256'],
            'tick':current['physical']['tick'],'N':current['physical']['N'],'profile':current['profile'],
            'snapshot':current['snapshot'],'snapshot_sha256':digest(snapshot),
            'snapshot_matches_original_pointer':current['snapshot_sha256']==old['record_content']['snapshot_sha256']and digest(snapshot)==current['snapshot_sha256']}
        if not row['record_bytes_unchanged']or not row['snapshot_matches_original_pointer']:issues.append('Protected identity changed: '+life)
        protected.append(row)
    lives=[]
    for life,save_case,state_case in [('EO02_MAIN','39_GUARDAR_MAIN.json.gz','40_ESTADO_MAIN_OTRO_PROCESO.json.gz'),('EO02_SENSORIAL_R10_T0','41_GUARDAR_R10.json.gz','43_ESTADO_R10_TRAS_COMMIT.json.gz')]:
        directory=a.sistema/'estado/vidas'/life;record_path=directory/'VIDA.json';record=read(record_path);snapshot=a.sistema/record['snapshot']
        record_hash_before=digest(record_path);snapshot_hash_before=digest(snapshot)
        world,proof=load_world_snapshot(snapshot);before_tick=int(world.runtime.current_tick);actual=physical(world,occupation=True)
        metadata=dict(world.runtime.snapshot_metadata_entries)
        receipts=[exact_receipt(x)for x in world.runtime.receipts];statuses=dict(collections.Counter(x['status']for x in receipts))
        pending=[x for x in receipts if x['status']in('pending','accepted','queued')]
        journal_path=directory/'HISTORIA.jsonl';journal=[json.loads(x)for x in journal_path.read_text(encoding='utf8').splitlines()if x.strip()]
        journal_balanced=bool(journal and journal[-1]['snapshot_sha256']==record['snapshot_sha256']and journal[-1]['tick']==actual['tick'])
        save=read(a.primarios/save_case);state=read(a.primarios/state_case)
        saved_physical=save['result']['physical'];saved_identity=save['result']['INSTRUMENTO']
        state_result=state['result'];state_witness=state_result['witness']
        checks={'encoded_hash_matches_pointer':snapshot_hash_before==record['snapshot_sha256'],
            'physical_matches_record':all(actual[k]==record['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),
            'physical_matches_saved_process':all(actual[k]==saved_physical[k]for k in('N','tick','RAW_sha256','clocks_sha256')),
            'saved_pointer_matches_current':saved_identity['snapshot_sha256']==record['snapshot_sha256'],
            'separate_process_loaded_same_tick':state['returncode']==0 and state_witness['tick']==actual['tick'],
            'journal_balanced':journal_balanced,'no_pending_receipts':not pending,
            'no_interrupted_future_marker':not(directory/'FUTURO_INTERRUMPIDO.json').exists(),
            'passive_load_no_tick_advance':before_tick==int(world.runtime.current_tick),
            'original_record_not_written':record_hash_before==digest(record_path),
            'original_snapshot_not_written':snapshot_hash_before==digest(snapshot)}
        if not all(checks.values()):issues.append({'life':life,'failed_checks':[k for k,v in checks.items()if not v]})
        service_key='DEE.Cognitive.System.1.1.EO02.service.v1'if life=='EO02_MAIN'else'DEE.Cognitive.System.1.1.EO02.sensorial.service.v1'
        service_entries={k:json.loads(v)for k,v in metadata.items()if 'EO02' in k}
        lives.append({'life':life,'profile':record['profile'],'branch':record['branch'],'parent':record.get('parent'),
            'record_sha256':record_hash_before,'snapshot':record['snapshot'],'snapshot_sha256':snapshot_hash_before,'storage_proof':proof,
            'physical':actual,'full_snapshot_loaded':True,'interfaces':len(world.interfaces),'protocols':len(world.protocols),
            'receipts_total':len(receipts),'receipt_statuses':statuses,'pending_receipts':pending,
            'metadata_entries':len(metadata),'metadata_sha256':hashlib.sha256(json.dumps(metadata,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'EO02_operational_metadata':service_entries,
            'last_journal_entry':journal[-1]if journal else None,'journal_entries':len(journal),'journal_sha256':digest(journal_path),
            'witness':state_witness,'checks':checks,'cross_process_primaries':[save_case,state_case],
            'pending_scope':'All official restored runtime receipts are terminal; complete native snapshot also includes interfaces/protocols/queues. No incomplete arrays were used.'})
    failed=read(a.primarios/'42_ESTADO_R10_OTRO_PROCESO.json.gz')
    preflight=read(a.primarios/'44_PREFLIGHT_R00.json')
    result={'schema':'EO02.final_state_identity_passive.v1','new_native_ticks':0,'new_worker_executions':0,
        'active':read(active),'active_pointer_unchanged':active_ok,'protected':protected,'lives':lives,
        'preserved_instrumental_negatives':[{'primary':'42_ESTADO_R10_OTRO_PROCESO.json.gz','sha256':digest(a.primarios/'42_ESTADO_R10_OTRO_PROCESO.json.gz'),'returncode':failed['returncode'],'stderr':failed['stderr'],'interpretation':'Concurrent read during commit was refused; later successful state43 retained. Not a cognitive failure or silent rollback.'},
            {'primary':'44_PREFLIGHT_R00.json','sha256':digest(a.primarios/'44_PREFLIGHT_R00.json'),'record':preflight}],
        'issues':issues,'source_sha256':digest(Path(__file__))}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':issues,'protected':[(q['life'],q['tick'])for q in protected],'lives':[(q['life'],q['physical']['tick'],q['snapshot_sha256'],q['pending_receipts'])for q in lives],'output':str(a.salida),'sha256':digest(a.salida)},ensure_ascii=False))
    return bool(issues)
if __name__=='__main__':raise SystemExit(main())
