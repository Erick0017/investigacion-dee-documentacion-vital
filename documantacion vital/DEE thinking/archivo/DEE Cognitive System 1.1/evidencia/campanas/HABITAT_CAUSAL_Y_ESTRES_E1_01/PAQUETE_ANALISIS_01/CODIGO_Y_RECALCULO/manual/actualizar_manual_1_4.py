"""Edit the retained manual without modifying it; content only, no native ticks."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from docx import Document
from docx.shared import RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_text(paragraph, text: str):
    # Keep the paragraph style and first run formatting of the retained source.
    runs = paragraph.runs
    if runs:
        runs[0].text = text
        for run in runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--habitat-text', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replace-sha256')
    args = parser.parse_args()
    root = args.root.resolve()
    original = root / 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx'
    before = sha(original)
    if args.output.exists() and (not args.replace_sha256 or sha(args.output) != args.replace_sha256):
        raise FileExistsError('Existing output requires its exact previous SHA-256 for an identified revision.')
    document = Document(original)
    baseline_count = len(document.paragraphs)
    if baseline_count != 290:
        raise ValueError(f'Unexpected source paragraph count {baseline_count}')
    p = document.paragraphs
    replacements = {
        8: 'DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.4  |  DCS11-MM-001',
        9: 'Corte documental actualizado: 21 de octubre de 2026\nPredeterminado protegido: E1_SOCIAL_11, T3154',
        15: 'La edición original se basó en el resumen funcional y las fuentes consignadas en sus apéndices. Esta edición integra los cambios operativos posteriores de Español Funcional 01, Paisaje Causal 01, Acceso Adaptativo 01 y Auditoría Retrospectiva 01, junto con el corte de Hábitat identificado en la sección nueva. Los resultados pertenecen a las vidas y controles indicados; no se suman como conocimientos del predeterminado.',
        16: 'El manual no sustituye los snapshots completos ni los contratos ejecutables. La incorporación editorial no repite las simulaciones históricas ni cambia el motor. Los estados y comprobantes de cada campaña prevalecen sobre una descripción desactualizada. La validación visual de esta edición se registra por separado.',
        96: '6. Estados del corte original y vida preferente',
        113: 'Para operar se necesita sistema/ con sus dependencias compatibles y los estados completos de las vidas seleccionadas. Los ZIP de análisis, resúmenes y este manual no reemplazan esos archivos. Reutilice el entorno instalado cuando funcione; no reinstale para un cambio documental.',
        114: 'Conserve el estado protegido y bifurque antes de experimentar. Una nueva instalación o traslado sólo corresponde cuando se necesita otro entorno; las instrucciones históricas siguientes no obligan a repetir una instalación válida.',
        144: 'Conservar sólo RAW/clocks o mediciones parciales no permite reponer interfaces, entradas pendientes y progreso operativo ausentes. Los paquetes de análisis CPC9, EF01, PC01, AA01, retrospectivo y Hábitat no son por su nombre respaldos completos de las vidas.',
        174: '16. Pendientes reales y mecanismos de deterioro',
        200: 'El software permanece 1.1.0 sobre DEE thinking 4.5.0 y v27. Este libro tiene edición documental 1.4. Una nueva vida no cambia automáticamente el perfil; una arquitectura nueva no continúa exactamente otra vida. La edición original y sus addenda se conservan como genealogía.',
        202: 'El Manual Maestro vigente se conserva directamente en la raíz DEE Cognitive System 1.1/, junto a sistema/, laboratorio/, evidencia/ y entregas/. Esta ubicación sustituye la sugerencia anterior de guardarlo sólo en sistema/documentacion/. Los cambios editoriales no justifican repetir física no afectada ni volver a empaquetar todo el sistema.',
        205: 'La edición 1.4 integra la continuidad posterior al corte inicial, corrige el alcance de información perdida y acceso, distingue instrumentos de capacidades y documenta el corte de Hábitat. No cambia el pasado de ninguna vida ni promueve por sí misma una rama.',
    }
    for index, text in replacements.items():
        replace_text(p[index], text)
    # Keep the control table; distinguish the original release from this edition.
    for row in document.tables[0].rows:
        if row.cells[0].text == 'Documento':
            row.cells[1].text = 'DCS11-MM-001 / Edición documental 1.4'
        elif row.cells[0].text == 'Base principal':
            row.cells[1].text = 'Manual original 1.0, addenda 1.1 a 1.3 y corte Hábitat 01'
        elif row.cells[0].text == 'Estado de esta edición':
            row.cells[1].text = 'Actualización documental; no modifica el software ni los estados físicos'
    # Insert the integrated current section immediately before the appendices.
    anchor = next(q for q in document.paragraphs if q.text == 'Apéndice A. Inventario de las 73 entradas')
    def add(text, style='Normal'):
        return anchor.insert_paragraph_before(text, style)
    add('21. Continuidad integrada y Hábitat causal', 'Heading 1')
    add('El activo protegido sigue siendo E1_SOCIAL_11 T3154. Una rama posterior con más ticks no lo reemplaza automáticamente. E1_ESPANOL_01 T28012, ES01_LATE_ACCESS29_passive T36403, las ramas PC01 y E1_ACCESO_ADAPTATIVO_01 T47146 conservan futuros propios. Sus snapshots no son piezas para fusionar recuerdos. La ficha de cada campaña identifica el corte real, el padre, las entradas pendientes y las operaciones utilizables.')
    add('Español y funciones actuales', 'Heading 2')
    add('Español Funcional investigó cerca/lejos respecto de un marco físico preparado, más/menos mediante magnitudes y referencia adquirida, e igual con acceso contextual intermitente. Toca/no toca distingue contacto y trayecto libre en cuerpos concretos; no toca no demuestra negación general. La transmisión de un código pudo modificar un receptor y permitir uso posterior, sin convertirlo en una mente completa. No se demostraron YO/TÚ funcionales, conversación libre ni 65 significados.')
    add('Paisaje Causal delimitó transformaciones de lectores, confluencias, fases y ocupaciones locales. Las ramas amplias protegidas PC01_CONTINUIDAD28_far_guard/far_divert T39752 preservan un panel finito. PC01_NORMALIZADO45 T41318 utiliza un lector preparado posterior a una transformación; no interpreta por ello cualquier escena nueva. PC01_RETENCION40_guard/divert T44635 y E1_PAISAJE_01 T44300 conservan ganancias y pérdidas. Ninguna es una ganadora universal.')
    add('Acceso adaptativo y asistencia', 'Heading 2')
    add('Acceso Adaptativo consiguió, en un aparato finito, que consecuencias anteriores modificaran el estado que seleccionó la ruta de una consulta genérica. Las oportunidades, la transducción de consecuencias y los tiempos siguen preparados. Esto delimita una revisión local de acceso por consecuencias, no una política general R2, diagnóstico autónomo del fallo, elección de cuándo consultar o de interlocutor.')
    add('En AA40/46 el contenido había sido adquirido originalmente en dos soportes. Tras fallar el lector de uno, una nueva enseñanza del acceso, sin repetir ese contenido, permitió usar el otro. Omitir o cortar el soporte y omitir la enseñanza de acceso impidió ese uso; los controles sham lo mantuvieron. La recepción inmediata no demuestra retención ilimitada. E1_ACCESO_ADAPTATIVO_01 T47146 conserva el fallo tardío real; las ramas AA01_ACCESO_LISTO_plus/minus T45857 mantienen nueve entradas pendientes cada una y no son ese futuro final. Las ramas receptoras 14/21 tienen dominios propios.')
    add('Información perdida y observación', 'Heading 2')
    add('La auditoría retrospectiva no avanzó vidas. En AA13 las historias convergieron en campos físicos y protocolo futuro, pero el diario del propietario aún conservaba la carga enseñada. Leer ese diario no es memoria del ente; el uso posterior requirió reenseñanza. En el encuentro tardío de MAIN, retirar una contribución produjo el mismo estado físico global posterior: se delimitó la pérdida de esa contribución, no la desaparición de toda la información histórica. Otras diferencias persistentes no acreditan acceso funcional si ningún mecanismo nativo las utilizó.')
    add('Los tramos continuos registrados establecen retornos espaciales concretos, no retorno del microestado completo. Los huecos de registro impiden atribuir un linaje único hasta cualquier encuentro tardío. Las lecturas CPC9 de 57/65, 53/65 y 4/65 corresponden a formas físicas; el control NO_NEW omitía intentos docentes, no todas las consultas. Ocupación, carga interna y consumo eléctrico no son magnitudes equivalentes.')
    add('La operación inspeccionar-snapshot es una herramienta del auditor: lee archivos y compara campos, agenda y secciones operativas sin restaurar o avanzar el mundo. El atlas y los cálculos no alimentan respuestas de E1. Silencio, rechazo y lectura fuera de fase no se traducen automáticamente como NO.')
    add('Uso y continuidad', 'Heading 2')
    add('Se utiliza el gestor existente y sus guías ESPANOL_FUNCIONAL_01, PAISAJE_CAUSAL_01 y ACCESO_ADAPTATIVO_01. Bifurcar conserva el prefijo y crea otro futuro; restaurar no crea un individuo vacío. Las consultas materiales se contabilizan en la vida que las recibe. Los estados listos se bifurcan antes de consumir oportunidades. Una interrupción sin guardado completo no autoriza a presentar un puntero anterior como el estado alcanzado.')
    add('Hábitat causal y estrés', 'Heading 2')
    if args.habitat_text:
        habitat = args.habitat_text.read_text(encoding='utf-8')
        for paragraph in habitat.split('\n\n'):
            if paragraph.strip():
                add(paragraph.strip())
    else:
        raise ValueError('The final Habitat text is mandatory; no placeholder is authored.')
    add('Fuentes de esta actualización', 'Heading 2')
    add('Addendum Español Funcional 01; addendum consolidado EF01/PC01 edición 1.1; addendum EF01/PC01/AA01 edición 1.2; addendum retrospectivo edición 1.3; fichas de continuidad correspondientes; resultados e índice de evidencia HABITAT_CAUSAL_Y_ESTRES_E1_01. Las fuentes, contratos y snapshots completos se conservan localmente. El análisis transportable no reemplaza los estados necesarios para continuar.')
    for name in ('Title', 'Subtitle', 'Heading 1', 'Heading 2'):
        style = document.styles[name]
        style.font.color.rgb = RGBColor(0, 0, 0)
    for paragraph in document.paragraphs:
        if paragraph.style.name in ('Title', 'Subtitle', 'Heading 1', 'Heading 2'):
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(0, 0, 0)
    # Existing TOC lines are static. Add a current-section locator without an invented page.
    for paragraph in document.paragraphs:
        if paragraph.style.name == 'TOCline' and '\t' in paragraph.text:
            replace_text(paragraph, paragraph.text.split('\t', 1)[0])
    toc_anchor = next(q for q in document.paragraphs if q.text.startswith('Apéndice A. Inventario') and q.style.name == 'TOCline')
    toc_anchor.insert_paragraph_before('21. Continuidad integrada y Hábitat causal    antes del apéndice A', 'TOCline')
    settings = document.settings.element
    update = settings.find(qn('w:updateFields'))
    if update is None:
        update = OxmlElement('w:updateFields')
        settings.append(update)
    update.set(qn('w:val'), 'true')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document.save(args.output)
    after = sha(original)
    if before != after:
        raise RuntimeError('The retained original changed unexpectedly.')
    check = Document(args.output)
    record = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'original': str(original), 'original_sha256': before,
        'output': str(args.output.resolve()), 'output_sha256': sha(args.output),
        'original_unchanged': before == after,
        'previous_candidate_sha256': args.replace_sha256,
        'paragraphs': len(check.paragraphs), 'tables': len(check.tables),
        'sections': len(check.sections), 'authoring': 'actual DOCX edit from retained source',
        'render_and_visual_review': 'not established by this authoring script',
        'static_toc_page_numbers': 'removed because the updated pagination is unverified; section names remain',
    }
    verification = args.output.with_suffix('.edicion.json')
    verification.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
