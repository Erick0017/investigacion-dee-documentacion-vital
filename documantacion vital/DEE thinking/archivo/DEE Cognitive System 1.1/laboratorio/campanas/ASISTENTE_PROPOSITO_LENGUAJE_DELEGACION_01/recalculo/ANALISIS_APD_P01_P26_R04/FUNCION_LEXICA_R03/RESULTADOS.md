# Función numérica dependiente de la historia léxica — R03

Dos bifurcaciones completas de igual edad T106738, procedentes de R02 `paired` y `reversed`, recibieron las mismas oportunidades y calendario. No hubo docencia durante este ensayo. La forma literal codificó únicamente el origen y la dirección del cue. Un lector único de veinte puertas produjo un signo físico; la transducción fija `+ → suma nativa preparada`, `− → diferencia afín nativa preparada` utilizó ese signo, no un diccionario de significados de las palabras.

| Oportunidad común | Historia emparejada | Historia invertida |
| --- | --- | --- |
| agrega, operandos 7 y 4 | signo +; resultado 11 | signo −; resultado 3 |
| resta, operandos 16 y 5 | signo −; resultado 11 | signo +; resultado 21 |
| agrega, operandos 2 y 9 | signo +; resultado 11 | signo −; resultado −7 |

Las seis respuestas numéricas fueron válidas y concordantes con la operación físicamente seleccionada. Después se usaron consecutivamente las diez formas anteriores: 10/10 signos accesibles en cada vida, conservando su propia historia. Cada bifurcación solicitó 619 entradas únicas y las 619 fueron aplicadas; no se excluyeron rechazos del denominador. Las dos vidas comparten un prefijo y no constituyen réplicas biográficas independientes.

## Estados alcanzados

- `APD01_LEX_R03_paired`, T108212; snapshot SHA-256 `af0150596f4e114f2a8a35e3cd4d3648ce10feb3e775c00b09fb2526b83bb429`.
- `APD01_LEX_R03_reversed`, T108212; snapshot SHA-256 `0612b853ad9f8d7d871c958a0b529450368c5a4ef479c470196c18b7364a4cab`.

Sus snapshots completos permanecen en `sistema/estado/checkpoints/`, localizables mediante los registros de esas vidas; no se incluyen como respaldo operativo en el análisis compacto. El padre R02 y el activo protegido no se modificaron. No se incorporó el aprendizaje de una bifurcación a otra ni a MAIN.

## Qué acredita y qué no

HECHO COMPUTACIONAL: el recálculo independiente decodificó 78,022 observaciones RAW exactas, comprobó veinte puertas fijas, signos, operandos comunes, calendario, resultados numéricos y recibos, sin discrepancias y sin avanzar ticks. Las respuestas opuestas no son sólo etiquetas distintas: cambió la función numérica ejecutada.

MECANISMO Y CAPACIDAD ACOTADA: las asociaciones adquiridas anteriormente alteran cuál de dos operaciones nativas preparadas se utiliza con operandos nuevos. Durante R03 no se proporcionó la palabra correcta, un signo docente, el resultado esperado ni un cálculo externo como respuesta de la organización.

LÍMITES: el investigador preparó los canales, la anatomía de consulta, el lector y las dos operaciones. No se demostró adquisición del algoritmo aritmético, sintaxis española general, doce procedimientos, NSM65, elección autónoma de cuándo consultar ni una política aprendida de delegación. La evaluación aritmética externa aparece sólo en el recálculo del auditor. Los controles sin enseñanza y desacoplado se conservan en R01/R02; R03 contrasta únicamente las dos historias opuestas ya adquiridas.

## Evidencia y recálculo

Los primarios exactos están en `evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/APD01_LEX_R03_FUNCION/`, junto a las revisiones ejecutadas del código. `recalcular_funcion_lexica_r03.py` utiliza únicamente la evidencia exportada y el auditor stdlib `recalcular_primarios_apd.py`.

El protocolo original de 58,311,806 bytes se conserva localmente, SHA-256 `aca542d66aa19491257897ded758b6cf6ea5e57b2a19b9f5cc7db0f7ff2c480c`. Repetía íntegramente dos resultados R02 ya incluidos. El análisis usa `PROTOCOLO_DEDUPLICADO.json` de 12,100 bytes y referencias con hashes a esos mismos primarios. `deduplicar_protocolo_r03.py --compacto ... --base ... --restaurar ...` reconstruye y verifica los bytes exactos del protocolo original. Esto elimina duplicación documental, no evidencia única ni estado físico; el paquete compacto no reemplaza la instalación ni los snapshots de continuidad.
