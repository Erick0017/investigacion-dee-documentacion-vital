# PI09 — antecedente aritmético y contraste de acceso

Esta revisión es documental y geométrica. El agente F1 no ejecutó DEE, no creó un Runtime ni modificó el principal. Las cuatro series Native nuevas fueron ejecutadas por Root tras sellar sus planes. El recálculo histórico lee seis primarios congelados de PI08 y reproduce las decodificaciones y calendarios; no reproduce esas vidas. El recálculo de las series nuevas también analiza archivos ya cerrados.

## Qué falló y qué sigue abierto

En el panel de B_REAL, la suma preparada 6+7 produjo el entero Native **7**. La siguiente diferencia recibió ese **7 real**, aplicó la representación independiente de −5 y produjo **2**. B_NONE presenta exactamente esos mismos enteros, ventanas y dosis. En el clon diagnóstico abierto desde A861426, los dos usos produjeron **13** y después **8**. Los seis lectores C cumplen la misma firma: sitio (12,17,18), SEM1, estado activo y dirección (+X,−Y,−Z). Las 176 solicitudes directas de cada operación constan aplicadas. No hubo NULL, entrada rechazada ni sustitución del resultado.

Por tanto, el segundo número erróneo de B no acredita una segunda pérdida independiente. El fallo de suma reaparece sin retorno negativo: ese retorno no es condición necesaria del fallo. Tampoco se ha demostrado pérdida de contenido, que la experiencia B cause por sí sola el deterioro, ni que el operando izquierdo deje de existir globalmente. La cifra 7 aislada no identifica un portador por ascendencia ni prueba qué contribución faltó o se canceló.

| Vida / operación | Antes | Consulta q | q mod67 | q mod391 | q mod782 | C material | Decodificado |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_RP suma6+7 | 864503 | 864559 | 58 | 58 | 449 | payload13 | 13 |
| B_REAL / NONE suma6+7 | 877797 | 877853 | 19 | 58 | 449 | payload7 | 7 |
| A_RP diferencia13−5 | 864701 | 864757 | 55 | 256 | 647 | payload40, bias32 | 8 |
| B_REAL / NONE diferencia7−5 | 877995 | 878051 | 16 | 256 | 647 | payload34, bias32 | 2 |

Los casos A y B coinciden en las fases 391 y 782 de ambas consultas; difieren en fase 67 e historia/edad completa. Es una pista acotada para estudiar acceso y encuentros. No aísla que 67 sea la única causa. Las observaciones originales sólo cubren C/E/S/A/B en las seis ventanas finales: no registran los nodos tempranos que permitirían localizar la primera divergencia.

## Circuito reutilizado y cobertura de lectura

Se leyeron completos los tres códigos instalados `aritmetica_directa_eci02.py`, `aritmetica_apd_01.py` y `percepcion_cruda_fi01.py`. De `mente_unificada_01.py` se reabrieron sólo `current_read`, protección de fase y calendario de consulta; de `gestionar.py`, las entradas de acceso pertinentes. No se repitió una lectura integral de Thinking, CORE o Ingenierías. La síntesis dirigida PI08 `fuentes/F1_PLASTICIDAD_Y_REUTILIZACION_DIRIGIDA_PI08_R01.md` conserva la cobertura histórica de Ingeniería01/02, CORE06/07 y M1/M2/U0; aquí se reutiliza como antecedente, sin convertirla en una lectura nueva.

El modo directo selecciona externamente la operación y llama `native_pair` sobre la vida recibida. El codec coloca el izquierdo en el componente0; coloca el derecho en componente1 para suma y el complemento32−derecho para diferencia. Cada canal se transforma por separado. El lector toma C en `datum_tick−2`: suma usa su payload material; diferencia sustrae el bias32 de ese payload. La función del circuito es preparada y no acredita que la vida haya descubierto una operación binaria.

La geometría estática sitúa el componente0 en (47,55,53), dirección (+1,−1,+1), y el componente1 en (14,46,20), dirección (+1,+1,+1). Los recibos exactos se eligieron por el nombre fijo de puerto, nunca buscando un payload conveniente. Los primeros nodos nominales son:

