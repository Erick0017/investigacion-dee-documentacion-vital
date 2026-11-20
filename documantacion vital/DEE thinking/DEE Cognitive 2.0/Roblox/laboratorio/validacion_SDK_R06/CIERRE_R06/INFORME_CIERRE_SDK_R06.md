# Comprobante de cierre local del SDK R06 — candidato 0.1.1

Este informe reúne **Core K1–K4, diez solicitudes CAP y el contraste focal de seis oportunidades por brazo, todos cerrados**. La validación es local, diagnóstica y asistida por el operador. **K5 externo: 0 participantes.** El vídeo está terminado y verificado. Los 16 archivos críticos protegidos conservaron sus bytes y SHA-256; no se declara un PASS global.

Las rutas enlazadas son relativas a `VALIDACION/CIERRE_R06`. El runtime privado se desplegó en `tests/_sdk_r06_valid_20261118/RUNTIME_PRIVADO_LOCAL` para evitar el límite real de longitud de ruta de las DLL de Windows. No se abrió el Principal como propietario de pruebas. La campaña vigente cuenta desde el 18 de noviembre de 2026 a las 13:37:40 UTC: última admisión 20:37:40 y cierre 21:37:40, sin reiniciar ese reloj.

## Resultado local y continuidad

La vida diagnóstica es `ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_SDK_DEMO_3666B1B0A4134233`, con instancia diagnóstica privada `SDK_DEMO_3666B1B0A4134233` y sesión `SDK_SESSION_ca791f9b9f5d4afeb8d3a3e69dac9c1f`. Se creó desde el prefijo experimental completo PAR28, **N67/T991187**, con su historia; no desde T0 ni desde el Principal protegido T947395.

| Comprobación | Evidencia local cerrada | Límite |
|---|---|---|
| K1: instalación y configuración | Paquete candidato, escena privada y servicio se ejecutaron localmente. La prueba material usó Studio Run, servidor sin PlayerClient. | No publicación cloud ni compatibilidad universal. |
| K2: conexión Native real | Solicitudes HTTP durables, propietario oficial, resultados Native y ACK reales en CORE1/CORE2. | La interfaz y el operador eligen iniciar el uso; no se atribuye autonomía de integración. |
| K3: ciclo ordinario | Dos ciclos, cada uno Q1 ASK_STATION, Q2 EXIT_1, efecto corporal/ACK y feedback aceptado; cierre normal y SDK_PAIR. | Dos oportunidades locales, no un estudio de rendimiento o generalización. |
| K4: guardar, restaurar y volver a usar | Misma vida/sesión: secuencia local 2→4, ciclos 1→2 y T992751→994315. Prueba de restauración persistida antes de observar y antes del nuevo Native. | Reapertura local concreta; no recuperación indefinida ni validación externa. |
| K5: evaluación externa | **0 participantes externos.** | Pendiente; no sustituida por pruebas del operador. |

El [recálculo K4](DEMOSTRACION/RECALCULO_K4_CORE2_R06.json) verifica **12 comprobaciones verdaderas y 0 diferencias** en los ocho campos acordados: namespace, fingerprint, bindings, estado, acciones, herramientas, cuerpo y mundo. La tolerancia `1e-5` se limita a poses/transformaciones documentadas; identidad, contadores, recibos, cursores y demás campos mantienen igualdad literal. Después de la prueba constan tres fases Native nuevas completadas, efecto con ACK y retorno comprometido. No se fingió una fase BOUNDARY ni se descartaron colisiones para obtener igualdad.

| Corte cerrado | Tick Native | Secuencia local | Ciclos Core | Estado |
|---|---:|---:|---:|---|
| Padre PAR28 | 991187 | 0 local; offset físico heredado | 0 nuevos | Prefijo completo conservado |
| CORE1 | 992751 | 2 | 1 | Propietario cerrado, pending0, SDK_PAIR |
| CORE2 / K4 | 994315 | 4 | 2 | Propietario cerrado, pending0, SDK_PAIR |
| CAP final | 995895 | Core permanece en4; CAP10 | 2 | Propietario Native cerrado, pending0; **WorldPair histórico** |

