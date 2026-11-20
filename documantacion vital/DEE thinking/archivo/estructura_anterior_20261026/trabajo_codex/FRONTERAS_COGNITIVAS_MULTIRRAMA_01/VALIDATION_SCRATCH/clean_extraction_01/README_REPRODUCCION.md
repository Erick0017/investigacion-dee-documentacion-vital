# FRONTERAS COGNITIVAS NATIVAS DEE — MULTIRRAMA 01

Proyecto DEE Universe. Autor: Ivan Erick Tlaltecatl Morales.
Instrumento congelado: DEE thinking 3.0.0, kernel v27. Esta entrega no modifica MBP4.

## Instalación

Windows x64 y CPython 3.13. No requiere NumPy, Internet ni corpus externo.
Ejecutar desde la carpeta extraída; las rutas relativas siguientes son PowerShell.

```powershell
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-index --no-deps .\SHARED_TOOLS\dee_thinking-3.0.0-cp313-cp313-win_amd64.whl
```

SHA-256 WHL: `9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db`.
El binario nativo usado se comparó byte por byte contra el WHL; el source del kernel
consultado está en SHARED_TOOLS/product_reference. No se recompiló el motor.

## Una ejecución completa en salida nueva

```powershell
& .\.venv\Scripts\python.exe -I -B .\RUNNER\run_multibranch.py --mode reproduce --replica-root .\REPLICA_01
```

Recrea las preparaciones congeladas en mundos nuevos y separados; conserva las
continuidades de cada caso y sus consultas diagnósticas. Ejecuta los casos medidos,
el replay externo declarado de L03 y el cruce. Compara Phi y RAW/clock finales
contra esta entrega. No modifica los checkpoints de referencia ni publica otro ZIP.
Los dos intentos fallidos por contrato de puerto quedan como errores históricos;
se reproduce su sustitución explícita con el contrato Runtime, no se reintenta
indefinidamente el mismo rechazo. Duración máxima del runner: 90 min, con reserva
de cierre; cada caso tiene un horizonte finito. Un hilo nativo, un proceso de
simulación por vez. Los helpers se ejecutan secuencialmente, no mediante threads.

## Reanudación de una reproducción interrumpida

```powershell
& .\.venv\Scripts\python.exe -I -B .\REPLICA_01\RUNNER\run_multibranch.py --root .\REPLICA_01 --mode resume
& .\.venv\Scripts\python.exe -I -B .\REPLICA_01\RUNNER\run_contingency_replay.py .\REPLICA_01
& .\.venv\Scripts\python.exe -I -B .\REPLICA_01\RUNNER\run_combination.py .\REPLICA_01
```

La cola salta resultados cuyos checkpoints ya tienen hashes válidos. Los casos
incompletos se reconstruyen desde su receta registrada; no se reconstruyen los ya
terminados. El corte original está sellado y `resume` lo rechaza. No cambiar su
deadline para continuar una ejecución sin registrar una nueva reproducción.

## Un caso individual

```powershell
& .\.venv\Scripts\python.exe -I -B .\RUNNER\run_multibranch.py --mode case --case L05/full --replica-root .\CASO_L05_01
```

Los casos disponibles constan en CAMPAIGN_CONFIG.json. Los cuatro controles
suplementarios de replay L03 están definidos en L03_replay_control_lock y su helper.
Se necesita una carpeta de salida nueva. El import de módulos no lanza campañas.

## Integridad del ZIP

```powershell
& .\.venv\Scripts\python.exe -I -B .\RUNNER\run_multibranch.py --mode verify --output 'RUTA\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip'
```

Verifica CRC, HASHES.sha256, MANIFEST y miembros esenciales. Los snapshots tienen
RAW y clock uint64 completos, tick, canales, cola, recibos y metadatos del Runtime;
el protocolo/receta y los puertos personalizados están en CASE_CONFIG/APPARATUS.
Se restauran con Runtime.load_snapshot, no con BasalWorld.load_snapshot para una
receta arbitraria. No se serializan punteros ni se reintegran forks.

## Lectura de la evidencia

RUN_SUMMARY da contadores de casos conservados; BRANCH_MEASUREMENTS da contrastes
descriptivos por rama. MEASUREMENTS, TRACE, INPUTS, intervenciones y snapshots son
la evidencia primaria. Nivel 0/1/2 describe exploración/reservas/extensión ejecutadas,
no niveles de inteligencia ni veredictos cognitivos. Los ticks de una trayectoria
no son réplicas. Los contadores no incluyen como experiencias las entradas rechazadas.

P identifica entradas físicas controladas por canales registrados; N identifica
evolución nativa después de preparación; DIAGNOSTIC identifica cortes, daños,
consultas en forks y el replay externo de L03. El host no selecciona acciones ni
escribe respuestas adaptadas al resultado. El full-state sólo lo lee el científico.

L02 mide una ruta histórica anterior a la consecuencia: no separa por sí sola
expectativa temporal aprendida de transporte. L03 no ejecutó adquisición C/U ni
intercambio de contingencias. L04 explora equivalencias finitas de consulta bajo
rutas instaladas, no categorías generales. L07 separa la calibración heredada H3
de la evolución del cuerpo dañado sin reparación del host. L08 usa relaciones
móviles finitas y no afirma dos cuerpos materializados completos. L09 conserva el
intento: la condición oculta también llega bajo fondos no informativos, por lo que
no aisló la selección adquirida de P frente a Q. Las otras limitaciones están
registradas por rama. No hay adjudicación científica final automatizada.

El seguimiento móvil usa segmentos balísticos toroidales y observaciones reales
en sus posiciones previstas; no es un tracker universal. Una intersección puede
tener varios contribuyentes. Las genealogías aquí se acotan por las recetas y los
cortes físicos medidos, no sólo por semejanza de carga o dirección.

## Reempaquetar sin repetir ciencia

```powershell
& .\.venv\Scripts\python.exe -I -B .\RUNNER\run_multibranch.py --mode package --output 'RUTA\DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip'
```

Preserva la identidad del corte sellado, usa únicamente los archivos inmutables
del laboratorio y verifica antes de publicar atómicamente. Excluye cachés, venvs,
VALIDATION_SCRATCH y ZIPs anidados. No vuelve a ejecutar tratamientos por un fallo
de empaquetado. No hay workers persistentes de esta campaña al terminar.
