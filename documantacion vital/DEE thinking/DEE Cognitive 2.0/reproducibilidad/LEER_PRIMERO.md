# Selección vigente y alcance histórico

Al reorganizar, el único principal es `ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`, N67/T947395, COMMITTED; Manual 1.40. Consulte [la selección](../sistema/estado/ACTIVO.json) y [la entrada actual](../LEER_PRIMERO.md). Las recetas siguientes conservan sus prefijos y cortes históricos; no se actualizaron sus estados ni se ejecutaron de nuevo.

El campo `current_operational_option` del contrato histórico SERVICIO_PERSISTENTE_MU01 conserva PI01. No se cambió ese contrato congelado: para selección vigente prevalecen ACTIVO, PROYECTO y selección personal concordantes. No interprete ese campo aislado como promoción.

---

# Reproducibilidad de Cognitive

Este apartado conserva recetas y materiales compartidos. No es otro ente principal ni un respaldo universal. El estado aprendido, su adquisición, el recálculo de registros y la recuperación de acceso se identifican por separado.

En el corte histórico PI03, el principal adoptado era `ECI02_PI03_MAIN`, N67, T775355, descendiente físico de `ECI02_PI02_MAIN` T753346 mediante las preparaciones declaradas. Conserva su estado completo y dos ofertas externas de tarea disponibles: 26 cápsulas preparadas, 24 consumidas, 19 productos y 5 rechazos. El puente PI02 separado tiene 10 productos, 16 episodios y 4 paquetes de control, y queda pausado. Son recursos y resultados del entorno; no conceptos ni energía del ente.

Desde `DEE Cognitive 2.0`, usando el Python oficial ya incluido:

```bat
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad listar
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad verificar pi03_guardia_cola_R05c
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad recalcular --destino D:\destino_nuevo_recalculo --grupos E
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad reproducir pi03_uso_final_OP3 --variante una_oportunidad --vida ECI02_PI03_REPRO_USO_NUEVO_01 --destino D:\destino_nuevo_uso
```

Sustituya los destinos por carpetas nuevas cuyo padre ya exista. Las dos primeras órdenes sólo leen archivos y no importan DEE. `recalcular` sólo ejecuta verificadores documentales stdlib sobre el material preservado: no ejecuta el motor. `reproducir` sí presenta experiencias materiales a una copia completa y consume su historia; exige destino explícito y un ID diagnóstico nuevo. Nunca cambia ACTIVO ni promueve controles.

La puerta del gestor se ejecuta como primer comando, sin `--system-root`. El acceso directo por `reproducibilidad/reproducir.py` sigue disponible. La corrección instrumental OP4 captura y reenvía stdout/stderr explícitamente para Windows; se comprobó con JSON no vacío de listar y verificar, sin alterar ACTIVO, estado, motor ni las cinco herramientas materiales. Su único archivo y referencia a la cápsula completa C están en `codigo_preservado/PI03_OP4_FORWARDING/` y `RECURSOS.json/instrument_deltas`.

`pi03_uso_final_OP3` consulta progreso, ofrece una oportunidad y vuelve a consultar el estado en un clon desde T775355. Está preparada y sus requisitos están localizados: **no se ejecutó Native esta receta desde ese corte final**. El uso retenido real de MAIN terminó en T775355; no se atribuye a esa receta futura ni a otro panel completo. El último panel de doce usos terminó en T769703, seguido de dos trabajos O/H hasta T771503 y más trabajos PI03 hasta el corte final.

La receta `pi03_guardia_cola_R05c`, variante `guard`, sí se ejecutó Native desde el prefijo científico T768317: llegó a T772227, produjo cero material en el lector q+6 y un nuevo producto real de 64 bytes. Cinco entradas de tarea y una de guarda se aplicaron, sin rechazos; la comprobación pasiva verificó las seis IDs y coincidencia exacta N/T/RAW/clocks con el caso B. Es reproducción de protección preparada P0, no aprendizaje de esa guarda o regulación general. Sus verificaciones y evidencia pequeña permanecen en `verificaciones/pi03_guardia_cola_R05c/` aunque el árbol diagnóstico cerrado se haya archivado.

`RECURSOS.json` resuelve materiales grandes dentro del producto. `recetas/` fija prefijo, variantes, entradas, lectores, ventanas ya implementadas por los módulos preservados, criterios y asistencia. `codigo_preservado/PI02_R04_OP1` conserva la revisión compartida, separada de modificaciones posteriores del producto. `codigo_preservado/historico_PI02` conserva los originales exactos y su procedencia; esos originales se estudian como texto, porque sus rutas históricas no son portables. Las adaptaciones ejecutables son los scripts de este apartado y tienen revisión propia.

