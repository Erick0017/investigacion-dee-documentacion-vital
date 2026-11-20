# E3 — contingencia frente a la misma dosis de señales

Estado: diseño dirigido y código puro preparados; ninguna ejecución Native por este agente. El principal y PI03 permanecen intactos. Este control debe acompañar la progresión C2 de PI04; no es una nueva adquisición que pueda sumarse desde otra vida.

## Qué dejó abierto PI03

PI03 R02 real obtuvo 11/14 productos, `return_nonfailure` 7/14 y `actuator_null` 0/14. El código original `PI03/codigo/pi03_tarea_diferida_R02.py`, función `opportunity`, devuelve `effect['failed']` en real y siempre `False` en el control constante. Ambos completaron 422/422 entradas Native, incluidas fuentes aritméticas y tarea. La cantidad de entradas se igualó, pero no la mezcla de canales de retorno: la rama real tuvo fallos y la constante ninguno. Ese contraste acredita utilidad del bucle bajo sus condiciones; por sí solo no separa contingencia con el resultado propio de los efectos de recibir otra secuencia física de pulsos.

Los controles de calibración R01W omitieron la copia eferente o desplazaron un tick la coincidencia. Separan enlaces del mecanismo local; no igualan una historia de actuaciones y retornos útiles durante el aprendizaje funcional. Sus resultados no deben presentarse como el control E3 ya ejecutado.

Fuentes exactas leídas como texto: `PI03/codigo/PROTOCOLO_PI03_TAREA_R02.json`; `pi03_tarea_diferida_R02.py:opportunity`; `pi03_credito_generico_R01_BORRADOR.py:schedule_trial,submit_generic_outcome`; recálculos y calibraciones PI03 ya conservados. La API de retorno sólo admite booleano genérico y tick: no banco, acción ni solución.

## Contraste mínimo viable

1. Congelar antes de ejecutar el brazo real: prefijo completo común; tarea C2; lector; interfaz; ventanas; dosis; regla de permutación; número finito de oportunidades y criterio de detención. Las dos ramas comparten prefijo, no son réplicas independientes.
2. Ejecutar una historia **real**: la salida Native controla el dispositivo verdadero; éste produce su consecuencia y el transductor fijo devuelve su bit de fallo. Guardar todas las consecuencias, incluidas las que no convienen al investigador.
3. Formar, antes de abrir el control, un plan de retorno a partir de **todos** los episodios incluidos de ese brazo. Usar una rotación circular de una posición dentro de cada estrato de misma demora y fase del contacto. La regla no se escoge después de observar una diferencia favorable. Congelar el plan y su SHA-256.
4. Ejecutar una copia completa del mismo prefijo, con las mismas condiciones iniciales y perturbaciones exógenas. Sus acciones serán exclusivamente sus propias salidas Native. El entorno sigue su evolución y consecuencias reales, pero al participante se devuelve el bit del índice precongelado, en la misma ventana física del retorno. El transductor no consulta acción, banco ni resultado esperado para elegir el bit.
5. Mantener sin cambios consulta, copia eferente de la salida real, lectores y actuadores. El dispositivo debe reconciliar el recibo del retorno aunque éste sea experimentalmente desacoplado. Conservar en el primario dos campos distintos: `actual_failed` y `returned_failed`; jamás cambiar el efecto real para que concuerde con la señal.

La ley del entorno y los suministros son los mismos, pero no se impone un futuro ambiental idéntico tras acciones distintas. Se igualan exposición exógena y secuencia marginal de tipos de señal, no las consecuencias endógenas.

## Igualdades y límites que deben comprobarse

- Por estrato: idéntico número de entradas `failure` y `nonfailure`, cargas cero legales, demora, sitios/interfaces, fase y oportunidades. La cantidad no es sinónimo de igual efecto físico: las diferencias de encuentro con la propia traza son la intervención que se estudia.
- Con calendario igual y una respuesta formada en cada oportunidad, la dosis solicitada de query/support/eferente/retorno debe coincidir. Conservar solicitado/admitido/rechazado/pendiente por canal y firma, sin sumar alias. Si surge NULL, no fabricar una copia eferente para igualar cuentas: detener según el criterio previo, guardar y declarar que ya no se igualó la dosis completa.
- El calendario se debe comparar **antes** de solicitar el siguiente retorno. Si diverge la ventana o la fase, no mover la lectura para recuperar igualdad: preservar el intervalo y declarar el emparejamiento incompleto.
- Informar por separado: productos reales, respuestas válidas, actuaciones, falsos retornos de fallo, fallos reales no señalados, cambios de banco y usos posteriores. No sumar protección y productos como una moneda improvisada.
- Calcular cuántas señales cambiaron frente a la secuencia original y cuántas discreparon de las consecuencias reales del control. Una permutación de bits todos iguales no desacopla nada. Si la secuencia coincide accidentalmente con sus consecuencias, E3 es **no informativo**; no volver a barajar buscando un efecto.

