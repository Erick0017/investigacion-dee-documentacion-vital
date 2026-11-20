# C2/E3: consulta, uso de información y controles PI09

Preparado antes de resultados Native PI09. Esta nota reúne el diseño causal; no añade otra campaña ni una aprobación. El principal leído en `DEE Cognitive 2.0/sistema/estado/ACTIVO.json` sigue siendo A, N67/T861426, snapshot `2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133`. La descendencia experimental elegida por Root es C íntegra, T884835, con historia B y seis oportunidades C conservadas; no se fusionan futuros.

## Pregunta y prioridad

La primera ganancia buscada es un acceso condicional íntegro y utilizable cuyo contenido contribuya causalmente a una acción Native útil. Aprender específicamente el valor de preguntar es una afirmación adicional. No se bloquea el primer hito por no acreditar esa segunda afirmación, ni se convierte un cambio de banco compartido en evidencia suficiente de ella.

La autoridad de evaluación es `codigo/CRITERIOS_PI09_R01.json`, fijada por Root antes de PI09 Native: piso de 8/12 resultados conjuntos y 4/6 en reserva; continuidad y reapertura completas; reproducción material decisiva; disponibilidad de los siete testigos lingüísticos/contextuales y tres comparaciones con signo. La posible indisponibilidad de los dos testigos aritméticos enlazados requiere delimitación y una ganancia informativa causal compensatoria. Esto no aprueba retrospectivamente PI08 B ni declara reparada la suma.

## Mecanismo leído y diferencia que permite el control

En `PI08/codigo/pi08_consulta_condicional_C_R03.py`, la muestra física de preview se captura en `(30,40,30)` a q1−1. Sólo su STATE entra a la primera TC; una partícula +X y una +Z con STATE1 son indistinguibles para esa selección. El RAW completo queda en un registro técnico externo. La elección Native +1 emite una petición fija +X en `(33,40,30)` a q1+7; el recibo propio aplicado y una firma física en `(34,40,30)` a q1+8 habilitan la liberación. Un +Z activo SEM1 se codifica como 1, +X activo SEM1 como 0 y ausencia RAW0 como 0. Firmas no reconocidas son NULL, sin rellenarlas a partir de una etiqueta.

Sin petición no entra esa observación adicional: la segunda TC recibe el cero material preparado para NoQuery. Ese cero, la ausencia medida, un +X observado y una elección Native cero pueden coincidir materialmente en ciertos puntos, pero mantienen procedencia distinta en el expediente. No se les atribuye información que el participante no recibió.

`pi08_consulta_condicional_C_segunda_R02.py` conserva la segunda selección, la copia eferente, el pulso transversal fijo, el mensaje y la comparación FI del cuerpo R03. El fallo genérico procede del resultado físico FI y de la entrega efectiva del mensaje, no de una respuesta preferida. El retorno de q2+408 no incluye un argumento para elegir banco o acción retrospectivamente.

Ambas selecciones comparten la TC y los bancos. C declara expresamente `no_generic_return_scheduled_for_first_trace=True`: sólo la segunda copia tiene el emparejamiento de retorno establecido. Una elección de preguntar que cambia después de la experiencia puede provenir del ajuste general producido por esa segunda etapa. PI09 R01 conserva ese límite; no atribuye crédito propio a preguntar ni capacidad aprendida de ordenar las dos consultas.

## Contraste prospectivo compacto

`codigo/PROTOCOLO_PI09_CONSULTA_R01.json` fija seis oportunidades de desarrollo, seis reservadas y seis de uso futuro no evaluadas. Las primeras doce contienen cuatro emisiones nominales threat, cuatro falsecue y cuatro none. Las palabras del currículo sólo preparan emisiones ambientales; el participante recibe los estados físicos observados. Residuos y ocupaciones pueden hacer que una amenaza nominal no llegue al sensor: eso es un resultado y se conserva.

Los cuatro brazos parten del mismo conjunto C completo y usan las mismas dos TC, lectores, ventanas y familia de oportunidades:

| Brazo | Primera actuación | Dato después de petición aplicada |
|---|---|---|
| Native real | Elección física Native | Muestra RAW propia del episodio |
| Always real | Referencia material: petición fija | Muestra RAW propia del episodio |
| Never | Referencia material: abstención fija | NoQuery0 preparado |
| Always desacoplado | Misma petición fija | Muestra RAW real de Always real, permutación prefijada |

La referencia cambia sólo la primera actuación y su copia física; los primarios distinguen la elección Native, el motor efectivo impuesto a la referencia, la petición y su admisión. Las referencias nunca dirigen a la candidata. La segunda actuación continúa siendo Native.

La permutación es `source_plus_5`, índices `[5,6,7,8,9,10,11,0,1,2,3,4]`, fijada antes de observar PI09. El plan sólo se crea tras completar los doce Always real; contiene las muestras RAW, hashes de observación y primario, y el hash del comprobante fuente. No contiene una respuesta calculada, una actuación correcta o una ruta a abrir por el actor. El validador comprueba también que los campos declarados decodifiquen literalmente del uint64 RAW. Un origen ambiguo bloquea el plan: no se cambia la permutación ni se inventa un bit.