Las recetas fijan un corte; no siguen ACTIVO automáticamente. `panel_12` y `pi02_uso_protegido` documentan el corte inicial PI02 T753346. Si se adopta una continuación con nuevos puentes o recursos, necesita su propia cápsula/receta comprobada; cambiar sólo el prefijo sería insuficiente. Una receta puede declarar `code_capsule_key`, resuelto en `RECURSOS.json/code_capsules`, para compartir una revisión posterior sin sustituir la PI02 histórica. Las nuevas ejecuciones fijan también los hashes de sus cinco scripts de instrumentación antes de abrir Native.

Una coincidencia de resultados con la receta no implica inteligencia general, determinismo binario universal ni adquisición nueva del principal. La comparación al importar comprueba RAW, clocks, interfaces, agenda y recibos sin nuevos ticks, permitiendo sólo el cambio administrativo de identidad. El diario completo se importa con el contrato existente y reconcilia recibos; no se purgan pendientes ni se repiten operaciones ambiguas.

Cada ejecución conserva `CONTEXTO_EJECUCION.json`, `IMPORTACION_DIAGNOSTICA.json`, `RESULTADO_REPRODUCCION.json`, primarios, diario, stdout/stderr y el estado diagnóstico completo. Los controles comparten un prefijo: no son réplicas independientes. El panel es material; cambiar de lector o consultar repetidamente puede alterar lo que se estudia.

Si falla el acceso: primero use `verificar`, sin actuar. Distinga material faltante, recurso agotado, fase/lector, rechazo de admisión, interferencia y contenido no demostrado. La receta `fi_recuperacion` documenta un caso concreto de retirada de interferencia sin restauración ni reenseñanza; no garantiza recuperar cualquier contenido. Cargar un prefijo antiguo sólo conserva su historia anterior, perdiendo las experiencias posteriores de la copia: es restauración externa, no autorreparación del ente.

No vuelva a ejecutar una operación incierta con otro ID. Un bloqueo `EJECUCION_MATERIAL.lock` preservado exige comprobar su PID, propietario y futuro interrumpido antes de retirarlo. El sistema no mata propietarios ni borra bloqueos automáticamente. La rueda se comparte mediante enlace duro de sólo uso previsto; si el destino está en otro volumen, use un destino diagnóstico en el volumen del producto. No se reinstala ni se modifica el motor.

La sección `verification` de cada receta distingue preparada, ejecutada en una copia, adquisición, uso y control. Una receta preparada no se declara comprobada hasta que su evidencia de ejecución y alcance estén registrados.

Después de una ejecución diagnóstica realmente completada y cerrada, el responsable puede registrar su evidencia sin ejecutar DEE:

```bat
motor\python313\python.exe -I -B -X utf8 reproducibilidad\registrar_verificacion.py --resultado D:\destino_nuevo_panel\RESULTADO_REPRODUCCION.json --nota "Reproducción diagnóstica, no promoción"
```

El registro comprueba identidades, importación y primarios; conserva también los resultados locales negativos. `listar` y `verificar` muestran estas comprobaciones separadas de la receta preparada. Registrar una comprobación no cambia el decodificador, el estado aprendido, ACTIVO ni la clasificación cognitiva; tampoco convierte un uso desde un estado aprendido en reproducción de su adquisición.

La preparación de una revisión PI03 posterior usa `preservar_revision_pi03.py --descriptor <JSON>` para verificar fuentes sin actuar. `--aplicar --comprobante <archivo_nuevo>` conserva una cápsula y pares completos explícitos y añade recetas; no ejecuta DEE. La receta inicial `pi03_tarea_R02_adquisicion` conserva su condición histórica de preparación. La revisión `pi03_tarea_R02_adquisicion_reproducible` sí se ejecutó en una copia: 11 productos en 14 oportunidades, 422/422 entradas Native aplicadas y coincidencia final N/T/RAW/clocks con el estado aprendido T764407. Su comprobante está en `verificaciones/pi03_tarea_R02_adquisicion_reproducible/`; los controles fuente 7/14 y 0/14 siguen identificados por separado y no se presentan como ejecuciones nuevas de las otras variantes de esa receta. Si un lector R02 devuelve NULL, se conserva esa oportunidad y se cierra sin enviar la siguiente; el resumen distingue cierre limpio de reproducción completa. Cero material nunca activa esa parada.

Cinco ejecuciones diagnósticas cerradas y siete controles de calibración se preservaron en un archivo local deduplicado con todas sus rutas, archivos y carpetas vacías. Sus verificaciones conservan la procedencia histórica y añaden `archive_locator`; las recetas siguen resolviendo sus prefijos completos en el almacén estable del producto. El archivo no sustituye al principal ni aporta recuerdos de los controles a otra vida.

`mover_par_cerrado_pi03.py` permite verificar y trasladar un único export completo ya cerrado a `materiales/`, en el mismo volumen, sin crear otra copia de sus cientos de megabytes. Exige el hash del manifiesto, corte exacto y una comprobación reciente de ausencia de propietario. Su modo predeterminado sólo verifica; `--aplicar` requiere además un comprobante nuevo y conserva la correspondencia entre origen histórico y ubicación estable. Nunca mueve el estado operativo vivo, importa DEE ni promueve una vida.


