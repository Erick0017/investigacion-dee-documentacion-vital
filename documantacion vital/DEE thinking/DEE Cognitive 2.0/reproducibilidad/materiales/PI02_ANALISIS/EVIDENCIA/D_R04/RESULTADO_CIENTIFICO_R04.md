# PI02 R04 — lectura causal del desarrollo y los cortes cerrados

Análisis pasivo de registros,8nov2026. `RECALCULAR_HABITAT_R04.py` verifica la cadena del diario, RAW→firmas, transducción de acciones, cargas externas, recursos y paquetes materiales sin importar DEE ni abrir SQLite. Esta nota distingue desarrollo, reserva y los seis controles/casos reservados ya cerrados; la sección final de contraste actualiza las cautelas provisionales del análisis temprano conservado abajo. No se cambia el protocolo para mejorar retrospectivamente sus resultados.

## Desarrollo: qué ocurrió y qué no llegó a probarse

`ECI02_PI02_DEV_HAB`,N67,T740937→745537, recibió una ventana genérica4600ticks. Se iniciaron6oportunidades por retornos físicos con rutasA,B,A,A,A,B. Hubo69retornos,60rechazados por capacidad/refractario preparado y3posteriores al banco agotado; no son69decisiones de tarea independientes. Cuatro accesosFIformaron cuatro respuestas válidas y2acciones útiles; dos oportunidadesBoperaronTOGGLE y consumieron2paquetes reales de64bytes. Se obtuvieron2recursos de64bytes. Los costes y recursos se mantienen separados; no son energía ni una medida de metabolismo.

El registro contiene713recibosNativeúnicos:695aplicados,6rechazados por conflicto y12por ocupación. Los alias repetidos en estados/resúmenes no se suman como eventos nuevos. El diario tiene168eventos con cadena exacta y0inconsistencias del recálculo; los dos recursos y los dos paquetes gastados se contrastaron con sus bytes y hashes locales.

La primera experiencia ofrecióW7 como preámbulo preparado. La perturbación real produjo `raw0.rejected_conflict` enT741087; sólo después de observar ese recibo terminal el transductor emitióU11, admitidaT741090. W/U llegaron alH enT741093 y se registró+Y18, sin insertar el producto desde Python. El sensor externo aporta la clasificación del rechazo; no es un detector aprendido de perjuicio y ese rechazo por sí solo no define dolor ni pérdida cognitiva.

No huboCLOSE. Esto no fue una prueba negativa de la asociación: la única oportunidad posterior con advertencia configurada, episodio5, tomó rutaB y no inició trabajoFI; por contrato tampoco se programó la nuevaW. El contador «advertencia configurada» difiere de señal realmente solicitada, admitida y utilizada. Una futura evaluación no debe ocultar esta ausencia de exposición ni reemplazarBporA para fabricar una demostración.

La ocupación global reportada pasó91→95sitios activos de300763, con max_s_reg4530en ambos cortes. Son dos fotografías y magnitudes distintas de RAM o contenido funcional; no un mapa exhaustivo del máximo local ni prueba de estabilidad ilimitada. No se observó ni se atribuye asfixia o dolor.

## El rechazo de una entrada no predice siempre el fallo de tarea

En desarrollo, episodio0, cargas10/4, la perturbación y raw0se rechazaron por conflicto; FIformó−1 y produjo11/3, empeorando el objetivo. En episodio2, la válvula preparada por el TOGGLEprevio impidió la perturbación, raw0se aplicó y FI0mantuvo6/6de forma útil. En episodio3, pese a otro conflicto de raw0, FI−1mejoró3/12→4/11. En episodio4, el conflicto coincidió conFI−1perjudicial para14/6. Por tanto no se equiparan rechazo, ausencia de toda percepción y error funcional; depende del contenido y del contexto.

Los Bde los episodios1y5cerraron una válvula con duración22N. Su operación fue propia de un retorno nativo bajo transducción fija, pero el coste deBrecibe valencia negativa preparada y no se ha acreditado que la organización descubra la política óptima del dispositivo. Tampoco esos dos casos constituyen negociación, autoabastecimiento ni regulación general.

## MAIN reservado: hechos ya comprobados del corte cerrado

