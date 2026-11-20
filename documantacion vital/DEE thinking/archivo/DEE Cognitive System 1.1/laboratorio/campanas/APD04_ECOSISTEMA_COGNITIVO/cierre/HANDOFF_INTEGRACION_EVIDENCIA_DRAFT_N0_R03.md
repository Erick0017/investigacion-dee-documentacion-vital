# APD04: integración de evidencia DRAFT R03

No es una autorización de entrega o promoción. No se editó S, Word o Full. No se ejecutó Native ni se creó ZIP. Los componentes archivados y revisiones previas permanecen intactos.

## Material para el cierre de Root

- Selección validada estructuralmente: `BORRADOR_INTEGRACION_FINAL_N0_R03/RESULTADOS_FINAL.json`, SHA256 `31a95a15e9c2d8e40739508ea8afd95877aa72a92ead2433bc4522435247e23b`.
- Informe científico: `INFORME_CIENTIFICO_RESULTADOS_BORRADOR_APD04_R02.md`.
- Tablas JSON: `CAPACIDADES_POR_VIDA`, `COMPARACION_DE_VIDAS`, `DEMOSTRABILIDAD`, `COBERTURA` y fuentes en esa misma carpeta. Conservar null como desconocido; los momentos históricos y las vidas no se suman.
- Prosa para el Word, todavía DRAFT: `../manual/BORRADOR_MANUAL_APD04.json`. Root debe completar cierres, actualizar frente y autorizar su edición una única vez. Este JSON no es un Word actualizado.
- CAS: `CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R03`, 1039 rutas originales exactas, 788 objetos distintos, 42952711 bytes sumando rutas originales. Manifiesto SHA256 `51dfe2e4bb2dfcf5cea2359652e3b8dea9b30d844e801bfb31eecb5b536538a5`.
- Ocho recálculos portátiles terminados y byte-exact: `REFERENCIA_CAS_EXTENDIDO_PORTABLE_N0_R03.json`, SHA256 `165c7e27e3412af15b3851b7853cf8e75f7d50893546c7c77468e6851d01a2c6`. Estimación comprimida CAS 11458337 bytes; no es el tamaño de un ZIP final inexistente.

La extensión incluye cuatro niveles, reserva interrumpida por guarda, R03 post10 y huella P1 local. La base conserva revisiones ejecutadas y fallidas, los negativos, ABC y sus correcciones, prologue, controles, R04 y actuador R02. No usa el código actual de S como sustituto de revisiones históricas.

## Recalcular sin Native

Desde un CPython ya disponible, ejecutar el script `recalcular_cas_en_proceso_apd04_n0_r01.py --package CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R03 --out NUEVO_RESULTADO.json`. El destino no debe existir. La materialización y los ocho recálculos se hacen en una carpeta nueva junto al resultado, en proceso, sin motor y sin subprocesses. Su resultado debe coincidir con la referencia R03.

El comprobador `probar_cas_en_cerca_n0_r02.py --lab LAB --cas CAS --reference REFERENCIA --proof NUEVA_PRUEBA.json` ensaya la cerca maestra real en otra copia temporal; no crea un ZIP ni toca las fuentes originales. La prueba de la base ya estaba cerrada; consultar el resultado R03 antes de afirmar que también acabó.

## Extender sin rehacer el corpus

`extender_cas_apd04_n0_r02.py --root RAIZ --spec NUEVA_ESPEC.json --out NUEVO_CAS --report NUEVA_ESTIMACION.json` acepta como base el manifiesto exacto de R03, añade componentes portátiles con manifiestos y archivos explícitos, deduplica por SHA y conserva todas las rutas originales. Los jobs nuevos deben recalcular desde los primarios exportados, no leer S o snapshots omitidos. No editar una revisión ya ensayada: producir nuevo spec, CAS y referencia.

## Cierres que todavía no pueden aprobarse

Los resúmenes exactos de CIRCULAR_REAL y PERSISTENTE_REAL ya están seleccionados fuera del CAS: 3/6 y 1/6 completos, ambos con pending, STOP no confirmado y sin FULL final. La tercera vista y la reserva temprana no se completan por inferencia. Falta incorporar su dossier cerrado, la prueba Full exacta, la continuación seleccionada y Word. La semilla Full prospectiva está fijada por Root antes de esos resultados; sus validaciones finales no se adelantan aquí.

R03 REAL muestra una diferencia histórica local asociada a WAIT, no una mejora útil general. old_work_gain0 en ambos brazos no se reemplaza por new_quality1/0. La diferencia externa μ20 en una rama densificada no es memoria nativa recuperada. No hay prueba de destrucción global de memoria.

Los 96 checks originales de cuatro niveles y los 158 posteriores se conservan. Los únicos 62 añadidos verifican hashes de miembros exportados y se anteponen; todos los demás campos científicos son iguales como valores JSON. No se proclama identidad de bytes entre esas dos referencias.

## Aprobación pendiente

La comprobación `preparar_entrega_apd04_r01.py check-selection --results SELECCION` sólo valida estructura. Root debe cerrar las fuentes pendientes y aprobar explícitamente antes de `assemble` y `seal`. Ningún mecanismo de este borrador promociona una vida, modifica ACTIVO o declara final una capacidad automáticamente.
