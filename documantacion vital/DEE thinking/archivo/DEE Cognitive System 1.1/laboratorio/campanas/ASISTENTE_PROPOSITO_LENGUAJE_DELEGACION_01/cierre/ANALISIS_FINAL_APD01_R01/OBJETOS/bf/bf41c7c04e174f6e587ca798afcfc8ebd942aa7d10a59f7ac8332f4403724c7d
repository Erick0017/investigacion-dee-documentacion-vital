"""Targeted editorial changes to new text only; no DOCX, physics or source IDs changed."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAME='DATOS_MANUAL_APD01_FINAL_PARA_APROBACION.json'
def main():
    target=HERE/NAME;old_bytes=target.read_bytes()
    expected='4b19cdce656f7edb2271b1359b204d62b6583d2be4418989ce46ab118b6ca71a'
    assert hashlib.sha256(old_bytes).hexdigest()==expected
    x=json.loads(old_bytes);changes=[]
    backup=HERE/'_VERSIONES_INSTRUMENTALES/DATOS_MANUAL_APD01_FINAL_ANTES_LEGIBILIDAD.json'
    with backup.open('xb')as f:f.write(old_bytes)
    # Literal corrections only in new replacement values and new method additions.
    pairs=[('capítulo32','capítulo 32'),('Word1.15','Word 1.15'),('capítulos20–31','capítulos 20–31'),
        ('edición1.15','edición 1.15'),('Cognitive1.1.0','Cognitive 1.1.0'),
        ('thinking4.5.0','thinking 4.5.0'),('Universev27','Universe v27'),
        ('vigente es1.15','vigente es 1.15'),('científicos20–31','científicos 20–31'),
        ('original de73 entradas','original de 73 entradas')]
    for key,before in list(x['inline_replacements'].items()):
        after=before
        for a,b in pairs:after=after.replace(a,b)
        if before!=after:
            x['inline_replacements'][key]=after
            changes.append({'section':'inline_replacements','source_anchor':key,'before':before,'after':after})
    for key,paragraphs in x['method_additions'].items():
        for i,p in enumerate(paragraphs):
            before=p['text'];after=before
            for a,b in pairs:after=after.replace(a,b)
            if before!=after:
                p['text']=after
                changes.append({'section':'method_additions','heading':key,'paragraph':i,'before':before,'after':after})
    chapter={
      6: 'Los contrastes léxicos invirtieron correspondencias sin cambiar el lector. LEX_R03 recibió las mismas tres formas y operandos en historias opuestas: resultados 11/11/11 frente a 3/21/−7; ambas conservaron diez accesos. Eso acredita que una asociación adquirida cambia la función numérica utilizada. Los algoritmos de suma, diferencia afín y conteo siguen preparados y acotados. No se aprendió un alfabeto numérico general ni se acreditan nuevos significados NSM.',
      8: 'P26 preparó la ampliación sin enseñar total/quita: diez formas anteriores correctas y regresión numérica 11/11/2. SERVICIO_R03 continuó la misma MAIN y aplicó 2/2 entradas para total+, 2/2 para quita− y 3/3 para revisar beta+. Después utilizó total en 5/5 oportunidades y quita en 4/4; quedaron dentro del presupuesto 3/5 usos de total y 4/4 de quita. SERVICIO_R04 reutilizó total y quita tres veces cada una sin volver a enseñarlas. Son adquisiciones de MAIN, no recuerdos trasplantados de LEX_R04.',
      11: 'La lección de MAIN P16 utilizó un docente externo, siete ticks y dos de dos entradas aplicadas; los cinco usos de P17 emplearon 42 ticks y diez de diez entradas, sin otra llamada al docente. Los tiempos de host de 9.449939 s y 7.481554 s incluyen carga, guardado y E/S: no son mediciones de CPU ni demuestran ahorro amortizado, y el dominio acumulativo no equivale a SUMA binaria general.',
      14: 'MAIN P22 utilizó consecutivamente la ruta externa, la ayuda neutra activa y la ruta nativa, con resultados 18, 23 y 17 y coste modelado total 11 bajo su ley. Los controles auxiliares real/omitido/sham del mismo prefijo dieron costes 11/15/15 y resultados 8, 9 y 13 en cada historia. La tercera decisión dependió de una diferencia física localizada de referencia, sin copiar diarios como respuestas. Es selección modificada por consecuencias con utilidad local; no debe omitirse el positivo de MAIN ni sumarse el aprendizaje auxiliar a su biografía.',
      15: 'Al invertir qué procedimiento era barato desde el futuro auxiliar ya adquirido, el selector mantuvo la ruta nativa cara y su sesgo se profundizó. Las referencias externas realmente ejecutadas —siempre nativa, siempre externa y adaptativa convencional— realizaron 15 tareas matemáticas y de archivo correctas y 1505 entradas aplicadas, nunca controlando MAIN. Partieron del prefijo auxiliar T105181 y de su futuro T107574, no de MAIN P22. Las comparaciones de coste 11 frente a 3/15/7 y de reversión 10 frente a 10/2/6 reutilizan el learner auxiliar correspondiente; no son un nuevo ensayo emparejado de MAIN. Los costes 11 de MAIN y del auxiliar coinciden numéricamente pero no pertenecen a la misma trayectoria. El positivo MAIN conserva su propia evidencia de resultados 18, 23 y 17. Estas cifras no son una puntuación global y las referencias meramente analíticas siguen separadas.',
      19: 'SERVICIO_R03 alcanzó T325311 con 4411,296152 s habilitados tras pausas y recarga entre dos propietarios. El prefijo nuevo produjo 61/61 signos concordantes, 61/61 números correctos dada la operación emitida y 61/61 archivos; 42/61 quedaron dentro del presupuesto. Todas las 61 rutas fueron nativas− y no hubo reversión competente. Las 36/36 consultas nuevas de memorias concordaron con su historia revisada. Los totales de 65 etapas y 40 consultas incluyen cuatro heredadas de cada tipo, no nuevas. Conteo 9/9, composiciones 10/10 y crudos128 5/5 tienen denominadores separados. Las últimas observaciones preceden al ocio restante.',
      20: 'SERVICIO_R03 registró 140 intentos literales: 131 admitidos, seis rechazos de capacidad y tres de validación; los 17 controles técnicos se contabilizan aparte. Aplicó 15406/15406 entradas nativas. Su exportación emparejada postSTOP conserva la cola vacía y ningún pendiente nativo o externo, con epoch abierto. No obstante, clean_closure=false: cada Job informó un proceso activo después de esperar al launcher y antes de close_job. No se resolvió si era un contador tardío o un hijo aún vivo terminado al cerrar. La ausencia posterior de PIDs no reescribe ese límite; no es un fallo cognitivo demostrado ni un cierre limpio.',
      21: 'El mapa de 26 fuentes de SERVICIO_R03 omitió el actor asistente_proposito_01.py. Se conservaron sus bytes exactos P26, pero no se acredita monitoreo continuo retrospectivo ni congelación completa. El mapa prospectivo de 27 fuentes de SERVICIO_R04 sí lo incluye. No se suman minutos ni muestras entre revisiones para resolver estos límites.',
      22: 'SERVICIO_R04 completó 3720,089030300034 s propios con un único PID nativo, 81368, sin pausa, recarga o reinicio intermedios. El cierre limpio, el propietario detenido y la cola vacía se comprobaron por separado. Hubo 25/25 peticiones materiales admitidas y completadas, cinco controles técnicos aparte y 4244/4244 entradas nativas aplicadas. Los 17 pasos APD tuvieron signos, números y archivos correctos; 15/17 quedaron dentro del presupuesto 2. Todas las rutas continuaron nativas−, incluidas las dos oportunidades caras. Conteo 3/3, composiciones 2/2 y crudos128 2/2 no se suman como nuevas mentes o conceptos.',
      23: 'Se reenseñó beta− con 3/3 entradas y las 10/10 consultas de memoria concordaron con la historia. El panel posterior fue alfa−, beta−, gamma+, delta−, epsilon− y zeta+: 6/6 entre T355305 y T355640. Después, seis pares reservados produjeron suma 28, diferencia 20, agrega 21, resta 19, total 23 y quita 19; la actuación del conjunto terminó en T360704. Las lecturas y actuaciones preceden al ocio final: no se inventa una consulta adicional en T361114 ni disponibilidad indefinida.',
      24: 'SERVICIO_R04 fue un protocolo distinto y más espaciado: 23 oportunidades previas separadas al menos 150 s y dos paneles secuenciales, frente a 120 nominales, 14 burst y cuatro inválidas de SERVICIO_R03. Compartir genealogía no implica oportunidades, edad o dosis emparejadas. La hora de un propietario y la espera del Job hasta vaciarse son resultados de infraestructura, no mejora cognitiva ni mayor tolerancia bajo la misma carga. No se sumaron minutos entre reservas. No se demostró una política reversible ni R2 general.',
      31: 'Los hashes actuales de los ZIP se consultan en la verificación externa final. El Apéndice D conserva entregas anteriores históricas; sus hashes no identifican los paquetes APD actuales. El análisis compacto no sustituye los snapshots completos, diarios de transporte, entorno y artefactos necesarios para continuar.',
      32: 'Fuentes: primarios P01–P26; LEX_R01–LEX_R04; acumulación y retorno común; REFERENCIAS_EJECUTADAS_R2; corrección descriptiva del perímetro N0; ventanas SERVICIO_R01–SERVICIO_R04, corte final T361114 y par postSTOP. Las verificaciones de paquetes exactos se consultan externamente; no se anticipa un nuevo FullZIP verificado.'
    }
    old28=x['chapter'][28]['text']
    prefix=old28.split('Los componentes APD de asociación léxica')[0]
    chapter[28]=prefix+('Los componentes APD de asociación léxica, aritmética preparada, selección material de procedimiento, retorno común y actuación sintética permanecen ejecutables en Cognitive. '
        'También se conserva el código y el procedimiento histórico de acumulación finita para nuevas preparaciones compatibles; esto no significa acceso actual a apd-delta ni usos restantes del acumulador en MAIN. '
        'Su contrato de cinco oportunidades validadas quedó agotado, sin sexto ensayo físico ni destrucción del contenido demostrada. '
        'ASISTENTE_MAIN conserva su estado alcanzado y exportación postSTOP completa. Su epoch 6 permanece abierto y el propietario está detenido; no se libera a una continuación desnuda ni se promueve a ACTIVO global.')
    for i,after in chapter.items():
        before=x['chapter'][i]['text'];assert x['chapter'][i]['style']in('Normal','Source')
        x['chapter'][i]['text']=after
        changes.append({'section':'chapter','paragraph':i,'before':before,'after':after})
    assert x['status']=='FINAL_RESULTS_READY_FOR_ROOT_APPROVAL'
    encoded=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    target.write_bytes(encoded)
    receipt={'native_ticks':0,'Word_authored':False,'scope':'Only new replacement/method/chapter prose; historical anchors, identifiers, paths and hashes retained',
        'before_sha256':expected,'after_sha256':hashlib.sha256(encoded).hexdigest(),'changes':changes}
    with(HERE/'CAMBIOS_LEGIBILIDAD_MANUAL_APD01_N0.json').open('xb')as f:
        f.write((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'file':NAME,'sha256':receipt['after_sha256'],'changed_paragraphs':len(changes),
        'chapter_indices':list(chapter),'status':x['status']},ensure_ascii=False))
if __name__=='__main__':main()