Los seis pasos Native Core consumieron **3128 ticks**. CAP añadió **1580**: incremento total **4708**, equivalente a T995895−T991187. Los 1097 inputs citados abajo pertenecen solamente a CAP; no se suman denominadores acumulativos de Core como si fueran solicitudes nuevas.

## Capacidades asistidas realmente ejercitadas

El operador fijó diez solicitudes antes de su ejecución. El conductor adoptó el ID del primer RECALL existente y no lo volvió a publicar. Los operandos, orden, forma y enseñanza son aportes explícitos del llamador; los contenidos y signos de salida son Native. El conductor no calculó respuestas esperadas ni sustituyó un NULL.

| # | Solicitud declarada | Contenido Native observado | Ticks | Inputs applied |
|---:|---|---|---:|---:|
| 1 | RECALL `luma` | Signo +1, FORMED | 39 | 7 |
| 2 | COMPARE 5 / 4 | Lector q+4: +1; q+6: +1 | 198 | 176 |
| 3 | COMPARE 4 / 5 | Lector q+4: −1; q+6: −1 | 198 | 176 |
| 4 | COMPARE 5 / 5 | Lector q+4: **0**; q+6: **NULL** | 198 | 176 |
| 5 | NUMERIC `suma`, 4 / 5 | Resultado 9, FORMED | 198 | 176 |
| 6 | COMPOSE [`luma`,`nara`], [4,5,2] | Intermedio Native transportado 9; resultado Native 7 | 484 | 366 |
| 7 | LESSON `luma`, signo −1, revisión, paired | Entrega de enseñanza registrada | 60 | 3 |
| 8 | RECALL `luma` | Signo −1, FORMED | 71 | 7 |
| 9 | LESSON `luma`, signo +1, revisión, paired | Entrega de enseñanza registrada | 63 | 3 |
| 10 | RECALL `luma` | Signo +1, FORMED | 71 | 7 |
| **Total CAP** | **10 eventos completados** | **0 pendientes/otros; 0 rejected** | **1580** | **1097** |

Los primarios conservan el valor físico y ambos lectores de COMPARE; **0 y NULL son distintos**. La secuencia de enseñanza/relectura está observada para una forma; admitir los pulsos de LESSON no basta por sí solo para afirmar aprendizaje general. COMPOSE es una cadena de dos formas en orden preparado, no una gramática o planificador general.

La API acota dos formas (`luma`, `nara`), comparación de enteros 0..20 y entradas aritméticas 0..32. NUMERIC usa las operaciones literales `suma`/`diferencia`; el ensayo de diez eventos ejercitó `suma`. SOLVE está expuesto en la interfaz, pero no constituye un evento adicional ejecutado en esta lista. Los calendarios, encoders y lectores históricos se conservaron: su preparación temporal es asistencia de la anatomía experimental, no aprendizaje del host.

El circuito Core expone observación, consulta pagada, acción física, ACK y consecuencias/feedback reales. Estas interfaces no acreditan una nueva política aprendida. **No se ensayó aquí una comunicación Native B integrada e independiente**; tampoco se atribuye al Native elección autónoma de herramientas, de solicitudes CAP o de su orden.

## Incidencias y conciliaciones conservadas

1. **Guarda de acceso CAP, antes del primer evento.** El arranque original intentó leer `INSTANCE.json` desde el participante y fue bloqueado por `access_guard`. La reparación R03 eliminó esa lectura: el participante valida Scope sellado e identidad/metadatos Native; el host sigue validando INSTANCE fuera del participante. Se preservaron código/Scope/registry y FAILED anteriores, con igualdad Native/ledger y **0 ticks nuevos**. No se relajó `access_guard` ni se modificó Core26, Focal, lector o kernel.
2. **Fallos transitorios de GET.** La [traza cerrada del conductor](EXT_R06/TRAZA_DRIVER_CERRADO_R06.json) conserva errores y reanudaciones de lectura sobre el mismo operationId. La conciliación fue GET; no rePOST material ni sustitución de contenidos. Es intervención técnica dirigida, no una capacidad autónoma demostrada del Native.
3. **Recibo CLOSE perdido por lifecycle R03.** Native ya había cerrado y la fila `ext_close_634f178b-b102-4971-98cb-e41ab0efa44f` estaba COMPLETED. El servidor R03 terminó antes del siguiente poll del cliente. El servidor RO R04 entregó ese mismo recibo autenticado, sin POST, propietario, tick ni cambio de archivo; la traza final registra `CLOSED_ALL_TEN_RECEIPT_RECONCILED_RO_NO_REPLAY`.
4. **Mejora futura, no reensayo.** El servicio R04 mantiene una gracia HTTP finita de hasta60s para servir CLOSE. Esa variante de servicio sólo tiene fixtures, no una nueva ejecución Native. Se verificaron seis fixtures de lifecycle y cinco del servidor RO. El cierre real de los diez eventos sigue atribuido a R03 y a la conciliación RO, no a un servicio R04 material inexistente.
5. **Exportación, sin cambio científico.** El exportador R03 rechazó un locator relativo Windows. R04 valida el locator relativo, normaliza sus separadores y exige contención, ausencia de reparse y SHA/tamaño exactos; no acepta rutas absolutas, drive, UNC o traversal. El intento anterior queda preservado. El export CAP_R04 y su recálculo portable terminaron con `issues: []`.