`ECI02_PI02_MAIN`,N67,T740937→750137, completó12oportunidades en9200ticks. Se verificaron137retornos,120ocupados por la capacidad preparada y5posteriores al banco agotado. Hubo9accesosFI,6recursos reales,3TOGGLEy5CLOSEaplicadas. Las8actuaciones de dispositivo consumieron512bytes de paquetes de control. Los1605recibosNativeúnicos se distribuyen en1584aplicados,6conflictos y15ocupaciones. Se contrastaron RAW, cadena de diario y bytes de todos los recursos/paquetes consignados, con0inconsistencias documentales.

Esta línea adquirió su propio portador+Y18tras el fallo real de entrada del episodio0; no recibió el soporte de los prototiposR03. Las cinco nuevasWprogramadas se admitieron y formaronCLOSEenT744711,745448,746185,746922y748396, con cargas25,32,39,46y53. Los comandos provinieron delHobservado; el calendario, la lectura continua, TTL, límites de capacidad y transducciones siguen siendo preparación externa. Una recurrencia preparada no demuestra que el ente aprendió cuándo debe iniciar oportunidades.

La válvula ya estaba cerrada antes de cada una de estasCLOSEen la trayectoria observada. Por eso no se atribuye cada acierto inmediato a la últimaCLOSE. Las actuaciones normales renuevan su TTL. La oportunidad de falsa alarma, episodio7, gastó un paquete aunque no había perturbación. En el episodio8, la regla ambiental invertida hizo que la mismaCLOSEabriera la válvula: apareció conflicto de raw0, FI−1y el efecto18/5→19/4fue perjudicial. La firma adquirida persistió; no aprendió a condicionar o inhibir esa respuesta según la nueva conveniencia. Éste es un límite concreto, no un fallo universal del sustrato.

## Primer contexto común MAIN / unpaired

La comparación dirigida del episodio5se fijó por ser la primera advertencia posterior a enseñanza, no por escoger el mejor resultado. Los episodiosFI0,2,3y5tienen solicitudes176por frame exactamente iguales, los mismos framesFIregistrados y la misma observación tempranaRAW/clock. No se afirma igualdad de los mundos completos, puesHya contiene historias distintas.

En el episodio5las dos ramas tuvieron el mismo retornoq744647, Wcon carga7admitidaT744703 y G0admitidoT744775, con los mismos IDs115171/115172. En elHdeT744711 MAINformó(-X,+Y)25→CLOSE; unpairedformó+Y18→NULL. Las dos accionesFIinmediatas fueron+1útiles para16/3y la válvula ya estaba cerrada porTOGGLEdel episodio4. Esa primeraCLOSErenovó la duración, pero no es necesaria para explicar el acierto inmediato5.

El TOGGLEanterior expirabaT745384. MAINregistraCLOSE5hasta746185y otraCLOSE6en745448hasta746922. Al llegar la siguiente entradaFI, T745509, MAINmantiene la guarda y raw0se admite; FI+1mejora19/8→18/9. En unpaired, sinCLOSE, la guarda estaba abierta, raw0y la perturbación se rechazan por conflicto y FI−1empeora19/8→20/7. La separación está en la cadena física/operativa registrada, no en una respuesta escrita por el evaluador.

Los datos no prueban queCLOSE5sola fuese necesaria: CLOSE6también precede esa entrada y podría haber recerrado la válvula. Un corte de toda la conexiónCLOSEevalúa el canal/secuencia aprendida, no la necesidad de cada renovación individual. Esa comparación y los otros controles deben decidir la atribución final de utilidad;6/12frente a4/12de unpaired es por ahora el contraste observado, no una certificación aislada de regulación general.

## Contraste cerrado: ganancia local, límites y un resultado adverso decisivo

Se exportaron completos los seis brazos reservados y el desarrollo, seleccionando en cada caso exactamente el prefijo cuyo `log_count` y SHA están comprometidos en su resumen. El recálculo portátil de los siete prefijos y de los bytes de sus recursos/paquetes produjo cero inconsistencias. Los 78 episodios totales comprenden seis de desarrollo y doce por cada uno de los seis brazos; las ramas comparten pasado y no son 78 aprendizajes independientes.