| Ruta | Hoja q−53 | Intermedio q−47 | Raíz q−35 |
|---|---|---|---|
| Izquierda | (48,54,54) | (52,48,58) | (62,36,1) |
| Derecha | (15,47,21) | (19,53,25) | (29,65,35) |

La coordenada (52,48,58) es un punto de encuentro ya pertinente en PI05/PI06. Esa coincidencia de geometría justifica observar la ruta izquierda; no prueba que la historia actual contenga el mismo portador ni que una sola interferencia explique el fallo. El recálculo etiqueta todos estos nodos como **geometría nominal**, separada de las observaciones efectivamente incluidas en los primarios.

## Contraste acotado fijado antes de Native

Root fijó cuatro copias completas del mismo C884835: AR0, AR36, AR64 y AR0NOD. Las tres primeras usan el nuevo wrapper diagnóstico; la cuarta usa el modo directo anterior. El wrapper sólo avanza legalmente el mundo la espera declarada y llama la misma `native_pair(..., detailed=True)`. No escoge lector, respuesta, proveedor ni resultado. Las esperas 0/36/64 se aplican **antes de cada operación**, con el mismo valor en cada brazo. No se reajustan después de una respuesta.

Las cuatro secuencias son suma6+7 de desarrollo, suma4+5 reservada, suma8+3 reservada y diferencia del **entero realmente producido por esa última suma** menos2. Los valores normativos se guardan sólo en el evaluador. Un resultado no entero o NULL detiene el enlace; no se sustituye por11. Los planes R02 contienen el par completo real, hashes, fuentes, IDs exactos, horizonte finito por operación y posiciones/tiempos del lector. Los planes R01 anteriores se conservan como preparación no ejecutada con IDs superados antes de Native.

Desde C884835, la primera consulta sin espera será q884891 (mod67=22); con36, q884927 (58); con64, q884955 (19). Cambian también las fases391/782. Mantener simultáneamente esas dos fases y desplazar67 requeriría esperas de decenas de miles de ticks; Root eligió explícitamente este contraste local más pequeño. Las operaciones siguientes tienen sus propios calendarios previstos y no se presentan como cuatro repeticiones de una única fase67.

AR0 frente a AR0NOD compara la instrumentación existente detallada con la original: mismo origen, entradas y cadencia final. `detailed=True` añade lecturas de los42 nodos nominales y fronteras tempranas de avance; no añade solicitudes Native. La pasividad no se dio por supuesta: se contrastaron RAW, clocks, agenda, interfaces, recibos y metadatos pertinentes. El resultado y la diferencia documental efectiva se detallan al cierre, sin convertir igualdad física en igualdad de todo el entorno operativo.

## Reproducibilidad y localizadores

`fuentes/recalcular_antecedente_aritmetico_PI09_R01.py` produjo `ANTECEDENTE_ARITMETICO_RECALCULADO_PI09_R01.json` (36879 bytes; SHA256 `0065cf2315d810faa55b73253e6afe234aac323e9b0e76d2b35f5253a074d7df`). Conserva los seis localizadores exactos, tamaños, hashes, recibos completos de los dos canales pertinentes, firmas C y calendarios nominales. Native0; imports DEE0.

El wrapper `codigo/pi09_aritmetica_diagnostica_R01.py` tiene SHA256 `9011507985f5edb3d9a4fcf251e349ff6edf314353008b182944e94aab6e61b9`. Sus cinco pruebas puras, incluidas2346 comparaciones del calendario contra la función oficial extraída por AST, constan en `fuentes/PRUEBAS_PURAS_WRAPPER_ARITMETICA_PI09_R01.json`, SHA256 `c13324ab152c465f14db7bb4fb8d6794798fc9f15a1b9451e0979d4aa4f6f69a`. Las pruebas Fake comprueban orquestación y retención de NULL; no son ensayos físicos.