## Estado preservado y artefactos verificables

Antes de CAP se preservó el **corte operativo completo K4**: 5828 archivos, 539648316 bytes, con Native fuente idéntico y 0 ticks de copia. Su manifiesto privado es:

`tests/_sdk_r06_valid_20261118/RUNTIME_PRIVADO_LOCAL/estado_demo/prefijos/SDK_R06_K4_COMPLETO/MANIFIESTO_COPIA_K4.json`

SHA-256: `6de762874de10ba34e948a524ecbdc4aca3debb5df6f4ca10a16ee628f4c788b`.

Ese corte corresponde a **T994315**. Tras CAP el Native actual está en **T995895**, snapshot `8fc514c161c4b9efc93adc3267d23d1972ea2983f27a52ca916206fd4b76c1fa`, DB `332c8afcc12a9493faffa7bf5fbfa671c13b1200c59d180b9d02564367b9be75` y card `4c5e36e1f45d96ef96332007bff7a7d7f17b3c48d6b1f3d3657be83ef2340be0`. Su propietario está cerrado y pending0. El JSON SDK_PAIR de K4 pasa a ser **PRE_CAP histórico**: no se presenta como WorldPair actual ni como respaldo ejecutable completo del Native posterior.

| Artefacto cerrado | Qué permite revisar |
|---|---|
| [CORE1](EXPORT_CHATGPT/CORE1_R06/COMPROBANTE_CIERRE.json) y [CORE2](EXPORT_CHATGPT/CORE2_R06/COMPROBANTE_CIERRE.json) | Cierres, vida/sesión, ticks y cursores; primarios HTTP/ACK y recibos en sus carpetas |
| [Recálculo K4](DEMOSTRACION/RECALCULO_K4_CORE2_R06.json) | Restauración de los ocho campos contratados, hashes de pair/prueba y uso posterior |
| [CAP manifiesto](EXPORT_CHATGPT/CAP_R04/MANIFIESTO.json) | 31 miembros cerrados; SHA `71bd9a3596f43d28869a9554ece67d8ccb05e3928db212052d0fe902fb4eb289` |
| [CAP recálculo](EXPORT_CHATGPT/CAP_R04/RECALCULO.json) | Cadena de ticks, diez primarios, solicitudes/recibos literales y denominadores |
| [CAP recálculo portable](DEMOSTRACION/RECALCULO_CAP_PORTABLE_R04/RECALCULO.json) | Mismos datos recalculados desde la extracción; exit0/issues0 |
| [Traza cerrada](EXT_R06/TRAZA_DRIVER_CERRADO_R06.json) | Orden predeclarado, IDs, errores GET y recibo CLOSE conciliado; SHA `2c0a8c73cfb14d0e095a30b261e055d676fe4fb1d5b2fa4f32d570b58d717259` |

El export CAP incluye por separado el estado R03 actual, el FAILED histórico R02 y el recibo de reparación, ligados por SHA. No incluye snapshots Native, DB, credenciales o runtime privado. Por tanto sirve para revisión documental/recálculo; no sustituye los estados privados completos.

Recetas pasivas, con Python estándar y **destinos nuevos** (no repetir Native):

```text
python -I -S -B DEMOSTRACION/recalcular_K4_R06_ro.py --export-root EXPORT_CHATGPT/CORE2_R06 --comparison-code DEMOSTRACION/restoration_contract_RO.py --output K4_RECALCULO_NUEVO.json
```