## Qué control no resuelve la pregunta

Reproducir sin permutación la señal de la misma trayectoria determinista y desde el mismo prefijo puede producir exactamente esa trayectoria: no rompe la contingencia. Sirve como referencia técnica si existe, pero no es imprescindible repetirla. Un desplazamiento de un tick rompe la coincidencia física además de la asociación con el resultado, por lo que se mantiene como otro control de mecanismo, no como sustituto de este contraste.

En una muestra finita, permutar no garantiza independencia estadística. Se exige registrar la manipulación efectiva y se limita la conclusión al contraste observado. Si el brazo real y el permutado rinden igual, no se concluye ausencia universal de aprendizaje: puede bastar una regla fija, la historia heredada o una señal no informativa en ese conjunto. Si difieren, el resultado separa esos dos historiales físicos sin demostrar iniciativa general ni planificación.

## Código preparado y punto de integración

`codigo/E3/e3_retorno_desacoplado_R01.py` es puro stdlib, no abre mundos ni importa DEE. Construye un plan con rotación fija dentro de `(delay_laps, reference_contact_phase)`, conserva los recuentos y rechaza cambios de calendario. Para real se utiliza el bit actual del dispositivo; para el control `replay_signal` sólo recibe plan, índice y calendario, nunca acción ni resultado actual.

La raíz debe integrar el punto de sustitución en **su nuevo código PI04**, preservando el código PI03 exacto. En el lugar equivalente a `returned_failed = effect['failed']`, usar `effect['failed']` en real y `replay_signal(plan, ordinal, calendar)` en el control. Después, reutilizar `submit_generic_outcome`, `mark_feedback_scheduled` y `reconcile_feedback` con la misma semántica de recibos. El plan es instrumentación del control, no memoria del ente. No se promueve la rama desacoplada por obtener un valor favorable.

El código incluye `--self-test` con datos sintéticos explícitos: comprueba mezcla/fase/dosis, rechazos y ausencia de argumentos de acción. Su resultado no es un experimento DEE. No se requiere una arquitectura nueva para ejecutar E3; la posibilidad de usarlo en C2 depende de que esa progresión mantenga un retorno genérico y ventanas emparejables.

## Contrato R01 concreto aprobado para ejecución por la raíz

El plugin `codigo/E3/pi04_e3_contingencia.py` admite sólo descendientes completos `ECI02_PI03_REPRO_PI04_*` del corte N67/T775355, manteniendo los contadores heredados24/26 y el soporte OP3 ya adquirido como anatomía preparada. No vuelve a instalar ese soporte. Exige el puente O/H pausado y sin trabajo FI pendiente.

Modos reales:

```json
{"modo":"eci01-pi04-e3-admitir","brazo":"real"}
{"modo":"eci01-pi04-e3-oportunidad"}
{"modo":"eci01-pi04-e3-estado"}
```

La segunda rama se admite con `brazo="desacoplado"` y `plan` igual a la cadena `replay_plan_encoded` que devuelve el estado real al completar18 oportunidades. El campo contiene sólo JSON comprimido mediante el codec acotado E3Z1; no un archivo ni código. La entrada se limita a6144caracteres, la descompresión a32768bytes y se comprueban hash, forma y permutación completa. La prueba pura de18slots midió1602bytes del literal JSON, por debajo del límite8192; no se relaja el transporte global.

Las18 oportunidades consumen primero las2ofertas+1/L4 heredadas. **Antes** de solicitar las oportunidades3,7,11y15, el runner debe enviar explícitamente las cuatro órdenes siguientes por el modo R03 existente:

```json
{"modo":"eci01-pi03-tarea-suministrar","cantidad":4,"conexion":-1,"demora_periodos":2}
{"modo":"eci01-pi03-tarea-suministrar","cantidad":4,"conexion":1,"demora_periodos":4}
{"modo":"eci01-pi03-tarea-suministrar","cantidad":4,"conexion":-1,"demora_periodos":2}
{"modo":"eci01-pi03-tarea-suministrar","cantidad":4,"conexion":1,"demora_periodos":4}
```

