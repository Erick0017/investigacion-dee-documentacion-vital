"""Finalize a NEW editorial input only from actual D COMMITTED and selected0.

No DOCX, product, Native, DEE, SQLite or approval action. The draft is literal.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

P = Path(__file__).resolve().parents[1]
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'

def require(ok, why):
    if not ok:
        raise ValueError(why)

def read(name):
    return json.loads((P / name).read_text('utf-8-sig'))

def ref(name):
    path = P / name
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    names = ('control/ADOPCION_D_PRODUCTO_PI09.json', 'control/REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09_R02.json')
    missing = [name for name in names if not (P / name).is_file()]
    if missing:
        print(json.dumps({'status': 'WAIT_ACTUAL_COMMITTED_AND_SELECTED0', 'missing': missing, 'output_written': False}))
        return
    adoption, selected = [read(name) for name in names]
    require(adoption.get('phase') == 'COMMITTED' and adoption.get('schema') == 'DEE.PI09.D.same_identity.adopted_product.R01' and adoption.get('life_id') == LIFE, 'Actual exact D COMMITTED proof required')
    require(selected.get('schema') == 'DEE.PI09.D.product_public0.reopening.R01' and selected.get('life_id') == LIFE, 'Exact actual D public reopening')
    require(all(selected.get(k) is True for k in ('selected', 'closed', 'owner_closed', 'physical_unchanged', 'operational_state_valid', 'stock_unchanged', 'Native_parent_unchanged')), 'Closed selected D with preserved physics, stock and parent')
    require(selected['new_ticks'] == selected['new_Native_inputs'] == 0 and selected['initial_tick'] == selected['final_tick'] == 922371, 'Selected0 has no material advance')
    require(selected['material_public_use_executed'] is False and all(selected['Native_field_equalities'].values()), 'No selected material use invented')
    stock = selected['stock_after']
    require(stock['D'] == {'ordinal': 7, 'total': 12, 'remaining': 5} and selected['stock_before'] == stock, 'Exact finite D stock')
    require(stock['R02'] == {'ordinal': 12, 'total': 18, 'remaining': 6} and stock['FI8'] == {'ordinal': 3, 'total': 8, 'remaining': 5} and stock['C2C'] == {'ordinal': 31, 'total': 32, 'remaining': 1}, 'Ancestral and current counters are distinct')
    combined = read('control/EVALUACION_COMBINADA_D_PI09_R01.json')
    require(combined['all_fixed_evidence_gates_met'] is True and all(g['satisfied'] for g in combined['gates'].values()), 'Actual six gates must be met; no approval is generated here')
    final_recalc = read('control/D_FINAL_RESULTADO_RECALCULO_R04.json')
    require(final_recalc['integrity_passed'] is True and final_recalc['Native_executed'] is False, 'Final copied evidence recalculated')
    d = read('documentos/HECHOS_FINALES_1_38_PI09_BORRADOR.json')
    require(d['closed_for_authoring'] is False and d['schema'] == 'DEE.PI09.final_document_facts.R02', 'Preserved draft only')
    d['closed_for_authoring'] = True
    d['selected_life_is_provisional_for_final_editorial_cut'] = False
    d['selected_material_function_test_pending'] = True
    d['selected_life'] = {'life_id': LIFE, 'N': 67, 'T': 922371,
                          'snapshot': selected['after_snapshot']['path'],
                          'snapshot_sha256': selected['snapshot_sha256'],
                          'historical_C1_main': {'life_id': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01', 'N': 67, 'T': 903603},
                          'stock': stock}
    d['cut_utc'] = selected['recorded_utc']
    require(datetime.fromisoformat(d['cut_utc'].replace('Z', '+00:00')).tzinfo is not None, 'Actual zoned cut')
    d['description'] = 'Edición 1.38: consulta condicional C1 y readaptación local D incorporadas mediante transferencia completa de la misma vida. D seleccionado en N67/T922371, con cinco ofertas D restantes. Crédito de consulta compartido; sin agencia general ni uso material posterior a COMMITTED.'
    d['front'] = {
        'edition_summary': 'Edición 1.38. C1: 12/12 usos útiles con ocho consultas. D: readaptación local 5/6 frente a 3/6 y 1/6, repetición material estricta y continuación útil. D incorporado y seleccionado en T922371.',
        'principal_summary': 'Principal único ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01, perfil fisica_directa, N67/T922371. Misma vida completa; hito C1 Native T903603 preservado como principal anterior. Sin fusión de memorias de controles ni reinicio desde T0.',
        'functional_summary': 'Dos selecciones Native dentro de una secuencia preparada enlazan información registrada y acción material. El contenido contribuye causalmente. D revisa la cadena compartida tras un fallo propio; no se aísla el crédito individual de preguntar ni se demuestra agencia general.',
        'conservation_summary': 'C1: dos clones con 12/12 más 5/5; la asistencia aritmética P0 no añadió ganancia. Tras D: panel 12/12 en T920520, seguido de un uso D útil hasta T922371. Las reaperturas de fuente y producto preservaron física, historia y stock a cero ticks.',
        'resume_summary': 'Continuar la vida existente mediante la interfaz principal o el gestor pausado. D está en 7/12, con cinco ofertas; FI8 en 3/8, con cinco; C2C en 31/32, con una. R02 ancestral conserva 12/18 como historia de sólo lectura en D. No iniciar una vida libre con --nueva.',
        'coverage_summary': 'Lectura dirigida de contratos, código y primarios decisivos; reutilización explícita de PI01–PI08. Se distinguen ejecución Native, recálculo portable, pruebas puras y preparación. No se declara una nueva lectura integral del corpus ni observación de todas las trayectorias.',
        'control_table': {
            'Documento': 'DCS11-MM-001 / Edición documental 1.38 / PI09',
            'Corte de liberación registrado': 'D COMMITTED y seleccionado: N67/T922371, ordinal 7/12. Último uso material EP6 anterior a COMMITTED; apertura pública posterior a cero ticks.',
            'Base principal': 'Manual completo 1.37 y Compendio preservados. Capítulo 54 nuevo; capítulos 1–53 y apéndices históricos literales.',
            'Estado de esta edición': 'Hechos cerrados para autoría después de seis gates, Source0, COMMITTED y selected0 reales. La publicación literal 1.38 y su QA visual se registran mediante comprobantes separados.'}}
    m = d['manual_sections']
    m[0]['paragraphs'] = [
        'El principal único efectivo es ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01, perfil fisica_directa, N67/T922371. Root completó la adopción COMMITTED de la vida entera y la reapertura pública seleccionada a cero ticks y cero entradas Native. Se conservan el prefijo causal, los bancos, las interfaces, la agenda, los recibos y los recursos. El movimiento administrativo no es aprendizaje ni mezcla de memorias.',
        'C1 Native T903603 queda preservado como principal anterior. Discovery procede de su copia postpanel T907543 y mantiene la genealogía C T884835, B y A de PI08. Su historial R02 de doce oportunidades sigue literal. La operación actual usa el contrato D; la API material ancestral R02 queda de sólo lectura en este sistema. Los controles permanecen en vidas separadas.']
    m[0]['sources'] = list(names) + ['control/ADOPCION_PRODUCTO_PI09.json', 'control/EVALUACION_COMBINADA_D_PI09_R01.json']
    m[4]['paragraphs'][1] = 'La receta de familia DRF también se ejecutó por el frente RP: preparación, seis episodios y estado final. Son ocho solicitudes y seis oportunidades, con 10136 ticks y 1139 entradas solicitadas: 1137 aplicadas y dos conflictos. Reprodujo cinco usos útiles y el primer fallo, sin ocultarlo. La comparación completa Native y de prefijo fue positiva; el registro posterior añadió cero ticks. Esta repetición representa la adquisición de seis casos. El panel y el uso posteriores del estado maduro tienen sus propios comprobantes y no se presentan como otra repetición independiente.'
    m[8]['paragraphs'].append('El recálculo final conserva los seis casos evaluados por brazo y separa un único uso futuro D real, EP6. Entre D5 y D6 hubo 2841 ticks de un panel anterior de doce funciones: sus trece primarios, plan y cierre están enlazados por hash y orden temporal. Ese intervalo añade historia física y no se cuenta como otra oportunidad D ni como aprendizaje D. Por ello, la utilidad posterior no aísla la retención frente a la experiencia intercalada.')
    supplement = read('control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json')
    require(supplement['applied'] is True and supplement['Native_ticks'] == supplement['Native_inputs'] == 0 and supplement['only_one_of_24_deployed_rows_changed'] is True and supplement['scientific_sources_and_all_other_registry_pins_unchanged'] is True, 'Actual narrow administrative registry supplement only')
    m[8]['paragraphs'].append('La primera apertura de D en producto se detuvo antes de solicitar estado o material: un pin del registro nombraba el alcance global Native en vez del alias ancestral D que ya existía. El intento y la conciliación de procesos se conservaron. Root aplicó un suplemento administrativo de un único pin entre veinticuatro filas, con cero ticks y cero entradas, sin cambiar los actores, sensores, calendarios, decodificadores ni el alcance global Native. Las aperturas posteriores efectivamente cerradas son los comprobantes de operatividad; el suplemento no se cuenta como readaptación ni reparación Native.')
    m[8]['sources'] += ['control/D_FINAL_RESULTADO_RECALCULO_R04.json', 'control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json', 'control/PROCESOS_D_TRAS_FALLO_CARGA_R02.json', 'control/REAPERTURA_D_PRODUCTO_PI09_R02.json', 'ensayos/PI09_D_PRODUCT0_UNSELECTED_R01_d8d93c91.stderr.txt']
    m[9]['paragraphs'] = [
        'La continuidad efectiva quedó seleccionada en D T922371. El lote D conserva ordinal 7/12 y cinco ofertas futuras; FI8 conserva 3/8 y cinco; C2C conserva 31/32 y una. R02 mantiene 12/18 y sus seis ofertas históricas, pero su interfaz material ancestral es de sólo lectura en D. Los recursos disponibles son finitos y no se reiniciaron contadores.',
        'El panel de doce funciones se comprobó en T920520. Después se reabrió y ejecutó un nuevo uso D ordinal 6: fue útil, con 190/190 entradas admitidas, FI+ y mensaje íntegro, hasta T922371. Su primera selección Native fue cero válido y produjo NoQuery material; no fue NULL. El panel no se repitió íntegro después de ese uso. Tampoco se ejecutó una nueva oportunidad material tras COMMITTED: las aperturas posteriores fueron estados públicos a cero ticks.',
        'C1 conserva su resultado histórico de doce oportunidades y su reproducción material. No se afirma que las doce situaciones antiguas sin la nueva guarda se hayan vuelto a aprobar después de D. La revisión útil demostrada es local y usa un retorno compartido, sin crédito individual de preguntar. WSLS quedó preparada sin ejecución material. El Manual 1.37 y sus capítulos se preservan literales; esta entrada autoriza la autoría de la edición 1.38, cuya publicación y validación visual requieren sus testigos separados.']
    m[9]['paragraphs'].extend([
        'Los comandos exactos se conservan en fuentes/COMANDOS_PUBLICOS_D_PI09_R01.txt y se revisaron contra el gestor real. Con C como raíz de DEE Cognitive 2.0, PY=C/motor/python313/python.exe, G=C/sistema/gestionar.py y D como la identidad Discovery indicada, la interfaz mantenida se abre con PY -I -B -X utf8 C/aplicacion/inicio.py --sistema --vida D. La GUI permite el acceso balance L R. No ofrece un atajo textual D_EP; ese uso se solicita por el gestor estructurado. No abrir dos propietarios a la vez.',
        'Para el gestor, en una terminal: PY -I -B -X utf8 G mente-unificada-iniciar --vida D --backend mente_unificada --eci01 --pausado --intervalo 60 --guardar-cada 3600 --max-segundos 1800. En la segunda, usar mente-unificada-pedir --vida D --id ID_NUEVO --situaciones \'[{"modo":"eci01-pi09-d-episodio"}]\' --retorno real --actuador closed --esperar 0; después mente-unificada-reanudar --vida D --id ID_CONTROL_NUEVO --esperar 30 y mente-unificada-resultado --vida D --id ID_NUEVO. Todos los subcomandos llevan el mismo prefijo PY -I -B -X utf8 G. Cada episodio consume una de las cinco ofertas D restantes.',
        'Mientras el resultado siga queued o processing, consultar con el mismo ID de tarea, sin volver a pedirla ni borrar la cola. Conservar failed_preserved y uncertain. Sólo después de resultado terminal coherente, pausar, guardar y detener mediante sus subcomandos mente-unificada-pausar, mente-unificada-guardar y mente-unificada-detener, con --vida D, IDs de control nuevos y --esperar 30. La reapertura usa iniciar otra vez con la misma vida. mente-unificada-estado lee el estado publicado; para una observación D nueva en el propietario se pide el literal [{"modo":"eci01-pi09-d-estado"}] con retorno omit. La ficha no ejecutó ningún episodio posterior a COMMITTED.'])
    m[9]['sources'] = list(names) + ['control/REAPERTURA_SOURCE_D_PI09_R01.json', 'control/PI09_PANEL_POST_D12_R03.json', 'control/PI09_D_RETENCION7_R03.json', 'control/D_FINAL_RESULTADO_RECALCULO_R04.json', 'fuentes/COMANDOS_PUBLICOS_D_PI09_R01.txt']
    for i in (0, 4, 8, 9):
        d['compendium_sections'][i] = {'heading': m[i]['heading'], 'paragraphs': [' '.join(m[i]['paragraphs'])], 'sources': list(m[i]['sources'])}
    d['pending_finalization'] = {'publication_1_38': 'Se registra separadamente tras autoría y publicación literal por Root',
                                 'visual_QA_1_38': 'No inferida del contenido XML; requiere testigo de intento y resultado real'}
    d['actual_finalization'] = {'six_D_gates_met': True, 'D_COMMITTED': True, 'selected_public_zero_reopening_passed': True,
                                'last_material_use': {'ordinal': 6, 'before_tick': 920520, 'after_tick': 922371, 'useful': True},
                                'full_panel_before_last_material_use': {'tick': 920520, 'correct': 12, 'total': 12},
                                'post_COMMITTED_material_use_executed': False,
                                'selected_material_function_test_pending': True,
                                'source0_snapshot_sha256': read('control/REAPERTURA_SOURCE_D_PI09_R01.json')['snapshot_sha256'],
                                'current_selected_snapshot_sha256': selected['snapshot_sha256'],
                                'query1_credit_isolated': False, 'general_agency_demonstrated': False}
    d['last_observed_D_material_cut'] = d.pop('last_observed_D_experimental_cut')
    d['last_observed_D_material_cut'].pop('not_yet_attributed_as_selected', None)
    d['last_observed_D_material_cut']['selected_after_unchanged_zero_reopening'] = True
    existing = {x['path'] for x in d['evidence']}
    for name in names + ('control/REAPERTURA_SOURCE_D_PI09_R01.json', 'control/EVALUACION_COMBINADA_D_PI09_R01.json', 'control/D_FINAL_RESULTADO_RECALCULO_R04.json', 'control/D_FINAL_PORTABLE_R04/INDICE_D_PI09_R04.json', 'fuentes/COMANDOS_PUBLICOS_D_PI09_R01.txt', 'control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json', 'control/PROCESOS_D_TRAS_FALLO_CARGA_R02.json', 'control/REAPERTURA_D_PRODUCTO_PI09_R02.json', 'ensayos/PI09_D_PRODUCT0_UNSELECTED_R01_d8d93c91.stderr.txt'):
        r = ref(name)
        if r['path'] not in existing:
            d['evidence'].append(r)
            existing.add(r['path'])
    # Editorial spacing only. Identifiers, localizers and hashes are preserved.
    replacements = {'sinfallo': 'sin fallo', 'nofallo': 'no fallo', 'NoFail,': 'NoFail,', 'Manual1.37': 'Manual 1.37', 'publicación1.38': 'publicación 1.38', 'capítulo54': 'capítulo 54'}
    for group in ('manual_sections', 'compendium_sections'):
        for section in d[group]:
            section['paragraphs'] = [text for text in section['paragraphs']]
            for j, text in enumerate(section['paragraphs']):
                for old, new in replacements.items():
                    text = text.replace(old, new)
                section['paragraphs'][j] = text
    for item in d['evidence']:
        require(ref(Path(item['path']).relative_to(P))['sha256'] == item['sha256'], 'Final evidence drift')
    output = P / 'documentos/HECHOS_FINALES_1_38_PI09.json'
    require(not output.exists(), 'Final editorial input is new; preserve drafts')
    output.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'file': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'closed_for_authoring': True,
                      'DOCX_or_Native_executed': False, 'draft_preserved': True}, ensure_ascii=False))

if __name__ == '__main__':
    main()
