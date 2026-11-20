"""One PI11 scientific report from Root's explicit CLOSED final facts.

No DEE/Native/owner/Word import; no product write. --schema prints the minimal
input shape. --facts FILE --check is read-only. --write-report NEW_MD writes
the unique final report; optional --document-facts NEW_JSON makes the exact
content input for actualizar_documentos_PI11_R01.py, not a DOCX or new Manual.
It neither fills missing outcomes nor interprets pending trials as failures.
All scientific prose, including the400–600word opening, is closed by Root.
"""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import re

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
HISTORY = P / 'fuentes/CUERPO_HISTORICO_PARA_INFORME_PI11_R01.txt'
HISTORY_SHA = '56eba4dbe81bbf0a3a29ffd16ea7b9a729817a32b5bae9765e971714bb53da19'
CONTROL_LABELS = {'Documento', 'Corte de liberación registrado', 'Base principal', 'Estado de esta edición'}
ARM_FIELDS = ('role', 'label', 'life_id', 'status', 'requested', 'completed', 'attributed', 'physical',
              'FI_uses', 'certificate_reuses', 'native_ticks', 'source_ids', 'explanation')
OPENING_GUIDE = [
    'Párrafo1: organización, padre, hábitat, qué hizo y qué cambió realmente; corte del bloque frente al corte final.',
    'Párrafo2: decisión Native adicional y correspondencia preparada; oportunidad/calendario/RAW9ticks/certificado externo.',
    'Párrafo3: MAIN frente heredado, coste de FI y recursos separados, sin convertirlos en energía ni superioridad general.',
    'Párrafo4: reserva, retorno y controles efectivamente ejecutados; distinguir None bloqueado a0ticks de un resultado negativo.',
    'Párrafo5: núcleo conservado, reproducción, reapertura y adopción realmente comprobadas, con sus cortes distintos.',
    'Párrafo6: coste/pérdida/límites y punto continuable; sin anticipar agencia general o causa única de Q1episodio13.',
]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def nonempty(text):
    return isinstance(text, str) and bool(text.strip())


def regular(path):
    p = Path(path).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No linked source')
    need(p.is_file() and p.resolve().is_relative_to(R.resolve()), 'Existing DEE source required')
    return p.resolve()


def new_campaign_file(path):
    p = Path(path).absolute()
    need(not p.exists() and not p.is_symlink(), 'Existing output preserved')
    for node in p.parents:
        need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No linked output ancestor')
    need(p.parent.is_dir() and p.resolve().is_relative_to(P.resolve()), 'Output limited to existing PI11 campaign directories')
    return p


def no_placeholders(value):
    if isinstance(value, str):
        need('{{' not in value and '}}' not in value and not re.search(r'\bROOT:', value), 'Unclosed editorial placeholder')
    elif isinstance(value, dict):
        for v in value.values():
            no_placeholders(v)
    elif isinstance(value, list):
        for v in value:
            no_placeholders(v)


