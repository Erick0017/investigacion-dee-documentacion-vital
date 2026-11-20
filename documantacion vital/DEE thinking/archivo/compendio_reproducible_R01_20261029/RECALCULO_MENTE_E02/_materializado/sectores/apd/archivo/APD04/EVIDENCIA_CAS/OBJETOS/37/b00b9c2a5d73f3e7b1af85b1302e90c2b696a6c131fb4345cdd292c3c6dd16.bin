"""N0 exporter-schema correction only; no Native, repeat or changed RAW reader.

The APD04 reader names its no-target witness differently from legacy readers.
R01 data and failed calculation source are preserved; only this field alias is
normalized. No absent output is filled, no result or score is reclassified.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
ATTEMPT=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/SEMILLA_PANEL24_DIAGNOSTICO_R01'
BASE=ATTEMPT/'EVIDENCIA_PORTABLE_N0_R01'
OUT=ATTEMPT/'EVIDENCIA_PORTABLE_N0_R02'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    if OUT.exists():raise FileExistsError('Preserve the closed N0 correction; no overwrite.')
    source=BASE/'exportar_panel24_semilla_n0_r01.py';before=source.read_text(encoding='utf8')
    token="reader['reader_uses_target_or_token']"
    assert before.count(token)==2
    after=before.replace(token,"reader.get('reader_uses_target_or_token',reader.get('reader_uses_token_target_or_expected_sign'))")
    ast.parse(after)
    OUT.mkdir()
    for path in BASE.rglob('*'):
        if path.is_file():
            target=OUT/path.relative_to(BASE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    target=OUT/'recalcular_panel24_r02.py'
    with target.open('x',encoding='utf8',newline='\n')as stream:stream.write(after)
    spec=importlib.util.spec_from_file_location('panel24_corrected_schema_only',target);module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result=module.recalculate(OUT)
    emit(OUT/'RECALCULO_R02.json',result)
    shutil.copy2(__file__,OUT/Path(__file__).name)
    emit(OUT/'ACLARACION_ALIAS_R02.json',{'new_native_ticks':0,'Runtime_created':False,'Native_experiment_repeated':False,
        'R01_original_preserved':str(BASE),'R01_source_sha256':sha(source),
        'R02_recalculation_source_sha256':sha(target),'only_change':'Normalize legacy reader_uses_target_or_token versus APD04 reader_uses_token_target_or_expected_sign witness field; RAW/direction/score logic unchanged.',
        'R01_failure':'KeyError on nondecision metadata witness after the Native experiment and FULL seal had already completed cleanly.',
        'exact_primary_bytes_unchanged':True,'R02_output':'RECALCULO_R02.json'})
    emit(OUT/'MANIFIESTO_R02.json',{'members':[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]})
    print(json.dumps({'out':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO_R02.json'),
        'families':result['families'],'typed_queries':result['typed_queries'],'host_requests':result['host_material_requests'],
        'Native_receipts':result['Native_receipts_unique'],'statuses':result['Native_statuses'],'new_native_ticks':0},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