| Caso reservado | Recursos / oportunidades | Marcos FI realmente emitidos | CLOSE formadas / aplicadas | Nuevas W posteriores al entrenamiento, aplicadas | Coste de dispositivo |
|---|---:|---:|---:|---:|---:|
| MAIN, historia emparejada | 6/12 | 9 | 5/5 | 5 | 512 bytes |
| Historia desacoplada | 4/12 | 8 | 0/0 | 4 | 256 bytes |
| Sin entrenamiento W/U | 4/12 | 8 | 0/0 | 4 | 256 bytes |
| Corte de CLOSE después de formarse | 4/12 | 8 | 4/0 | 4 | 256 bytes |
| Sin valencia del selector O | 7/12 | 12 | 5/5 | 5 | 320 bytes |
| Todos los actuadores anulados | 0/12 | 6 | 3/0 | 3 | 0 bytes |

Hay cinco posiciones ambientales de advertencia preparadas por brazo. Una ruta B no presenta W: por eso cinco posiciones no equivalen a cinco señales percibidas en todos los brazos. La W inicial de calentamiento se contabiliza aparte: una en MAIN, desacoplado, corte, omisión de valencia y actuadores anulados; ninguna sin entrenamiento. Todas las W realmente solicitadas en estos siete registros tuvieron recibo aplicado. El resultado sin entrenamiento tiene menor dosis y no sustituye al control desacoplado ni al corte después de producir la señal.

El control `warning_cut` confirma el enlace que el contraste temprano con unpaired sólo sugería. En el primer episodio común5, MAIN y el corte tienen idénticos W/G admitidos, RAW/clock de H, firma CLOSE y los mismos 176 recibos/frame FI. En el corte la firma se forma pero su actuación se anula. Los dos aciertan todavía ese episodio porque la guarda del TOGGLE4 no ha expirado. Después, al episodio6, las renovaciones CLOSE5/6 mantienen protegida la entrada MAIN; el corte tiene la guarda expirada y la perturbación produce conflicto. Las lecturas FI posteriores difieren y sus consecuencias son, respectivamente, útiles y perjudiciales. El resultado agregado6/12 frente a4/12 respalda una contribución funcional del canal aprendido en este protocolo. No identifica la necesidad de una renovación aislada ni supone futuros idénticos después de que las actuaciones divergen.

La asociación temporal tiene un dominio concreto: W/U emparejadas formaron una contribución Y que cambió el procesamiento de W posteriores; las separadas un tick y la ausencia de entrenamiento no produjeron esa misma firma. Los intervalos ambientales61,128y195ticks antes de la entrada mantienen una fase común módulo67. Se reutilizó la asociación con referentes de trabajo reservados y varios plazos congruentes. Esto no demuestra generalización a fases arbitrarias, estimación aprendida de intervalos ni descubrimiento de qué significa la interfaz. El investigador preparó H, fuentes, lectores, calentamiento, sensor del rechazo, vocabulario de acciones y transductor CLOSE→dispositivo.

La falsa alarma7 produjo una CLOSE y gastó64bytes sin perturbación que evitar. La inversión del dispositivo8 produjo la misma firma adquirida, abrió la guarda y perjudicó el trabajo. El mecanismo conserva la respuesta de aviso pero no aprendió su nueva conveniencia. No hay base para llamarlo regulación general R2 ni adaptación competente a cualquier cableado. Sí hay una asociación adquirida con efecto protector local, frente a una guarda que se activara siempre por sí sola.

El resultado adverso del selector O es central: omitir su valencia produjo7/12recursos, más que los6/12de MAIN. Al mantener A, la omisión ofreció doce trabajos FI, frente a nueve de MAIN; por eso la mejora del canal C no acredita que la selección O haya aprendido una política globalmente mejor. La candidata MAIN era la predeclarada y no se sustituye retrospectivamente por la rama7/12para afirmar aprendizaje competente. Los cambios de ruta reales se conservan como dependencia de consecuencias, con utilidad global no mejorada en este conjunto.