def validate(f):
    need(f.get('schema') == 'DEE.PI11.closed_report_facts.R01' and f.get('closed_for_report') is True,
         'Root must explicitly close actual facts; no provisional report publication')
    need(datetime.fromisoformat(f['cut_utc'].replace('Z', '+00:00')).tzinfo is not None, 'Actual timezone-aware cut required')
    life = f['selected_life']
    need(nonempty(life.get('life_id')) and life.get('N') == 67 and type(life.get('T')) is int
         and life['T'] >= 947395 and re.fullmatch('[0-9a-f]{64}', life.get('snapshot_sha256', '')),
         'Explicit real selected state required; unchanged PI10 is allowed')
    need(f.get('selection_status') in ('COMMITTED', 'UNCHANGED_COMMITTED', 'PRESERVED_NOT_ADOPTED'), 'Actual selection status required')
    opening = f.get('opening_paragraphs')
    need(isinstance(opening, list) and 4 <= len(opening) <= 8 and all(nonempty(t) for t in opening), 'Actual4..8opening paragraphs required')
    words = len(' '.join(opening).split())
    need(400 <= words <= 600, f'Opening must be400..600words, actual{words}')
    sections = f.get('sections')
    need(isinstance(sections, list) and 1 <= len(sections) <= 10, 'Explicit1..10final explained sections required')
    sources = f.get('sources')
    need(isinstance(sources, list) and sources, 'Decisive current evidence references required')
    source_map = {}
    for source in sources:
        need(set(source) == {'id', 'path', 'sha256', 'locator'} and nonempty(source['id']) and nonempty(source['locator']), 'Explicit source identity/hash/locator required')
        need(source['id'] not in source_map and re.fullmatch('[0-9a-f]{64}', source['sha256']), 'Duplicate/invalid source identity')
        need(sha(regular(source['path'])) == source['sha256'], 'Current evidence changed: ' + source['id'])
        source_map[source['id']] = source
    def links(values):
        need(isinstance(values, list) and values and all(v in source_map for v in values), 'Source IDs must resolve to exact current evidence')
    links(f.get('opening_source_ids'))
    for section in sections:
        need(nonempty(section.get('heading')) and isinstance(section.get('paragraphs'), list)
             and section['paragraphs'] and all(nonempty(t) for t in section['paragraphs']), 'Actual section prose required')
        links(section.get('source_ids'))
    arms = f.get('arms')
    need(isinstance(arms, list) and arms and len({a.get('role') for a in arms}) == len(arms), 'Distinct explicit arms required')
    for arm in arms:
        need(set(arm) == set(ARM_FIELDS) and nonempty(arm['label']) and nonempty(arm['explanation']), 'Explicit arm metrics/explanation required')
        links(arm['source_ids'])
        need(arm['status'] in ('executed_closed', 'blocked_before_Native', 'not_executed', 'preserved_partial'), 'Actual arm execution status required')
        for key in ('requested', 'completed', 'attributed', 'physical', 'FI_uses', 'certificate_reuses', 'native_ticks'):
            value = arm[key]
            need(value is None or type(value) is int and value >= 0, 'Exact metric or explicitNULL required: ' + key)
        if arm['status'] == 'executed_closed':
            need(all(type(arm[k]) is int for k in ('requested', 'completed', 'attributed', 'physical', 'FI_uses', 'certificate_reuses', 'native_ticks')),
                 'Executed arm must have measured complete denominators')
            need(arm['attributed'] <= arm['physical'] <= arm['completed'] <= arm['requested'], 'Arm opportunity/attribution denominators conflict')
        elif arm['status'] in ('blocked_before_Native', 'not_executed'):
            need(arm['native_ticks'] == 0 and arm['completed'] in (0, None)
                 and arm['attributed'] is None and arm['physical'] is None,
                 'Unavailable trial is not a cognitive0score; useNULLoutcomes')
    attribution = f.get('attribution_rows')
    need(isinstance(attribution, list) and attribution and all(set(row) == {'function', 'Native', 'assistance', 'domain', 'limit'}
         and all(nonempty(v) for v in row.values()) for row in attribution), 'Actual Native/assisted/domain attribution rows required')
    front = f.get('front')
    need(isinstance(front, dict), 'Current documentary front required')
    for key in ('edition_summary', 'principal_summary', 'functional_summary', 'conservation_summary', 'resume_summary', 'coverage_summary'):
        need(nonempty(front.get(key)), 'Actual front text required: ' + key)
    need(set(front.get('control_table', {})) == CONTROL_LABELS and all(nonempty(v) for v in front['control_table'].values()), 'Four exact documentary-control values required')
    need(sha(HISTORY) == HISTORY_SHA, 'Historical working text changed; inspect version before including')
    no_placeholders(f)
    return source_map, words


def cell(value):
    if value is None:
        return 'No ejecutado / no medido'
    return str(value).replace('|', '\\|').replace('\n', ' ')


def source_text(source):
    return source['id'] + ': ' + source['path'] + ' — ' + source['locator'] + '; SHA-256 ' + source['sha256']


