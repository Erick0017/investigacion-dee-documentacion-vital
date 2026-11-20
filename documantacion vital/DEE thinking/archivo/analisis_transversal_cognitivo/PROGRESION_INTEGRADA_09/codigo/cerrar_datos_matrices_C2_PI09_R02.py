"""Actual final capability/gap rows after D COMMITTED and selected0, no Native."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import runpy

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'

def read(name):
    return json.loads((P / name).read_text('utf-8-sig'))

def sha(name):
    return hashlib.sha256((P / name).read_bytes()).hexdigest()

def main():
    ap = 'control/ADOPCION_D_PRODUCTO_PI09.json'
    sp = 'control/REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09_R02.json'
    if not all((P / p).is_file() for p in (ap, sp)):
        print(json.dumps({'status': 'WAIT_ACTUAL_D_COMMITTED_AND_SELECTED0', 'output_written': False}))
        return
    a, s = read(ap), read(sp)
    assert a['phase'] == 'COMMITTED' and a['schema'] == 'DEE.PI09.D.same_identity.adopted_product.R01' and a['life_id'] == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
    assert s['selected'] and s['closed'] and s['owner_closed'] and s['stock_unchanged'] and s['physical_unchanged']
    assert s['new_ticks'] == s['new_Native_inputs'] == 0 and s['final_tick'] == 922371 and not s['material_public_use_executed']
    assert s['stock_after']['D'] == {'ordinal': 7, 'total': 12, 'remaining': 5}
    runpy.run_path(str(H / 'preparar_datos_matrices_C2_PI09_R01.py'), run_name='PI09_final_closed_base_rows')
    data = read('codigo/DATOS_MATRICES_C2_PI09_R01.json')
    table, gaps = data['tables']
    headers = table['headers']
    rows = [dict(zip(headers, row)) for row in table['rows']]
    by = {r['id']: r for r in rows}
    by['C01'].update(capacidad='Hito C1 incorporado, hoy principal anterior', despues='Native PI09 N67 T903603, conservado íntegro al incorporar D', estado='HISTORICO_COMMITTED_PRESERVADO', limite='La continuidad seleccionada actual es D T922371; R02 material ancestral queda de sólo lectura en D')
    by['C06'].update(capacidad='Función del corte histórico C1', estado='EQUIVALENCIA_HISTORICA_COMPROBADA', limite='STATE0 fue directo; C1 EP11 útil está en su historia. No atribuir otro ensayo de las doce situaciones antiguas al corte D')
    by['D01_real']['estado'] = 'ADOPTADO_D_ALCANCE_FINITO'
    for arm in ('none', 'yoked'):
        by['D01_' + arm]['estado'] = 'CONTROL_CERRADO_NO_ADOPTADO'
    by['D05'].update(limite_adquisicion='Control externo con una señal negativa; no política Native aprendida', limite='Posición de la señal prefijada; una sola historia por brazo, sin optimizar la permutación')
    def add(identity, capability, before, after, status, tick, num, den, basis, p0, p1, acquisition, source, pointer, limit):
        row = dict.fromkeys(headers, '')
        row.update(id=identity, capacidad=capability, antes=before, despues=after, estado=status,
                   corte_tick=tick, numerador=num, denominador=den, base_constatacion=basis,
                   asistencia_P0=p0, uso_P1=p1, limite_adquisicion=acquisition,
                   credito_query1_aislado=False, agencia_P2_general_demostrada=False,
                   fuente=source, localizador_JSON=pointer, sha256=sha(source), limite=limit)
        rows.append(row)
    add('D06', 'Conservación posterior a los seis D evaluados', 'D Real seis casos hasta T917679', 'Panel histórico 12/12, 947/947 Applied, hasta T920520', 'EJECUTADO_NATIVE_EN_MISMA_VIDA', 920520, 12, 12,
        'Cierre, trece primarios, plan y ventana enlazados; recálculo R04', 'Pausa de hábitat y lectores históricos declarados', 'Uso de doce funciones conservadas', 'No es otra oportunidad ni aprendizaje D',
        'control/PI09_PANEL_POST_D12_R03.json', '/closed', 'El panel ocurrió antes del uso D futuro; no se afirma un panel nuevo completo en T922371')
    add('D07', 'Uso D futuro después del panel y reapertura', 'Seis casos evaluados; D ordinal 6', 'EP6 útil, primera choice0 válida NoQuery, FI+ y mensaje11 íntegro; 190/190 Applied', 'USO_FUTURO_SEPARADO_DE_EVALUACION', 922371, 1, 1,
        'Primario material posterior y testigo inmediato recalculados desde copias', 'Nuevo suministro futuro declarado antes del ensayo; misma secuencia', 'Continuación física útil de la misma vida', 'No vuelve a puntuar los seis casos evaluados',
        'control/PI09_D_RETENCION7_R03.json', '/closed', 'Entre EP5 y EP6 hubo experiencia de panel; la retención no queda aislada de ese intervalo')
    add('D08', 'Continuidad seleccionada final', 'Source D útil en T922371', 'Transferencia completa de misma identidad, COMMITTED y reapertura pública seleccionada0', 'ACTUAL_COMMITTED_Y_SELECCIONADO', 922371, None, None,
        'Estado público0 directo; función material previa más igualdad completa del prefijo causal', 'Movimiento completo, permisos externos y comprobación de estado', 'Disponibilidad operativa finita sin consumo posterior', 'La administración no es aprendizaje',
        sp, '/Native_field_equalities', 'No hubo oportunidad material después de COMMITTED; el snapshot administrativo corriente puede diferir del de la promoción')
    add('D09', 'Reproducción material D por familia DRF', 'Fuente Discovery T907543', 'Seis episodios, 5/6 útiles y primer fallo preservado, 10136 ticks; comparación estricta positiva', 'CLI_NATIVE_REPLAY_REAL_REGISTRADO', 917679, 5, 6,
        'Receta real: PREPARE+6EP+STATE, ocho solicitudes;1139 entradas,1137 Applied y2 conflictos', 'Binding administrativo acotado; cuerpo D literal', 'Mismo futuro físico/causal observado', 'Repetición técnica de la adquisición; no nuevas muestras independientes',
        'control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json', '/registered', 'No reproduce como otra muestra el panel y uso posteriores del estado maduro')
    add('D10', 'Recursos públicos finitos actuales', 'Lotes preservados, sin reinicio', 'D7/12:5 futuras; FI8 3/8:5; C2C31/32:1; R02 12/18 histórico readonly', 'ESTADO_PUBLICO_DIRECTO_CERO_TICKS', 922371, 5, 12,
        'Contadores antes y después del estado seleccionado idénticos', 'Oferta ambiental explícita y permisos P0', 'Continuar recursos disponibles sin crear una vida nueva', 'No capacidad de suministro inagotable',
        sp, '/stock_after', 'Las seis ofertas históricas R02 no se habilitan como material ancestral en D; usar sólo las rutas actuales permitidas')
    table['rows'] = [[r.get(h, '') for h in headers] for r in rows]
    gh = gaps['headers']
    grows = [dict(zip(gh, row)) for row in gaps['rows']]
    gb = {r['id']: r for r in grows}
    gb['G01'].update(cobertura='D COMMITTED y estado público seleccionado0 en T922371', fuente=sp, localizador='/Native_field_equalities', sha256=sha(sp), hueco_o_limite='No nuevo uso material tras COMMITTED; función final observada antes por EP6 e igualdad causal completa', conclusion_permitida='D es la continuidad operativa actual en el alcance finito comprobado')
    gb['G11'].update(cobertura='Seis gates reales y adopción Root COMMITTED', fuente=ap, localizador='/phase', sha256=sha(ap), tipo_lectura='Decisión efectiva y comprobante de incorporación leídos', hueco_o_limite='Revisión de cadena compartida local, sin crédito query1 individual ni agencia general', conclusion_permitida='D actual incorporado; C1 permanece como historia y principal anterior')
    for values in (
        ['G12', 'Intervalo real entre D5 y D6', 'Panel exacto 917679 a920520,2841ticks y947 entradas', 'control/D_FINAL_RESULTADO_RECALCULO_R04.json', '/interleaved_non_D/0', sha('control/D_FINAL_RESULTADO_RECALCULO_R04.json'), 'Recálculo portable de13primarios literales y plan/cierre', 'La experiencia intercalada puede contribuir al estado futuro; no se atribuye a D ni se borra', 'Uso futuro útil observado después de historia adicional certificada'],
        ['G13', 'Último corte material y apertura corriente', 'EP6 útil a922371 y selected0 sin avance', sp, '/material_public_use_executed', sha(sp), 'Apertura pública real0 y comprobantes materiales anteriores', 'Estado0 no constituye otro ensayo material; el panel12 antecede aEP6', 'Disponibilidad al corte por función material observada e igualdad causal'],
        ['G14', 'Stock ancestral y operativo', 'D7/12,FI8 3/8,C2C31/32;R02 12/18 readonly', sp, '/stock_after', sha(sp), 'Estados públicos exactos y sin consumo', 'Recursos finitos; no prometer --nueva libre ni repetir stock agotado', 'Continuación actual con cinco ofertas D y cinco FI8, más una C2C'],
        ['G15', 'Corrección de carga administrativa D', 'Primer intento detenido antes de STATE; suplemento aplicado de un pin entre 24, cero ticks y entradas', 'control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json', '/applied', sha('control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json'), 'Comprobante CAS aplicado y fallo original preservado', 'Corrige nombre de alcance en registro; actores y alcance global Native intactos, sin reparación ni aprendizaje Native', 'Operatividad sustentada por las reaperturas reales posteriores, no por el suplemento solo']):
        grows.append(dict(zip(gh, values)))
    gaps['rows'] = [[r.get(h, '') for h in gh] for r in grows]
    # Whitespace corrections affect authored prose only, never paths or hashes.
    phrases = {'hasta T':'hasta T', 'a920520':'a 920520', 'a922371':'a 922371', '2841ticks':'2841 ticks', '947 entradas':'947 entradas', 'de13primarios':'de 13 primarios', 'aEP6':'a EP6', 'D7/12':'D 7/12', 'FI8 3/8':'FI8 3/8', 'C2C31/32':'C2C 31/32', 'R02 12/18 readonly':'R02 12/18 de sólo lectura', '1137 Applied y2':'1137 Applied y 2', 'solicitudes;1139':'solicitudes; 1139', 'choice0':'choice 0', 'mensaje11':'mensaje 11', 'seleccionada0':'seleccionada 0', 'pública0':'pública 0'}
    for t in data['tables']:
        for row in t['rows']:
            for col, head in enumerate(t['headers']):
                if head in ('fuente', 'localizador_JSON', 'localizador', 'sha256', 'id') or not isinstance(row[col], str):
                    continue
                for old, new in phrases.items():
                    row[col] = row[col].replace(old, new)
    data['recorded_utc'] = datetime.now(timezone.utc).isoformat()
    data['selected_D_actual'] = {'life_id': s['life_id'], 'N': 67, 'T': 922371, 'snapshot_sha256': s['snapshot_sha256'], 'stock': s['stock_after']}
    data['selected_material_function_test_pending'] = True
    out = H / 'DATOS_MATRICES_C2_PI09_R01.json'
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'FINAL_SOURCE_ROWS_READY', 'file': str(out), 'sha256': sha(out.relative_to(P)), 'rows': [len(t['rows']) for t in data['tables']], 'Native_executed': False}))

if __name__ == '__main__':
    main()
