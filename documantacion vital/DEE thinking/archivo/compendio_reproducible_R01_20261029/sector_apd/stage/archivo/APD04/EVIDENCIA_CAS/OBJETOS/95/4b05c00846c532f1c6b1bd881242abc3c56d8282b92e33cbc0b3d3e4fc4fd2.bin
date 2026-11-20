"""Correct receipt schema coverage; cross-check exact saved FULLs; causal dossier.

N0 only. Uses the previously exported old records, never current REAL VIDA.
Original R01 calculations remain byte-for-byte preserved.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
BASE=EV/'ACTUADOR_R02_AUX_R01/EVIDENCIA_PORTABLE_R01'
OUT=EV/'ACTUADOR_R02_AUX_R01/CORRECCION_Y_DOSSIER_N0_R02'
PAIR=ROOT/'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PARENT_SHA='771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def receipt_inputs(row):
    entries={}
    for item in walk(row):
        if'id'in item and('port'in item or'channel'in item)and isinstance(item.get('receipt'),dict):
            identifier=int(item['id'])
            if identifier in entries and item['receipt']['status']in('queued','scheduled'):continue
            entries[identifier]={'id':identifier,'channel':item.get('channel',item.get('port')),
                'tick':item['tick'],'value':item.get('payload',item.get('value')),'receipt':item['receipt']}
    return entries


def main():
    if OUT.exists():raise FileExistsError('Closed correction exists; no overwrite')
    OUT.mkdir();sources=[]
    def copy(source,relative):
        target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);before=sha(source);shutil.copy2(source,target)
        if sha(target)!=before or sha(source)!=before:raise ValueError('Bytes changed while extracting')
        sources.append({'source':source.relative_to(ROOT).as_posix(),'exported':relative,'sha256':before,'bytes':target.stat().st_size})
    # Explicit source-only correction, no altered response criteria or experiments.
    old=(BASE/'resumir_actuador_r02_n0_r01.py').read_text(encoding='utf8')
    changed=old.replace("raw=int(row['raw']);state=(raw>>60)&15;semantic=raw&0xffffffff", "raw=int(row['raw']);state=raw&0xffffffff;semantic=(raw>>60)&15")
    changed=changed.replace("if'id'in entry and'port'in entry and isinstance(entry.get('receipt'),dict):", "if'id'in entry and('port'in entry or'channel'in entry)and isinstance(entry.get('receipt'),dict):")
    changed=changed.replace("summary.N0.r01", "summary.N0.r02")
    if changed==old:raise ValueError('Expected explicit correction pattern missing')
    (OUT/'resumir_actuador_r02_n0_r02.py').write_text(changed,encoding='utf8',newline='\n')
    old_panel=(BASE/'recalcular_panel_actuador_r02_n0.py').read_text(encoding='utf8')
    new_panel=old_panel.replace("raw=int(observation['raw']);semantic=raw&0xffffffff;state=(raw>>60)&15", "raw=int(observation['raw']);state=raw&0xffffffff;semantic=(raw>>60)&15")
    if new_panel==old_panel:raise ValueError('Expected explicit RAW-field correction missing')
    (OUT/'recalcular_panel_actuador_r02_n0_r02.py').write_text(new_panel,encoding='utf8',newline='\n')
    copy(HERE/'contabilizar_dosis_total_actuador_n0_r02.py','contabilizar_dosis_total_actuador_n0_r02.py')
    copy(Path(__file__),Path(__file__).name)
    for script,target,selector in(('resumir_actuador_r02_n0_r02.py','RECALCULO_PORTABLE_R02.json','--index'),
        ('recalcular_panel_actuador_r02_n0_r02.py','RECALCULO_PANEL_R02.json','--index'),
        ('contabilizar_dosis_total_actuador_n0_r02.py','DOSIS_COMPLETA_R02.json','--evidence')):
        inp=BASE/'INDICE.json'if selector=='--index'else BASE
        result=subprocess.run([sys.executable,'-I','-B',str(OUT/script),selector,str(inp),'--out',str(OUT/target)],capture_output=True,text=True,encoding='utf8')
        if result.returncode:raise RuntimeError(result.stderr)
    summary=read(OUT/'RECALCULO_PORTABLE_R02.json')
    if summary['discrepancies']:raise ValueError('Corrected Native RAW/action recalc differs from physical reader')
    observer_source=ROOT/'sistema/capacidades/observador_causal_retrospectivo_01.py'
    copy(observer_source,'observador_causal_retrospectivo_01.py')
    observer=load('existing_snapshot_parser_N0_only',observer_source)
    parent=observer.Snapshot(PAIR/'VIDA.deetsnap.gz',verify_checksum=False)
    if parent.encoded_sha256!=PARENT_SHA:raise ValueError('Exact FULL parent SHA differs')
    before={row['id']:row for row in parent.receipts}
    parent_summary={'snapshot':(PAIR/'VIDA.deetsnap.gz').relative_to(ROOT).as_posix(),
        'sha256':parent.encoded_sha256,'N':parent.N,'tick':parent.tick,'receipt_count':len(before),
        'pending_count':len(parent.pending),'next_event_id':parent.next_event_id,
        'checksum_scope':'SHA rechecked against already verified exact complete prefix; FNV not recomputed here.'}
    del parent
    proofs=[];branches={};index=read(BASE/'INDICE.json')
    for life,info in index['lives'].items():
        record=read(BASE/info['record'])  # OLD exported record; current REAL is already continuing.
        path=ROOT/'sistema'/record['snapshot']
        snapshot=observer.Snapshot(path,verify_checksum=False)
        if snapshot.encoded_sha256!=record['snapshot_sha256']or snapshot.tick!=656420:raise ValueError('Fixed old FULL cut differs')
        all_after={row['id']:row for row in snapshot.receipts};new={identifier:row for identifier,row in all_after.items()if identifier not in before}
        primary_inputs={};work_rows=[]
        for operation in record['operations']:
            relative=operation.get('result_file','')
            if'apd04_actuator_'not in relative:continue
            encoded=(BASE/relative).read_bytes()
            if hashlib.sha256(encoded).hexdigest()!=operation['result_sha256']:raise ValueError('Primary source changed')
            primary=json.loads(encoded);primary_inputs.update(receipt_inputs(primary['result']))
            for block in primary['result'].get('rows',[]):
                for row in block.get('rows',[]):
                    if isinstance(row,dict)and'selection'in row:work_rows.append({'source':relative,'row':row})
        expected=set(primary_inputs);actual=set(new)
        changed_old=[identifier for identifier,row in before.items()if all_after.get(identifier)!=row]
        proof={'life':life,'old_FULL_snapshot':path.relative_to(ROOT).as_posix(),'sha256':snapshot.encoded_sha256,
            'tick':snapshot.tick,'parent_receipts_preserved_identically':not changed_old,'changed_parent_ids':changed_old,
            'new_FULL_receipt_count':len(new),'primary_unique_receipt_count':len(expected),
            'FULL_ids_missing_from_primaries':sorted(actual-expected),'primary_ids_missing_from_FULL':sorted(expected-actual),
            'Native_status_enum_counts':dict(Counter(str(row['status'])for row in new.values())),
            'new_FULL_receipts_exact':[new[key]for key in sorted(new)],
            'native_pending_exact':snapshot.pending,'next_event_id':snapshot.next_event_id,
            'all_new_primary_statuses':dict(Counter(row['receipt']['status']for row in primary_inputs.values())),
            'checksum_scope':'Full encoded SHA checked against the preserved old VIDA record; FNV not recomputed.'}
        if expected!=actual or changed_old:raise ValueError('FULL/primary Native receipt reconciliation failed')
        for identifier,item in primary_inputs.items():
            if item['channel']not in new[identifier]['channels']:raise ValueError('Primary channel differs from FULL receipt')
            if item['tick']!=new[identifier]['requested_tick']:raise ValueError('Primary tick differs from FULL receipt')
        proofs.append(proof);branches['REAL'if'REAL'in life else'OMIT']=work_rows
        del snapshot
    write(OUT/'CONCILIACION_RECEIPTS_FULL.json',{'parent':parent_summary,'lives':proofs,
        'new_native_ticks':0,'scope':'Exact Native receipt-ID sets and inherited receipts from original FULL snapshots. '
        'Exports selected receipt records, not restorable snapshots; no current REAL state was read or modified.'})
    aa=branches['REAL'];bb=branches['OMIT'];a4=aa[3]['row'];b4=bb[3]['row']
    causal_prior=[]
    for number in(1,2,3):
        a,b=aa[number-1]['row'],bb[number-1]['row']
        causal_prior.append({'opportunity':number,'query_ticks':[a['selection']['query_tick'],b['selection']['query_tick']],
            'public_before_equal':a['public_before']==b['public_before'],
            'choices':[a['selection']['physical_choice'],b['selection']['physical_choice']],
            'effects':[a['committed_effect'],b['committed_effect']],
            'REAL_return':a['native_return'],'OMIT_return':b['native_return'],
            'primary_sources':[aa[number-1]['source'],bb[number-1]['source']]})
    prior_a={identifier:item for wrapped in aa[:3]for identifier,item in receipt_inputs(wrapped['row']).items()}
    prior_b={identifier:item for wrapped in bb[:3]for identifier,item in receipt_inputs(wrapped['row']).items()}
    def specifications(entries):return Counter((r['channel'],r['tick'],r['value'])for r in entries.values())
    extra_a=specifications(prior_a)-specifications(prior_b);extra_b=specifications(prior_b)-specifications(prior_a)
    write(OUT/'DOSSIER_PRIMERA_DIVERGENCIA_OP4.json',{
        'schema':'APD04.actuator_R02.first_divergence.causal_dossier.N0.r02',
        'opportunity':4,'same_complete_parent_sha256':PARENT_SHA,
        'same_current_public_before':a4['public_before']==b4['public_before'],
        'public_before_REAL':a4['public_before'],'public_before_OMIT':b4['public_before'],
        'same_query_tick':a4['selection']['query_tick']==b4['selection']['query_tick'],
        'query_ticks':[a4['selection']['query_tick'],b4['selection']['query_tick']],
        'raw_elementary_components':[a4['raw_sensor_components'],b4['raw_sensor_components']],
        'REAL_selection':a4['selection'],'OMIT_selection':b4['selection'],
        'REAL_effect':a4['committed_effect'],'OMIT_effect':b4['committed_effect'],
        'real_native_classification_operation':a4['native_operation'],
        'prior_three_completed_histories':causal_prior,
        'prior_extra_material_specs_REAL_only':[{'channel':key[0],'tick':key[1],'value':key[2],'multiplicity':n}for key,n in extra_a.items()],
        'prior_extra_material_specs_OMIT_only':[{'channel':key[0],'tick':key[1],'value':key[2],'multiplicity':n}for key,n in extra_b.items()],
        'interpretation':'Before opportunity4, the visible cached value/tag/goal, elementary bits and query tick agree. '
        'Prior real generic FAILURE consequences altered physical references/trace context; Native selects+1/USE versus−1/INSPECT. '
        'This local acquired-history selection change is distinct from installing the same P0 R02 codec in both branches. '
        'The REAL classification is correct but not useful by the frozen criterion (wrong tag/goal and unchanged prior bin). '
        'No improved utility, general contextual policy, P2/R2 generality or independent replication is established.',
        'new_native_ticks':0})
    clarification={'schema':'APD04.actuator_R02.accounting_correction.N0.r02',
        'R01_port_only_counts_10op_REAL_OMIT':[179,140],
        'R02_all_schemas_counts_10op_REAL_OMIT':[211,140],
        'R02_separate_old_panel_counts':[154,154],
        'R02_total_native_inputs_all_committed_operations':[365,294],
        'all_statuses':'applied;0rejected;0Nativepending at old final cuts',
        'previous_39_extra_entries':'39 was REAL−OMIT within port-schema records only. '
            '32additional channel-schema entries occur in REAL, so the complete10op dose difference is71, not39.',
        'RAW_field_names_correction':'The decoded native layout is state=low32, semantic=high4. '
            'R01 summary/panel code reversed these local variable names/tests; the decisive candidates all hadstate1/semantic1, '
            'so corrected R02 gives identical choices/actions/panel signs. The general RAW decoder is corrected, not inferred equivalent outside these cases.',
        'source_evidence_not_modified':True,'R01_results_preserved':True,'new_native_ticks':0,
        'base_portable_index':{'relative_to_this_folder':'../EVIDENCIA_PORTABLE_R01/INDICE.json','sha256':sha(BASE/'INDICE.json')}}
    write(OUT/'ACLARACION_R01_Y_CONTEOS_R02.json',clarification)
    generated=[{'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size}for path in sorted(OUT.rglob('*'))if path.is_file()]
    write(OUT/'MANIFIESTO_R02.json',{'original_copied_sources':sources,'members_without_self':generated,'new_native_ticks':0})
    print(json.dumps({'folder':str(OUT),'FULL_receipt_counts':[p['new_FULL_receipt_count']for p in proofs],
        'same_public_before_op4':a4['public_before']==b4['public_before'],'prior_REAL_only_specs':len(extra_a),
        'prior_OMIT_only_specs':len(extra_b),'RAW_discrepancies':summary['discrepancies'],'new_native_ticks':0},indent=2))


if __name__=='__main__':main()