Planes efectivos: `codigo/PLAN_AR0_R02.json`, `PLAN_AR36_R02.json`, `PLAN_AR64_R02.json`, `PLAN_AR0NOD_R02.json`; hashes en `fuentes/PLANES_AR_PREPARADOS_PI09_R02.json`. Su fuente es `pares/C_HEREDADA_T884835/EXPORTACION_SERVICIO.json`, no una reconstrucción de arrays. El código, recálculo y planes no habilitan actuaciones sobre el principal ni promueven ningún diagnóstico.

## Primer brazo Native cerrado: AR0

Root cerró AR0 desde884835 hasta885627:792ticks, cuatro operaciones con176 solicitudes aplicadas cada una. Los enteros efectivos fueron **13,5,11,9**. La reserva4+5 no funcionó; se conserva. La tercera suma produjo11 y ese entero material se transportó a la diferencia−2, que produjo9. Esto tampoco acredita disponibilidad universal de suma.

En la reserva4+5, q885089 tiene fase67=19. La observación de la hoja izquierda (48,54,54) a q−53 registra payload4, SEM1 activo y dirección−Y. El intermedio (52,48,58) a q−47 registra RAW0. La raíz izquierda (62,36,1) a q−35 registra SEM1 activo con payload0. Los tres nodos correspondientes de la derecha registran5. C produce5. En las otras tres operaciones, los mismos tres nodos izquierdos registran respectivamente6,8 y11.

La evidencia acota una discrepancia de la ruta muestreada entre hoja e intermedio. No observa todos los ticks ni todo el mundo; RAW0 en un lugar no prueba pérdida global del4. Tampoco establece qué portador produjo cada registro. El cierre AR0NOD delimita la instrumentación en las cuatro operaciones concretas, con el efecto de metadatos explicado a continuación.

Los primarios y el recálculo ya transportable están en `control/AR_PORTABLE_AR0_R01`. `RESULTADO_RECALCULO.json` tiene SHA256 `481829b7c9b7cc46a945f0949399196442bade34b6a08d6ead5a8df5cc633054`. La selección exacta de seis nodos por operación está en `fuentes/F1_AR0_NODOS_OBSERVADOS_PI09_R01.json`. Este análisis añadió cero ticks y no cambió el circuito después del error.

Root cerró también AR36:936ticks hasta885771, cuatro dosis de176 entradas aplicadas y enteros **13,9,11,9**. Los seis nodos prefijados conservan las respectivas contribuciones en las cuatro operaciones. Sus consultas tienen fases67 **58,24,57,23**. La diferencia frente a AR0 muestra disponibilidad contextual de la misma función con otra historia temporal; todavía no identifica una causa única ni demuestra que una espera fija36 sirva indefinidamente.

## Contexto físico exploratorio, sin cambio de protocolo

Después de leer AR0/AR36 y mientras AR64 ya estaba en ejecución se leyó una única fila completa del snapshot fuente congelado C884835. En (52,48,z) hay cinco registros activos SEM1, payload0 y dirección+Z, en z20,23,30,39,53. Los otros62 sitios tienen RAW exactamente0. Esto está registrado en `fuentes/F1_FILA_FUENTE_C884835_PI09_R01.json` (SHA256 `6a81cfdcf4681cb006047be95032b4268d7d58b8d2a54a11250bd9b5293d95cf`). Son posiciones materiales simultáneas, no cinco identidades rastreadas por su payload.

Un modelo explícitamente condicional de traslación toroidal sin encuentros sitúa el registro inicialmente en z53 sobre el intermedio z58 en q−48 de la operación fallida4+5 de AR0:206ticks desde la fuente equivalen a5mod67. El mismo cálculo predice esa ocupación para la primera operación AR64. Los otros casos de los tres planes no presentan esa coincidencia según este modelo. La proyección se conserva en `F1_PROYECCION_EXPLORATORIA_PADRE_PI09_R01.json`, marcada exploratoria, posterior a AR0/36 y **no preregistrada antes del Native de AR64**. No fue información entregada al ente ni intervino en selección de esperas o lectores.