Desde `EXPORT_CHATGPT/CAP_R04`:

```text
python -I -S -B RECALCULAR_CAPACIDADES_R06_R04.py recalculate --package-root . --output CAP_RECALCULO_NUEVO
```

## Contraste focal de disponibilidad — resultado cerrado

Es un ensayo separado del SDK básico, con dos copias completas del mismo PAR28 **N67/T991187**, geometría, actor Native, lector y codec heredados. No son dos individuos independientes ni experiencias sumables al SDK de capacidades. El brazo OSC es `SDK_DEMO_4072F463AD7868BB`; CONTROL es `SDK_DEMO_D48B1D97DBF3E85A`. El [GO prospectivo](FOCAL_EXPORT/FUENTES_PUBLICAS_ESENCIALES/GO_PROSPECTIVO_ROOT_R06.json) conservó las seis oportunidades por brazo, cuatro de desarrollo y dos reservadas, y los límites originales de 20:37:40/21:37:40 UTC. No se modificaron condiciones después de observar resultados.

La ley preparada consume un permiso local al verificar el paso por un puerto y lo repone tres épocas ambientales después. Su control mantiene los permisos disponibles. Consultar cuesta una unidad de stock y pasar por un puerto sin permiso cuesta dos. Ese stock pertenece al entorno simulado: no es energía interna ni metabolismo. La información local sólo llega materialmente a Native tras una consulta pagada; no se le entrega la disponibilidad global ni una ruta óptima. El peaje, por sí solo, **no activa `generic_failed`** en el actor heredado.

| Brazo | Oportunidades cerradas | T final | Ticks nuevos | Consulta / selección | Inputs Native | Stock y coste |
|---|---:|---:|---:|---|---|---|
| OSC | 6/6 | 1000571 | 9384 | 6 ASK y 6 EXIT_1 | 78 aplicados, 0 rechazados | 164→154; consultas6 y peajes4 |
| CONTROL | 6/6 | 1000571 | 9384 | 6 ASK y 6 EXIT_1 | 78 aplicados, 0 rechazados | 164→158; consultas6 y peajes0 |

OSC se cerró normalmente y selló `sdk_checkpoint_dcaf31bd-944a-43de-a66a-034580916dbb`. Su [paquete cerrado](EXPORT_CHATGPT/FOCAL_OSC_R06_R02/MANIFIESTO.json) conserva 29 archivos, con manifiesto SHA-256 `f90c3503bc95f3ac71e38e93abdb31d3930a7e1baefab3aaa5ef7155d5ee1726`. El recálculo portable terminó con `issues: []`. Se acreditaron seis datos Q2 aplicados y ninguna omisión. En los ciclos4 y5, el tag0 del panel codificó los precios de los puertos `[0,2]`: la salida1 tenía peaje2; el6 estaba repuesto. Tag0 es información codificada del panel, no precio monetario cero ni ausencia de consulta. Las seis actuaciones conservaron EXIT_1; no se afirma una mejora aprendida a partir de ese resultado aislado.

La trayectoria OSC fue **0→3→2→3→2→3→2**: cinco de seis movimientos exitosos pertenecen a 2↔3, con una racha de cinco. No hubo salida observada de ese conjunto tras entrar. De las reposiciones ambientales registradas, sólo el panel de estación3 fue consultado en la oportunidad6 después de su reposición en la época5: eso no significa que Native observara directamente el evento interno de recarga. No se cuentan como exposiciones las otras dos reposiciones. El tag0 del panel de los ciclos4 y5 se transdujo en los payloads Native9 y6, con recibos155198 y155211 aplicados; el panel posterior a reposición produjo payload10, recibo155224 aplicado. Ese tag no equivale a pulso cero, NULL, NoQuery o castigo Native. Los [recibos y métricas](FOCAL_EXPORT/OSC_TRAYECTORIA_METRICAS_R06.json) conservan esos denominadores y su procedencia sin ejecutar nuevamente Native.