def assemble(f, sources):
    out = ['# PI11 Hábitat persistente adaptación sistémica y cierre de etapa',
           'Corte documental: ' + f['cut_utc'], '## Síntesis científica', *f['opening_paragraphs'],
           'Fuentes: ' + ', '.join(f['opening_source_ids']), '## Resultados por trayectoria',
           '| Brazo | Estado | Solicitadas | Cerradas | Usos atribuibles | Entregas físicas | FI ejecutadas | Reusos | Ticks Native |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for a in f['arms']:
        out.append('| ' + ' | '.join(cell(v) for v in (a['label'], a['status'], a['requested'], a['completed'], a['attributed'], a['physical'], a['FI_uses'], a['certificate_reuses'], a['native_ticks'])) + ' |')
    out.extend(a['label'] + ': ' + a['explanation'] + ' Fuentes: ' + ', '.join(a['source_ids']) for a in f['arms'])
    out.extend(['## Atribución por función', '| Función | Contribución Native | Asistencia | Dominio | Límite |', '|---|---|---|---|---|'])
    for a in f['attribution_rows']:
        out.append('| ' + ' | '.join(cell(a[k]) for k in ('function', 'Native', 'assistance', 'domain', 'limit')) + ' |')
    for section in f['sections']:
        out.extend(['## ' + section['heading'], *section['paragraphs'], 'Fuentes: ' + ', '.join(section['source_ids'])])
    history = HISTORY.read_text('utf8').strip()
    history = history.replace('Los resultados PI11 se integrarán únicamente cuando estén cerrados.',
                              'Los resultados PI11 cerrados se presentan en los apartados anteriores con sus fuentes y límites.')
    history = history.replace('PI11 debe evaluar un hábitat persistente con cambios irregulares y transferir un enlace viable adicional a Native.',
                              'Ésa fue la frontera de partida de PI11; los apartados anteriores describen el hábitat y la transferencia de control realmente ejecutados.')
    history = history.replace('Cualquier ganancia final tendrá que distinguir sus costes, controles y núcleo conservado, sin atribuir al ente la secuencia elegida por el operador ni anticipar el resultado.',
                              'El cierre separa costes, controles y núcleo conservado; no atribuye al ente la secuencia elegida por el operador ni transforma resultados pendientes en logros.')
    out.extend(['## Trayectoria acumulativa y cierre de etapa', history,
                '## Fuentes decisivas y cobertura', f['front']['coverage_summary']])
    out.extend(source_text(source) for source in sources.values())
    return '\n\n'.join(out) + '\n'


def document_facts(f, sources, report):
    translated = [{'heading': s['heading'], 'paragraphs': s['paragraphs'],
                   'sources': [source_text(sources[k]) for k in s['source_ids']]} for s in f['sections']]
    metrics = [a['label'] + ': ' + a['explanation'] for a in f['arms']]
    manual_sections = [{'heading': 'Organización y resultado del cierre', 'paragraphs': f['opening_paragraphs'],
                        'sources': [source_text(sources[k]) for k in f['opening_source_ids']]}] + translated
    manual_sections.append({'heading': 'Comparación de trayectorias y ejecución real', 'paragraphs': metrics,
                            'sources': [source_text(s) for s in sources.values()]})
    compendium_sections = f.get('compendium_sections') or [manual_sections[0], manual_sections[-1], translated[-1]]
    return {'schema': 'DEE.PI11.final_document_facts.R01', 'internal_edition': '1.40',
            'closed_for_authoring': True, 'cut_utc': f['cut_utc'],
            'description': 'PI11 hábitat persistente y cierre acumulativo con resultados y asistencia delimitados',
            'selected_life': f['selected_life'], 'front': f['front'],
            'manual_sections': manual_sections, 'compendium_sections': compendium_sections,
            'evidence': [{'path': s['path'], 'sha256': s['sha256']} for s in sources.values()],
            'scientific_report': {'path': str(report.resolve()), 'sha256': sha(report)},
            'actual_authoring_marker_registered_by_root': bool(f.get('actual_authoring_marker_registered_by_root', False))}


def schema():
    return {'schema': 'DEE.PI11.closed_report_facts.R01', 'closed_for_report': False, 'cut_utc': 'ACTUAL_TIMEZONE_CUT',
            'selected_life': {'life_id': 'ACTUAL_SELECTED_LIFE', 'N': 67, 'T': None, 'snapshot_sha256': 'ACTUAL_HASH'},
            'selection_status': 'COMMITTED_OR_UNCHANGED_COMMITTED_OR_PRESERVED_NOT_ADOPTED',
            'opening_paragraphs': OPENING_GUIDE, 'opening_source_ids': ['S01'],
            'sections': [{'heading': 'Pregunta protocolo y resultados', 'paragraphs': ['ACTUAL_FINAL_PROSE'], 'source_ids': ['S01']}],
            'arms': [{k: None for k in ARM_FIELDS}],
            'attribution_rows': [{'function': 'ACTUAL_FUNCTION', 'Native': 'ACTUAL_CONTRIBUTION', 'assistance': 'ACTUAL_HOST_ROLE', 'domain': 'PROVEN_SCOPE', 'limit': 'ACTUAL_LIMIT'}],
            'sources': [{'id': 'S01', 'path': 'ABSOLUTE_EXISTING_EVIDENCE', 'sha256': 'ACTUAL_SHA256', 'locator': 'PRECISE_KEY_SECTION_OR_LINES'}],
            'front': {**{k: 'ACTUAL_TEXT' for k in ('edition_summary', 'principal_summary', 'functional_summary', 'conservation_summary', 'resume_summary', 'coverage_summary')},
                      'control_table': {k: 'ACTUAL_TEXT' for k in sorted(CONTROL_LABELS)}},
            'actual_authoring_marker_registered_by_root': False}


def main(args):
    if args.schema:
        print(json.dumps(schema(), ensure_ascii=False, indent=2)); return
    need(args.facts is not None, 'Explicit Root facts required')
    facts_path = regular(args.facts)
    input_sha = sha(facts_path)
    f = read(facts_path)
    sources, words = validate(f)
    if args.check or args.write_report is None:
        need(args.document_facts is None, 'Document facts require the newly written unique report')
        print(json.dumps({'valid_closed_facts': True, 'opening_words': words, 'read_only': True,
                          'sources': len(sources), 'Native_imported': False, 'Word_authored': False})); return
    report = new_campaign_file(args.write_report)
    docs = new_campaign_file(args.document_facts) if args.document_facts else None
    need(docs != report, 'Report and content facts are distinct artifacts')
    text = assemble(f, sources)
    need(sha(facts_path) == input_sha, 'Facts changed before report writing')
    with report.open('x', encoding='utf8', newline='\n') as out:
        out.write(text)
    if docs:
        value = document_facts(f, sources, report)
        with docs.open('x', encoding='utf8', newline='\n') as out:
            json.dump(value, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps({'report': str(report), 'bytes': report.stat().st_size, 'sha256': sha(report),
                      'opening_words': words, 'document_facts': str(docs) if docs else None,
                      'Native_imported': False, 'Word_authored': False, 'product_modified': False}, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--schema', action='store_true')
    ap.add_argument('--facts', type=Path)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write-report', type=Path)
    ap.add_argument('--document-facts', type=Path)
    main(ap.parse_args())
