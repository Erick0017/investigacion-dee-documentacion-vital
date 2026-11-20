"""Lossless compact Full proof export, ONLY after its actual run. No Native.

Also --recalculate validates every member and recalculates the journal from
the exported exact bytes using the pure stdlib calculator. No historical path
is imported; original locations/hashes are audit metadata, not actor memory.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')


def load(path):
    spec=importlib.util.spec_from_file_location('full_compact_pure_archive_recalculation',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def recalculate(folder):
    manifest=json.loads((folder/'MANIFIESTO.json').read_bytes())
    for item in manifest['members']:
        path=folder/item['path']
        if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:
            raise ValueError('Portable member differs: '+item['path'])
    module=load(folder/'CODIGO/recalcular_full_apd04_sesiones_n0_r01.py')
    events=[json.loads(line) for line in gzip.decompress((folder/'PRIMARIOS/SESIONES_ORIGINALES.jsonl.gz').read_bytes()).splitlines() if line.strip()]
    result=module.recalculate(events,json.loads((folder/'CRITERIOS/CRITERIO_NUMERICO_FULL_ANTES_DE_EJECUCION_R01.json').read_bytes()),json.loads((folder/'CRITERIOS/PROTOCOLO_FULL_APD04_CERRADO_R02.json').read_bytes()))
    golden=json.loads((folder/'RECALCULO_COMPLEMENTARIO.json').read_bytes())
    golden.pop('sources',None)
    if result!=golden:
        raise ValueError('Portable primary recalculation differs from archived result')
    receipt_tool=load(folder/'CODIGO/conciliar_native_ids_full_n0_r01.py')
    rows,ids,duplicates,starts=receipt_tool.requests_from_journal(events,module.walk)
    ledger=json.loads(gzip.decompress((folder/'RESULTADOS/FULL_CONCILIACION_NATIVE_IDS_N0_R01.json.gz').read_bytes()))
    if set(ids)!=set(ledger['new_native_receipts']) or len(ids)!=ledger['new_native_union'] or len(rows)!=ledger['UI_requests'] or starts!=ledger['owner_starts']:
        raise ValueError('Portable new Native primary union differs from exported exact full-snapshot delta')
    for key,value in ledger['new_native_receipts'].items():
        primary=ids[key]['receipt']
        if primary['channels']!=value['channels'] or primary['requested_tick']!=value['requested_tick'] or primary.get('effective_tick')!=value['effective_tick']:
            raise ValueError('Portable new Native receipt context differs')
    return {'native_ticks':0,'manifest_members_verified':len(manifest['members']),
            'journal_events':len(events),'golden_equal':True,
            'Native_NEW_ID_union_equals_exported_snapshot_delta':True,'Native_NEW_ID_count':len(ids),
            'numeric_outcomes':{p['criterion']['probe']:p['outcome'] for p in result['numeric']},
            'scope':'Archive arithmetic only, NOT Native reproduction or an autonomous capability.'}


def export(root,extraction,external,out):
    root=root.resolve();extraction=extraction.resolve();external=external.resolve();out=out.resolve()
    if out.exists():raise FileExistsError('Preserve existing dossier: '+str(out))
    package=extraction/'cognitive sistem'
    actual=package/'trabajo_personal/resultados/APD04_FULL_PERSONAL_R01'
    sessions=actual/'SESIONES_ORIGINALES.jsonl'
    if not external.is_file() or not sessions.is_file():
        raise FileNotFoundError('Actual external report and exact original journal required; no fabricated Full evidence')
    # Successful and adverse proof executions are both exportable. No PASS gate.
    lab=root/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/distribucion'
    out.mkdir(parents=True)
    copied=[];omitted=[]
    def copy(source,target,compress=False):
        if not source.is_file():
            omitted.append({'local':str(source),'reason':'Not produced by this actual execution; not replaced.'});return
        value=source.read_bytes();dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True)
        if compress:value=gzip.compress(value,mtime=0)
        with dest.open('xb') as f:f.write(value)
        copied.append({'package':target,'original_local':str(source),'original_sha256':sha(source),'original_bytes':source.stat().st_size,'lossless_gzip':compress})
    copy(sessions,'PRIMARIOS/SESIONES_ORIGINALES.jsonl.gz',True)
    copy(external,'RESULTADOS/VERIFICACION_FINAL_EXTERNA.json.gz',True)
    ledger=root/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/FULL_CONCILIACION_NATIVE_IDS_N0_R01.json'
    copy(ledger,'RESULTADOS/'+ledger.name+'.gz',True)
    for path in sorted(actual.iterdir()):
        if path.is_file() and path.suffix=='.json' and (path.name.startswith(('FASE_','RESULTADOS_')) or path.name.endswith('_EJECUCION.json')):
            copy(path,'RESULTADOS/'+path.name+'.gz',True)
    for parent in (actual,extraction):
        for path in sorted(parent.glob('*STDERR.txt')):
            if path.stat().st_size:
                copy(path,'INCIDENCIAS/'+('OUTER_' if parent==extraction else '')+path.name+'.gz',True)
            else:omitted.append({'local':str(path),'bytes':0,'sha256':sha(path),'reason':'Empty original stderr, no adverse text omitted.'})
    for name in ('recalcular_full_apd04_sesiones_n0_r01.py','probar_full_apd04_entrada_r01.py','verificar_full_apd04_exacto_r01.py','conciliar_native_ids_full_n0_r01.py'):
        # Executed helper comes from the extracted exact ZIP, never replacement S.
        source=package/'actualizaciones'/name if name=='probar_full_apd04_entrada_r01.py' else lab/name
        copy(source,'CODIGO/'+name)
    copy(Path(__file__).resolve(),'CODIGO/'+Path(__file__).name)
    for name in ('acciones_nativas_apd04.py','lexico_compartido_apd04.py','mente_unificada_01.py','percepcion_cruda_fi01.py','observador_causal_retrospectivo_01.py'):
        copy(package/'sistema/capacidades'/name,'CODIGO/CAPACIDADES_EJECUTADAS/'+name)
    for name in ('CRITERIO_NUMERICO_FULL_ANTES_DE_EJECUCION_R01.json','PROTOCOLO_FULL_APD04_CERRADO_R02.json'):
        copy(lab/name,'CRITERIOS/'+name)
    module=load(lab/'recalcular_full_apd04_sesiones_n0_r01.py')
    events=[json.loads(line) for line in sessions.read_bytes().splitlines() if line.strip()]
    criteria=json.loads((lab/'CRITERIO_NUMERICO_FULL_ANTES_DE_EJECUCION_R01.json').read_bytes())
    protocol=json.loads((lab/'PROTOCOLO_FULL_APD04_CERRADO_R02.json').read_bytes())
    result=module.recalculate(events,criteria,protocol)
    emit(out/'RECALCULO_COMPLEMENTARIO.json',result)
    requests={}
    for i,event in enumerate(events):
        if event.get('event') in ('literal_material_submission','literal_material_result','same_id_read_only_result'):
            entry=requests.setdefault(event['id'],{'id':event['id'],'journal_lines':[],'puts':0,'polls':0})
            entry['journal_lines'].append(i+1)
            if event['event']=='literal_material_submission':entry['puts']+=1
            if event['event']=='same_id_read_only_result':entry['polls']+=1
            if 'result' in event:
                row=event['result'].get('request') or event['result']
                entry['latest_status']=row.get('status')
    emit(out/'INDICE_SOLICITUDES.json',{'all_primary_material_requests_positive_and_negative':list(requests.values()),
          'exact_journal_events':len(events),'same_ID_polling_is_NOT_new_acquisition':True})
    actual_report=json.loads((actual/'RESULTADOS_FULL_APD04.json').read_bytes())
    final=actual_report['continuity']['final_record']
    snapshot=(package/'sistema'/final['snapshot']).resolve()
    emit(out/'CONTINUIDAD_Y_ALCANCE.json',{'life_id':final['life_id'],'world_id':final['world_id'],
        'parent':final['parent'],'final_physical':final['physical'],'snapshot_local':str(snapshot),
        'snapshot_sha256':sha(snapshot),'snapshot_bytes':snapshot.stat().st_size,
        'complete_operational_state_local':[str(package/'trabajo_personal/estado/vidas'/final['life_id']),str(package/'trabajo_personal/estado/servicios_persistentes'/final['life_id']),str(package/'trabajo_personal/estado/servicios_locales'/final['life_id']),str(package/'trabajo_personal/entrada_sencilla/vidas'/final['life_id'])],
        'protected_selected_seed_unchanged_and_NOT_replaced_by_this_descendant':True,
        'scope':'Operational proof in a new extraction on the SAME computer, not independent hardware. A new explicitly imported full-state descendant; its one lexical revision is not written back to the seed.',
        'baseline_final_denominator':'16 inherited finite forms +6 MA context accesses +2 APD04 finite forms; not24 independent cognitive capacities or24Spanish meanings.',
        'nominal_numeric_denominator':'Three separate raw numerical probes:43,9/3,47; no learned-control or arithmetic-generalization inference.',
        'contrary_cases_policy':'Every actual Full submission/result is included in the lossless journal, without outcome filtering. This proof produced no wrong numerical case; adverse campaign worlds remain in the other campaign evidence, not fabricated here.'})
    emit(out/'INDICE_FUENTES_Y_OMISIONES.json',{'copied_exact':copied,'omitted_specific':omitted,
        'kept_local_not_in_this_analysis':['Exact complete collaborator ZIP (identified by external report)',
         'Extracted embedded interpreter and engine/WHL','Complete snapshots, SQLite/outboxes and UI life states under extracted trabajo_personal',
         'Verbose stdout duplicates of material primary results already conserved in the exact journal'],
        'not_a_continuable_state_backup':True,'no_failure_filtered_by_outcome':True,
        'journal_contains_original_submission_payloads_and_original_native_result_payloads':True,
        'recalculate_cli':'python CODIGO/exportar_full_exacto_compacto_n0_r01.py --recalculate .',
        'scope':'Exact ZIP execution on another directory of the same computer; not independent hardware.'})
    members=[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]
    emit(out/'MANIFIESTO.json',{'schema':'APD04.exactFull.compact.primary_manifest.N0.R01','members':members,'no_self_hash':True})
    test=recalculate(out)
    # Printed verification is outside manifest, so no self-referential member.
    print(json.dumps({'output':str(out),'manifest_sha256':sha(out/'MANIFIESTO.json'),'verification':test},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--recalculate',type=Path);p.add_argument('--root',type=Path)
    p.add_argument('--extraction',type=Path);p.add_argument('--external',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.recalculate:print(json.dumps(recalculate(a.recalculate.resolve()),ensure_ascii=False))
    elif all((a.root,a.extraction,a.external,a.out)):export(a.root,a.extraction,a.external,a.out)
    else:p.error('Use --recalculate, or all --root --extraction --external --out after actual Full proof')
