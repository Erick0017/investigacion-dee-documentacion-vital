# Validación diferencial 4.0 → 4.5

Esta carpeta separa datos de trayectoria, comparación y alcance. El corte final `final6` completó 68 trayectorias, 32 comparaciones de backends y cuatro continuaciones cruzadas, todas correctas. `TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json` reúne las pruebas; `FINAL6_ARTIFACT_BINDING.json` enlaza sus 68 primarios al único WHL final y al PYD ejecutado. Los resultados `candidate1` se conservan como historia de desarrollo, no como sustituto de estas pruebas finales.

WHL final: `09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c`. PYD final: `17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d`.

- `NEUTRAL_DIFF_final6.json`: 16 aparatos × tres backends; RAW/clocks completos uint64, tick, canales y recibos; la cola pendiente se comprueba mediante continuación exacta del snapshot. Incluye entradas inválidas, tardías y simultáneas, carga cero, direcciones en registros inactivos, fuentes, contexto, saturación, wrapping y clocks mayores que 2^53. Las cuatro recetas tienen N34/N31/N47/N127 propios.
- `BASELINE_BACKEND_EQUIVALENCE.json` y `FINAL6_BACKEND_EQUIVALENCE.json`: 32 comparaciones por versión entre DenseSequential y DenseParallel/Lazy.
- `CPC_PORT_DIFF_final6.json`: diez aparatos. El intérprete 4.0 utiliza constructores congelados seleccionados; el 4.5 utiliza fábricas y operaciones nativas instaladas. La implementación 4.5 no importa el laboratorio histórico.
- `FINITE_REVISION_DIFF_final6.json`: seis aparatos K2, M1/M2, controles offpath y dos historias/consultas trasladadas reservadas. El control z+10 no se extrapola a 16/65 planos poblados.
- `EXPERIMENTAL_REGULATION_DIFF_final6.json`: cuatro trayectorias del pulso direccional de carga cero adquirido, comparadas contra la preparación CPC5 exacta: emparejado, desacoplado, dirección contraria y reserva trasladada. Véase la nota de alcance a continuación.
- `cross_process_final6/*_CHECK.json`: restauración y evolución entre versiones en cuatro procesos separados, en ambos sentidos, con entradas pendientes. Son snapshots Runtime y OrganizationalWorld heredados; no se promete que 4.0 interprete el nuevo descriptor 4.5.
- `API_DIFF_final6.json`: cero símbolos y cero métodos/atributos públicos retirados; 21 símbolos añadidos. No es un compromiso de ABI binaria C++.
- `tests/external_consumer`: consumidor nuevo y copia byte-exacta del consumidor heredado 4.0. Ambos se construyen contra el paquete CMake instalado 4.5 y `DEE::thinking`. El consumidor legado recibe un archivo de snapshot; el nuevo recibe un directorio de salida inexistente.

La igualdad de arrays se verifica descomprimiendo los streams little-endian uint64 y comparando todos los bytes, no sólo una muestra, una distancia float o un hash declarado. Cada `CONFIG.json`, `RESULT.json`, `PROCESS.json` y comando supervisado conserva identidades, tiempos y códigos de salida.

## Incidencias conservadas

Dos ejecuciones Dense N127 de 4.0 terminaron y guardaron todas sus fronteras, pero alcanzaron su timeout en comprobaciones posteriores. Se retomó su snapshot pendiente en un proceso nuevo, sin preparar ni enseñar de nuevo, y se comprobó la continuación contra las arrays terminales ya existentes. `INDEX_COMPLETED.json` enlaza las pruebas; el índice y los timeouts originales siguen intactos.

Una escritura atómica de JSON encontró `AccessDenied` de Windows mientras otro proceso leía el archivo activo. Se conservó el fallo, se añadió una espera acotada sólo al publicador JSON y se retomó el checkpoint pendiente K65. Las fronteras 134/265 se comprobaron byte a byte antes de continuar a396. No cambió ninguna entrada ni transición física. Véanse `tools/INSTRUMENTATION_CHANGES.json` y `cpc_ports_4_0_recovery/`.

## Reproducción

Los scripts resuelven sus fuentes respecto a la raíz extraída. Crear dos entornos aislados e instalar sus WHL respectivos; no incluir los venv en la entrega. Ejecutar con `python -I -B` y salidas nuevas:

```text
python -I -B validation/tools/neutral_batch.py --config validation/tools/neutral_config.json --expected-version 4.5.0 --out SALIDA_NUEVA
python -I -B validation/tools/cpc_port.py suite --expected-version 4.5.0 --out SALIDA_NUEVA
python -I -B validation/tools/revision_port.py suite --expected-version 4.5.0 --out SALIDA_NUEVA
python -I -B validation/tools/neutral_checks.py versions --before BASELINE --after CANDIDATO --out COMPARACION.json
python -I -B validation/tools/cpc_port_compare.py --before BASELINE --after CANDIDATO --out COMPARACION.json
```

Las pruebas no leen respuestas esperadas del expediente para producir la respuesta del mundo. Los comparadores se ejecutan después de las trayectorias. El orden de recibos cue/event se canoniza cue-first en ambos motores para coincidir con el helper público; se conservan los mismos puertos, cargas y ticks, sin atribuir los IDs event-first históricos a esta adaptación.

Una repetición determinista comprueba reproducibilidad de software; no constituye otra muestra científica independiente. Las formas opacas, sus dos clases físicas y las tareas de revisión finita no se convierten en 65 significados NSM por aparecer en una API común.

## Pulso regulador adquirido: perfil experimental reutilizable

`from dee_thinking.experimental_regulation import CPC5RegulationSession` ofrece una preparación N67 y una sesión persistente 0..437. Dos experiencias reales de carga cero adquieren un producto móvil direccional; su contacto nativo con un residual permite una consecuencia posterior distinta. La historia emparejada y la reserva conservaron la función del banco Flat; las historias desacoplada y de dirección opuesta conservaron la alternativa recurso sin esa función. Los estados completos y los controles coinciden con los constructores originales 4.0, sin importar esos constructores desde el producto.

La geometría, las oportunidades y el currículo finito son diseño del investigador. La dirección del producto depende de la historia física. El encaminamiento de su contacto no es una política seleccionada por refuerzo. Este perfil se publica como receta Python experimental sobre el Runtime C++/v27, separado del constructor C++ estable U0. El constructor completo CPC5 aún no tiene una función C++ nominal propia; C++ conserva su acceso general a Runtime, recetas, puertos y snapshots.

El ejemplo `source/examples/experimental_acquired_regulation.py` ejecuta adquisición, contacto y lecturas posteriores; no reproduce una transcripción guardada. El módulo proporciona `create`, `run_until`, `observe`, `fork`, `save_snapshot` y `load_snapshot`, con stub y procedencia seleccionada del CPC5 canónico. Los cuatro casos guardan una frontera292 y prueban también fork/guardado/carga350→437 sin editar MAIN. Las lecturas de bancos son observaciones físicas, no cuatro nuevas consultas independientes ni una nueva campaña científica.