Always real frente a Always desacoplado fija las peticiones y el mecanismo de liberación, por lo que es el contraste principal de contenido. Se registrarán coincidencias residuales de bits: una permutación fija no garantiza ausencia total de información. Si un contraste no separa el contenido efectivamente recibido, se declara no resolutivo. Native real frente a Never y Always real compara acceso/selección material; no calcula productos contrafactuales a partir de las acciones observadas en una sola vida.

Las consecuencias reales y, por tanto, el número de retornos de fallo pueden divergir después de desacoplar el dato. No es un control de valencia negativa igualada. La primera divergencia útil de acción/efecto bajo prefijo y calendario pertinentes puede sostener una contribución local del contenido; el total posterior incluye la historia causada por esos retornos. No se le atribuye exclusivamente al bit instantáneo si los bancos ya divergen.

## Tiempo, coste y alcance

En el dispositivo heredado, preguntar añade un nacimiento Native. Las dos consultas TC y sus ventanas seriales están presentes incluso en Never. No se ha agregado un conflicto funcional al coste de preguntar: Always puede resultar óptimo dentro de este dominio. Se publicarán utilidad, peticiones, entradas Native y ticks por separado, sin una moneda arbitraria ni llamar energía a s_reg o a memoria del anfitrión.

La muestra es histórica respecto a la liberación: q1−1 a q1+8 son nueve ticks; su edad a la segunda entrada será la que resulte del q2 efectivo. No es una lectura fresca ni memoria adquirida Native. Las esperas reservadas 3/11 son preparaciones temporales; el normalizador puede realinearlas. Se compararán q1/q2 efectivos y residuos 67/391/782, no sólo los tiempos nominales, sin exigir una invariancia universal de fase.

La nueva preparación PI09 tiene cero ticks y cero entradas Native: admite un lote ambiental versionado y un journal nuevo. Conserva literalmente los metadatos C/B/R03 heredados y sus ordinales, y conserva los bancos físicos. Reutiliza los puertos y el sink C existente; no instala una guarda tras un fallo. Las seis ofertas futuras están declaradas antes de la evaluación, no son seis aciertos anticipados. Sólo la vida Native real exacta puede recibir posteriormente el permiso COMMITTED; las referencias nunca pueden convertirse en principal.

## Lecturas y reutilización dirigidas

- Leído completo: adjunto PI09 y `codigo/CRITERIOS_PI09_R01.json`.
- Leídos como texto: C.R03 y segunda R02, protocolo C.R02 y contrato de muestra/petición; helper `pi03_credito_generico_R01_BORRADOR.py`, en particular `schedule_trial` y la fase 391/782.
- Reutilizados: seis primarios, testigos y productos PI08 del bundle `control/C_PORTABLE_FINAL_R01`, cuyo recálculo cerrado separa 5/6 útiles y cuatro peticiones. No se contabilizan como nuevos ensayos PI09.
- Reutilizados literalmente para recálculo documental: `RECALCULAR_C_PI08_R05.py` SHA `4e8dd7b8df3d574c2cc7cd123ac47dc18881e285b926aa9d96ead97712523c91` y el decodificador RAW/recibos PI07 SHA `bbc81b6c01ca455ed961ae3cb53f29a6650374676ddc31df5f55af9a8a8b3470`.
- Pruebas nuevas exclusivamente puras: contrato de plan, ocho anclas del adaptador local, separación elección/motor de referencia, flujo Fake, ausencia de imports DEE y recálculo de fixture sintético derivado de PI08. No acreditan pasividad material de un observador nuevo ni resultados Native PI09.

No se realizó un inventario general, una nueva lectura de todo el corpus, una ejecución Native, una modificación del producto, una reenseñanza ni una intervención sobre RAW/clocks. La lectura dirigida resuelve el diseño actual; las causas abiertas de la aritmética posterior de B permanecen abiertas.

## Revisión técnica R02, previa a la primera consulta PI09

Antes de ejecutar PREPARE o episodios PI09, I4 detectó un riesgo de cuota administrativa: la guardia heredada de `_encoded` admite como máximo 65.536 bytes JSON por progreso y C conservaba la primera etapa completa dentro de `first_stage_rows`. R01 y su protocolo quedaron preservados. Root confirmó que no había KEY PI09 R01 ni consultas nuevas en la vida importada; sus controles aritméticos independientes no se reinterpretan como experiencias de este circuito.

`codigo/pi09_consulta_selectiva_R02.py` abre KEY/FOLDER/VERSION y sello R02 nuevos, sobre el mismo protocolo de 18 ofertas SHA `cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5`. La única diferencia AST del episodio científico respecto al adaptador R01 es que el append administrativo de la primera etapa almacena ordinal, q1 y referencia verificable al testigo. El primer registro completo sigue en el testigo inmediato, el evento del journal y el primario; el registro actual de muestra pendiente no se compacta ni cambia. No varían llamadas, entradas, tiempos, lectura, selección, actuación ni retorno Native.

