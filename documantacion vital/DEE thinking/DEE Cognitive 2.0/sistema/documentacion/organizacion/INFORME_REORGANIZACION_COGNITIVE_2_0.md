# Informe de reorganización controlada — DEE Cognitive 2.0

**INVESTIGACIÓN DEE · cierre 2026-11-18T21:32:14.498781-06:00.** Base: auditoría estructural existente; sólo se reabrieron las dependencias necesarias para trasladar archivos con seguridad. No es una campaña científica ni una validación Native.

## 1. Resultado ejecutivo

Se mantiene **un único Cognitive**, con núcleo, motor, ente principal y almacén de reproducción en sus ubicaciones originales. Roblox dispone de una entrada modular, SDK público canónico 0.1.1, documentación y ejemplos enlazados, laboratorio identificado y referencias privadas separadas. El compendio histórico PI01–PI10 pasó al archivo interno, con sus once archivos íntegros y sus diez originales externos conservados.

Se completaron dos grupos de traslado, tres correcciones documentales/de acceso y once archivos nuevos de entrada/protección, además de este informe. No se borró contenido, no se publicó nada ni se inicializó Git. No se instaló ninguna dependencia.

La organización general de `documantacion vital` y los proyectos independientes Universe/Thinking quedan intactos. No se crearon contenedores «Cognitive operativo», otro producto ni otra vida principal.

## 2. Estructura real resultante

```text
DEE Cognitive 2.0/
├── ABRIR_DEE_COGNITIVE.bat                       [sin cambios]
├── LEER_PRIMERO.md                             [nueva entrada]
├── .gitignore                                 [preventiva; no licencia]
├── PROYECTO.json                               [sin cambios]
├── CONTINUIDAD_DEE_COGNITIVE_2_0.json            [sin cambios]
├── DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx
├── aplicacion/                                 [sin cambios]
├── sistema/                                    [núcleo sin cambios]
│   ├── app/ · capacidades/ · contratos/ · organizaciones/
│   ├── runtime/ · estado/                      [sin cambios]
│   └── documentacion/organizacion/             [este informe]
├── motor/                                      [sin cambios]
├── reproducibilidad/                           [materiales/recetas sin cambios]
│   └── LEER_PRIMERO.md                         [actualidad aclarada]
├── Roblox/
│   ├── LEER_PRIMERO.md · LOCALIZADORES.json
│   ├── sdk/
│   │   ├── 0.1.1/                              [SDK público íntegro trasladado]
│   │   │   ├── KIT_DESARROLLADOR/ · KIT_EXTENSION/
│   │   │   ├── GUIAS/ · herramientas/ · METADATOS/
│   │   │   └── MANIFIESTO.json y metadatos originales
│   │   ├── LEER_PRIMERO.md
│   │   └── VERIFICAR.ps1                        [puro, sin Native]
│   ├── documentacion/LEER_PRIMERO.md            [índice de guías originales]
│   ├── ejemplos/LEER_PRIMERO.md                 [acceso a escenas del SDK]
│   ├── laboratorio/LEER_PRIMERO.md              [referencias al laboratorio]
│   └── privado/LEER_PRIMERO.md                  [referencias; sin token copiado]
├── archivo/
│   ├── LEER_PRIMERO.md
│   └── COMPENDIO_PI01_PI10/                     [10 ZIP + índice intactos]
├── laboratorio/DEE_ROBLOX_RBX01/                [se conserva: escenas abiertas]
└── entregas/
    ├── DEE_ROBLOX_SDK_PILOTO/                   [provisión/evidencia/compatibilidad]
    │   ├── KIT_DESARROLLADOR/ · KIT_EXTENSION/  [fuentes congeladas]
    │   ├── RUNTIME_PRIVADO_LOCAL/               [bundle largo; no operativo]
    │   ├── VALIDACION/ · DEMOSTRACION/           [rutas históricas conservadas]
    │   └── ZIP, VERSION y localizador original conservados
    └── otras entregas                          [sin cambios]
```

Las categorías `archivo/distribuciones_cerradas`, `validaciones_cerradas` y `documentos_historicos` no se crearon vacías: no hubo un traslado adicional a ellas que pudiera cerrarse con las comprobaciones permitidas. La estructura es lógica y funcional; no se sacrificaron dependencias para reproducir un dibujo.