El plugin no autoabastece ni modifica esas conexiones según la respuesta. Cada suministro reutiliza el producto aritmético real actualmente conservado y añade archivos ambientales; no restaura contadores ni inserta memoria. Las dos ramas reciben las mismas órdenes exógenas, conservando todos sus productos/rechazos anteriores y nuevos.

Presupuesto esperado:18×782=14076ticks por brazo,28152losdos; el horizonte duro heredado es1500ticks por oportunidad,27000porbrazo. Admitir, estado y esos suministros sin `recalcular_fuente` no añaden ticks. Con18respuestas formadas, la dosis de tarea esperada es90entradas porbrazo; si aparece NULL se preserva y se reporta la pérdida de igualdad de dosis sin inyectar una copia motora ficticia.

La autoverificación pura `control/E3_FUENTES_Y_PRUEBA_PURA_R01.json` compara el AST del cuerpo con la oportunidad PI03 exacta. Se mantienen todas las llamadas de avance, consultas, lector, copia eferente, dispositivo y conciliación. Las cuatro transformaciones son nombre de función, comprobación de calendario antes de la consulta, selección del bit de retorno y etiqueta del registro. Una metadata E3 separada conserva su diario; la tarea heredada sigue acumulando su misma historia. La raíz debe preservar todos los diarios/SQLite/recibos al guardar el mundo.

## Resultado E3 ejecutado por la raíz, revisión técnica R02

R01 completó dos usos útiles hastaT776919 y se interrumpió antes de añadir nuevos recursos: la metadata de tarea estaba cerca de la cuota Native1MiB y el séptimo suministro habría repetido124177bytes de fuente aritmética. Se preservó el futuro adverso; es un fallo de instrumentación, no un fallo cognitivo ni otra réplica. La medición pasiva identifica1.009.525bytes en775355 y1.010.307en el último checkpoint cerrado antes del intento. El límite Python de8MiB no sustituye al límite Native1MiB. Los registros que incluyen ya el intento tienen otro alcance y tamaño.

La adaptación R03_R02 conserva literalmente los seis items históricos y la fuente actual completa. Sólo los nuevos items guardan referencia a una copia canónica deduplicada, con hash, valor real y prueba de lector; la fuente completa permanece además en el diario externo. La cuota se comprueba antes de escribir el diario. La prueba de almacenamiento fue pura, sin Native; los primeros dos usos repetidos en R02 igualaron N/T/RAW/clocks y entradas de R01. No se contó esa repetición técnica como otra adquisición independiente.

Ambas historias R02 terminaron enT789431: **real14/18 y desacoplada18/18**. Cada una solicitó y aplicó90entradas nuevas únicas de tarea, sin rechazo, pendiente ni NULL. La fase de contacto391y los calendarios fueron iguales. Por tipos de retorno: demora2tuvo2fallos+6nofallos y demora4tuvo2fallos+8nofallos, idénticos entre brazos. La rotación cambió8señales respecto del real; el control recibió4fallos falsos y no sufrió ningún fallo real. Los archivos útiles son64bytes comprobados contra las fuentes Native realmente conservadas, no sólo un contador.

Este resultado **no muestra ventaja de la contingencia verdadera** en esta tarea. El desacoplamiento conservó otra estructura útil: los cuatro pulsos de fallo del control ocurrieron en ordinales1/5/9/13, inmediatamente antes de cambios de conexión2/6/10/14 (índicesdesde0). La señal artificial preparó el cambio siguiente. No se le atribuye advertencia descubierta, anticipación autónoma ni planificación. El plan de control procede de una permutación predeclarada de una trayectoria registrada y no se adopta como memoria del principal.

Las referencias analíticas que reaccionan a su propia consecuencia verdadera obtienen8(fija−),10(fija+),9(alternante),13(WSLSinicial−)y14(WSLSinicial+). Una descripción posterior adicional, con **la misma señal recibida** que cada brazo, reproduce las18actuaciones de cada uno y obtiene18productos en el control y14en el real: mantener ante nofallo y cambiar ante fallo recibido, inicial+1. Evita comparar injustamente el control con una referencia que no recibe sus señales preparatorias. Se registra como análisis descriptivo posterior, no como otro ensayo preregistrado.

