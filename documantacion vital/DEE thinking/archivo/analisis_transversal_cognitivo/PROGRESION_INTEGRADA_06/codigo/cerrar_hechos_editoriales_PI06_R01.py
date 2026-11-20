"""Root review of frozen scientific facts, before authoring the existing DOCX.

Changes prose, not experiments. No DEE import or operational mutation.
"""
from pathlib import Path
import datetime, hashlib, json

P = Path(__file__).resolve().parents[1]

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    source = P/'control/CIERRE_CIENTIFICO_PI06_BORRADOR.json'
    target = P/'control/CIERRE_CIENTIFICO_PI06.json'
    raw = source.read_bytes()
    if sha(raw) != '111f7b051bdab755d7c3f8f0219c9bbc9724ec67f513aa15f15bedea58f0af44':
        raise ValueError('The reviewed scientific draft changed')
    if target.exists():
        raise FileExistsError('Never replace closed scientific facts')
    m = json.loads(raw)
    assert m['Native_ticks_all_branches'] == 7882 and m['diagnostic_worlds'] == 12
    m['schema'] = 'DEE.PI06.scientific_document_closure.ROOT.R01'
    m['closed_for_authoring'] = True
    m['root_review_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    m['reviewed_frozen_draft_sha256'] = sha(raw)
    m['cover_summary'] = ('Edición 1.33. PI06 confirma una interferencia material situada y una recuperación asistida P0; reproduce su trayectoria adversa y caracteriza la expansión de una nube preparada. No demuestra regulación adquirida ni promueve otra vida. El principal continúa siendo ECI02_PI03_REPRO_PI04_PI05_MAIN_01, N67, T824911.')
    m['resume1'] = ('El único principal sigue siendo ECI02_PI03_REPRO_PI04_PI05_MAIN_01, perfil fisica_directa, N67, T824911, COMMITTED. Su padre físico es ECI02_PI03_MAIN, T775355. PI06 protege su estado y las guardas heredadas; las experiencias de los controles no se suman a esta vida.')
    m['resume2'] = ('PI06 cerró 7.882 ticks Native entre doce mundos diagnósticos. Una contribución izquierda produce tres signos sucesivos −/+/−, frente a +/+/+ sin ella o con sham. La reserva cambia carga, datos y espera, y conserva esa diferencia. Se demuestra accesibilidad dependiente del paisaje, sin atribuir autorregulación al acierto intermedio.')
    m['resume3'] = ('El contraflujo legal recupera la comparación frente a su sham, por intervención externa. La nube general supera el umbral de soporte en el paso 15; ambas ramas con nube se detienen por seguridad antes de FI/C2C. El control sin nube produce una comparación y un producto C2C reales, pero su paso C2C excede el límite local previsto: ese ensayo conserva su estado FAILED_PRESERVED.')
    m['resume4'] = ('Reanudación: capítulo 49, informe y mapas de PROGRESION_INTEGRADA_06, junto con los recursos estables de reproducibilidad. La trayectoria transitoria tiene reproducción Native fría comprobada; la receta de contraflujo está preparada con requisitos verificados, la nube permanece bloqueada y R04 conserva IDs históricos fijos. Recálculo, restauración y adquisición son modalidades distintas.')
    m['release_cut'] = ('Corte científico del 10 de noviembre de 2026: 7.882 ticks y doce mundos diagnósticos. Se preserva el principal PI05 en T824911, con sus dos recursos C2C todavía disponibles. Los futuros adversos y el control útil permanecen separados. Universe v27 y Thinking 4.5.0 siguen congelados.')
    m['state_of_edition'] = ('La edición interna 1.33 añade PI06 al mismo Manual rector. Conserva literalmente los capítulos 1–48 y los apéndices, y actualiza el frente de continuidad. El nombre operativo terminado en 1_21 se mantiene por compatibilidad. La publicación documental no constituye una promoción del ente.')
    m['review_scope'] = ('Revisión dirigida sobre las coberturas PI01–PI05: primarios D7 y ensayos 20X/21X recuperados de cápsulas, fundamentos pertinentes y contratos de evolución, observación y persistencia. Se distingue lectura de texto/XML, recálculo, ejecución Native y reproducción fría. No se declara una nueva lectura integral del corpus ni revisión visual de documentos que no se pudieron renderizar.')
    m['core_description'] = ('PI06: interferencia situada, recuperación asistida P0, reproducción Native de una trayectoria adversa, expansión de una nube preparada y una restricción estática localizada del source. No hay sucesor adoptado ni regulación adquirida demostrada. Principal PI05 N67 T824911 preservado; 7.882 ticks en doce mundos y desviación local de protocolo documentada.')
    paragraphs = [
        [
            'PI06 estudia qué organización produce la dinámica DEE y qué funciones sostiene o recupera sin que el investigador coloque una solución particular tras cada fallo. Distingue persistencia o relajación, regulación endógena, regulación adquirida y flexibilidad cognitiva. Una densidad estable, una valencia negativa o un acierto temporal no bastan para demostrar las otras propiedades.',
            'La base de los ensayos es una copia completa y coherente del principal PI05 en N67, T824911, snapshot SHA-256 af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832. El comprobante de cierre verifica ACTIVO, VIDA y snapshot críticos iguales antes y después. No afirma inmutabilidad de todo el árbol. Las guardas heredadas siguen presentes y las nuevas experiencias pertenecen exclusivamente a sus ramas diagnósticas.'
        ],
        [
            'El primario D7 recuperado de la cápsula del libro de Procesamiento Nativo registra un retorno de cinco descriptores en un mundo N48 denso, tras eliminar externamente RAW y clocks en un 5 % de los sitios elegibles. El otro finalista N32 ya estaba vacío. Se recalcularon 28/28 distancias, con error máximo de 2,78×10⁻¹⁷. D7 no midió una función cognitiva recuperada ni igualdad del microestado.',
            'HOLISTICREPAIR20X, TRAINEDREPAIR21X y HOMEOSTATICMEMBRANE21X conservaron resultados negativos en otras preparaciones v25: doce condiciones, cuatro condiciones y seis condiciones de ocho ciclos, respectivamente. El resumen EA3 inspeccionado contiene doce condiciones con sondas y ningún baseline funcional interpretable. Sus versiones, edades, observables y limitaciones se conservan por separado; no son réplicas de D7 ni aprendizajes del principal.',
            'La prueba estática del source oficial kernel_v27.cpp, SHA-256 fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31, obtiene una cota L1 de 5.111.730 a partir de s_reg uint16 y la vecindad Moore. El cociente entero por 19.665 es como máximo 259, inferior al umbral 966, con intermedios dentro de int32. Esa rama de cristalización por gradiente resulta inalcanzable bajo el source y ABI identificados. No es una medición del binario ni prueba de imposibilidad general de organización: quedan las otras ramas de la ley.'
        ],
        [
            'Dos copias evolucionaron de T824911 a T825849 durante 938 ticks por brazo, sin nuevas entradas materiales. La captura global y el avance normal coinciden exactamente en RAW/clocks completos, interfaces, agenda, recibos y prefijo Native. Cambian tres claves de metadatos de identidad, servicio y segmentación de intervalos, enumeradas en la evidencia. El contraste no acredita igualdad de todo SQLite, outbox o entorno externo ni pasividad universal.',
            'Los 25 fotogramas del baseline muestran 309→308 sitios con RAW distinto de cero, 106→105 activos y 203 sitios con estado cero y RAW relevante. Diez referencias aumentan tres unidades conservando las diferencias Q−4 y MU−20. Diez de catorce pares muestreados, separados por 67 ticks, repiten RAW; ninguno repite clocks. Por tanto se observan recurrencias de una proyección, sin demostrar periodicidad del estado causal completo.'
        ],
        [
            'En el desarrollo se consultó FI128 con datos 14/3 tres veces consecutivas, sin reiniciar la vida. Una entrada legal SEM1, carga 0 y dirección +Z precede a la primera consulta; hay seis ticks adicionales antes de la tercera. El brazo IZQ0 produce −/+/−, con q825905, q826103 y q826307 y 529/529 entradas aplicadas. NONE y SHAM dan +/+/+ con las mismas queries y 528/528 y 529/529 entradas. La ruta derecha produce −/+/+ con 529/529. Ambos lectores, q+4 y q+6, coinciden; no hubo NULL ni rechazos en estas secuencias.',
            'En la primera y tercera consulta izquierda, a q−48 una firma activa de carga 0 y dirección +Z ocupa el padre (52,48,58). En la consulta intermedia, ese padre tiene RAW 0 y forma el agregado 14; los campos posteriores C/S son 17 frente a 31. La tercera query dista 402=6N de la primera. Las observaciones y controles apoyan una interferencia dependiente del encuentro y la fase; no identifican una partícula únicamente por compartir carga.',
            'La reserva prospectiva cambia simultáneamente a carga 7, datos 20/7 y espera previa de once ticks. IZQ7 vuelve a dar −/+/− y NONE +/+/+, con q825916, q826114 y q826318; las dosis son 529/529 y 528/528. Es transferencia local del contraste bajo esa variante conjunta. La espera de trece ticks quedó preparada y no ejecutada. Las consultas son experiencias materiales y el calendario sigue siendo externo.'
        ],
        [
            'Desde el futuro posterior a IZQ0, T826449, se compararon un contraflujo legal de carga 0 y dirección −Z y un sham de igual dosis fuera de su ruta. Cada rama completó 201 ticks y admitió 177/177 entradas. Con la misma query q826508, CONTRA produjo +1 y SHAM −1 en ambos lectores. En T826452, sitio (52,48,50), CONTRA registra estado 1, SEM1, carga 0 y dirección cero; SHAM registra los mismos primeros campos y dirección +Z. En el siguiente fotograma CONTRA tiene RAW 0 allí y SHAM continúa hacia z51.',
            'La intervención prueba que modificar esa contribución formada cambia causalmente la comparación posterior. El operador preparó el contraflujo tras analizar la interferencia: es recuperación asistida P0, sin iniciativa ni regulación adquirida acreditadas. La observación local de RAW 0 no demuestra destrucción de toda información histórica. Tampoco se mezclan las experiencias de CONTRA y SHAM con la vida principal.'
        ],
        [
            'La exploración ambiental ofrece una nube general fijada antes del ensayo: semilla 61001, probabilidad solicitada 0,4 en una caja de 5³ sitios y carga 7. De 61 nacimientos solicitados se aplican 58 y se rechazan tres por ocupación, incluyendo RAW relevante con estado cero. No se sobrescribe ni se limpia el contexto. El avance posterior procede de Native, con las mismas guardas heredadas.',
            'El ensayo de comprobación muestreada se detiene por seguridad del anfitrión a +67, T826516. El soporte RAW pasa de 309 a 297.471 sitios y hay 297.268 activos; s_reg máximo es 19.664. Se capturan los pasos 0–10 y 67; tres momentos posteriores planificados quedan sin ejecución. No hubo pruebas FI ni C2C en esa rama, de modo que no se declara su pérdida funcional ni utilidad del patrón denso.',
            'Una copia de confirmación mantiene la nube y comprueba el soporte en cada frontera. Se detiene a +15, T826464, con 3.007 sitios de RAW distinto de cero; a +14 había 2.372. Sus dieciséis fotogramas reproducen exactamente RAW/clocks de los once momentos 0–10 comunes con el ensayo anterior. Esta reproducción técnica localiza el primer cruce; la parada es del anfitrión y no autoprotección aprendida.',
            'Un testigo registrado en T826452→T826453 muestra que el origen (33,33,37) permanece activo con carga 7 mientras el destino (32,32,38), antes vacío, recibe estado 1, carga 7 y la dirección de la fuente. Entre sus veintiséis vecinos hay una sola fuente entrante y la condición XNOR es falsa. El testigo apoya copia dirigida con supervivencia, sin atribuir identidad de partícula ni todo el crecimiento a ese mecanismo. En el paso 67 también se registran 5.636 activos SEM7, compatibles con la rama XNOR; su primera aparición queda sin localizar dentro del hueco temporal original.'
        ],
        [
            'El control continúa la misma descendencia DISC desde T826449, sin nube, y declara las mismas 61 interfaces sin emitir nacimientos. Después de 67 ticks conserva soporte RAW 309. La consulta FI 14/3 devuelve +1 en ambos lectores y aplica 176/176 entradas; dura 202 ticks incluida su normalización. En C2C ordinal 28, la primera elección Native −1 utiliza DIF, obtiene realmente 30−7=23 y entrega ese 23 a una segunda interacción Native. Su salida +1 produce un archivo de 64 bytes por la ruta 1, con 186/186 entradas aplicadas. La secuencia, el transporte y el dispositivo permanecen preparados; no son un plan descubierto.',
            'El paso C2C tarda 1.031 ticks y supera en 231 el máximo local de 800 congelado antes de ejecutarlo. La secuencia completa usa 1.300 frente a 1.075 previstos. El runner detecta el exceso después de la operación y cierra FAILED_PRESERVED en T827749. El primario C2C registra completed y un producto útil verdadero; eso no valida el plan ni borra su desviación. El contrato heredado seguía siendo finito. Se conserva la previsión insuficiente y su resultado; no se amplía retrospectivamente el límite ni se repite el control.'
        ],
        [
            'La receta pi06_transitorio_izq0_y_continuacion_R01 conserva un prefijo operativo completo y el código exacto. Su reproducción Native fría, sin captura global, ejecutó 600 ticks, aplicó 529/529 entradas y repitió −/+/−: tres respuestas formadas, una pertinente. Coinciden RAW/clocks, interfaces, agenda y prefijo Native con el desarrollo registrado; las tres diferencias de metadatos se declaran. La receta original mantiene su etiqueta histórica PREPARADA y el registro posterior acredita la ejecución real.',
            'Se distinguen lectura y recálculo de registros, reproducción Native desde un estado conocido, adquisición desde un prefijo anterior, uso comprobado en el principal y recuperación ante un fallo definido. PI06 verifica las dos primeras modalidades para el transitorio y una recuperación asistida P0 en las ramas causales. No demuestra una adquisición reguladora nueva del principal. Restaurar un snapshot tampoco demuestra autorreparación.'
        ],
        [
            'Se cerró la fase Native con 7.882 ticks entre doce mundos diagnósticos. Ninguna candidata satisface los criterios de ventaja adquirida, conservación y continuidad necesarios para promoción. El principal sigue siendo ECI02_PI03_REPRO_PI04_PI05_MAIN_01, N67, T824911, con padre físico PI03 en T775355. El futuro útil T827749 y los estados densos quedan como evidencia separada.',
            'La incorporación instrumental sí fue ejecutada: INCORPORACION_REPRODUCIBILIDAD_INSTRUMENTAL_PI06_R01.json, SHA-256 f5073752e8abf9cfc054d037d9f5e61b244934d32152a556b15e968b754c7d73. Preserva una cápsula de 304 archivos y 3.295.582 bytes, manifiesto 257a36b387607ae9cd166a7c15a4c9e7b2f4b29f031057f25d5a49b83e33d326, el prefijo completo postinterferencia y el contrato PI06_REPRODUCIBILIDAD_INSTRUMENTAL_R01. Agrega al catálogo dos entradas de instrumentos y procedimientos P0, sin cambiar selectores, dispatchers operativos, código RP anterior ni la receta R01.',
            'La nueva receta pi06_interrupcion_causal_y_sham_R02 permite preparar dos variantes de 201 ticks y 177 entradas; su reproducción fría desde el nuevo punto de entrada queda pendiente. La receta de nube R03 permanece bloqueada y R04 conserva IDs históricos fijos. El gestor verificó estáticamente los materiales R02 con cero imports DEE y cero ticks: 304 archivos de código y 4.198 miembros del prefijo, 252.033.224 bytes. El registro transversal incorpora un anexo PI06, conservando los valores históricos; su comprobante es REVISION_TRANSVERSAL_PI06_ANEXADA_R01.json.'
        ],
        [
            'La siguiente incertidumbre decisiva es si la organización puede activar una gestión pertinente de esa interferencia a partir de su propia historia. Ya se dispone del contraste IZQ/NONE/SHAM y de un mecanismo externo de recuperación. Un nuevo contraste deberá mostrar beneficio posterior y dependencia de experiencia con exposición comparable, sin que el anfitrión diagnostique el fallo y coloque su solución ni confunda una oscilación con regulación.',
            'Para investigar la expansión, hace falta una función informativa antes del estímulo y una ventana de exposición que permita observar su uso sin sobrepasar la seguridad. Este cierre conserva la dosis ensayada y sus fracasos de procedimiento, sin reducirlos para aparentar éxito. La cota del gradiente es una restricción localizada del source; las demás posibilidades de organización siguen abiertas. La representación visual de los documentos se declarará según el intento de render y sus comprobantes reales.'
        ]
    ]
    for section, content in zip(m['sections'], paragraphs):
        section['paragraphs'] = content
    m['sections'][7]['commands'] = [
        'Desde la raíz del producto: motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad listar',
        'Desde la raíz del producto: motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad verificar pi06_transitorio_izq0_y_continuacion_R01',
        'Comprobación estática R02 ya ejecutada: motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad verificar pi06_interrupcion_causal_y_sham_R02'
    ]
    m['compendium_current_summary'] = ('Se añade interferencia situada confirmada, recuperación asistida P0, reproducción de la trayectoria adversa y expansión de una nube preparada. No se demuestra regulación adquirida ni se adopta otro principal: PI05 permanece en T824911. Los resultados útiles y las desviaciones de protocolo se informan por separado.')
    m['compendium_paragraphs'] = [
        'PI06 continuó en copias completas del principal PI05, N67, T824911, con Universe v27 y Thinking 4.5.0 congelados. Ejecutó 7.882 ticks entre doce mundos diagnósticos. Dos baselines de 938 ticks, sin nuevas entradas materiales, demostraron igualdad Native acotada con y sin captura global; no se declara pasividad universal ni igualdad de todo el estado operativo externo.',
        'Una entrada izquierda de carga 0 altera tres comparaciones sucesivas: −/+/− frente a +/+/+ en controles intacto y sham de la misma edad. La reserva de carga 7, datos 20/7 y espera de once ticks conserva el contraste. Se distingue una disponibilidad que cambia por encuentros y fase de una regulación aprendida. La receta del transitorio reprodujo Native 600 ticks, 529 entradas aplicadas y el patrón adverso, con igualdad de RAW/clocks y prefijo causal.',
        'Un contraflujo legal y su sham, con 201 ticks y 177 entradas cada uno, producen +1 frente a −1 en la comparación posterior. El registro observa primero un estado estacionario local y después RAW 0 en el brazo de contraflujo. Es una recuperación asistida P0: la intervención fue elegida por el investigador, no por el ente.',
        'Una nube general solicita 61 entradas, admite 58 y rechaza tres por ocupación. A los 67 ticks el soporte RAW aumenta de 309 a 297.471 sitios. La confirmación por frontera, con la misma dosis, reproduce once buffers comunes y localiza el primer cruce de 3.000 sitios en +15: 3.007 frente a 2.372 en +14. Ambas detenciones son del anfitrión. No se ejecutan FI/C2C en las ramas con nube y no se declara pérdida funcional de esas capacidades.',
        'El control sin nube produce una comparación pertinente y utiliza el resultado real 30−7=23 en otra interacción Native para generar un producto de 64 bytes, con 186/186 entradas admitidas. Su paso C2C consume 1.031 frente al máximo local de 800; el plan cierra FAILED_PRESERVED con 1.300 frente a 1.075 ticks previstos. El resultado material útil no borra esa desviación ni justifica una promoción.',
        'La revisión recupera D7 y los negativos 20X/21X, distingue versiones y recalcula 28 distancias históricas. Una cota estática del source hace inalcanzable una rama específica del gradiente: 259<966. No es medición binaria ni imposibilidad general de organización. Un testigo local registra copia dirigida con supervivencia, sin atribuirle toda la expansión ni confundir suma de s_reg con energía.',
        'Se incorporan efectivamente una cápsula de 304 archivos, el prefijo completo, contrato, catálogo y anexo transversal. R01 tiene verificación Native fría registrada; R02 queda preparada con requisitos comprobados y reproducción fría pendiente; R03 está bloqueada y R04 conserva IDs históricos. La mejora incorporada corresponde a instrumentos y procedimientos P0. El principal PI05 sigue protegido, sin nueva regulación adquirida declarada.'
    ]
    m['document_publication_status'] = 'CLOSED_SOURCE_FACTS_BEFORE_AUTHORING_SEE_SUBSEQUENT_PUBLICATION_WITNESS'
    m['visual_QA_status'] = 'NO_VISUAL_APPROVAL_INFERRED_FROM_SCIENTIFIC_FACTS'
    m['root_actions_before_authoring'] = [
        'Scientific primary results, Native ledger and actual instrumental incorporation reviewed.',
        'The immediately following DOCX operation must have its single skill marker and retain source facts unchanged.',
        'Subsequent structural/render/publication witnesses determine document delivery status, without principal adoption.'
    ]
    m['sources'].append('control/RP_PI06_CIERRE_CLI_SOLO_LECTURA_R01.json')
    for source_name in m['sources']:
        if not (P/source_name).is_file():
            raise FileNotFoundError('Missing scientific localizer: '+source_name)
    for name, expected in json.loads((P/'control/PI06_CONFIRMACION_CONTROL67_R04.json').read_text(encoding='utf8'))['protected_main_after'].items():
        assert sha(Path(name).read_bytes()) == expected
    with target.open('x',encoding='utf8') as f:
        json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'closed_facts':str(target),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'Native_ticks_this_command':0}))

if __name__ == '__main__':
    main()