El exportador inicial se detuvo, antes de crear una entrega, al comparar literalmente dos representaciones de `/evidence`. El adaptador existente y congelado resume esa rama e incorpora el SHA-256 canónico del resultado Native completo; todos los demás campos son literales. La revisión R02 del **lector externo**, con fixtures, exige esa proyección exacta, el mismo ID, el hash completo y todos los campos funcionales. Conserva diario Native, DTO, ACK y pareja cerrada. No cambió el adaptador material ni se repitió una decisión. El locator de evidencia antiguo que contiene el texto `DEE_SDK_NATIVE_0_1_0` queda identificado como metadato heredado; la evidencia se resuelve por diario e identificador comprobados, sin inventar una ruta.

CONTROL se cerró normalmente y selló `sdk_checkpoint_8ba7df15-6f7f-43ce-92f7-0227982137ec`. Su [paquete cerrado](EXPORT_CHATGPT/FOCAL_CONTROL_R06_R02/MANIFIESTO.json) conserva 29 archivos, manifiesto SHA-256 `0fb4c5440c76c9db2d085305f61c9f85c95b934ac23806f0a685fdc5df29f3a3`. Exportación, recálculo portable y [comparación](DEMOSTRACION/COMPARACION_FOCAL_R06_R02/COMPARACION_DESCRIPTIVA.json) terminaron sin incidencias. En los seis pares se conservaron las mismas consultas y selecciones de salida; la trayectoria CONTROL también fue **0→3→2→3→2→3→2**, con5/6 movimientos2↔3 y ninguna salida observada. En4 y5 difirieron el tag y el peaje: OSC tag0/peaje2 frente a CONTROL tag1/peaje0. La ley consumidora produjo **cuatro unidades adicionales de coste**, sin una adaptación útil observada en este horizonte. Los datos llegaron materialmente a Native, pero eso no demuestra que adquiriera su significado económico. No hubo señal genérica de fallo por esos peajes. Son dos historias de un mismo prefijo, no una estimación poblacional ni un límite universal de DEE.

La comprobación administrativa de lease avanzó cero ticks y conservó igualdad física/prefijo causal. El observador histórico también registró la diferencia de una clave nueva de lease: eso impide hablar de identidad binaria global del contenedor, sin implicar una diferencia del estado físico importado. La operación administrativa no constituye aprendizaje o recuperación autónoma.

## Incorporación local efectivamente aplicada

La carpeta `DEE Cognitive 2.0/entregas/DEE_ROBLOX_SDK_PILOTO` ofrece ahora la revisión **0.1.1**: `KIT_DESARROLLADOR`, `KIT_EXTENSION`, la copia exacta `PUBLICO_0_1_1`, `LEER_PRIMERO.md`, `VERSION.txt`, `LOCALIZADORES_0_1_1.json` y el verificador `SDK_VERIFICAR_0_1_1.ps1`. El [recibo de incorporación](INCORPORACION_APLICADA_R06_01.json) registra `COMPLETED`, los hashes públicos y de vídeo y la comprobación del archivo anterior. Sólo se cambiaron estos elementos del SDK: no hubo promoción, nueva adquisición ni tick por copiar los archivos.

El verificador ejecutado desde la raíz actual del SDK devolvió `integrity: VERIFIED`, **42 miembros**, manifiesto `c8bfa14a29c190eed76458e6770728cbd6ad8ffb4c6c79c6b6994e9d6f04c187`, sin importar o ejecutar Native. Ese resultado acredita hashes y defaults públicos; los ensayos materiales están documentados por separado arriba.

Los anteriores README/VERSION/KIT se conservaron en `ANTERIOR_SDK_0_1_0`; el ZIP 0.1.0 histórico y su vídeo de 15 s permanecen intactos. El vídeo actual se copió además a `DEE_ROBLOX_SDK_PILOTO/DEMOSTRACION/DEE_ROBLOX_SDK_0_1_1_CIERRE_R06.mp4`, con el mismo SHA que el render verificado.

El kit compartible permite inspeccionar módulos, abrir los ejemplos y usar PREVIEW; Native requiere el backend privado y el estado autorizado en el equipo de demostración. El primer piloto está definido como **local acompañado**: no se ofrece servicio remoto ni se ha medido instalación o utilidad por un desarrollador externo. El protocolo del cliente acepta cuotas anunciadas de hasta 12 eventos; **el Scope material de esta validación autorizó 10 y ejecutó 10**. CLOSE y GET no son eventos Native adicionales.

