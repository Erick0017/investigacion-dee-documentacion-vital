"""Synchronize the existing campaign diary after actual document publication.

This does not touch the principal, motor, selectors or experiments.
"""
from pathlib import Path
import datetime, hashlib, json
P = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    publication = P/'documentos/DOCUMENTOS_PUBLICADOS_PI06_1_33.json'
    proof = json.loads(publication.read_text(encoding='utf8'))
    assert proof['status'] == 'PUBLISHED_LITERAL_STRUCTURALLY_VERIFIED'
    assert proof['protected_operational_equal'] is True
    assert proof['documents']['Manual']['published']['sha256'] == '55f77c470b2b442e8fce341dd0eb9d669a6e8e565d35b9ca9f3236f34459922d'
    diary = P/'REGISTRO_CAMPANA.json'
    oldbytes = diary.read_bytes()
    m = json.loads(oldbytes)
    assert m['Native_ticks_closed'] == 7882 and m['latest_closed_science']['diagnostic_worlds'] == 12
    assert 'documentary_close_PI06' not in m
    m['manual_at_campaign_start_internal_edition'] = m['manual_internal_edition']
    m['manual_internal_edition'] = '1.33'
    m['phase'] = 'SCIENCE_CLOSED_DOCUMENTS_PUBLISHED_ANALYSIS_PACKAGE_IN_PREPARATION'
    m['documentary_close_PI06'] = {
        'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'publication':str(publication),'publication_sha256':sha(publication),
        'Manual':proof['documents']['Manual']['published'],
        'Compendium':proof['documents']['Compendium']['published'],
        'prior_registry_sha256':hashlib.sha256(oldbytes).hexdigest(),
        'principal_promoted':False,'principal_Native_ticks':0,
        'new_capability_attribution':'Experimental instruments and operator-assisted P0 procedures, not a new principal skill.',
        'visual_QA':'NOT_VALIDATED: LibreOffice soffice.exe unavailable; actual attempts and structural proof preserved.'}
    assert diary.read_bytes() == oldbytes
    diary.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    home = P/'entrega';home.mkdir(exist_ok=True)
    guide = home/'00_LEER_PRIMERO.txt'
    with guide.open('x',encoding='utf8') as f:
        f.write('''DEE PI06 — ORGANIZACIÓN, ACCESO Y REPRODUCCIÓN
Corte real: 10 de noviembre de 2026, America/Mexico_City.

DECISIÓN
Se conserva el único principal ECI02_PI03_REPRO_PI04_PI05_MAIN_01,
fisica_directa, N67, T824911, COMMITTED. Su padre físico es ECI02_PI03_MAIN
T775355. No se añadió una regulación adquirida ni se promocionó un clon.
El principal no recibió nuevas consultas o ticks durante PI06.

QUÉ APORTA ESTE EXPEDIENTE
Se ejecutaron 7.882 ticks Native entre doce mundos diagnósticos completos.
Una contribución situada altera la comparación y vuelve a interferir tras
un acierto intermedio. El contraflujo legal recupera el resultado frente a
sham, pero lo prepara el operador. Su recuperación es P0, no iniciativa del
ente. Una nube fija amplifica actividad; su primer cruce del umbral de
seguridad se localiza en +15. No se midió FI/C2C en las ramas con nube.
El control sin nube sí produjo un producto C2C real; su plan se conserva
como FAILED_PRESERVED porque el paso excedió el límite local previsto.

INCORPORACIÓN EFECTIVA
Cognitive dispone de los prefijos completos, código exacto, contrato,
catálogo y recetas PI06. R01 fue reproducida realmente con el motor desde
una copia fría: 600 ticks, 529/529 entradas y signos −/+/−, una de tres
respuestas pertinente. R02 está preparada y sus requisitos fueron
verificados estáticamente; su nueva reproducción fría sigue pendiente.
La receta de nube R03 está bloqueada. R04 conserva IDs históricos fijos.
Estos estados no deben confundirse con un aprendizaje nuevo del principal.

DOCUMENTOS
02_MANUAL contiene copias literales completas del Manual Cognitive vigente,
edición interna 1.33 (nombre compatible terminado en Edicion_1_21), y del
Compendio actualizado. Se preservaron literalmente capítulos 1–48 y
apéndices. La estructura DOCX fue comprobada; el render real falló por
ausencia de LibreOffice soffice.exe. No se validó visualmente la paginación.

ORDEN DE LECTURA
01_INFORME_CIENTIFICO.md; 03_MAPAS/CONTINUIDAD_PI06.json y matriz;
capítulo 49 del Manual; controles y primarios en 04_EVIDENCIAS.
Los protocolos y versiones usadas permanecen en 06_CODIGO. Las omisiones
y localizadores completos se detallan en 05_CONTROL.

RECÁLCULO DEL ZIP, SIN DEE
Desde la extracción, con Python y un archivo de salida nuevo:
python -I -B 05_RECALCULO/RECALCULAR_PRIMARIOS_PI06.py --raiz . --salida resultado_PI06_nuevo.json
El bundle GLOBAL_PORTABLE reconstruye los RAW/clocks registrados y verifica
sus hashes; sus huecos no se interpolan. Las fuentes incluyen recálculos
separados de D7, la cota del source y el testigo local de copia. Un recálculo
no ejecuta el motor ni reproduce una adquisición.

USO LOCAL DESDE COGNITIVE
Desde la raíz del producto, estos modos sólo listan o verifican:
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad listar
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad verificar pi06_interrupcion_causal_y_sham_R02
El uso material requiere receta, variante, ID diagnóstico nuevo y destino
vacío explícitos. No actuar sobre MAIN, reutilizar IDs ni ejecutar fuentes
del ZIP indiscriminadamente. El lanzamiento normal permanece en
ABRIR_DEE_COGNITIVE.bat; PI06 no lo abrió ni modificó.

ALCANCE DE LA ENTREGA
Este ZIP es un expediente de análisis, no un respaldo operativo ejecutable.
Los estados completos, SQLite, colas, artefactos, recursos, capturas
originales y dependencias oficiales permanecen localmente con sus
manifiestos y rutas. El código y datos de evaluación no alimentan al ente.
No se borraron originales, no se modificaron Universe v27/Thinking 4.5.0
y no se publicó material en servicios externos.
''')
    print(json.dumps({'diary':str(diary),'diary_sha256':sha(diary),
                     'guide':str(guide),'guide_sha256':sha(guide),'Native_ticks':0},ensure_ascii=False))

if __name__ == '__main__':
    main()
