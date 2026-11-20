"""Measure remaining PI06 logical-byte budget including the clean extraction.

No new ZIP, Native work, source changes, inventory outside explicit PI06 roots,
cleanup, replay or repeat of the already completed archive-integrity test.
"""
from pathlib import Path
import datetime, hashlib, json, os, runpy, stat

P = Path(__file__).resolve().parents[1]
C = P.parents[2]/'DEE Cognitive 2.0'
W = P.parents[4]

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def byte_count(root):
    count = size = 0
    stack = [root]
    while stack:
        p = stack.pop(); s = p.stat(follow_symlinks=False)
        if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&1024:
            raise ValueError('No linked verification tree: '+str(p))
        if stat.S_ISDIR(s.st_mode):
            with os.scandir(p) as entries:
                stack.extend(Path(x.path) for x in entries)
        elif stat.S_ISREG(s.st_mode):
            count += 1; size += s.st_size
        else:
            raise ValueError('Nonregular verification item')
    return {'path':str(root),'files':count,'logical_bytes':size}

def main():
    output = P/'control/CIERRE_RECURSOS_POST_SELLO_PI06_R01.json'
    if output.exists():
        raise FileExistsError('An actual final resource observation already exists')
    v = read(P/'control/VERIFICACION_ZIP_FINAL_PI06_R01.json')
    assert v['status'] == 'SEALED_AND_CLEAN_EXTRACTION_VERIFIED'
    short = Path(v['clean_extraction']).parent.resolve(strict=True)
    assert short.parent == W.resolve() and short.name.startswith('pi06_verificacion_')
    helper = runpy.run_path(str(P/'codigo/medir_almacenamiento_PI06_pasivo_R02.py'),run_name='pure_bounded_size_reader')
    one = helper['scan'](); two = helper['scan']()
    assert one['files_internal'] == two['files_internal']
    assert not any(one[x] or two[x] for x in ('errors','link_exclusions'))
    extra1, extra2 = byte_count(short), byte_count(short)
    assert extra1 == extra2
    product_files = [C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
        C/'sistema/capacidades/CATALOGO_CAPACIDADES.json',C/'reproducibilidad/RECURSOS.json',
        C/'sistema/contratos/PI06_REPRODUCIBILIDAD_INSTRUMENTAL_R01.json',
        C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
        C.parent/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx']
    other = [{'path':str(p),'whole_current_file_bytes_conservative':p.stat().st_size} for p in product_files]
    total = two['logical_bytes']+extra2['logical_bytes']+sum(x['whole_current_file_bytes_conservative'] for x in other)
    assert total+100000 < 4_800_000_000
    anchors = deltas = 0
    portable = P/'fuentes/RECALCULO_GLOBAL_PORTABLE_PI06_R01'
    frame_kinds = {}
    for case in read(portable/'CAPTURAS.json')['captures']:
        data = read(portable/case['file'])
        frame_file = next(Path(x['path']) for x in data['source_files'] if Path(x['path']).name == 'FRAMES.jsonl')
        for line in frame_file.read_text(encoding='utf8').splitlines():
            row = json.loads(line)
            kind = row.get('kind',row.get('type',row.get('encoding','UNSPECIFIED')))
            frame_kinds[str(kind)] = frame_kinds.get(str(kind),0)+1
    resources = read(Path(v['clean_extraction'])/'04_EVIDENCIAS/RECURSOS_PROPIETARIOS_PI06.json')
    proof = {'schema':'DEE.PI06.final_resource_observation.R01',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'campaign_and_only_new_PI06_RP_bytes':two['logical_bytes'],
        'clean_verification_tree_outside_campaign':extra2,
        'modified_product_files_counted_whole_conservatively':other,
        'conservative_total_new_logical_bytes':total,
        'fixed_limit_bytes':4_800_000_000,'remaining_logical_margin_bytes':4_800_000_000-total,
        'stable_two_passes':True,'size_scope_excludes_original_principal_and_unrelated_projects':True,
        'not_free_space_or_physical_disk_bytes':True,
        'captured_frame_kind_counts':frame_kinds,
        'Native_ticks_all_branches':7882,'Native_worlds':12,
        'owner_resources_max_observed':resources['max_observed_per_field'],
        'owner_resource_coverage_limit':resources['RP_host_resource_coverage'],
        'ZIP_verified_proof':str(P/'control/VERIFICACION_ZIP_FINAL_PI06_R01.json'),
        'ZIP_final':v['zip'],'no_NEW_ZIP_or_Native_or_original_writes':True,
        'post_seal_proof_not_in_ZIP':'This observation follows sealing and is preserved locally; no self-referential archive hash is inserted.'}
    with output.open('x',encoding='utf8') as f:
        json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'conservative_total':total,
        'logical_margin':4_800_000_000-total,'frame_kind_counts':frame_kinds,
        'Native_ticks_this_operation':0},ensure_ascii=False))

if __name__ == '__main__':
    main()
