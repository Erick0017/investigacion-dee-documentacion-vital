"""Preserve release primaries and produce a concise, evidence-linked review."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,csv,ctypes,hashlib,json,os,platform,shutil,time
ROOT=Path(__file__).resolve().parents[4]
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
    p=argparse.ArgumentParser();p.add_argument('--first',type=Path,required=True);p.add_argument('--second',type=Path,required=True);a=p.parse_args();r=ROOT;ev=r/'evidencia';v1=read(a.first/'VERIFICACION_EN_CURSO.json');v2=read(a.second/'VERIFICACION_EN_CURSO.json');release=ev/'verificaciones/RECUPERACION_FINAL_DESDE_ZIP';release.mkdir(parents=True,exist_ok=False)
    copy(a.first/'VERIFICACION_EN_CURSO.json',release/'CANDIDATO01_FASES_EJECUTADAS.json');copy(a.second/'VERIFICACION_EN_CURSO.json',release/'CANDIDATO02_FASES_ANTES_AUDITORIA.json')
    for src in(a.first/'HERENCIA_FINAL').glob('native_*/RECOVERY.json'):copy(src,release/'HERENCIA_FAMILIAS'/src.parent.name/'RECOVERY.json')
    for family in('core06','core07'):
        src=a.first/'HERENCIA_FINAL'/('native_'+family)/'PRIMARY_TRANSITIONS.json';copy(src,release/'HERENCIA_FAMILIAS'/('native_'+family)/src.name)
    copy(a.first/'HERENCIA_FINAL/REGRESION_HEREDADA.json',release/'REGRESION_HEREDADA_LIMPIA.json')
    for base,name in((a.first/'PERFILES_C/pruebas','PERFILES_CANDIDATO01'),(a.second/'PERFILES_C/pruebas','PERFILES_CANDIDATO02')):
        for src in base.iterdir():
            if src.is_file():copy(src,release/name/src.name)
    for src in(a.second/'comandos').iterdir():
        if src.is_file():copy(src,release/'COMANDOS_CANDIDATO02'/src.name)
    for src in(a.first/'HERENCIA_FINAL').glob('*.log'):copy(src,release/'LOGS_HERENCIA'/src.name)
    # Exact source recovery for the prior external controller. This avoids a
    # source-hash claim pointing only at a later edited helper.
    current=r/'laboratorio/campanas/CONSOLIDACION_1_1/herramientas/verificar_entrega.py';source=current.read_text(encoding='utf8');old=source.replace('import argparse,atexit,','import argparse,');start=old.index('    # One writer for the external report');end=old.index('    controller=None',start);old=old[:start]+old[end:];oldbytes=old.encode('utf8');expected=v2['source_controller_sha256'];reconstructed=hashlib.sha256(oldbytes).hexdigest()
    sourceproof={'candidate01_preserved_source':{'file':'evidencia/genealogia/VERIFICADOR_CANDIDATO_01.py','sha256':sha(ev/'genealogia/VERIFICADOR_CANDIDATO_01.py'),'recorded_sha256':v1['source_controller_sha256']},'candidate02_previous_controller_expected_sha256':expected,'candidate02_reconstructed_from_exact_recorded_patch_sha256':reconstructed,'candidate02_exact_source_recovered':expected==reconstructed,'current_controller_sha256':sha(current)}
    if expected==reconstructed:(ev/'genealogia/VERIFICADOR_CANDIDATO_02.py').write_bytes(oldbytes)
    put(release/'IDENTIDADES_VERIFICADORES.json',sourceproof)
    initial=read(ev/'genealogia/INVENTARIO_INICIAL.json');integrity=[]
    for row in initial['sources']:
        actual=sha(Path(row['path']));integrity.append({'path':row['path'],'before_sha256':row['sha256'],'after_sha256':actual,'unchanged':actual==row['sha256']})
    kernel=r.parents[2]/'4.5/trabajo_codex/BUILD_4_5_0_20261018_094838/source/src/kernel_v27.cpp';kh=sha(kernel);integrity.append({'path':str(kernel),'before_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31','after_sha256':kh,'unchanged':kh=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'})
    put(ev/'verificaciones/ORIGINALES_SIN_MODIFICAR.json',{'files':integrity,'all_unchanged':all(x['unchanged']for x in integrity),'scope':'Actually opened reference archives and frozen kernel source; no claim that every untouched file in the whole corpus was read.'})
    if not all(x['unchanged']for x in integrity):raise AssertionError('Original source identity changed')
    table=read(r/'laboratorio/campanas/CONSOLIDACION_1_1/TABLAS_PARA_EXPORTAR.json');csvchecks=[]
    for name,expected_rows in table.items():
        with(r/'sistema/documentacion'/name).open(encoding='utf-8-sig',newline='')as f:actual=list(csv.DictReader(f))
        normalized=[{k:str(v)if v is not None else''for k,v in row.items()}for row in expected_rows];equal=actual==normalized;csvchecks.append({'file':name,'sha256':sha(r/'sistema/documentacion'/name),'rows':len(actual),'all_cells_equal_authoritative_intermediate':equal})
    put(ev/'verificaciones/TABLAS_CSV_RELECTURA.json',{'tables':csvchecks,'ArtifactTool_authored':True,'formula_scope':'Plain research matrices; no formulas or visual encoding required. CSV preserves identifiers and categories as exact text.','missing_vs_zero':'Missing/null states are not converted to positive measurements.'})
    if not all(x['all_cells_equal_authoritative_intermediate']for x in csvchecks):raise AssertionError('CSV export changed a cell')
    class Memory(ctypes.Structure):_fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(x,ctypes.c_ulonglong)for x in('total_physical','available_physical','total_pagefile','available_pagefile','total_virtual','available_virtual','available_extended_virtual')]
    mem=Memory();mem.length=ctypes.sizeof(mem);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem));budget=read(r/'REANUDACION.json')['budget'];elapsed=time.perf_counter()-budget['start_monotonic']/budget['monotonic_frequency']
    put(ev/'informes/RECURSOS_Y_PRESUPUESTO_FINAL_PRESELLO.json',{'schema':'DCS1.1.resource_budget.v1','original_budget':budget,'measured_utc':datetime.now(timezone.utc).isoformat(),'elapsed_monotonic_seconds':elapsed,'remaining_seconds':21600-elapsed,'machine':platform.node(),'platform':platform.platform(),'logical_cpu':os.cpu_count(),'physical_memory_total_bytes':int(mem.total_physical),'physical_memory_available_bytes_now':int(mem.available_physical),'initial_RAM_label_caveat':'Initial available_ram_bytes was the initial reported machine quantity; current total and available values are explicitly separated here.','disk_free_bytes_now':shutil.disk_usage(r).free,'per_worker_memory_limit_bytes':4*1024**3,'global_concurrency_caveat':'Target two native workers. Brief prepare/profiles controller overlap is documented; strict global concurrency is not certified during that transition. Each owned job retained its4GiB limit.','no_energy_measurement':True,'supervision_gap':'EarlyR1launcherRSS is not nativeworkerRAM; later jobs and actualworkers are measured.','no_budget_reset':True})
    copy(r/'sistema/capacidades/CATALOGO_CAPACIDADES.json',ev/'informes/CATALOGO_CAPACIDADES_1_1.json')
    calc=read(ev/'informes/CALCULOS_DESDE_PRIMARIOS.json');put(r/'laboratorio/pruebas_integracion/INDICE_EJECUCIONES.json',{'native_trajectory_sources':calc['sources'],'profile_checks':{'candidate02':len(read(a.second/'PERFILES_C/pruebas/RESULTADOS.json')['checks']),'proof':'evidencia/verificaciones/RECUPERACION_FINAL_DESDE_ZIP/PERFILES_CANDIDATO02/RESULTADOS.json'},'fresh_recovery_families':v1['heritage_release']['families'],'not_independent_replica_counts':True})
    put(r/'laboratorio/diagnosticos/INDICE.json',{'source_collision':'evidencia/diagnosticos/PUENTE_S00_R1/TRANSPORTE_LOCAL.json','causal_cut_sham':'evidencia/controles/PUENTE_CAUSAL_R1B/CONTROLES.json','expansion':'evidencia/diagnosticos/EXPANSION_MICRO_R1/MICRO_EXPANSION.json','selective_update':'evidencia/diagnosticos/REVISION_MICRO_R1/MICRO_REVISION.json','management_failure':'evidencia/diagnosticos/GESTION_FALLOS_PARCIALES/CAMBIO_R1_R2.json','verifier_overlap':'evidencia/diagnosticos/VERIFICADOR_SUPERPOSICION/RECONCILIACION.json','all_edits_are_diagnostic_or_explicit_declared_experiences':True})
    summary='''# DEE Cognitive System 1.1: resultado científico y operativo

Se construyó una capa de sistema sobre DEE thinking 4.5.0 oficial, sin modificar el WHL ni v27. Incluye cinco perfiles, nueve estados completos seleccionados, una entrada común y gestión explícita de creación, importación, bifurcación, continuación, exportación y promoción.

## Lo que puede continuarse

La vida preferente **E1_SOCIAL_11, T3154**, es una rama identificada del E1 de CPC9 importado en T1907. Adquirió nuevas correspondencias por comunicación física dentro del mismo Runtime, revisó una referencia cuantitativa de 67 a 78 mediante un aporte físico de 11, y mantuvo acceso al comparador anterior R36/O16. Cuatro de ocho portadores sociales siguieron siendo funcionalmente consultables. Un ejemplo nuevo continúa una copia hasta T3221; la verificación limpia guardó una petición pendiente y la utilizó en otro proceso hasta T3288. No se reemplazó el individuo por una receta sin entrenar.

Los otros perfiles son independientes: repertorio oficial N131 de 65 formas con acceso por fase, repertorio N67 sin el cuerpo anterior, U0 oficial con 14 asociaciones comprobadas y física directa vacía. No se atribuyen sus repertorios a E1.

## Herencia recuperada

Las 34 familias del núcleo pasaron recuperación desde una extracción sin ZIP históricos. Conservan memoria, predicción, comparación, acción, asociación, composición, comunicación, acceso, regulación y persistencia en sus dominios originales. Son contratos que comparten mecanismos, no 34 conceptos ni 34 perfiles biográficos interactivos. Dieciséis filas históricas amplias siguen documentales; otros alcances específicos conservan su estado pendiente en el catálogo.

Tras corregir únicamente la conservación de operaciones fallidas en el gestor, se repitieron las 25 pruebas de perfiles afectadas. El núcleo y su almacén, motor, dependencias y trabajadores se comprobaron byte por byte iguales; se ejecutaron referencias dirigidas desde el ZIP corregido. No se cuentan esas reproducciones como nuevas muestras científicas.

## Qué se aprendió sobre el deterioro

El cuerpo integrado reprodujo barridos K65 de 57/65, 53/65 y 4/65, seguidos de pérdida de acceso. El N67 sin ese cuerpo conservó 65/65 durante diez barridos y en una reserva con carga de consulta distinta. Esto descarta inferir un techo universal de 65 a partir de ese fallo; la alternativa pierde las funciones del cuerpo integrado.

Las sondas contribuyeron al problema: desde un mismo pasado sin consultas, la primera lectura tardía logró 61/65, mientras que las consultas repetidas degradaron el acceso. Sin las sondas, el control llegó a T3560 con 326 sitios ocupados; con ellas se aproximó a 297 mil. Ocupación, saturación de registros, energía eléctrica y muerte no son equivalentes.

Los 16 testigos locales de recepción con el origen aún ocupado y los 16 nacimientos compatibles con XNOR no establecen una causa global única. “Supervivencia” significa aquí ocupación del sitio, no identidad demostrada del mismo portador. La expansión ya estaba en marcha antes del nacimiento local señalado en T2292. Se conservan pre/postestados y los huecos de genealogía.

## Acceso, actualización y comunicación

En una misma vida N131 se adquirieron 32 formas y después 33. Una ventana común sólo veía 33; ventanas separadas recuperaron las 65, sin reenseñar. Una receta privada de continuación revisó L01 y dejó las otras 64 accesibles en las ventanas probadas. El control fuera de ruta también afectó L06: no se trata como sham globalmente inocuo.

La comunicación E1→B→E1 produjo adquisición y uso posterior. B es un aprendiz físico simple, no otra mente completa. La primera utilización fue 7/8; omitir experiencia o asociación y cortar ida o retorno dieron 0/8. Un corte diagnóstico selectivo recuperó 8/8, pero esa copia no devolvió su solución a MAIN. El lector móvil posterior conserva cuatro usos, no ocho ni seis por encontrar firmas pasivas.

Las oportunidades, rutas, lectores y suministros están preparados externamente. Parte de las emisiones depende de historia nativa. No se demostró una estrategia general aprendida de cuándo o a quién consultar, ni regulación R2. “R2” en nombres de revisiones experimentales no significa ese nivel regulador.

## NSM65

Se preservan las 65 entradas oficiales, sus preguntas y dimensiones por vida. El máximo episódico histórico de E1 era 60 E0, cuatro E2 y un E3, todos en realizaciones operacionales limitadas. Este corte no acredita otra primitiva ni convierte K65 en 65 significados. El campo físico llamado semantic en RAW tampoco mide por sí mismo significado lingüístico. YO/TÚ funcional, negación general y productividad semántica siguen abiertos.

## Fiabilidad y límites de la entrega

El gestor conserva también una entrada admitida antes de un error posterior y un futuro nativo ya evolucionado antes de una excepción. No rebobina automáticamente. El verificador tuvo una superposición de escritores y un diff usó transitoriamente un nombre canónico cambiado; los intentos inválidos y primarios se conservaron, se reconciliaron sin repetir física y se añadieron bloqueo e identidades inmutables.

Se compararon 1.082 estados regenerados. 984 contenedores coincidieron exactamente; los otros 98 tenían metadatos distintos. En estos 98 coincidieron RAW/clocks y el Runtime serializado sin metadatos, y se preservaron sin pérdida ambos contenedores completos. No se sustituyó toda la memoria por un resumen escalar.

SISTEMA funciona sin laboratorio ni evidencia. AUDITORIA conserva datos, controles, fallos, recálculos, estados auxiliares y decisiones, sin duplicar el motor. La barrera de archivos del CLI es una auditoría Python, no un sandbox del sistema operativo. Los dos manuales DOCX 4.5 solicitados no se localizaron; se usaron contratos ejecutables y documentación técnica realmente abierta. No se afirma acceso a conversaciones de ChatGPT no leídas.

Esta entrega demuestra funciones finitas y una continuidad utilizable. No certifica mente general, conciencia, comprensión humana ni estabilidad ilimitada. El comprobante externo identifica los ZIP exactos, sus comprobaciones y sus límites.
'''
    (ev/'informes/RESUMEN_CIENTIFICO_1_1.md').write_text(summary,encoding='utf8');copy(ev/'informes/RESUMEN_CIENTIFICO_1_1.md',r/'entregas/RESUMEN_CIENTIFICO_1_1.md')
    for src in(r/'LEER_PRIMERO.md',r/'sistema/documentacion/GUIA_DE_USO_1_1.md'):copy(src,r/'entregas'/src.name)
    print(json.dumps({'families':len(v1['heritage_release']['families']),'profile_checks':len(read(a.second/'PERFILES_C/pruebas/RESULTADOS.json')['checks']),'all_originals_unchanged':True,'all_CSV_cells_preserved':True,'prior_controller_source_recovered':expected==reconstructed,'elapsed_seconds':elapsed}))
if __name__=='__main__':main()