La prueba pura con la metadata C6 cerrada y un buffer conservador adicional de 6.500 bytes reproduce 81.300 bytes al guardar 18 primeras etapas completas, frente a un máximo de 19.785 bytes con referencias. Ejecuta la guardia literal heredada con codificadores stdlib sustitutos, sin DEE. El contraste AST y la prueba de flujo Fake preservan la distinción entre referencia compacta y evidencia externa completa. Estos datos acreditan el arreglo de almacenamiento dentro de la cota ensayada; no son un ensayo Native de los 18 episodios.

Las identidades futuras se fijan en el sello antes de consultar: referencia/read-only, reproducción Native y continuación experimental son clases separadas. La continuación experimental sólo admite KEY R02 heredada y política Native real, nunca PREPARE/reset ni selección como principal. El permiso seleccionado sigue limitado a la vida canónica Native real y a una adopción COMMITTED real. Exportador y recálculo distinguen R01/R02 por vida y versión y conservan los errores; los tags previstos para la consulta ejecutable son ahora `PI09_NATIVE_R02`, `PI09_ALWAYS_R02`, `PI09_NEVER_R02` y `PI09_YOKE_R02`.

La revisión posterior de transporte R03 conserva el cuerpo R02 y el protocolo científico. Root informó un primer PREPARE R02 rechazado antes de entradas/ticks por comparar el sello de ocho campos con `_physical` de cuatro; preservó ese intento y corrigió exclusivamente la representación esperada del sello. Los nuevos tags son `PI09_NATIVE_R03`, `PI09_ALWAYS_R03`, `PI09_NEVER_R03` y `PI09_YOKE_R03`, sin reenviar el identificador rechazado. Las utilidades incluyen por defecto R02 y R03 para mantener esa incidencia; el cambio de tag no se cuenta como experiencia nueva ni como resultado funcional positivo.

## Extensión condicional propuesta: inversión física de utilidad

Esta propuesta aún no es un resultado ni una autorización de Native. Sólo tendría prioridad tras consolidar el primer hito, con A y el nuevo principal protegidos. Root propone una continuación DISCOVERY y un control NoFail desde el mismo corte completo, con el mismo soporte P0. El viejo progreso R02 ordinal12 quedaría literal; un nuevo namespace declararía seis oportunidades de entorno y conservaría bancos e historia, sin reset físico.

El único sitio propuesto es `(52,48,48)`: nacimiento legal estacionario, STATE0/SEM4/carga0/dirección0, admisión T+2 y tres ticks de preparación, tras preflight RAW0 íntegro. Si está ocupado, se rechaza esa preparación sin cambiar de sitio ni limpiar. El cue +Z declarado en46 puede alcanzar el sensor47 a q2−1 antes de encontrar48; la muestra independiente del preview y su código +Z siguen siendo físicos. El mensaje legítimo conserva su puerto `(53,48,56)` y su dirección +X. Si se programa también la petición de pulso al mismo puerto/tick, el coste es el conflicto de admisión Native: se registran ambos recibos, sin llamar aplicado a un pulso rechazado.

F1 reabrió como texto `4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp`, SHA `fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`: SEM_OBSERVER=4, línea49; `actualizar_voxel`, línea248, conserva ese RAW y avanza clock antes de procesar vecinos; el DEMUX también lo omite, línea434. El soporte no cuenta como vecino activo por tener STATE0. La predicción es bloqueo de la copia al destino48, no aniquilación global ni garantía sobre otras trayectorias. Guardas previas se conservan. Esta geometría es preparación externa, no una regulación descubierta.

Con comparación y mensaje útiles, la información +Z que antes justificaba proteger puede ahora acompañar una situación donde abstenerse conserva la entrega. El retorno seguirá procediendo de FI/mensaje reales y sólo tendrá el emparejamiento conocido de la segunda etapa. Una disminución de consultas iniciales puede ser efecto del banco compartido; no prueba por sí sola aprendizaje del valor de preguntar. Si la fuente ya inicia absteniéndose, ambos brazos podrían acertar sin nueva revisión: se declara ese resultado y no se fuerzan referencias, datos o errores para producir una curva.

Seis oportunidades por brazo y dos preparaciones de tres ticks acotan la extensión en `2×6×2110+6 = 25.326` ticks máximos, sujetos al saldo real, almacenamiento y slots que Root compruebe. El control NoFail diferencia historia con/sin señales de fallo; no iguala la dosis negativa y no aísla superioridad de contingencia verdadera frente a una yoke. No se añaden réplicas o calendarios después de ver respuestas. El soporte persistente permite una inversión, sin prometer otra inversión posterior dentro de esos seis casos.

El nuevo NoFail necesita una identidad diagnóstica exacta y una vista read-only del KEY R02 heredado: el sello R02 congelado sólo preveía DISCOVERY. Eso debe resolverse mediante adaptación administrativa versionada antes de abrir ese control, conservando el sello y actor R02 literales; no mediante ampliar una allowlist en el fichero ya usado. Una receta posterior debe preservar el prefijo completo, la preparación P0 y la historia resultante; no reconstruir la continuación desde respuestas guardadas.
