"""Directed source-to-mechanism inventory; never runs historic campaigns."""
from pathlib import Path
import hashlib
import json

EXT = Path(__file__).resolve().parents[1]
BASE = EXT.parents[1]

ROWS = [
 ('lexical', ['src/linguistic.py', 'resultados/language_D01/MEASUREMENTS.json'],
  'Emparejamiento físico, dirección adquirida, señal sola y acceso toroidal de ocho formas.',
  'Ocho formas de dos clases direccionales durante tres rondas; nuevas consultas pueden cambiar la historia.',
  '¿Qué conserva un repertorio mayor y qué relaciones de otra clase requieren otra representación?',
  'Capacidad nueva 8/16/32/65 y controles de historia; diversidad semántica en cohortes identificadas.'),
 ('compound', ['src/compound.py', 'resultados/compound_reuse_D01/MEASUREMENTS.json'],
  'Acumulación físicamente acoplada con respaldos adquiridos por experiencias adicionales.',
  'Cuatro contribuciones sucesivas; cadena 37→44→60→76→83; costo de redundancia explícito.',
  '¿Pueden conservarse tipos de relación diferentes y acceder a ellos sin buscador externo?',
  'A1–A4 en panel común; retención y combinación con papeles y contexto declarados.'),
 ('graphs', ['src/network.py'],
  'Portadores aprendidos en rutas de un único Runtime; encuentros seriales y componentes en paralelo.',
  'Cuatro etapas producen 73 y ocho 165 en sus casos; no unidades de profundidad conceptual.',
  '¿Dos, tres o cuatro agrupaciones usan información local distinta ante una consulta?',
  'Canal intacto/cortado, historia ausente, papeles invertidos y combinación reservada.'),
 ('relative_bridge', ['src/heterobridge.py', 'src/heterogeneous.py'],
  'Interfaz móvil hacia comparador de un cuerpo relativo aprendido; coexistencia de familias.',
  'Historia AB/BA cambia signo de expresión ante portador común; puerto ocupado no implica olvido.',
  '¿Qué distingue memoria, acceso y función al unir clases de representación?',
  'Historia opuesta, desacoplada y offpath con el mismo lector y posterior consulta.'),
 ('regulation', ['src/regulation_forks.py'],
  'Contrastes explícitos en forks completos y sham; pulso direccional adquirido.',
  'Corte selectivo del pulso cambia consecuencia conservando MAIN; no política elegida por recompensa.',
  '¿Una regulación aprendida puede conservar acceso al incorporar otras relaciones?',
  'Distinguir fuente externa, interna preparada, estado adquirido y selección por consecuencias.'),
 ('CPC4_ABCD', ['referencias/cpc4_red/regulated_session.py', 'referencias/cpc4_red/dual_session.py'],
  'Comunicación contextual A/B/C/D y contraflujo externo fijado; consecuencias posteriores por v27.',
  'Agenda de neutralizador y geometría preparadas; preservación de recibos y metadata.',
  '¿Qué cambia al distribuir memoria y contexto entre compuestos?',
  'Referencia breve pertinente, sin reejecutar todo CPC4 ni trasladar resultados a CPC5 por nombre.'),
 ('CPC4_relative', ['referencias/cpc4_relative/dual_sustained.py', 'referencias/cpc4_relative/sustained_regulation.py'],
  'Historia relativa y acceso renovado con cuerpos físicos y clocks continuos.',
  'Memoria diferencial y expresión son mediciones separadas; contexto y fase importan.',
  '¿Qué conocimiento queda utilizable con experiencias nuevas y espera?',
  'Consulta previa y posterior con rechazo, silencio y relación medida como estados distintos.'),
 ('SEM01', ['referencias/sem01/participant.py', 'referencias/sem01/experiment.py'],
  'Asociación por colisión y consultas con interfaces fijas.',
  'Historias opuestas y desacopladas delimitan dependencia de experiencia; geometría preparada.',
  '¿La señal puede asociarse después de la función y conservar participantes/orden?',
  'Distinguir adquisición nueva, réplica técnica y exposición adicional para enseñar un nombre.'),
 ('instrument', ['referencias/producto4/PRODUCT_CONTRACT.json', 'referencias/producto4/organizational.hpp',
                 'referencias/producto4/kernel_v27.cpp', 'referencias/producto4/API_AND_SCOPE.md'],
  'OrganizationRecipe.research, Runtime único, interfaces declaradas y persistencia integral.',
  'WHL/PYD oficiales4.0 congelados; API_AND_SCOPE heredado conserva título3.5 y no se corrige el original.',
  '¿Las nuevas preparaciones mantienen física, continuidad y procedencia?',
  'Verificar versión/hash, entradas reales, save/load en otro proceso y observación sin mutación.'),
 ('NSM', ['referencias/NSM65_CATALOGO_CPC4.json'],
  'Inventario lingüístico65 con formas españolas, fuentes y dimensiones independientes de evidencia.',
  'Catálogo completo no demuestra65significados; el corte anterior conserva aproximaciones finitas.',
  '¿Qué versión operacional tiene adquisición, retención, uso, comunicación y composición?',
  'Matriz65 completa con pruebas independientes; no agrupar automáticamente conceptos por una señal.')
]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): h.update(block)
    return h.hexdigest()


def main():
    parent = json.loads((EXT/'PARENT_MEMBERS.json').read_text(encoding='utf-8'))
    inherited = {row['path']: row for row in parent['members']}
    rows = []
    for id, paths, mechanism, inherited_result, question, test in ROWS:
        files = []
        for name in paths:
            path = BASE/name
            if not path.is_file(): raise FileNotFoundError(path)
            member = 'CPC5/'+name; actual = sha(path)
            assert inherited[member]['sha256'] == actual, 'Frozen selected source differs'
            files.append({'member': member, 'bytes': path.stat().st_size, 'sha256': actual,
                          'parent_byte_exact': True})
        rows.append({'id': id, 'selected_sources': files, 'mechanism_reused': mechanism,
                     'inherited_result_and_limits': inherited_result, 'new_question': question,
                     'planned_new_test': test, 'new_scientific_result_claimed_here': False})
    result = {'schema': 'CPC5.extension.directed-source-matrix.v1',
              'parent_archive_sha256': parent['sha256'], 'rows': rows,
              'scope': 'Directed inherited source inventory, not a new execution or re-reading of the complete corpus',
              'hierarchy': 'code/states → controls/telemetry → contracts → synthesis',
              'external_sources': 'NSM bibliography is inherited with hashes and citations; no new linguistic inventory invented'}
    target = EXT/'revision/SOURCES.json'; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'rows': len(rows), 'selected_members': sum(len(r['selected_sources']) for r in rows),
                      'sha256': sha(target)}, ensure_ascii=False))


if __name__ == '__main__': main()