No se capturó globalmente q−48 en estas pruebas. Los encuentros podrían cambiar el recorrido, y la coincidencia geométrica no acredita ascendencia única. El hallazgo justifica una explicación de acceso interferido compatible con las notas anteriores; necesita una observación o intervención causal específica para elevarla sobre esa compatibilidad. No se ha borrado ni editado ninguno de esos registros.

## Cierre de las cuatro series y del observador

| Condición | T final | Ticks añadidos | Enteros observados | Usos normativos |
|---|---:|---:|---|---:|
| AR0 | 885627 | 792 | 13,5,11,9 | 3/4 |
| AR36 | 885771 | 936 | 13,9,11,9 | 4/4 |
| AR64 | 885892 | 1057 | 7,9,11,9 | 3/4 |
| AR0NOD, control del instrumento | 885627 | 792 | 13,5,11,9 | 3/4 |

Son3577ticks Native y2816 solicitudes directas aplicadas, cero rechazos y cero resultados numéricos NULL. Los tres brazos de fase dan10/12 usos normativos; AR0NOD es un control emparejado de instrumentación, no una réplica funcional independiente que aumente esa muestra. Todos comparten el prefijoC884835. En AR64, la primera suma6+7 vuelve a registrar hoja izquierda6, intermedio RAW0 y raíz izquierda payload0 a fase67=19, con fases391/782 diferentes de la reserva4+5 fallida de AR0. Las otras operaciones de ese brazo conservan sus contribuciones. Esto refuerza una condición temporal local; no prueba una ley universal de acceso.

AR0 y AR0NOD presentan igualdad exacta de RAW, clocks y del prefijo binario Native completo en los cuatro checkpoints: fase, interfaces, agenda pendiente y recibos incluidos. Los resultados, observaciones comunes y176 recibos por operación coinciden. **No hay igualdad literal del estado operativo completo.** La única diferencia de metadatos no administrativa identificada está en la lista `paused_intervals` del puente PI02R04, desactivado en ambas copias. El lector detallado divide `run_until` en más segmentos y ese puente guarda los últimos16 intervalos. Todos los demás campos R04, incluido `last_tick`, coinciden después de normalizar exclusivamente los nombres/rutas de transporte.

La revisión dirigida de `pi02_habitat_R04.py`, líneas74 y213–214, localiza la inicialización/escritura de esa lista y no encuentra un consumidor de ella en el código actual de capacidades. Esto explica el efecto registral; no autoriza llamarlo una lectura universalmente pasiva ni anticipar cualquier uso futuro de ese historial. El criterio estricto de igualdad operativa queda negativo y preservado en `control/CONTRASTE_OBSERVADOR_AR_COMPLETO_PI09_R01.json` (SHA256 `1d473b9796828820aa68fb8c070b4bbd0fca27791492aa71e61a4683a5e851d3`). El alcance positivo Native y el efecto documental de las cuatro comparaciones constan en `control/OBSERVACION_AR_ALCANCE_PI09_R02.json` (SHA256 `ff62599a531610c86b50fb14c3237c6cd32f678eff3111fb79e9fcf838335c9c`). No se borró ni excluyó retrospectivamente esa discrepancia para declarar igualdad total.

El paquete documental íntegro de las cuatro series está en `control/AR_PORTABLE_CUATRO_R01`: dieciséis primarios, cuatro pruebas de cierre, lector stdlib e índice de21 miembros hashados. `codigo/ARITMETICA_PORTABLE_PI09_R01.py recalcular --raiz <extracción> --salida <JSONnuevo>` utiliza sólo esos miembros relativos. Verifica el codec y C desde RAW, las dosis directas, los nodos registrados y el enlace de la última suma real a la diferencia−2. Es recálculo de evidencia, no repetición Native ni respaldo ejecutable.

## Revisión P0: preparación fijada y cierre negativo posterior