Reproducción documental completada: `ensayos/EVIDENCIA_E3_PORTABLE/` contiene61archivos/451711bytes; se verificó una extracción ZIPDeflate limpia en memoria sin crear otro ZIP de entrega. `RECALCULAR_E3.py` comprobó primarios, RAW del lector, recibos únicos, ley del dispositivo, bytes reales, fuente aritmética, permutación, fase y calendario. `control/PORTABILIDAD_RECALCULO_E3_R02.json` y `control/E3_ALINEACION_SENALES_Y_REFERENCIA_EMPAREJADA_R02.json` conservan resultados. Las instantáneas completas y el estado causal global permanecen fuera de este expediente compacto; esta lectura no decide su igualdad ni demuestra pérdida de toda información histórica.

## Continuación real posterior: C2 adverso, sin importar el control

La candidata continuó desde el E3real14/18, no desde los18productos del control. Después de preparaciónP0hastaT789434, ejecutó11de12oportunidadesC2hastaT798033: diez primeras salidas+1seleccionaronSUMA, emitieron25y utilizaron segunda ruta+1; cinco contextos6produjeron archivos y cinco contextos4fallaron. Los cinco fallos cambiaronΔ=A−B desde+1a−4. La siguiente oportunidad de contexto4produjoNULLsin función ni segunda acción y fue detenida después de conservar el rechazo y retorno reales. No es cero material ni una respuesta correcta deDIF.

TotalC2:5productos/11oportunidades, seis rechazos;10/10aritméticas formadas correctas por evaluación posterior;1865/1865entradas Native aplicadas, sin rechazo ni pendiente. El recálculo pasivo de los11primarios usa ventanas reales eIDsdeduplicados (`control/C2_DENOMINADORES_PRIMARIOS_RECALCULADOS_PASIVO.json`). Una oportunidad de desarrollo, todas las reservas y la retención permanecen sin ejecutar. Los primeros fallos no se eliminaron al aparecer elNULL.

El par completo detenido está enRP/materiales/PI03_PI04_C2_NULL_T798033, manifiesto304ffb65d3bf9fd40b514ae3f2286a79e214f0d4cb2156dd18fa65f76dbf3c73. Se preservóhalted_reason; no se limpió ni se restauró el pasado. La propuestaC2Bañade un dato simétrico como nueva preparación identificada y, en este corte, sólo tiene diseño/pruebas puras. No se le atribuye todavía recuperación ni ganancia de selección contextual. La tabla antes/después y la explicación detallada están integradas en el mismo `INFORME_CIENTIFICO_PI04.md`;REGISTRO_CAMPANA, código, Manual y mundo no fueron editados por esta actualización documental.

## Atribución de la progresión C2B que se prepara

El anfitrión seguirá eligiendo e iniciando el algoritmo global consulta→FIaritmética→MU→actuador. Las dos selecciones físicas y los cambios de peso deben proceder deDEE; el orden, los plazos y los códigos sonP0preparados. La dependencia histórica de las salidas y una revisión útil por consecuencias deben medirse separadamente como dominiosP1/P2acotados, según contrato y controles. Incluso8/8reservas no demostrarían queDEEeligió iniciar, inventó el procedimiento o adquirió un plan general.

El currículo nuevo consta de26ofertas:12desarrollo,8reserva,2retención,2crucesy2stockfuturo. Un yoked20sólo puede usar efectos realmente observados de los primeros20, con regla fijada previamente; no se inventan las señales restantes si aparece otroNULL. Los cruces22/23usan entradas públicascontext2(29/4)ycontext6(6/5), para exigir que la ruta utilice el resultado real y no una equivalencia fija entre operación y conducto. Aún no son resultados. El análisisWSLS/fijas posterior debe distinguir referencias analíticas de productos efectivamente realizados y considerar qué señales recibe cada brazo. No se añadió código ni se ejecutó un control al dejar este criterio documental.

## C2B R01 ejecutada: admisión parcial y control20no construido

Posteriormente se ejecutaron tres oportunidades del mismo descendiente desdeT798033hasta800379: contextos4/6/4, las tres SUMA25y segunda ruta+,1/3productos. La modificación de referencias fueΔ−4→−5→−5→−5. Las tres operaciones aritméticas formadas fueron correctas según evaluación externa, sin que ello certifique admisión completa.

