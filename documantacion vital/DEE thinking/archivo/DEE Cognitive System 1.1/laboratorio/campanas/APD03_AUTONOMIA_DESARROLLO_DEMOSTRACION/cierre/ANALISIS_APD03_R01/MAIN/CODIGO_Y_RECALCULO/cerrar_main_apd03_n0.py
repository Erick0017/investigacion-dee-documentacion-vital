"""Seal compact Main scientific evidence; never run Native or open live state."""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def read(path):
    value=Path(path).read_bytes()
    return json.loads(gzip.decompress(value) if str(path).endswith('.gz') else value)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-evidence',required=True,type=Path)
    parser.add_argument('--io-evidence',required=True,type=Path)
    parser.add_argument('--quality-archive',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();source=args.main_evidence.resolve();target=args.out.resolve()
    if target.exists():raise FileExistsError('Do not overwrite a sealed stage')
    final=read(source/'REGISTROS_VENTANA.json.gz')
    if final['error'] is not None or not final['final_stopped_cut'] or final['enabled_seconds']<3600:
        raise ValueError('This closure requires the real completed Main window and stopped pair')
    if not final['sources_unchanged'] or not final['protected_originals_unchanged']:
        raise ValueError('The recorded source/original freeze did not hold')
    target.mkdir(parents=True);source_records=[];copied=[]

    def copy(origin,relative):
        destination=target/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        before=sha(origin);shutil.copyfile(origin,destination)
        if sha(origin)!=before or sha(destination)!=before:raise ValueError('Closed original changed while copied: '+str(origin))
        source_records.append({'source':str(origin),'file':relative,'bytes':origin.stat().st_size,'sha256':before})
        copied.append(relative)

    for folder in ('EVENTOS','BLOQUES','HEARTBEATS','FUENTES_ANTES_DE_NATIVE'):
        for origin in sorted((source/folder).rglob('*')):
            if origin.is_file():copy(origin,'EVIDENCIA_MAIN/'+origin.relative_to(source).as_posix())
    for origin in sorted(source.iterdir()):
        if origin.is_file():copy(origin,'EVIDENCIA_MAIN/'+origin.name)
    for folder in ('PAR_POSTSTOP_PENDIENTE','PAR_POSTSTOP_FINAL'):
        copy(source/folder/'EXPORTACION_SERVICIO.json','EVIDENCIA_MAIN/'+folder+'/EXPORTACION_SERVICIO.json')
    for origin in sorted((source/'CHECKPOINTS').rglob('*.json')):
        copy(origin,'EVIDENCIA_MAIN/'+origin.relative_to(source).as_posix())
    for origin in sorted(args.quality_archive.rglob('*')):
        if origin.is_file():copy(origin,'ARCHIVOS_CALIDAD_REALES/'+origin.relative_to(args.quality_archive).as_posix())
    for origin in sorted(args.io_evidence.iterdir()):
        if not origin.is_file():continue
        # The OS-only observer can append after Main closes. Preserve an
        # exact, line-complete byte prefix rather than invent a closed file.
        payload=origin.read_bytes()
        if origin.suffix=='.jsonl' and not payload.endswith(b'\n'):raise ValueError('OS log prefix captured in the middle of a line; preserve and choose another closure')
        destination=target/'RECURSOS_OS_NATIVE'/origin.name;destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as stream:stream.write(payload)
        following=origin.read_bytes()
        if not following.startswith(payload):raise ValueError('OS observer source is not append-only')
        source_records.append({'source':str(origin),'file':destination.relative_to(target).as_posix(),
            'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),
            'exact_source_prefix':True,'source_bytes_after_capture':len(following),
            'not_a_claim_of_future_observer_coverage':True})
    code_base=Path(__file__).parent
    for name in ('recalcular_main_integrado_n0.py','extraer_archivos_calidad_desde_par_n0.py',
                 'derivar_programa_referencias_n0.py','PROGRAMA_REFERENCIAS_DERIVADO_R02.json',
                 'cerrar_main_apd03_n0.py'):
        copy(code_base/name,'CODIGO_Y_RECALCULO/'+name)
    (target/'RESULTADOS').mkdir()
    command=[sys.executable,'-I','-B','-X','utf8',str(target/'CODIGO_Y_RECALCULO/recalcular_main_integrado_n0.py'),
        '--evidence',str(target/'EVIDENCIA_MAIN'),'--io-evidence',str(target/'RECURSOS_OS_NATIVE'),
        '--quality-artifacts',str(target/'ARCHIVOS_CALIDAD_REALES'),'--out',str(target/'RESULTADOS/RECALCULO_MAIN_FINAL.json')]
    started=time.monotonic();completed=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=180)
    if completed.returncode:raise RuntimeError('Archived zero-tick calculation failed: '+completed.stderr+completed.stdout)
    result=read(target/'RESULTADOS/RECALCULO_MAIN_FINAL.json')
    portable=Path(tempfile.mkdtemp(prefix='APD03_MAIN_N0_',dir=code_base))/'COPIA_INDEPENDIENTE'
    shutil.copytree(target,portable)
    repeated=portable/'RECALCULO_REPETIDO.json'
    command2=[sys.executable,'-I','-B','-X','utf8',str(portable/'CODIGO_Y_RECALCULO/recalcular_main_integrado_n0.py'),
        '--evidence',str(portable/'EVIDENCIA_MAIN'),'--io-evidence',str(portable/'RECURSOS_OS_NATIVE'),
        '--quality-artifacts',str(portable/'ARCHIVOS_CALIDAD_REALES'),'--out',str(repeated)]
    other=subprocess.run(command2,capture_output=True,text=True,encoding='utf8',timeout=180)
    if other.returncode or repeated.read_bytes()!=(target/'RESULTADOS/RECALCULO_MAIN_FINAL.json').read_bytes():
        raise RuntimeError('Independent-location standard-library calculation did not reproduce exact result bytes')
    emit(target/'PRUEBA_RECALCULO_PORTABLE.json',{'schema':'APD03.Main.portable_archive_calculation.R01',
        'commands':[command,command2],'returncodes':[completed.returncode,other.returncode],
        'stdout':[completed.stdout,other.stdout],'different_directory':str(portable),
        'byte_identical_result':True,'recalculated_sha256':sha(repeated),
        'seconds_for_both_recalculations':time.monotonic()-started,
        'native_ticks':0,'engine_imports':False,'another_computer_tested':False,
        'scope':'Two independent locations on this host, stdlib-only archived calculation, not a Native simulation or replay of learning.'})
    omitted=[]
    for folder in ('PAR_POSTSTOP_PENDIENTE','PAR_POSTSTOP_FINAL'):
        manifest=read(source/folder/'EXPORTACION_SERVICIO.json')
        omitted.append({'directory':str(source/folder),'reason':'Operational complete pair stays local; this analysis is not a continuation backup.',
            'member_index_in_package':'EVIDENCIA_MAIN/'+folder+'/EXPORTACION_SERVICIO.json',
            'index_sha256':sha(source/folder/'EXPORTACION_SERVICIO.json'),'omitted_member_count':len(manifest['members']),
            'omitted_member_bytes':sum(member['bytes'] for member in manifest['members'])})
    for origin in sorted((source/'CHECKPOINTS').rglob('*.deetsnap.gz')):
        omitted.append({'file':str(origin),'bytes':origin.stat().st_size,'sha256':sha(origin),
            'reason':'Dense complete Native checkpoint remains local; corresponding VIDA.json is included.'})
    emit(target/'INDICE_FUENTES_Y_OMISIONES.json',{'schema':'APD03.Main.compact_analysis_sources.R01',
        'sources':source_records,'omissions':omitted,'motor_or_WHL_included':False,
        'not_a_full_operational_backup':True,'same_physical_world_not_merged_forks':True,
        'final_tick':final['final_stopped_cut']['record']['physical']['tick'],
        'final_pair_manifest_sha256':final['final_stopped_cut']['manifest_sha256']})
    text=(
        '# APD03: evidencia de la trayectoria MAIN\n\n'
        'Este expediente conserva todos los eventos materiales del primer dueño y los dos resultados nuevos de la UI ordinaria tras reabrir: el mismo ID pendiente y el panel final. No contiene motor ni snapshots densos; no reemplaza los estados locales.\n\n'
        f"Ventana cronológica: {final['enabled_seconds']:.9f} s; tick final {final['final_stopped_cut']['record']['physical']['tick']}. La observation de FIN.owner es el recibo STARTUP cacheado, no una foto final: se contrastan controles, heartbeats y ticks materiales.\n\n"
        f"Recálculo: {result['checks']} comprobaciones de bytes, RAW, recibos y efectos; {len(result['issues'])} discrepancias. No es un veredicto de inteligencia.\n\n"
        'Los 8 goals produjeron archivos correctos; 14 oportunidades incluyeron 8 ACT y 6 QUERY, con cuatro hechos nuevos y dos consultas redundantes. Los hechos revelados permanecen observables en el entorno externo: esto no demuestra almacenamiento nativo del número. Las asociaciones luma+/nara− sí se enseñaron en MAIN y eligieron funciones preparadas; no son nuevas primitivas NSM ni aritmética general aprendida.\n\n'
        'Los tres casos antiguos de dos proveedores tuvieron dos aciertos y un fallo: el cálculo nativo 23 fue alterado por la ley ambiental explícita a24. Dos primitivas adicionales compusieron13→10 bajo orden suministrado por el operador. Los cinco archivos originales se copiaron únicamente del par final cerrado y se verifican por bytes.\n\n'
        'Los cuatro paneles son consultas materiales. Al final, las14 formas antiguas,6 lecturas MA y2 formas nuevas conservaron sus signos bajo ese contrato de suministro; no son22 capacidades independientes. El codec, las rutas, las oportunidades, los contextos, la docencia y el calendario son preparados. No se acredita R2 general, planificación nativa libre, curiosidad general ni ventaja universal.\n\n'
        'Recálculo sin motor: `python -I -B CODIGO_Y_RECALCULO/recalcular_main_integrado_n0.py --evidence EVIDENCIA_MAIN --io-evidence RECURSOS_OS_NATIVE --quality-artifacts ARCHIVOS_CALIDAD_REALES --out mi_recalculo.json`.\n\n'
        'I/O class9 del primer instrumento está reservado y no equivale a cero tráfico. RECURSOS_OS_NATIVE conserva class8 Windows, tráfico lógico acumulado del Job Native, no energía ni disco físico. No sumar CPU/RAM anidados. La supervisión TOTAL pertenece al expediente de recursos complementario.\n')
    (target/'LEER_RESULTADOS_MAIN.md').write_text(text,encoding='utf8')
    members=[]
    for origin in sorted(target.rglob('*')):
        if origin.is_file():members.append({'file':origin.relative_to(target).as_posix(),'bytes':origin.stat().st_size,'sha256':sha(origin)})
    emit(target/'MANIFIESTO.json',{'schema':'APD03.Main.scientific_stage_members.R01',
        'members':members,'no_self_hash':True,'created_utc':datetime.now(timezone.utc).isoformat(),
        'compressed_size_is_not_measured_by_expanded_bytes':True})
    print(json.dumps({'stage':str(target),'members':len(members)+1,
        'expanded_bytes':sum(item['bytes'] for item in members)+(target/'MANIFIESTO.json').stat().st_size,
        'manifest_sha256':sha(target/'MANIFIESTO.json'),'recalculation_sha256':sha(target/'RESULTADOS/RECALCULO_MAIN_FINAL.json'),
        'checks':result['checks'],'issues':len(result['issues']),'no_new_ticks':True},ensure_ascii=False))


if __name__=='__main__':main()