Root autorizó después de los pilotos una familia nueva de acceso temporal. No cambia los wrappers AR ni sus negativos. La regla preparada consulta exclusivamente el reloj y el calendario R3P0: si la siguiente consulta efectiva tiene fase67=19, avanza legalmente un tick y vuelve a pronosticar. El máximo es11ticks por el tramo de calendario protegido; si no se resuelve, se detiene conservando el futuro. No utiliza operandos, resultado esperado, estados de controles ni lecturas físicas para elegir la demora.

Las pruebas puras recorren los52394 ticks del período conjunto67×782. La alineación diagnóstica del desafío puede requerir133ticks porque el calendario protegido puede saltar una fase; se fija una cota145. La guardia puede requerir11. Son propiedades del cálculo de reloj, **no pruebas de éxito funcional**. La cota inicial78, insuficiente en una prueba pura, se corrigió antes de cualquier ejecución de esta revisión; el negativo está registrado.

`codigo/pi09_aritmetica_temporal_P0_R01.py` conserva intactos el codec, `native_pair` y lector C. El protocolo R02 vinculó dos copias del mismo futuro completo real que Root selló antes del nuevo lote; no permite combinar las memorias de AR. Sus nuevos pares reservados son2+8,9+7,5+11,3+4 y después diferencia del último entero real menos2. Ambos brazos usan la misma instrumentación detallada y una preparación de fase19 explícita; uno activa la guardia y otro no. Los operandos previos que se abrieron para descubrir esta regla ya son datos de desarrollo, no reserva de esta revisión.

La entrada pública propuesta `execute_public` conserva los cuatro campos del modo aritmético normal y fija internamente guardia activa/espera previa0. La selección COMMITTED y el contrato exacto pertenecen al hook externo de Root/I4; esta función no declara por sí misma una adopción. La interfaz diagnóstica sí rechaza sistemas seleccionados. Esta propuesta se sometió después al contraste siguiente y no se habilita como mejora: no es regulación adquirida ni aritmética descubierta por el ente.

Ambos brazos nuevos, desde el par completo Native T903603, cerraron la pausa administrativa, doce testigos publicados y cinco operaciones nuevas. PANEL terminó en T907542 con 3939 ticks; DISCOVERY terminó en T907543 con 3940. Ambos conservaron 12/12 y produjeron 10, 16, 16, 7, 5: 5/5 también sin guardia. Cada brazo aplicó 1827 solicitudes nuevas. El gate fijado antes de este lote exigía 5/5 con guardia, al menos dos aciertos más que el control y conservación no inferior. El resultado es `true/false/true`: la ganancia es 0 y el gate P0 queda negativo. Se conserva el acceso público legado y no se modifica ese criterio después de ver el resultado.

El control sin guardia tuvo las cinco consultas en la fase67=19; esa condición sola no fue suficiente para el fallo en esta historia material. La guardia pagó cinco ticks unitarios, mientras las esperas de alineación sumaron 98 ticks frente a 102: la diferencia total fue un tick. Antes de las reservas, RAW/clocks/tick de ambos brazos eran iguales; al final los hashes y la edad difieren aunque la utilidad coincide. Esa diferencia no prueba memoria útil.

La lectura posterior de dos checkpoints completos congelados, limitada a la misma fila de 67 sitios, encontró tres registros activos 0/+Z en T903603 (z28, z31, z47) y uno en T906450 (z61) antes de las reservas. La proyección exploratoria inicial de cinco registros ya no describe esa fotografía. No se infiere destrucción global, ascendencia única ni que una sola acción o retorno causara el cambio. Este resultado refina el problema de disponibilidad contextual, sin convertirlo en reparación aprendida.

Localizadores del cierre: `control/RECALCULO_PAREJA_P0_ARITMETICA_PI09_R01.json` (SHA256 `e22898150527dd3180908e4a00de1131a8b21c160bb603de410b35a1b3017cf3`), `mapas/MATRIZ_ARITMETICA_Y_CONSERVACION_PI09_R01.csv` y `documentos/FUENTE_ARITMETICA_MANUAL_PI09_CERRADA_R03.json`. Esta última fuente no autoriza Word por sí sola: Root debe fusionarla con el cierre real del principal y C1.
