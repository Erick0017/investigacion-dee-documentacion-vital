# Referencias externas ejecutadas APD03

Se ejecutaron tres políticas convencionales separadas, ninguna controló E1. Las tres completaron 8/8 objetivos del dominio de consulta/acción con aritmética nominal `native` y 1/3 casos de calidad/disponibilidad, es decir, 9/11 tareas por trayectoria. Este resultado no acredita superioridad de DEE ni del algoritmo externo: sólo caracteriza este conjunto limitado y los presupuestos compartidos.

## Contrato y preparación

El programa prospectivo derivado R02, SHA-256 `96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599`, se copió sin modificación antes de ejecutar referencias. No utiliza resultados de MAIN. El código R02 congelado tiene SHA-256 `6efc07876dd7461cedca265d2a26bf860e01a117d10d7dd9e9cfc161b063db34`.

Las seis asociaciones matemáticas anteriores (suma/agrega/total y diferencia/resta/quita) se proporcionaron explícitamente como pasado aprendido/preparación a las referencias; no son enseñanza nueva APD03 ni equivalencia de coste de adquisición. `luma` y `nara` no se convirtieron en alias aritméticos. Los comparadores no cubren los paneles físicos, memoria MA, composición asistida, adquisición léxica nueva ni evolución basal de una hora de E1.

Antes de elegir sólo están disponibles la forma matemática, el indicador de segundo operando presente/ausente y las interfaces/recursos generales fijos. Se ocultan magnitudes (`left=None`, `second=0` si existe, `None` si falta). El contexto es constante 0, porque el sensor nativo actual no transduce el contexto variable del wrapper. Las leyes cambiantes de disponibilidad, calidad, precio y demora no se entregan a la política; sólo actúan al comprometerse su acción. Los valores aritméticos reales se proporcionan al ejecutor elegido después de la elección.

La consecuencia es binaria y posterior a la acción: QUERY que revela un hecho nuevo resulta localmente útil; una consulta redundante no. ACT se verifica contra el archivo realmente escrito, dentro de las condiciones fijas. El último objetivo sin retorno omite efectivamente la entrega del binario también a las referencias. Los nombres, identificadores, semillas, metas privadas y diagnósticos no alimentan la política.

Ambos callbacks nominales son aritmética convencional. `native` en estos ensayos es el nombre de la misma interfaz ambiental, no una invocación v27. No se compara su CPU como si resolvieran físicamente la aritmética de la misma manera que E1.

## Tres trayectorias y sus límites

* **Procedimiento fijo:** consulta una vez por objetivo si esa interfaz está admitida, y después utiliza siempre la ruta nominal native. En ventanas ACT-only no inventa una consulta. Completó 9/11 tareas: 19 oportunidades, 8 QUERY, 11 ACT, dos archivos erróneos por el proveedor perturbado y ningún rechazo del ejecutor convencional.
* **Tabla contextual con memoria:** conserva éxitos/intentos por ruta. En esta comparación ciega el contexto siempre es el mismo; por tanto la tabla es una memoria global de rutas, no una ventaja sensorial contextual oculta. Prueba rutas no vistas y luego elige la mayor tasa observada. Completó 9/11: 15 oportunidades, 4 QUERY, 11 ACT. Acertó `quality_sum` mediante la ruta externa aún no ensayada; falló `quality_difference` al volver a native por su tasa histórica y `availability_difference` por seleccionar external indisponible.
* **Win-stay/lose-shift:** conserva una ruta, cambia después de fracaso ACT y respeta las interfaces admitidas. Completó 9/11: 15 oportunidades, 4 QUERY, 11 ACT. Fracasó `quality_sum`, cambió de ruta, acertó `quality_difference` y fracasó al desaparecer la disponibilidad externa. El objetivo intermedio sólo-native no borra su estado de preferencia externa.

Cada política produce sus propios archivos y su propio retorno. No se impone el futuro de MAIN ni se repiten sus respuestas. Los tres éxitos globales iguales ocultan errores diferentes; son precisamente esos eventos los que justifican conservar primarios por tarea. Las consultas y los objetivos de una trayectoria no son réplicas independientes; tampoco las tres políticas distintas son una muestra de tres aprendices equivalentes.

## Tiempo y recursos

Se ejecutó el mismo orden lógico de oportunidades y cambios ambientales; no se durmió artificialmente 3600 segundos. Las referencias no poseen la evolución física basal nativa que ocurre entre ventanas de MAIN. Los tiempos de habilitación se conservan para trazabilidad, no se reinterpretan como latencia aritmética ni continuidad física comparable.

Cada referencia corrió en un proceso propio, con job Windows limitado a 256 MiB. Se registraron CPU de proceso, reloj monotónico, RAM y E/S por decisión/ejecución/fase. Los contadores no incluyen un intérprete lanzador como si fuese el trabajador. El tramo `process_total` comienza dentro de `run` y termina antes de escribir el resumen final: no incluye toda la carga previa del intérprete. Los contadores acumulados del job, también incluidos, tienen un alcance temporal distinto; no deben sumarse al tramo para duplicar CPU.

Los picos de memoria de trabajo fueron aproximadamente 24,0; 23,8 y 24,0 millones de bytes. Los tramos instrumentados de CPU fueron 0,1875 s (fijo), 0,125 s (tabla) y 0,09375 s (WSLS); los valores exactos y reloj real están en cada `resumen.json`. Son tiempos cortos, afectados por granularidad, E/S y carga compartida. No sustentan un ranking estable ni equivalencia con el cálculo nativo. Energía: **NO MEDIDA**; no se infiere desde TDP.

## Verificación y uso de la evidencia

Cuatro fixtures N0 validaron la frontera binaria, ACT-only, invariancia de elección ante magnitudes/contexto/leyes privadas alteradas, tres ejecuciones convencionales pequeñas y ausencia efectiva de actualización por retorno omitido. No fueron simulaciones DEE ni resultados MAIN.

La evidencia científica está en `REFERENCIAS_CONVENCIONALES_R03/`: `eventos_primarios.jsonl`, archivos reales en `artifacts/`, programa exacto, resumen, fuente congelada y recálculo por política. El recálculo repite la política sólo desde su historia pública, vuelve a verificar los archivos archivados y comprueba categorías y denominadores sin invocar proveedores ni avanzar DEE.

El intento de carpeta R02 se detuvo antes de los fixtures y antes de cualquier trayectoria porque Windows rechazó un directorio de trabajo demasiado largo (`WinError 267`). Se preservó; R03 cambió únicamente el cwd del subproceso a una ruta temporal corta, manteniendo entradas y salidas absolutas. No fue un fallo de una política ni una repetición de resultados ajustados.

## Qué puede demostrarse

Puede mostrarse el contrato limitado compartido, la ausencia de solución filtrada, los archivos causados por acciones comprometidas y las distintas estrategias observadas. Para comparar con MAIN deben unirse los resultados nativos cuando estén cerrados, manteniendo separado: éxito de archivos, consultas, calidad, adquisición léxica, conservación física y dependencia del anfitrión. No se dispone de equivalencia de entrenamiento, sustrato, evolución basal o consumo energético; no procede una afirmación de ventaja tecnológica general.