## 3. Traslados ejecutados e integridad

Rutas relativas a `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0`:

| Origen | Destino | Archivos | Bytes | Verificación |
|---|---|---:|---:|---|
| `entregas/DEE_ROBLOX_SDK_PILOTO/PUBLICO_0_1_1` | `Roblox/sdk/0.1.1` | 42 | 344060 | Iguales antes/después |
| `COMPENDIO_PI01_PI10` | `archivo/COMPENDIO_PI01_PI10` | 11 | 69807987 | Iguales antes/después |

Todos los nombres, bytes y SHA-256 de cada grupo coinciden. No hay un segundo árbol público activo en la ubicación antigua. Las copias KIT congeladas conservadas en entregas se identifican como fuentes/procedencia, no como versiones activas contradictorias.

Los diez ZIP del compendio fueron comparados con sus diez originales externos antes del traslado, sin modificar estos últimos. También se comprobó su integridad ZIP al finalizar. El índice conserva literalmente su fecha, ruta y edición histórica de PI10: no se reescribió como si se hubiera creado en su nuevo destino.

## 4. Principal y componentes que permanecieron

**`ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01` · fisica_directa · N67/T947395 · COMMITTED.** ACTIVO, PROYECTO y selección personal siguen concordando. PI11 T979389 y los futuros de Roblox no sustituyen al principal. El panel 12/12 pertenece a T943970; no se atribuye al corte final otro panel no ejecutado.

Conjunto principal, sin traslado ni copia de bases:

- Vida: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\sistema\estado\vidas\ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`.
- Checkpoint: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\sistema\estado\checkpoints\ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01.T947395.035633918ed5.deetsnap.gz`.
- Servicio persistente: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\sistema\estado\servicios_persistentes\ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`.
- Recursos y artefactos locales: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\sistema\estado\servicios_locales\ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`.
- Capas `aplicacion/`, `sistema/app/`, capacidades, contratos, organizaciones, motor, materiales y recetas de reproducción permanecen en su sitio.

El conjunto completo exige snapshot con interfaces/agenda/progreso, vida/historia, diario y pendientes, SQLite/auxiliares, recibos, artefactos y recursos de sus contratos. No se trató un snapshot como respaldo completo, no se abrió SQLite y no se reconstruyó ni se restauró ningún estado.

Se verificaron antes/después **43 archivos críticos**, incluidos selectores, snapshot/vida/historia, archivos de primer nivel del servicio principal presentes en el corte, Manual, contratos seleccionados, RECURSOS, binarios/ruedas oficiales seleccionados y localizadores privados relevantes. Coinciden tamaño, hash y mtime en ese alcance. El manifiesto externo enumera exactamente cuáles: no es una certificación hash de todo el proyecto ni una prueba de coherencia interna de SQLite.

## 5. Roblox: organización y excepciones