La extensión proporciona interfaces para elegir un experimento y sus entradas, no para elegir automáticamente qué capacidad conviene. Consultas y consecuencias están conectadas en Core; aprendizaje nuevo de una política útil, comunicación entre dos participantes Native y selección autónoma de una cadena no se acreditaron aquí. No se transfirieron recuerdos al Principal ni entre las tres vidas diagnósticas.

## Verificación final, límites y continuidad

- **FOCAL:** ambos brazos cerraron6/6, cada uno con9384ticks nuevos; hay exportación, recálculo portable y comparación. La ley modificó la exposición y el coste, sin una mejora conductual observada. No se promociona una capacidad a partir de este negativo.
- **Vídeo terminado:** [MP4](DEMOSTRACION/MONTAJE_0_1_1_FINAL_R02/DEE_ROBLOX_SDK_CIERRE_R06.mp4), 129 s, 1920×1080 compuesto, H.264, 30 fps constantes, SAR 1:1, 3870 fotogramas y sin pistas de audio. Son **2333557 bytes**, SHA-256 `fedb353670a367c1eafa7b47d095ce4d9405e8ad6355a81a73078a55d0100906`. Se decodificaron todos los fotogramas y se revisaron 14 muestras y una vista horizontal reducida; no se declara reproducción humana continua ni prueba física de iPhone. El vídeo combina 15 segundos de captura histórica real R07 con explicaciones identificadas de los registros actuales del SDK. **No existe una nueva captura de juego de R06 acreditada**: la captura MCP no entregó datos y el control de ventana no consiguió acceder a esa superficie. La composición 1080p no convierte la captura histórica de menor tamaño en una captura nativa de esa resolución. La [verificación](DEMOSTRACION/MONTAJE_0_1_1_FINAL_R02/QA_FINAL/VERIFICACION_VIDEO_R06.json) conserva metadatos y cobertura. El MP4 anterior permanece intacto.
- **Protección final:** [antes](CRITICOS_ANTES.json) y [después](CRITICOS_DESPUES_R06.json) acreditan **16/16 archivos sin cambios** de tamaño o SHA-256, estables durante la lectura. El resultado posterior tiene SHA-256 `cbda7bd797f6fad2b09e0f35b03737bc062a4c4fa82eb81779a12a35e7373727`. Incluyen el selector, tarjeta y snapshot del Principal, el Manual1.40, kernel/WHL/PYD y los testigos del cierre anterior. Esto no certifica la inmutabilidad de archivos no comprobados.
- **K5 externo:** sigue en0. No se han obtenido participantes ni evaluación independiente.

El ledger final conserva **23476/40000 ticks nuevos**, sin intenciones pendientes y con todas las reservas en0: SDK Core/CAP4708, OSC9384 y CONTROL9384. Su SHA-256 local es `1c9384ad3581b26ece726f613ea368d0590a030441b8cd4370d3e4a78e5c43e8`, en `tests/_sdk_r06_valid_20261118/RUNTIME_PRIVADO_LOCAL/estado_demo/LEDGER_SDK_R06.json`. Estos ticks suman trabajo técnico en tres vidas, no experiencia de un único individuo ni réplicas independientes. Los propietarios Native terminaron y se cerraron únicamente las instancias de Studio abiertas por esta validación; los proyectos de Studio previamente abiertos se conservaron.

El Principal protegido continúa seleccionado como **ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01, N67/T947395**. La vida SDK asistida queda en **N67/T995895** y las dos copias focales en **N67/T1000571**, cada una con su propia genealogía y estado completo. No se modifica el Manual rector1.40, no se promueve ninguna de estas vidas y no se fusionan recuerdos.

El avance entregado es una integración operativa local: Core ordinario y reapertura, interfaces de memoria/revisión, comparación y aritmética/composición asistida, evidencia portable y vídeo comparativo honesto. El cuerpo, calendario, lectores, codec y orden de las solicitudes fueron preparados; Native produjo los signos, selecciones y resultados que se registran. Quedan concretamente sin acreditar la elección autónoma de herramientas, una política nueva útil por consecuencias, comunicación entre participantes Native dentro del SDK y evaluación externaK5. El contraste focal no resuelve esas preguntas ni invalida las capacidades locales demostradas.
