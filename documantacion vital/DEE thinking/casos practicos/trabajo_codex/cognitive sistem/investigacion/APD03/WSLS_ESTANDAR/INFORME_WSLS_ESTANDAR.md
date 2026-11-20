# Cuarta referencia: WSLS sobre la ruta efectivamente ejecutada

La cuarta trayectoria completó **10/11 tareas**: 8/8 objetivos de consulta/acción y 2/3 pruebas de calidad/disponibilidad. Hubo 15 oportunidades admitidas por el ejecutor convencional, 4 consultas, 11 ACT, un archivo incorrecto, ninguna ausencia de salida y ningún efecto incierto. El retorno del objetivo final se omitió en sus dos oportunidades. No se avanzó DEE ni se leyó el futuro de MAIN.

Se fijó antes de ejecutar el protocolo `PROTOCOLO_CUARTA_REFERENCIA_WSLS_ESTANDAR_R03.md`, SHA `ea683aaa36510903ac46eab31f027c08ed3801a47b76b21fd34a9e42b90bd5d4`; fuente ejecutada SHA `5ee7ad09854427ec8796606d93e7021212e318d7806cbb1e5bec706455ca8e60`. Conservó el programa común exacto SHA `96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599`, las observaciones cegadas R02, las experiencias, interfaces, oportunidades y consecuencias. Sólo cambió la ley convencional de actualización de preferencia: después de ACT SUCCESS conserva la ruta efectivamente ejecutada; tras FAILURE selecciona la otra. QUERY no elige un proveedor y no actualiza esta preferencia.

El primer ensayo `quality_sum` produjo un archivo incorrecto con native perturbado. El fracaso cambió la preferencia a external; `quality_difference` fue correcto. En `habitat_after_quality`, la única interfaz permitida fue native: su éxito mantuvo esa ruta como preferencia efectiva. Por ello `availability_difference` eligió native y tuvo éxito cuando external ya no estaba disponible. Éste es el contraste de código y secuencia que explica la diferencia con la tercera referencia; no se calculó la disponibilidad oculta para elegir.

La tercera referencia original, etiquetada `wsls` en su esquema congelado, conserva una **preferencia lose-shift** y no actualiza esa preferencia después de éxito en una ruta forzada por el conjunto de interfaces. Quedó documentada y ejecutada tal como estaba; su 9/11 no se reescribe. No se confunde con esta cuarta WSLS estándar sobre acciones realmente realizadas. Se informan ambas, sin seleccionar retrospectivamente sólo la más favorable.

## Cuatro referencias, un conjunto limitado

| Política ejecutada | Objetivos sólo-native | Calidad/disponibilidad | Total | Oportunidades | QUERY | ACT incorrecto/inutilizable |
|---|---:|---:|---:|---:|---:|---:|
| Procedimiento fijo | 8/8 | 1/3 | 9/11 | 19 | 8 | 2 |
| Tabla con memoria, contexto cegado | 8/8 | 1/3 | 9/11 | 15 | 4 | 2 |
| Preferencia lose-shift, nombre histórico `wsls` | 8/8 | 1/3 | 9/11 | 15 | 4 | 2 |
| WSLS estándar, ruta efectivamente ejecutada | 8/8 | 2/3 | 10/11 | 15 | 4 | 1 |

Seis asociaciones matemáticas anteriores se proporcionan como preparación histórica explícita, no como nueva adquisición de estas referencias. Las magnitudes no llegan a la selección; sólo `left=None`, `second=0/None` y contexto constante 0. Los valores reales se entregan al ejecutor después de comprometer la acción. Los cambios de ley ambiental no son observaciones de la política. Las dos rutas calculan convencionalmente: nominal native no significa que estas referencias usen v27.

Las once tareas no son once aprendices independientes. No se equivalen la física basal de MAIN, su aprendizaje léxico/MA ni su conservación bajo interferencia a estos programas clásicos. La cuarta variante se añadió tras identificar una diferencia algorítmica del tercer procedimiento, no como una nueva reserva independiente. No se usa para afirmar superioridad general de un sistema.

## Recursos y verificación

La cuarta referencia tuvo un trabajador propio PID 87284, job de 256 MiB y pico de trabajo registrado de 23.740.416 bytes. En el tramo instrumentado: CPU 140.625.000 ns y reloj 196.710.400 ns; no incluye todo el arranque del intérprete ni la escritura final del resumen. Los contadores OS de este trabajador registraron 48.042 bytes de transferencias leídas y 67.515 escritas. Son `GetProcessIoCounters`, no los campos reservados de class9, ni sectores físicos ni tamaño de archivos únicos. Un cero de intervalo no se convierte en ausencia global de I/O. Energía: **NO MEDIDA**.

Cuatro fixtures N0 precedieron la trayectoria y su código/protocolo se copiaron antes de la primera acción. El recálculo vuelve a ejecutar únicamente la política clásica desde observaciones públicas archivadas, comprueba retorno omitido, consulta real, todos los denominadores y los bytes de archivos comprometidos; no vuelve a llamar proveedores ni al motor DEE. El paquete portable contiene los negativos y las fuentes exactas. La evidencia no depende de capturas ni de un PASS global.
