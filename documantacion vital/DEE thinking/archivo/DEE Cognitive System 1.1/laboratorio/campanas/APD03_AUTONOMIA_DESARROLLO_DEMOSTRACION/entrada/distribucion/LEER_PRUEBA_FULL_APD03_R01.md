# Prueba Full APD03 preparada, todavía sin ejecutar

Este directorio contiene instrumentación candidata. No cambió `cognitive sistem`, su ZIP, el actualizador, S ni ninguna vida; las comprobaciones realizadas aquí son N0.

## Flujo aprobado para Root

1. Cerrar y guardar la candidata MAIN con su par completo. Registrar el alias, la vida, el tick y el snapshot exactos en una **nueva copia** del protocolo de este directorio. Mantener la versión candidata original como antecedente. Cerrar el protocolo con `status=CLOSED_FOR_EXACT_FULL_PROOF` sólo después de revisar ese corte.
2. La lección está prefijada: se exige luma+ y nara− utilizables en el primer panel y un uso de luma+; después se enseña explícitamente luma−. Si falta esa dependencia, la prueba se detiene en su futuro real sin retargetear la lección ni elegir otro checkpoint. SUM24,5 oculto y cuatro oportunidades están fijados antes de la prueba; no se ajustan al resultado.
3. Incorporar `probar_full_apd03_entrada.py` a `actualizaciones/` por el flujo ya existente. Incorporar la UI typed y su único contrato en `sistema/` y añadir la acción `usar` del diff mínimo cuando Root autorice la actualización. No se ha aplicado ninguno de esos cambios al Full desde este directorio.
4. Utilizar `actualizaciones/actualizar.py`, sus selecciones/cierres y `Build.finish`/sellado existentes. No crear otro constructor. El actualizador ya respalda el ZIP canónico anterior antes de sustituirlo; comprobar y conservar la identidad de ese respaldo. La referencia Full APD02 preservada es328112797bytes, SHA-256 `dcbd2c04f498776a5e26c9f17f6cee99e422c4def704dba22056f3defb53c85d`.
5. Sellar un candidato Full y ejecutar el verificador externo contra su hash exacto, nunca contra una carpeta operativa mezclada. Usar un directorio corto nuevo del workspace, no el árbol del colaborador. El verificador se niega a reutilizar un destino existente.

## Ejemplo de orden del verificador

La ruta del ZIP y su SHA se rellenan con el cierre real; no son valores ficticios aprobados:

```text
python verificar_full_apd03_exacto.py --zip RUTA_ZIP_REAL --zip-sha256 SHA256_REAL --destino RUTA_CORTA_NUEVA --protocolo PROTOCOLO_ROOT_CERRADO.json --salida VERIFICACION_FULL_APD03_EXTERNA.json --ejecutar-native
```

Sin la autorización explícita y el estado cerrado del protocolo no se inicia la prueba. El verificador sólo usa ejecutables/código dentro de la extracción y el intérprete incluido; no importa S original ni copia snapshots activos. La ruta de protocolo externa sólo aporta el guion de evaluación ya congelado y el corte declarado; no se ofrece al participante como memoria, plan o respuesta.

## Tres sesiones, una sola vida

Root aceptó tres sesiones UI secuenciales para comprobar la dependencia inicial sin añadir un controlador condicional a la UI:

- Sesión1: `--nueva`, panel material, uso anterior luma+, guardar y STOP. El instrumento comprueba después ese resultado. No se inicia docencia si la condición prefijada no se cumplió.
- Sesión2: `--vida` de la misma identidad, enseñanza explícita luma−, uso, panel, objetivo nuevo SUM24,5 oculto, cuatro oportunidades, guardar y STOP.
- Sesión3: `--vida` de esa misma identidad, otro valor/contexto, uso de lo revisado, panel de retención, guardar y STOP.

El estado DEE no se restaura entre sesiones ni se reimporta el padre. Son tres propietarios secuenciales, no un proceso ininterrumpido y no tres aprendices independientes. La reserva de una hora MAIN es otra comprobación y no se obtiene sumando estas sesiones.

## Qué se comprueba y qué queda fuera

El ZIP exacto se comprueba por CRC y hashes de miembros gestionados antes y después. El motor WHL conserva su hash oficial. Se registran argv absolutos, cwd corto del intérprete, recursos del árbol propio, fuentes, recibos, docencia, RAW de palabras/acciones/números, archivos reales, identidad, cortes y reaperturas. Los paneles son materiales; `estado` sigue siendo observación pasiva.

La aritmética de comprobación se ejecuta después de las acciones para auditar el resultado, nunca para responder por DEE. El objetivo admite sólo cálculo nativo después de ACT; el verificador exige un callback nativo y cero externos cuando hay efecto. Un objetivo no terminado en cuatro oportunidades queda documentado, no se reintenta con más oportunidades o un padre mejor.

El harness conserva el trabajo de la extracción nueva. No modifica el trabajo personal original, el Full APD02 ni el activo. El paquete reducido de análisis no sustituye las vidas completas guardadas localmente.

Las pruebas N0 de este directorio sólo cubren reglas de archivo, transporte, argv/cwd y decodificación de fixtures. No acreditan todavía la ejecución Full, energía, otra computadora, iniciativa propia ni inteligencia general.

## Corrección N0 R05 antes de cualquier ejecución Full

La lista congelada utiliza `sistema/capacidades/lexico_generico_apd03_r02.py`, que es el archivo realmente instalado; la variante R01 sólo queda como antecedente experimental. El codec de lectura de las dos formas nuevas sigue siendo K=(47,7,47), sin cambio de criterio.

El árbol exterior de la prueba tiene un límite total de1GiB que incluye al helper, UI, clientes del gestor y procesos Native descendientes. La UI conserva su propio límite existente de512MiB para el árbol del trabajador Native. El harness verifica ese valor contra el contrato de la UI. Son ámbitos anidados: no se suman sus picos. Se registrarán los recursos reales de los Jobs cuando Root autorice la prueba; estos límites no son una medición de consumo ni energía.

`PRUEBAS_HARNESS_FULL_N0_R05.json` registra19/19 fixtures, cero procesos Native y cero ticks nuevos. Las preimágenes de R04 quedaron en `revisiones/N0_R04_PRE_MEMORIA_Y_LEXICO/`. Ningún resultado Full está acreditado por esos fixtures.