## Incorporaciones PI04: instrumentos y reproducción experimental

El catálogo del mismo Cognitive incorpora `PI04_F1_OBSERVACION_EXTERNA_RECALCULABLE` y `PI04_C2C_ADQUISICION_EXPERIMENTAL_REPRODUCIBLE`. Su contrato es `sistema/contratos/PI04_OBSERVACION_Y_REPRODUCCION_01.json`. Son medios de producto disponibles; **no añaden estos aprendizajes a PI03_MAIN ni cambian el único principal ECI02_PI03_MAIN N67 T775355**.

F1 es una herramienta externa: recalcula su corpus congelado, verifica 47 cortes físicos y 28 diferencias globales. Sus rasgos y criterio fueron elegidos por el auditor, sin reserva ciega. No es memoria funcional adquirida por el ente. Desde la raíz del producto:

```bat
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad recalcular-f1 --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>"
```

C2C tiene una reproducción Native real registrada: desde el prefijo íntegro experimental T800379, la misma copia vivió 20 oportunidades hasta T816019 y produjo 19 recursos útiles; 8/8 en reserva, aritmética 20/20 y 3720/3720 entradas aplicadas. La salida Native seleccionó una función y su entero real alimentó una segunda selección Native; la secuencia, lector y entorno son preparados. Los controles fuente dieron 12/20 con retorno genérico constante de no fallo y 20/20 con retorno desacoplado; comparten prefijo. No hay ventaja de contingencia verdadera ni una secuencia autónoma demostrada.

```bat
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad listar
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad verificar pi04_c2c_adquisicion_20_R01
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad recalcular --receta pi04_c2c_adquisicion_20_R01 --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>"
motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad reproducir pi04_c2c_adquisicion_20_R01 --variante real --vida ECI02_PI03_REPRO_PI04_<ID_NUEVO> --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>" --material
```

Reemplace todos los campos entre ángulos. El destino debe ser **absoluto, nuevo y con padre existente**; el ID y sus solicitudes no pueden haberse usado. Los tres primeros modos no ejecutan DEE. El último sí ejecuta la adquisición en una copia y conserva su futuro, nunca ACTIVO. El recálculo de esta receta transporta sólo su evidencia original real20; el informe PI04 conserva por separado los controles y futuros adversos. `verification` mantiene la preparación histórica literal de la receta; `actual_registered_verifications` muestra la comprobación Native posterior real.

El par aprendido `materiales/PI03_PI04_C2C_POST_RES_T816019` conserva seis ofertas externas sin consumir de 26 preparadas. No es suministro ilimitado ni otro principal. La continuación original posterior T818074 falló el testigo FIplus14/3 del panel anterior: se comprobaron cinco usos y falló el sexto; los restantes no se ejecutaron. Por eso no se adoptó. Cargar o reproducir ese estado experimental no acredita conservación de todas las capacidades del principal, no repara el fallo ni fusiona recuerdos entre vidas.


## PI10 R02: adquisición12 reproducible desde P02 neutral

Fuente neutral completa T922377; código de evaluación sin forzar. El catálogo y la comprobación de requisitos no importan DEE. El recálculo usa únicamente RAW/recibos/recursos archivados. La ejecución material exige un ID nuevo y destino diagnóstico explícitos; nunca selecciona ni promueve. La reproducción Native acotada de adquisición12 quedó comprobada en un clon nuevo, con correspondencia física/Native y metadatos controlados. La adopción del principal se decide por separado.

Desde la raíz de Cognitive, con motor\python313\python.exe:

```text
reproducibilidad\reproducir.py listar
reproducibilidad\reproducir.py verificar pi10_consulta12_familia_desde_P02_R02
reproducibilidad\reproducir.py recalcular --receta pi10_consulta12_familia_desde_P02_R02 --destino D:\ruta\NUEVA_RECALCULO_PI10
reproducibilidad\reproducir.py reproducir pi10_consulta12_familia_desde_P02_R02 --variante real12 --vida ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_NUEVO01 --destino D:\ruta\NUEVA_REPRO_PI10 --material
```

La última orden avanza una copia completa:12 episodios,4+8,512MiB, hasta24192ticks nuevos; no es equivalente al recálculo. Antes de ejecutarla durante PI10, el coordinador reserva1mundo y24192ticks en el presupuesto compartido. En otros usos debe fijarse igualmente un presupuesto y un ID nunca usado. No se reintentan IDs inciertos ni se vacían colas. Estado adquirido y recuerdos históricos permanecen separados.


Verificación Native PI10 R02: ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_20261111A;12episodios en4+8;18762ticks nuevos y2269/2269entradas aplicadas. El NULL inicial se conservó. El IDdebe ser nuevo y el destino no usado: el replay no está limitado al IDde esta comprobación. El contexto/receta originales de esta ejecución siguen intactos y su hash163b está conservado; la nueva ficha sólo registra evidencia para usos posteriores. Recálculo archivado, reproducción Native y uso/adopción del principal son modalidades distintas.