SDK canónico: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\Roblox\sdk\0.1.1`.

Entrada del módulo: [Roblox/LEER_PRIMERO.md](<../../../Roblox/LEER_PRIMERO.md>); guías: [documentacion/LEER_PRIMERO.md](<../../../Roblox/documentacion/LEER_PRIMERO.md>); ejemplos: [ejemplos/LEER_PRIMERO.md](<../../../Roblox/ejemplos/LEER_PRIMERO.md>); localizador: [LOCALIZADORES.json](<../../../Roblox/LOCALIZADORES.json>).

Se reutiliza sin alterar el SDK 0.1.1. No se cambiaron fuentes Luau, Sources incrustados, contratos, configuraciones, capacidades o protocolo. El manifiesto público sigue con SHA-256 `c8bfa14a29c190eed76458e6770728cbd6ad8ffb4c6c79c6b6994e9d6f04c187`; el verificador informó 42 miembros e integridad VERIFIED, tanto desde la entrada nueva como desde la anterior. Eso comprueba archivos/defaults públicos; no ejecuta ni reproduce Native.

**Se conservaron en sus rutas:**

| Componente | Motivo y acceso actual |
|---|---|
| `laboratorio/DEE_ROBLOX_RBX01` completo | Studio mantiene escenas de R04, R05 y R07 abiertas, y otro proceso sin escena identificada. No se intervino ninguno. Rutas calculadas, scripts y primarios están cruzados; entrada desde `Roblox/laboratorio`. |
| `entregas/.../KIT_DESARROLLADOR` y `KIT_EXTENSION` | Copias fuente fijadas por backend, ensambladores y registros; no se declararon redundantes por nombre. El canónico público trasladado conserva su propia estructura portable y manifiesto. |
| `entregas/.../RUNTIME_PRIVADO_LOCAL` | Bundle de provisión con fuentes, dependencias y futuros completos; no se movió ni se confundió con el despliegue corto operativo. |
| `VALIDACION`, `DEMOSTRACION`, 0.1.0 y extracciones | Hay scripts/manifiestos que resuelven esas rutas y evidencia única. Un cierre científico no vuelve prescindible su material. Se conserva y se enlaza; no se impuso un archivo físico no comprobado. |
| Runtime operativo corto externo | Se mantiene la solución existente de carga DLL; sólo se añadió referencia organizativa. |

Runtime operativo exacto:

`D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_sdk_r06_valid_20261118\RUNTIME_PRIVADO_LOCAL`

El fallback al bundle largo sigue deshabilitado. No se tocó token, conexión, backend, locks, ledger, leases ni bases. `Roblox/privado` contiene únicamente orientación y enlaces; no se copiaron credenciales.

K1–K4 y diez respuestas EXT son resultados **históricos** de 0.1.1, con asistencia declarada. K5 continúa sin evaluación externa. La vida SDK T995895 no es el principal; la pareja Core T994315 es PRE_CAP y no acredita un loop Core restablecido después de EXT. La ventana R06 terminó el 18/11/2026 a las 21:37:40 UTC. La reorganización no la renueva ni autoriza nuevos start/continue.

Las referencias antiguas PUBLICO_0_1_1 en informes/ensamblados congelados siguen siendo procedencia histórica. Para localizar ese conjunto ahora, use el mapa de traslados de este informe. El instalador de incorporación histórica no se ejecuta como actualizador del módulo reorganizado.

## 6. Manuales y documentación vigente

- Cognitive: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\DEE Cognitive 2.0\DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx`. DCS11-MM-001, **contenido 1.40**, nombre compatible 1_21; bytes y hash originales intactos. No se modificó el Manual ni se reescribieron resultados.
- Thinking: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\4.5\DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx`.
- Thinking: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\4.5\DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx`.
- Universe: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\DEE_UNIVERSE_v27_DOCUMENTO_MAESTRO_CIERRE_DERIVACION_JUSTIFICACION_EVIDENCIA_V2_0.docx`.
- Compendio científico: `D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\CPC - Experimentos y mecanismos\COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx`.

Los documentos oficiales siguen en sus proyectos independientes, accesibles por enlaces desde la nueva raíz. Ninguna distribución completa Universe/Thinking se copió dentro de Cognitive.

## 7. Referencias corregidas y documentación creada

**Tres archivos existentes ajustados, con originales resguardados:**

1. `reproducibilidad/LEER_PRIMERO.md`: la apertura que presentaba PI03 como principal actual se convierte explícitamente en corte histórico PI03; se añade PI10 actual y sus selectores. Las recetas y sus propios cortes se conservan. El campo histórico PI01 `current_operational_option` de SERVICIO_PERSISTENTE_MU01 se explica como histórico; **no se modificó el contrato congelado**.
2. `entregas/DEE_ROBLOX_SDK_PILOTO/LEER_PRIMERO.md`: entrada de compatibilidad con enlace al único módulo actual; sus enlaces al árbol público apuntan al nuevo destino. Se conserva el cierre científico previo.
3. `entregas/DEE_ROBLOX_SDK_PILOTO/SDK_VERIFICAR_0_1_1.ps1`: delega en la entrada canónica. El verificador nuevo usa sólo stdlib (`-I -S -B`) y no abre el motor.

**Nuevos:** entrada raíz, `.gitignore`, entradas de Roblox/sdk/documentación/ejemplos/laboratorio/privado, LOCALIZADORES, verificador estático, entrada de archivo y este informe. No se duplicaron manuales, guías ni escenas; los índices enlazan a sus conjuntos íntegros.

| Archivo ajustado | SHA-256 anterior | SHA-256 posterior |
|---|---|---|
| `reproducibilidad/LEER_PRIMERO.md` | `644109904005bda6e5fd4de5dd4ba8298b830ac3cc9e387c25d711c608018a98` | `bd86ff972610c12f7ed76fe383dbf1f848cc4c9e4b356c067b13fc5df90fe20b` |
| `entregas/DEE_ROBLOX_SDK_PILOTO/LEER_PRIMERO.md` | `8f9209ea03f32dbf2a92ede7239e093892a42a22e405a9e37c6e6d209361f193` | `99918f7da18dbdb3941c0590bff2962a809061bd227d288782905e16ae14b4bf` |
| `entregas/DEE_ROBLOX_SDK_PILOTO/SDK_VERIFICAR_0_1_1.ps1` | `704e54c74170892f01dc45fad227390abe8e1f5936cea58fa80ebe72e82993d6` | `3da013c828e9651d7ae25aab608ecb651fe9c323ab69073dc84a870d800f335c` |

## 8. Comprobaciones ejecutadas y límites

- Resolución y contención de rutas origen/destino antes de cada movimiento; rechazo de enlaces/reparse. Movimientos mediante PowerShell `Move-Item -LiteralPath`, sin comodines ni borrados.
- Lectura de procesos: consulta CIM inicial impedida por el sandbox y completada con el permiso de lectura del sistema; tres rutas de escenas Studio identificadas, un cuarto Studio sin escena identificada. Se conservó íntegro el laboratorio. Los procesos Python observados durante las comprobaciones corresponden a estas herramientas de lectura stdlib; no se abrió propietario DEE.
- Inventarios con tamaño/hash limitados a los dos grupos movidos y a 43 archivos críticos; no nuevo censo de la biblioteca.
- Resguardo íntegro del árbol público y de los tres archivos ajustados; diez originales externos del compendio comprobados como preservados.
- Integridad antes/después de los 53 archivos trasladados, y CRC de los diez ZIP históricos.
- 51 enlaces de las nuevas entradas comprobados; JSON de 33 recetas legibles, sin modificarlas ni ejecutar sus protocolos.
- Verificador público stdlib, nueva entrada y entrada compatible: ambas salidas VERIFIED y `NativeExecutedByVerifier=false`.
- Análisis sintáctico puro de los tres scripts PowerShell nuevos/ajustados y de reversión: cero errores. La reversión comprobó sus destinos, archivos y resguardos en modo de sólo lectura; **no se aplicó**.
- Los selectores, archivos críticos y dependencias oficiales seleccionadas conservan hash/mtime.

**No se ejecutaron:** arranque de Cognitive, Native/Thinking, Studio, propietarios, experiencias, consultas materiales, nuevos ticks, reapertura funcional, coherencia de bases, DLL load, reproducción material ni ensayos científicos. No hay validación funcional Native nueva. La conservación estructural está comprobada en el alcance anterior; el funcionamiento material histórico mantiene únicamente sus comprobantes anteriores.

Quedan pendientes, fuera de este encargo: traslado físico del laboratorio activo; consolidación adicional de fuentes privadas y validaciones con consumidores congelados; comprobación funcional de cualquier futura migración que cambie imports o DLL; continuación material del SDK con ventana prospectiva y pareja coherente. No se requiere repetir experimentos sólo para ordenar entradas.

## 9. Distribución futura y privacidad

`.gitignore` previene inclusión accidental de estados, bases, colas, binarios/ruedas, runtime privado, laboratorio/entregas/archivo, escenas potencialmente inyectadas, tokens, secretos y manuales reconstructivos. **No es un escáner de secretos, no garantiza privacidad, no inicializa Git y no concede licencia.** Los ejemplos públicos se seleccionarán por la allowlist existente; no se levanta globalmente la exclusión de escenas.

No se publicó, envió ni subió nada. Antes de cualquier publicación es necesaria revisión expresa de derechos y **rotación o revocación del token privado detectado**. Su valor no se mostró, no se copió en documentación ni se cambió automáticamente. Un repositorio privado tampoco debe almacenar credenciales.

La distribución privada completa necesita estado coherente, recursos y motor autorizado; el SDK público no incluye cerebro ni estados. No se empaquetó otra distribución ni se duplicaron los proyectos Universe o Thinking.

## 10. Resguardo, reversión y continuación

Resguardo externo al producto y a `documantacion vital`:

`D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_resguardo_reorganizacion_Cognitive_20261118_R01`

- `PLAN_Y_HUELLAS_ANTES.json`: fuentes/destinos, hashes antes, 43 archivos protegidos y diez originales externos. No contiene tokens.
- `originales/`: copias literales de los tres documentos/scripts ajustados.
- `sdk_publico_original/`: resguardo estático del kit público. No contiene runtime ni estados privados.
- `TRASLADOS_EJECUTADOS.json`, `DOCUMENTACION_APLICADA.json`, `VERIFICACION_FINAL.json` y las dos salidas del verificador: hechos ejecutados, no planes de ciencia.
- `SINTAXIS_POWERSHELL.json` y `REVERSION_COMPROBADA_NO_APLICADA.txt`: comprobantes puros de los tres scripts y de reversión sin aplicación.
- `SELLO_CAMBIOS_FINAL.json`: huellas de todos los archivos nuevos/modificados del producto, incluido este informe. Su propio hash no se incluye en sí mismo.
- `REVERTIR.ps1`: comprobación por defecto; `-Aplicar` revierte sólo esta organización si los hashes siguen siendo los sellados. Rechaza cambios posteriores y destinos ocupados.

Comprobar la reversión **sin aplicarla**:

```powershell
& 'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_resguardo_reorganizacion_Cognitive_20261118_R01\REVERTIR.ps1'
```

En caso de necesitar revertir la organización, ejecutar ese mismo script con `-Aplicar` después de su comprobación. Preserva los documentos nuevos fuera del producto, restaura los tres archivos originales y devuelve los dos grupos a sus rutas de procedencia. No borra contenido, no restaura SQLite ni estados y no cambia selectores. Puede dejar carpetas vacías. Si algo cambió después, se detiene para conciliarlo; no sobreescribe ese futuro.

El compendio conserva además sus diez originales en las campañas científicas independientes; el ZIP pequeño histórico no se presenta como respaldo del ente. El resguardo externo no es otro Cognitive ejecutable ni un respaldo operativo Native.

**Punto de continuación:** usar [la entrada raíz](<../../../LEER_PRIMERO.md>) para Cognitive y [la entrada Roblox](<../../../Roblox/LEER_PRIMERO.md>) para el módulo opcional. Se conserva el principal y la separación de versiones/futuros. La reorganización segura se completó; las excepciones identificadas se dejaron funcionando en sus rutas originales.

## Anexo — archivos trasladados, bytes y SHA-256

Las rutas de esta tabla son destinos relativos a la raíz Cognitive. Se comprobó igualdad exacta con los archivos de origen y, en el compendio, con sus originales externos.

| Archivo destino | Bytes | SHA-256 |
|---|---:|---|
| `Roblox/sdk/0.1.1/ESTADO_VERIFICACION.json` | 3099 | `6c7094bd2c937eeeb662431764f42a2e9a8e00250411b8007d609f9e2e44c572` |
| `Roblox/sdk/0.1.1/FUENTES_PUBLICAS.json` | 404 | `4c126c56248e256ce11178baeb673e4068e0a9774d34c6c39166472f0fb52313` |
| `Roblox/sdk/0.1.1/GUIAS/EXCLUSIONES_Y_REPRODUCCION.md` | 756 | `fd84cc9df5ebff08810ae98bdfe99bc171008ccce6c31a9ba747718f2957fc82` |
| `Roblox/sdk/0.1.1/GUIAS/INICIO_Y_REQUISITOS.md` | 2902 | `8a0b557464702660d6864ae297a51bbd3a0d9bbcae99c9c4778caf1640ee907d` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/BackendBinding.luau` | 409 | `92a38399c7f450f3f4be2e26fe8d21217447ea66846ca316e84c6da286defbb0` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/DEEConnector_SDK_0_1_1.rbxmx` | 71487 | `2c9e6360b8939eede9065b2d01eb2ac96d9d8a6e1e593a3cf71dff10759672fb` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/Evidence_R06.luau` | 1617 | `3726fdc0707b4bf0b76995cfb4d17f5ea761e68c7d8840983193799c1748f052` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/HttpLoop.luau` | 10057 | `373544787524de9ebc1b4ab8fc989f6271b6832b1b564e48786e49441b61490f` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/HttpTransport.luau` | 7696 | `279ec04a9cd887acec73121bd4410d034b45f0361c55f2241f734afed35ad4ae` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/LiveAdapters_R06.luau` | 5663 | `cc477407b5eaf2fb775e353f48bc96bf877d64cef9a3484b310b12ea7d36d183` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/Main_R06.luau` | 18064 | `a4381dbbd3d38f6fc20e270910a14f9b8772df5bf7bb56cd2db0fec0306bdad8` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/MotorPathfinding_R06.luau` | 8622 | `c8832c21b4e62edc66b1dae5e0b7cadc60e587e1121e36b1d8adc5564196ef39` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/PersistenceChecks_R06.luau` | 4410 | `16beb77b16bfc7eea38118ec97a9ba2ff3beffb5627c694d221435fe9df430ea` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/SDKBootstrap.luau` | 2365 | `e7089ca392432e44d2af769e16dca48e44f5702389a576951d7ee1f111e57b46` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/conector/StateCodec_R06.luau` | 3496 | `a2b3646079e11936b63ffaea24c4bc523bc983848288e07318e516fcf9e1a7e9` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/configuracion/CONFIGURACION_PUBLICA.json` | 3734 | `ea7e3658d96cd0c31f135334eb23f25cbe378ed3fdf653434584fdf740b67d4b` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/configuracion/SDKConfig.luau` | 3831 | `b0168f69df0f6772e831594d8e8330f11d3cd901ce1f4b5d643ff09cfd32fbc5` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx` | 72424 | `d8fe545484c38bcaa6c5b12260c3a3a09135351f91b2cae912b44d67fd35bbd1` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/ejemplos/MapaEjemplo.luau` | 2038 | `3c4e86e0e87bd4732aeae2772cd8002f0ee4fb12b4ebd70c8c05f24b1dd3dde8` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/ejemplos/SDK_Arranque.server.luau` | 528 | `53e7748cfa92dd2e81ef66f20142e253bf2c1cc8833603768827294cd7ff77c4` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/guias/CONTRATO_K4_R06.json` | 4572 | `356b01d6db7a8000ac971e18260261c1318fe955fba6f2bc97c23c6421fe0a45` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/guias/CRITERIOS_PILOTO.md` | 2753 | `fd542680d11ee194c1b68f07846b4a7ccd20c53adbe5a4b50677ff532112e72b` |
| `Roblox/sdk/0.1.1/KIT_DESARROLLADOR/guias/FICHA_VALIDACION_EXTERNA.md` | 1088 | `6296e772382250c6294624403255b3a322d92ed5d3478766351673f9d401e3f6` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/conector/API_EXT_R06.luau` | 2741 | `7ee64055709bb7261d62c8a85a056f3a3c0e9ecc607fa51ef2288aa21f168a68` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/conector/CapabilitiesClient_EXT_R06.luau` | 10838 | `b05d992e519a9807e6b04d1e524a21ee68940b9c46e04b3e47371355d8d58078` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx` | 18978 | `aa6807c530f662ce11e21f107008978f9bf9ee003f28416c0f85a22fd3b107bb` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/conector/VistaES_EXT_R06.luau` | 3325 | `0665bf5b1ffbc991570f3c62ac1ada5318156604f1a430b784410d4b4bbf1500` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/configuracion/CONFIG_EXT_R06.json` | 584 | `395e339dafbc731c162b6b60517c508465b2685bee2edaa0b366564ad75d6b46` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/configuracion/Config_EXT_R06.luau` | 698 | `bc511ee35eb4fd27062256616e3b20a7f736a0511685645f96baee3e26f22163` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/ejemplos/Arranque_EXT_R06.server.luau` | 159 | `d78b470c25087ce80ce617ae0a1b311a85bbdc2d630629a415f36e5680b6792a` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/ejemplos/DEE_SDK_CAPACIDADES_EXT_R06.rbxlx` | 19915 | `912527d53e45adb1ae4d6924bb6ff91d45101cef3096f55371296753775342fe` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/guias/API_DESARROLLADOR_ES.md` | 3478 | `5afa74fe7f6d84952d24dc6f4c5827e1ebb65fb349bf1f6f948015312d511f61` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/guias/CONTRATO_EXT_R06_02.json` | 3638 | `9f6e4c94a388e3af06acf8ccdc89297642891d6ab1e5fc3944af5e0a43d980c1` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/guias/LEER_EXT_R06.md` | 4635 | `2804769086d2445c7e870b670c361c8ec9a69017225f1c11037c9fbdd6d6df7f` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/guias/RUTAS_WINDOWS_PREFLIGHT.md` | 1566 | `20e8ddf3958be691f7a98c90f283a27c954025dbdad099e4d7428abaf4651f32` |
| `Roblox/sdk/0.1.1/KIT_EXTENSION/pruebas/preflight_rutas_EXT_R06.py` | 1768 | `bba8a767aaad72fef781b4a134447a121e97871ec650d8ad9bcc1677c937495b` |
| `Roblox/sdk/0.1.1/LEER_PRIMERO.md` | 2402 | `d6cb090d614f0d813b81c17a40e7785119039d3515c405573572e6635876e845` |
| `Roblox/sdk/0.1.1/MANIFIESTO.json` | 8012 | `c8bfa14a29c190eed76458e6770728cbd6ad8ffb4c6c79c6b6994e9d6f04c187` |
| `Roblox/sdk/0.1.1/METADATOS/PINES_CORE_ORIGINALES.json` | 3276 | `00dc0e24d8ce93d1db4a7f6268852cc95bd027b505f11180906f80b9e17a97eb` |
| `Roblox/sdk/0.1.1/METADATOS/PINES_EXT_ORIGINALES.json` | 2289 | `9ed06122b7c9f72d0af142057946ce63034265054aedcd726c1dba7d3d7afac0` |
| `Roblox/sdk/0.1.1/VERSION.txt` | 28 | `49c333494945ba2b4e0bd21e19ba7b87ec3ae7c3aa39cece73b39b470d1f78a0` |
| `Roblox/sdk/0.1.1/herramientas/ensamblar_publico_R06.py` | 23715 | `a94cf70bcb0ba99fd7346ef2931dc2a83de4db9644f06d2bfa70291aa7dd8d08` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_01_2026_11_08_ANALISIS.zip` | 4475747 | `eab47a75e9df55ee32fefeac79bdc90d6c9435bb5d9b7b4bf8e8b256dd0e6e19` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_02_2026_11_08_ANALISIS.zip` | 6613706 | `cc94ed3cb4bf1ef47b9352c38c24bfbb443690d578f44140083d8ff2413a2bdb` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_03_2026_11_09_ANALISIS.zip` | 6193308 | `37f45b3258802334b022fa043c944e744f0fb2f8eda8777f2357a72d8c4fd54c` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_04_2026_11_09_ANALISIS.zip` | 4277070 | `93be33ca22bdb9f2c4a1e7362752243a7cd74d298fe0405b39d3b3972a50a14e` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_05_2026_11_09_ANALISIS.zip` | 5014650 | `49e40bd7942319411d31cb6b8fbb60385939b7993f36e9aeaea9db632c5fca29` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_06_2026_11_10_ANALISIS.zip` | 6628514 | `c9910596f1a9c7930168f18b0d0247bd225a61abc6969759e502098dc8028bb3` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_07_2026_11_10_ANALISIS.zip` | 9010119 | `f1e6311e526524f03b7416ce962e91eb6f08b46e11abd8e0cd4dddb21eb28604` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_08_2026_11_10_ANALISIS.zip` | 9578878 | `179ea56ce1b029685569f66cda421882bcf85cf41ea85ff17a1ba2550abe8b59` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_09_2026_11_11_ANALISIS.zip` | 6832856 | `c0ac56f17cb9dde30ba18a52bd5c4426e7515f4747b0669e3c99333dfde10bcc` |
| `archivo/COMPENDIO_PI01_PI10/DEE_PROGRESION_INTEGRADA_10_2026_11_11_ANALISIS.zip` | 11169489 | `0a05ffbe351736fec184cce4e0cf53ff5b8c4bd5ee20cece26e80f47d36e781b` |
| `archivo/COMPENDIO_PI01_PI10/INDICE_PI01_PI10.txt` | 13650 | `e81f0ce40f6c76b5e4bcffa157318865c55649ad0676a9430fe793a6443af461` |
