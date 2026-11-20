"""Revisión editorial mínima del Manual Maestro 1.21 sobre una copia.

No ejecuta el motor, no escribe estados y no sustituye el Word canónico.
Root debe registrar el inicio de edición con el marcador de documentos y
renderizar/comprobar el resultado antes de copiarlo a su ubicación vigente.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re
import shutil

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

W = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("reorganizar_dee_manual", W / "reorganizar_dee.py")
reorg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reorg)
ROOT = reorg.ROOT.resolve()
APP = ROOT / "DEE Cognitive 2.0"
NAME = "DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx"
SOURCE = APP / NAME
BACKUP = W / "manual_original_1_21.docx"
OUTPUT = ROOT / "archivo/_edicion/manual.docx"
REVISION = "Revisión de organización del 28 de octubre de 2026"
VIDEO = "archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4"
VIDEO_SHA = "312cdd7b58f951e61ef75a8ad3bfc6244e3d3f5b34d3ad82dff36b8095d03f14"
SNAPSHOT_SHA = "3ad3e16b772e8ea44a7814c197651d4cb8d841c8739a1950ad2f0e6953884b8f"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replace_paragraph(p, text):
    """Conserva estilo y propiedades del párrafo; sólo sustituye su prosa."""
    prototype = deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
    for child in list(p._p):
        if child.tag != qn("w:pPr"):
            p._p.remove(child)
    run = p.add_run(text)
    if prototype is not None:
        run._r.insert(0, prototype)


def internal_link(paragraph, text, anchor):
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), anchor)
    hyperlink.set(qn("w:history"), "1")
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "24333B")
    properties.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.append(underline)
    run.append(properties)
    value = OxmlElement("w:t")
    value.text = text
    run.append(value)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_bookmark(document, paragraph, name):
    identifiers = [int(element.get(qn("w:id"))) for element in document.element.iter(qn("w:bookmarkStart"))]
    identifier = str(max(identifiers, default=0) + 1)
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), identifier)
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), identifier)
    # Mantener pPr primero y los extremos alrededor del contenido del título.
    paragraph._p.insert(1 if paragraph._p.pPr is not None else 0, start)
    paragraph._p.append(end)


def chapter_numbers(document):
    values = []
    for paragraph in document.paragraphs:
        if paragraph.style.name == "Heading1" or paragraph.style.name == "Heading 1":
            match = re.match(r"^(\d+)(?:[. ]|$)", paragraph.text)
            if match:
                values.append(int(match[1]))
    return values


def latest_proof():
    events = reorg.read().get("prueba_operativa_aislada", {}).get("eventos", [])
    begin = max((i for i, e in enumerate(events) if e.get("etapa") == "previo"), default=0)
    recent = events[begin:]
    by_stage = {}
    for event in recent:
        by_stage[event["etapa"]] = event
    completed = (by_stage.get("resultado", {}).get("status") == "COMPLETED_WITH_READER_RESULT_RECORDED"
                 and by_stage.get("original_restituido", {}).get("original_unchanged") is True)
    return recent, by_stage, completed


def update():
    if (ROOT / "archivo/_resguardo_operativo").exists():
        raise RuntimeError("La prueba aislada sigue protegiendo el original; espere su cierre antes de editar el manual")
    assert SOURCE.is_file(), SOURCE
    source_sha = sha(SOURCE)
    if BACKUP.exists():
        assert sha(BACKUP) == source_sha, "El respaldo exacto ya existe con otros bytes; no se sobrescribe"
    else:
        shutil.copy2(SOURCE, BACKUP)
        assert sha(BACKUP) == source_sha
    document = Document(BACKUP)
    original_table_count = len(document.tables)
    original_chapters = chapter_numbers(document)
    assert original_chapters == list(range(1, 38)), original_chapters
    paragraphs = list(document.paragraphs)
    assert len(paragraphs) == 960, "La edición fuente cambió; comprobar parches por localizador antes de continuar"
    assert paragraphs[272].text.startswith("El Manual Maestro vigente se conserva directamente en la raíz DEE Cognitive System 1.1/")
    assert paragraphs[880].text.startswith("videos/DEE_Cognitive_2_0_Presentacion.mp4")
    assert paragraphs[58].style.name == "TOCline" and paragraphs[58].text.startswith("37 ")
    assert paragraphs[884].text.startswith("Apéndice A.")
    project = read(APP / "PROYECTO.json")
    life = read(APP / "sistema/estado/vidas/DEE20_DEMO_01/VIDA.json")
    assert project["selected_life"] == life["life_id"] == "DEE20_DEMO_01"
    assert life["world_id"] == "DEE20_DEMO_01" and life["physical"]["N"] == 67
    assert life["physical"]["tick"] == 697764 and life["snapshot_sha256"] == SNAPSHOT_SHA
    recent, proof, completed = latest_proof()

    replace_paragraph(paragraphs[9],
        "Edición documental 1.21, revisión de organización del 28 de octubre de 2026. "
        "Para el uso actual consulte los capítulos 37 y 38. ABRIR_DEE_COGNITIVE.bat permite elegir presentación, sistema o manual. "
        "La vida seleccionada sigue siendo DEE20_DEMO_01, guardada en T697764; la reorganización no añade aprendizajes ni cambia su identidad.")
    replace_paragraph(paragraphs[15],
        "Se conservan los capítulos 1 a 37, sus tablas, campañas y apéndices. El capítulo 38 actualiza organización, dependencias y continuidad, "
        "sin repetir las investigaciones. El capítulo 37 distingue la captura completa de DEE20_DEMO_01 de la presentación editorial actual, "
        "que también contiene resultados de aparatos independientes. La edición documental no cambia thinking 4.5.0 ni Universe v27.")
    replace_paragraph(paragraphs[272],
        "El Manual Maestro vigente se conserva directamente en DEE thinking/DEE Cognitive 2.0/, junto al lanzador y las carpetas operativas "
        "aplicacion/, motor/ y sistema/. La carpeta anterior DEE Cognitive System 1.1/ permanece íntegra bajo DEE thinking/archivo/. "
        "Su manual y sus estados conservan valor histórico; no sustituyen la selección operativa vigente. Los cambios editoriales no justifican repetir física no afectada ni reconstruir el sistema.")
    replace_paragraph(paragraphs[277],
        "DCS11-MM-001 es el mismo Manual Maestro lógico. Su edición vigente 1.21 se identifica en la raíz de DEE Cognitive 2.0; "
        "la revisión de organización del 28 de octubre de 2026 se describe en el capítulo 38. Las ediciones previas y las distribuciones históricas "
        "permanecen recuperables en archivo. Esta revisión documental no crea otra versión del motor ni fusiona las vidas de paquetes distintos.")
    replace_paragraph(paragraphs[859],
        "La vida de la grabación completa original y de su versión explicada es DEE20_DEMO_01, perfil fisica_directa, N67. "
        "Se importó una vez el par completo de APD05_MAIN T684418, sin preparación desde T0 ni fusión de recuerdos, y su trayectoria alcanzó T697764. "
        "DEE20_PRUEBA_TECNICA_01 es otra vida y no se suma a esos aprendizajes. La presentación editorial actual incluye también G07 y U0, "
        "aparatos independientes que se identifican por separado; sus resultados no pertenecen por ello a DEE20_DEMO_01.")
    replace_paragraph(paragraphs[880],
        "La presentación recomendada se conserva en " + VIDEO + ", con ruta relativa a DEE thinking. "
        "Dura 315,633333 segundos, aproximadamente 5 min 15,633 s; SHA-256 " + VIDEO_SHA + ". "
        "Combina escenas y datos existentes de DEE20_DEMO_01 y de G07 y U0 independientes. Las leyendas, acercamientos y edición explican la evidencia; "
        "no son una sola trayectoria física ni latencias instantáneas, y no enseñan contenido nuevo al ente. La presentación es opcional: su ausencia no impide abrir Cognitive.")

    # Identificación localizada; ninguna sustitución global de rutas o historia.
    identification = document.tables[0]
    replacements = {
        "Documento": "DCS11-MM-001 / Edición documental 1.21 / Revisión de organización 28 de octubre de 2026",
        "Corte de liberación registrado":
            "Corte físico conservado: DEE20_DEMO_01, T697764, N67. Padre de importación APD05_MAIN, T684418. "
            "La revisión editorial del 28 de octubre de 2026 no avanza ese estado. CONTINUIDAD_DEE_COGNITIVE_2_0.json y la ficha de la vida localizan el estado completo.",
        "Base principal":
            "Mismo documento lógico DCS11-MM-001. Se conserva exactamente el Word 1.21 recibido antes de esta revisión. "
            "Capítulos 1 a 37 y apéndices preservados; el capítulo 38 y los ajustes operativos localizados describen la organización actual.",
        "Estado de esta edición":
            "Edición documental 1.21 con revisión de organización 28 de octubre de 2026. Revisión de organización verificada sobre copia operativa; "
            "maquetación revisada en Word. El registro técnico conserva el alcance y las correcciones. No constituye una nueva versión de Cognitive, thinking o Universe.",
    }
    for row in identification.rows:
        if row.cells[0].text in replacements:
            replace_paragraph(row.cells[1].paragraphs[0], replacements[row.cells[0].text])
    for section in document.sections:
        for paragraph in section.header.paragraphs:
            if "DEE COGNITIVE 2.0" in paragraph.text and "MANUAL MAESTRO" in paragraph.text:
                replace_paragraph(paragraph, "DEE COGNITIVE 2.0  |  MANUAL MAESTRO  |  ED. 1.21  |  REV. 28 OCT 2026")
        # Los campos PAGE/NUMPAGES del pie permanecen intactos.

    anchor = paragraphs[884]._p
    toc = document.add_paragraph(style="TOCline")
    internal_link(toc, "38 Organización vigente y continuidad", "DCS11_reorganizacion_38")
    paragraphs[58]._p.addnext(toc._p)
    # El índice original agotaba la página 3 y su salto quedaba solo en la4.
    # Repartir entradas1–22 / 23–38 y apéndices llena esa página 4 y mantiene el
    # comienzo del capítulo 1 en la 5; se conserva el salto final del índice.
    continuation = document.add_paragraph("Índice de consulta continuación", style="Heading 2")
    continuation.paragraph_format.page_break_before = True
    paragraphs[44]._p.addprevious(continuation._p)

    def add(text, style="Normal"):
        paragraph = document.add_paragraph(text, style=style)
        anchor.addprevious(paragraph._p)
        return paragraph

    heading38 = add("38 Organización vigente y continuidad", "Heading 1")
    add_bookmark(document, heading38, "DCS11_reorganizacion_38")
    add("Revisión documental del 28 de octubre de 2026. Esta actualización organiza el uso y la conservación del proyecto. "
        "No es otra campaña científica, no cambia el kernel ni el producto oficial 4.5 y no añade recuerdos a ninguna vida.")
    add("38 1 Distribución del proyecto y excepción conservada", "Heading 2")
    add("La organización prevista de DEE thinking comprende cuatro unidades: 4.5 conserva intactos el producto y sus manuales oficiales; "
        "DEE Cognitive 2.0 contiene el sistema que se utiliza; CPC - Experimentos y mecanismos reúne el compendio acumulativo; "
        "archivo conserva los antecedentes, distribuciones y producción audiovisual. Archivar cambia la ubicación, no elimina investigación, código, estados ni genealogías.")
    add("Existe una excepción real: casos practicos continúa en la raíz porque Windows rechazó su traslado con error 5 de acceso, "
        "también fuera del entorno restringido. Se conserva en su lugar y no se fuerza la operación. Por tanto, no debe describirse la raíz como si ya contuviera únicamente cuatro carpetas. "
        "Los materiales de esa carpeta siguen siendo localizables y no se declaran trasladados.")
    add("El compendio científico se encuentra en CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx. "
        "Su índice forma parte del mismo documento. Explica mecanismos, controles, alcance e individuos a partir de los expedientes existentes; "
        "no es una tabla de respuestas accesible a DEE ni sustituye el estado operativo de una vida.")
    add("38 2 Estado vigente y vidas separadas", "Heading 2")
    add("La selección ordinaria de la aplicación se obtiene de PROYECTO.json y es DEE20_DEMO_01, T697764, N67. "
        "Su padre de importación es APD05_MAIN, T684418; el snapshot guardado conserva SHA-256 " + SNAPSHOT_SHA + ". "
        "La reorganización no selecciona por fecha un futuro distinto, no importa de nuevo la semilla y no cambia los recuerdos para facilitar una prueba.")
    add("El almacén operativo conserva por separado DEE20_DEMO_01 y DEE20_PRUEBA_TECNICA_01. Abrir la segunda no acredita las experiencias de la primera. "
        "E1_SOCIAL_11 y los cortes de las campañas anteriores permanecen en los expedientes archivados con sus estados y límites; "
        "no se convierten en conocimientos actuales de DEE20_DEMO_01 por compartir código o manual.")
    add("El estado operativo incluye el snapshot completo, la ficha de vida, interfaces, progreso, entradas pendientes, SQLite, recibos, colas y protocolos. "
        "sistema/estado no se recorta por considerar sus registros mera telemetría. Una captura RAW/clocks, un resumen, un video o el manual por separado no permiten continuar toda la organización.")
    add("38 3 Abrir utilizar guardar y continuar", "Heading 2")
    add("ABRIR_DEE_COGNITIVE.bat", "Code")
    add("El menú sigue ofreciendo presentación, sistema y manual. La presentación es opcional y su traslado al archivo no bloquea ABRIR DEE COGNITIVE. "
        "El lanzador PowerShell prefiere motor/python313/python.exe incluido y la vida seleccionada por PROYECTO.json. "
        "No reinstala componentes, no busca silenciosamente otro binario parecido y no crea una vida vacía si falta el corte esperado.")
    add("Dentro de la aplicación, Abrir / Continuar carga la misma vida y arranca su propietario pausado. Vivir permite evolucionar; Pausar física, Guardar y Detener tienen efectos distintos. "
        "Espere el recibo terminal de una operación antes de cerrar. Si hay un ID pendiente o incertidumbre, consulte el mismo ID; no reenvíe la experiencia. "
        "Para experimentar sobre una copia, preserve todo el par operativo y su identidad de bifurcación; no mezcle archivos de futuros diferentes.")
    add("palabra luma --retorno omit --actuador nulled", "Code")
    add("Esta petición finita es un ejemplo de consulta material, no observación pasiva. El retorno se omite y el actuador externo queda anulado de forma explícita; "
        "la respuesta nativa y sus rechazos deben leerse en sus recibos. No promete una respuesta correcta en cualquier fase ni dominio. "
        "Las tareas con herramientas o efectos externos conservan sus contratos; no se habilitan por el mero hecho de abrir la interfaz.")
    add("38 4 Construcción de copias y dependencias declaradas", "Heading 2")
    add("La unidad emparejada completa de APD04 se copió desde el expediente 1.1 archivado para conservar disponible el constructor que la requiere. "
        "El par completo de APD05 ya existente también se conserva. Copiar esos paquetes no importa ninguna vida ni transfiere su conocimiento al individuo seleccionado. "
        "El constructor debe respetar los manifiestos, identidades y contratos de cada corte y declarar una nueva copia cuando se utilice.")
    add("Para uso ordinario se mantienen aplicacion, motor, sistema y el Manual Maestro vigente. El motor oficial y sus dependencias locales no se duplican ni recompilan. "
        "Los manuales técnicos oficiales permanecen en la carpeta hermana 4.5, intacta. El archivo histórico contiene el sistema 1.1 anterior y sus evidencias, "
        "pero su procedencia no se presenta como una importación necesaria para cada respuesta actual.")
    add("La modalidad externa de Hábitat conserva una dependencia especial de Python 3.12 y sus paquetes en una caché local del equipo. "
        "No se instaló otro entorno durante esta reorganización ni se certifica autosuficiencia absoluta de todos los perfiles. "
        "La apertura ordinaria y la prueba finita descrita aquí no ejecutan ese trabajador externo. Una distribución a otro equipo debe resolver explícitamente esa dependencia si pretende utilizar dicho perfil.")
    add("38 5 Verificación del traslado y límites de esta revisión", "Heading 2")
    if completed:
        opening = proof.get("primera_apertura_N0", {})
        saved = proof.get("corte_guardado", {})
        reopened = proof.get("segundo_proceso_N0", {})
        query = proof.get("consulta_nueva_sobre_copia", {})
        result = proof["resultado"]
        before_tick = opening.get("physical", {}).get("tick")
        after_tick = saved.get("physical", {}).get("tick")
        answer = query.get("reader", {}).get("formed_native_command")
        add("Se comprobó una copia aislada completa desde otra ubicación, con bases SQLite copiadas coherentemente y cero solicitudes no terminales del servicio seleccionado. "
            "El original estuvo temporalmente resguardado para impedir una lectura accidental desde su ubicación habitual y después se restituyó sin intercambiarle el estado evolucionado de la copia.")
        add("La copia abrió pausada en T" + str(before_tick) + ", con identidad, RAW y clocks iguales al corte inicial. "
            "Se ejecutó la única consulta nueva documentada, se guardó un corte en T" + str(after_tick) + " y otro proceso abrió exactamente ese estado sin avanzar ticks, "
            "sin importación desde T0 y conservando vida y padre. El original permanece T697764. La nueva historia pertenece exclusivamente a la copia de prueba.")
        add("La consulta finita produjo comando nativo " + str(answer) + "; su calificación registrada fue "
            + ("válida dentro del lector ensayado" if result.get("response_qualified") else "no calificada por el lector ensayado")
            + ". Los recibos y campos decisivos permanecen en REGISTRO_REORGANIZACION.json, bajo archivo/reorganizacion_20261028, "
            "y los estados y logs de la copia permanecen en archivo/_prueba_aislada. No se ocultaron errores de instrumentación ni se repitieron las campañas científicas para esta comprobación.")
    else:
        failures = [e for e in recent if e.get("etapa") in {"fallo_prueba_copia", "cierre_copia_no_confirmado"}]
        detail = (failures[-1].get("type", "") + ": " + failures[-1].get("detail", "")) if failures else "No consta un cierre completo de la prueba en el registro vigente."
        add("El registro vigente no acredita una verificación operativa completa del traslado. Se conserva el alcance realmente ejecutado y la excepción: " + detail
            + ". No se declara superada la reapertura entre procesos ni una nueva capacidad a partir de una comprobación incompleta. "
            "La ficha de vida original y el registro técnico indican el corte que debe preservarse.")
    add("La revisión es operativa y documental. No vuelve a medir todas las capacidades históricas, no prueba episodios externos, no crea aprendizaje nuevo y no convierte "
        "la recuperación de una señal finita en comprensión general del español. Las conclusiones científicas de cada capítulo conservan sus propios controles, dominios e individuos. "
        "Si una operación queda bloqueada, se conserva su estado y se informa la excepción; la limpieza visual de carpetas nunca prevalece sobre continuidad o evidencia.")

    properties = document.core_properties
    properties.title = "DEE Cognitive 2.0 Manual Maestro Edición 1.21 Revisión de organización 28 de octubre de 2026"
    properties.subject = "Uso local y continuidad de vidas existentes; reorganización documental sin cambio del motor"
    properties.last_modified_by = "INVESTIGACION DEE"
    properties.modified = datetime.now(timezone.utc)
    properties.revision = properties.revision + 1
    properties.comments = "Mismo documento lógico DCS11-MM-001 y edición 1.21. Revisión de organización del 28 de octubre de 2026; original exacto preservado."
    assert chapter_numbers(document) == list(range(1, 39))
    assert len(document.tables) == original_table_count
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    reopened = Document(OUTPUT)
    assert chapter_numbers(reopened) == list(range(1, 39))
    assert len(reopened.tables) == original_table_count
    assert sha(SOURCE) == source_sha == sha(BACKUP)
    assert reopened.paragraphs[0].text == paragraphs[0].text
    print("Copia editorial creada:", OUTPUT)
    print("Original exacto preservado:", BACKUP, "SHA256", source_sha)
    print("Capítulos 1 a 38; tablas originales:", original_table_count)
    print("Prueba operativa leída del registro:", "completada" if completed else "incompleta o pendiente")
    print("Pendiente root: renderizar, inspeccionar y sólo después sustituir el Word canónico; este script no lo sustituye.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--autorizar-edicion", action="store_true", help="Ejecutar sólo después del marcador de operación documental")
    args = parser.parse_args()
    if not args.autorizar_edicion:
        print("Código de edición preparado. No se ha escrito ningún DOCX.")
    else:
        update()
