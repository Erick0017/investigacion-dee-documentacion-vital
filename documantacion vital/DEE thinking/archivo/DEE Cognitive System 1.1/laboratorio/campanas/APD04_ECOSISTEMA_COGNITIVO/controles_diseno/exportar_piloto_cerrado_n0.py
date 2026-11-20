"""Lossless essential export of a CLOSED APD04 pilot, zero new Native ticks."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True)
    parser.add_argument('--evidence',required=True);parser.add_argument('--recalc',required=True)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    root=Path(args.root).resolve(strict=True);evidence=Path(args.evidence).resolve(strict=True)
    recalc=Path(args.recalc).resolve(strict=True);output=Path(args.output).resolve()
    if not evidence.is_relative_to(root/'evidencia'/'campanas'/'APD04_ECOSISTEMA_COGNITIVO'):
        raise ValueError('Explicit closed pilot evidence must belong to this campaign')
    if output.exists():raise FileExistsError('Keep previous export')
    output.mkdir(parents=True);originals=[]
    def export_file(source,destination,compressed=False):
        data=source.read_bytes();destination.parent.mkdir(parents=True,exist_ok=True)
        exported=gzip.compress(data,compresslevel=9,mtime=0)if compressed else data
        destination.write_bytes(exported)
        if (gzip.decompress(destination.read_bytes())if compressed else destination.read_bytes())!=data:
            raise ValueError('Byte preservation failed')
        if source.read_bytes()!=data:raise ValueError('Source changed while exporting; not a closed evidence file')
        originals.append({'original':str(source),'original_bytes':len(data),'original_sha256':sha(data),
                          'exported':destination.relative_to(output).as_posix(),'exported_bytes':len(exported),
                          'exported_sha256':sha(exported),'compression':'gzip_lossless_mtime0'if compressed else'none',
                          'decompressed_equals_original_bytes':True})
    trajectory=evidence/'TRAYECTORIA'
    export_file(trajectory/'EVENTOS.jsonl',output/'PRIMARIOS'/'EVENTOS.jsonl.gz',True)
    for name in('ANTES_DE_NATIVE.json','INICIO_VENTANA.json','FIN_VENTANA.json','RESULTADO.json'):
        source=trajectory/name
        if source.is_file():export_file(source,output/'CIERRE'/name)
    for name in('RESULTADO_SUPERVISION.json','ANTES_DEL_PROCESO.json','MUESTRAS_TOTALES_CLASS8.jsonl'):
        source=evidence/name
        if source.is_file():export_file(source,output/'CIERRE'/(name+'.gz'if name.endswith('.jsonl')else name),name.endswith('.jsonl'))
    for source in sorted((trajectory/'FUENTES_ANTES_DE_NATIVE').iterdir()):
        if source.is_file():export_file(source,output/'CODIGO_EJECUTADO'/source.name)
    report=json.loads(recalc.read_text(encoding='utf8'))
    export_file(recalc,output/'RECALCULO'/'RECALCULO_COMPACTO.json')
    export_file(Path(__file__).with_name('compactar_recalcular_taller_n0.py'),output/'RECALCULO'/'compactar_recalcular_taller_n0.py')
    artifacts=[]
    for row in report['rows']:
        name=row.get('artifact_locator')
        if name is None:continue
        source=Path(name).resolve()
        if not source.is_relative_to(root):
            artifacts.append({'original':str(source),'status':'outside_declared_source_root_not_read'});continue
        if not source.is_file():
            artifacts.append({'original':str(source),'status':'missing_local_file'});continue
        data=source.read_bytes();body=json.loads(data)
        equal=body.get('effect')==row['committed_effect']
        destination=output/'ARTEFACTOS'/(sha(data)+'_'+source.name)
        if not destination.exists():export_file(source,destination)
        artifacts.append({'original':str(source),'status':'copied_exact','sha256':sha(data),
                          'effect_matches_primary':equal,'episode':row['episode']})
        if not equal:raise ValueError('Artifact effect differs from primary')
    manifest={'schema':'APD04.closed_pilot_essential_export.N0.R01','life':report['life'],
              'new_native_ticks':0,'source_status':'Closed by Root; additionally each source checked unchanged before/after read.',
              'originals':originals,'artifacts':artifacts,
              'counts':{'opportunities':report['unique_opportunities'],'useful':report['useful'],'actions':report['action_counts'],
                        'checks':report['checks'],'issues':len(report['issues']),'receipts':report['last_observation_exported_receipt_status']},
              'omitted':'Complete operational checkpoints and SQLite remain local in the canonical system. This is analysis evidence, not a continuable E1 package.',
              'manifest_does_not_hash_itself':True}
    (output/'MANIFIESTO_PILOTO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'members':sum(1 for p in output.rglob('*')if p.is_file()),
                      'bytes':sum(p.stat().st_size for p in output.rglob('*')if p.is_file()),
                      'artifacts':artifacts,'new_native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