Los primarios contienen561IDs nuevos únicos:559aplicados y2rejected_occupied. Outer21/21yMU12/12;FI526/528. El tercerFIrechazó IDs122307y122323al encontrar RAWno vacío en[57,53,63]T800111y[6,47,12]T800117, ambos con payload0y canalesleft.root*.turn.3. No se reenvían ni limpian. Se detuvo antes de reservas; los controlesC2Bnone/yoked/context-cutno se ejecutaron. El propietario quedó cerrado según el supervisor. La comprobación documental propia está en `control/C2B_DENOMINADORES_PRIMARIOS_R01.json`, sin nuevoNative.

Se preparó `codigo/RECALCULAR_C2B_R01.py` como instrumento externo: exporta sólo lotes cerrados, comprueba firmas/aritmética/recibos/productos, compara referencias analíticas y admite una rotaciónE3Z1de20señales sólo desde20efectos reales cerrados. La prueba sintética fue compatible con el codecE3oficial, conservó3/20fallos y rechazó19slots/fase equivocada. No se fabricó el plan real porque faltan17efectos y hay rechazos en el prefijo. Este trabajo de código puro sí es posterior al criterio documental previo; no es una ejecuciónNative ni incorporación de la funciónC2B.

## C2C desarrollo cerrado: contexto5 cambia después de un fallo

La misma candidata continuó desde800379con un dato único y lector centralQq+4fijado antes de evaluar, reteniendo el comando hastaq+6y efcopyq+7. Es preparaciónP0, no iniciativa de reparación. La calibración alternativa450ticks0/4/5→−1/−1/0sin retornos permanece en su propia rama.

El lote realC2Ccerró12usos enT809763:11productos64Bverificados,12aritméticas correctas y2232/2232entradas aplicadas, sinNULLni rechazo. OP1context5produjo firma material0SEM1state1[0,1,−1]→DIF7/ruta−y falló; el retorno genérico cambióΔ−5→−4. OP4mismo contexto5produjo+1→SUMA25/ruta+y un archivo útil. Los usos posteriores preservaron esa distinción contextual; el contexto4siguióDIF7/ruta−. Seis de las12primeras firmas fueron cero material, no silencios.

Es un enlace funcional observado de experiencia→referencia→selección distinta→consecuencia útil dentro de la misma vida y del secuenciador preparado. El contraste de historia/retorno, las ocho reservas y la adopción aún no están hechos en este corte. Pruebas: `control/PI04_C2C_REAL_DEV_R01.json` y recálculo propio `control/C2C_DEV12_PRIMARIOS_RECALCULADOS_PASIVO_R01.json`. No se atribuye inicio autónomo del algoritmo, plan adquirido ni ganancia adoptada antes de esos controles.

## Continuación C2C hasta20: reserva8/8y control aún pendiente

Posteriormente la misma candidata alcanzóT816019con ocho reservas correctas:8productos/8oportunidades y1488/1488entradas aplicadas, acumulando19/20productos,20aritméticas correctas y3720entradas admitidas sinNULLni rechazo. Contextos1/2/3/8son nuevos;5es familiar. El recálculo portable desde extracción limpia coincidió byte a byte y no abrió originalesPI04ni importóDEE/app. Localizadores: `control/PI04_C2C_REAL_RES_R01.json`, `ensayos/EVIDENCIA_C2C_REAL20_PORTABLE_R01/` y `control/C2C_PORTABLE_REAL20_EXTRACCION_VERIFICADA_R01.json`.

Se preservó el plan fijo20rotación+1E3Z1en `control/PLAN_C2C_YOKE20_R01.json`:1fallo+19nofallos, dos cambios de señal y fallo rotado aordinal0. Puede ser preparatorio, por lo que un eventual control favorable no se rebautiza como anticipación autónoma. No se ejecutaron todavía none/yoked/context-cut/enlace al cerrar este registro. Las referencias4/8fijas,2/8WSLSglobaly7/8o5/8WSLSporcontextoson cálculos analíticos con sus comienzos e información declarados, no otros productosNative. Sigue pendiente aislar el papel del aprendizaje mediante controles y conservar antes de adoptar.

Genealogía del criterio:Δ−4ya existía enC2R02T798033(q6NULL);B0lo cambió a−5yC2Ccontext5falló y lo reajustó a−4. El lector tempranoP0y el reajuste se separan. El mismo escalar no es el mismo microestado ni certifica una memoria idéntica recuperada. La novedad funcional combina selección de operación, número real y segundo uso en una secuencia todavía iniciada por el anfitrión. Los aciertos en contextos nuevos se compararán connonepara distinguir repertorio previo y efecto del reajuste; no se anticipan esos resultados.