La regla ambiental explica un límite del objetivo aprendido: el contrato marca B como coste inmediato y emite valencia negativa por esa oportunidad; no asigna crédito diferido cuando su TOGGLE protege un FI posterior. El retorno de A depende de su efecto actual. Es una preparación explícita del evaluador, no una optimización del rendimiento acumulativo realizada por DEE. El brazo de omisión retira todas las valencias y por sí solo no identifica qué penalización individual causó la pérdida; tampoco demuestra que otra regla de crédito mejoraría el resultado sin ensayarla. La evidencia localiza así una cuestión de asignación temporal de consecuencias, además del límite de adaptación de CLOSE al cambio de cableado.

La anulación de actuadores dejó0/12recursos aunque se formaron seis lecturas FI y tres CLOSE. No se sustituye una ausencia de actuación por una acción neutral competente. MAIN incluyó además un cero FI material válido en el episodio11; éste mantuvo8/8y obtuvo un recurso. Es diferente de NULL y de una lectura inexistente. Los recursos son archivos externos de64bytes liberados por la consecuencia real de la transducción fija; no representan alimento ni energía nativa.

En conjunto, R04 demuestra en la misma genealogía del candidato una experiencia de rechazo→cambio Native→respuesta ante señal posterior→actuación fija→protección de un acceso FI→acción útil y recurso externo. La iniciativa por retorno reduce la orden individual del anfitrión, pero el periodo, backpressure y banco de oportunidades están preparados. No se ha demostrado aprendizaje del momento de iniciar, exploración autónoma general, invención de herramientas, dolor ni conciencia. Tampoco se deduce pérdida universal de memoria de un conflicto periférico.

## Reproducción documental y cobertura

Resultados numéricos: `RESULTADO_CIENTIFICO_HABITAT_DEV_R04.json`, `RESULTADO_CIENTIFICO_HABITAT_MAIN_R04.json`, `RESULTADO_CIENTIFICO_HABITAT_UNPAIRED_R04.json` y `COMPARACION_PRIMER_AVISO_R04.json`. Se pueden verificar con Pythonestándar suministrando diario, resumen y, para comprobar recursos reales, su banco local/copias exportadas. La herramienta admite diariosgzip y selecciona el prefijo exacto por log_count/hashdel resumen cuando existe una continuación posterior, nunca por aciertos.

La observación del diario registra puertos fijos y framesFI. No es seguimiento exhaustivo de cada encuentro del mundo. La igualdad de frames locales no acredita igualdad causal global. Los estados operativos completos siguen locales y las actuaciones de válvula pertenecen al entorno simulado; no son control libre del sistema operativo.

La contabilidad de ticks está separada: `CONTAR_TICKS_PI02.py` suma una vez cada MATERIAL_REQUEST desde sus primarios y conserva el intento fallido de0ticks. La comparación de registros no suma ticks. Los dos controlesOHañadieron134+134ticksreales; tras desarrollo/OH la base era34931. La reserva planificada6×9200 lleva a90131antes del panel/continuación. El parámetro `--reserved-batch-total55200` descuenta automáticamente los TIMEya cerrados y evita doble contar los brazos del lote.

El cierre posterior del libro de ejecución, `TICKS_NATIVE_PI02_CIERRE_FINAL.json`, registra100solicitudes materiales canónicas y93340ticks reales acumulados entre todas las vidas ensayadas:90131hasta las reservas,1409posteriores para el panel y1800para uso tras reapertura. Los0ticksdel intento fallido se mantienen. No había sesiones registradas abiertas ni inconsistencias y quedaban6660ticks del límite100000. Esta suma es gasto de cómputo experimental multirrama, no edad de la vida principal ni número de experiencias independientes.

La comprobación OH se exporta sin pérdida como un prefijo causal común y dos sufijos binarios: el recálculo reconstruye íntegramente los36086707/36086711bytes Native descomprimidos, verifica sus SHA y compara1013interfaces,0pendientes,114458recibos,RAW/clocks y todos los metadatos no administrativos. Los contenedores gzip originales se identifican con sus hashes, pero no se duplican. La evidencia tiene un alcance de134ticks con segmentación igual y sin hábitat admitido; no certifica pasividad universal, equivalencia de SQLite ni inocuidad de sondas materiales.