## C2C none20cerrado: ganancia localizada, sinvalencianegativa

El control de retorno constante **material** de nofallo completó800379→816019con12/20productos y6/8reservas,3720/3720entradas aplicadas y20aritméticas correctas;Δquedó−5. Elreal19/20y8/8difirió exclusivamente en siete usos posteriores decontexto5, incluidos los ordinales reservados13/16con operandos15/8y17/8. RealSUMA23/25/ruta+producearchivo;control0material→DIF7/9/ruta−falla la función pedida. Los cuatro contextos nuevos1/2/3/8ya funcionaron también en elcontrol. La ganancia adquirida queda en dos correcciones reservadas del contexto familiar5con datos nuevos, no ocho aprendizajes nuevos.

Los calendarios y cantidades de entradas están emparejados; la mezcla de retornos no(1fallo/19nofallosvs20nofallos). Se acredita beneficio local de historia/señal de fallo y reajuste físico, no necesidad de contingencia verdadera antes delyoked. Yoked/context-cut/enlace y conservación/adopción aún pendientes. Portable combinado `ensayos/EVIDENCIA_C2C_REAL_NONE20_PORTABLE_R01/`; prueba limpia y pares completos en `control/C2C_REAL_NONE20_CONTRASTE_DOCUMENTAL_R01.json`, sin nuevoNative. No se modificaron elprincipal ni sus selectores al recalcular.

## Número encadenado: RAWreal, códec afínP0y evaluación separada

La lectura estática de las cinco fuentes comunesS2/base y20primarios confirmó que `numeric_result`viene deC[12,17,18]en `datum_tick−2`: bits32…47delRAW, firmaSEM1/direcciónfija. DIFusa la representación preparada(izquierda,32−derecha) y decodifica payload−32; Python hace esas transformaciones afines, no la resta binaria final ni un fallbackdelobjetivo. Se debe decir aritmética preparada, no algoritmo aprendido. Se cotejaron2560componentes→solicitudes y20números reales→`MU.current.datum`; realRAWcon39→7ycon25→25son ejemplos trazables.

`aritmetica_directa_eci02.py`mantieneSHA2ef575…ydevuelve el lectorliteral; elAPIflag `operator_selected_operation=True`es heredado del instrumento explícito yC2Cle proporciona la operación a partir de su primera salidaNative. MU.currentinyectaese valor exacto y lee firmasNative, sin umbralPythondelactor. Los cortes4/20evalúan sólo después de actuar;left±rightdelrunneresreferencia posterior. El informe y `control/C2C_TRAZA_NUMERICA_FISICA_Y_CODEC_R01.json`dan rutas/líneas/hash/RAW/testsJSONpuros; no se importóDEE ni se alteró un mundo para comprobarlo.

## C2C yoke20cerrado: no necesidad de contingencia verdadera

Yoke20cerró20/20productos,8/8reserva,3720/3720aplicadas y20aritméticas correctas,800379→816019. La metadata delcontrol conserva exactamente la rotación+1de los20efectos reales y fuentecongelada. Dose/cal/fase391L4matchean. La mezclaes1fallo+19nofalloscomoelreal. Cambian dos slots de lafuente, pero sólo hayunfallofalso frente al efecto realdelcontrol:ord0c4DIF7/ruta−producearchivo(actual_failedfalse)perorecibefallo(returnedtrue),109/114→111/115/Δ−4antesc5. Elresto también producearchivo.

Se demuestra reajuste localporseñalhistórica y uso contextual, sin ventaja/necessidaddecontingenciaverdadera. El pulso falsopreparatorio esexterno, noanticipación aprendida. No se importaesecontrol alMAINreal19/20. Elportable conjunto109archivos1.914.612bytes fue recalculado desdeextracciónlimpia, sinoriginales/DEE/app y con salidaidéntica: `control/C2C_TRES_HISTORIAS20_CONTRASTE_DOCUMENTAL_R01.json`. No hubo comparación globalnueva deestados; ctx/link/conservación/adopciónaúnpendientesenestecorte.

DGCseparó un cero materialQq4delNULLq6y comprobó observaciónROIpasiva sólo en su condición emparejada782ticks; no demuestraH4globalni recuperación autoiniciada. La coincidenciaRAW/clocksfinalE3tampoco es igualdad del conjunto operativo:12recibos, cincometadatos y entornos33/37productos difieren. El informe científico conserva estos alcances y las fuentes exactas sin declarar otra ablación o genealogía material no registrada.
