# Taller situado APD04

APD04 está disponible como opción experimental acotada del mismo Cognitive 1.1. La opción continuable es ahora `APD04_CONTINUABLE_R01`, una bifurcación completa desde el pasado T639374 de `APD04_MAIN`. No es una reparación de su futuro adverso. Conserva esa historia, no los aprendizajes de ramas auxiliares. No reemplaza al activo protegido ni convierte los resultados en atención adquirida, planificación, R2 o lenguaje general.

## Vida y corte comprobado

El ancestro científico es el par completo de `APD03_MAIN`, N67, T604825. El padre directo de la bifurcación continuable es el prefijo exploratorio `APD04_MAIN` T639374, conservado en:

```text
sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01/
```

Su manifiesto `EXPORTACION_SERVICIO.json` tiene SHA-256 `5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db`; el snapshot tiene SHA-256 `771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8`. Deben conservarse también SQLite, resultados y artefactos del trabajador: el snapshot por sí solo no permite continuar exactamente este servicio.

`APD04_MAIN` siguió después y quedó con último snapshot comprometido T658938, una petición en procesamiento y `FUTURO_INTERRUMPIDO.json`. La supervisión agotó la espera y no confirmó STOP mientras el Job nativo aún contenía procesos. No se borra el marcador ni se repite la petición. Su continuación normal está bloqueada por un posible futuro no comprometido; no se declara un crash cognitivo o destrucción general de memoria.

La importación completa de T639374 produjo la nueva identidad `APD04_CONTINUABLE_R01`. Su primera sesión operativa duró 90 segundos, cerró correctamente y alcanzó T639847, con snapshot SHA-256 `843289fb5a150e4ba23bce37ce6abb0890816125338ad1925c59af2e4c7be4ab`. Es un ensayo corto, no la reserva de una hora. Dos consultas reales de las palabras nuevas y las mediciones nativas nuevas `clasifica 37` y `equilibra 8/2` se completaron. No se da por revalidado todo el repertorio histórico en ese corte posterior.

Quedó en cola la petición exacta `apd04continuable_exact_pending_r01`, con payload SHA-256 `d96da9e74acb60c22b02bd3f5b7155c6ed70fb8b035076554fbeb3b44e6a3271`. El siguiente propietario debe consumir ese mismo ID, no enviarlo de nuevo. Se conservan snapshot, SQLite, resultados, artefactos y protocolo UI. No se presenta todavía un nuevo manifiesto de exportación completa T639847 como si ya existiera.

## Cómo utilizar la vida existente

Desde la raíz de Cognitive:

```bat
INICIAR.bat usar --vida APD04_CONTINUABLE_R01
```

No abrir otro propietario mientras la investigación o una sesión ya la esté utilizando. El gestor rechazará el conflicto; no hay que borrar locks ni importar otra vida para ocultarlo. El propietario comienza en pausa. Una secuencia de uso posterior al cierre del propietario actual puede ser:

```text
estado
resultado apd04continuable_exact_pending_r01
reanudar
resultado apd04continuable_exact_pending_r01
```

Antes de otra tarea, esperar a que `resultado` confirme el desenlace del mismo ID. Si sigue procesándose, volver a leer ese ID sin reenviar material. Después pueden utilizarse las funciones, `guardar`, `detener` y `salir`. `estado` observa la publicación pasiva. La consulta de palabra es material y puede modificar la vida. No es una comprobación inocua de memoria. Las dos consultas de palabra del CLI ya se ejecutaron realmente en la bifurcación; la prueba del ZIP Full final y las demás grafías nuevas del CLI queda pendiente del cierre. `--nueva` todavía usa la fuente seleccionada anterior, no importa APD04 implícitamente.

## Comandos del mismo parser

```text
ecosistema-iniciar --semilla 4071 --fuentes 2 --goal 0 --palabra clasifica --cargas 8 4
ecosistema-vivir 1 --sensor independent_balanced
ecosistema-cambio --goal 1 --palabra equilibra --cargas 3 7 --rotar 1
ensenar-ecosistema clasifica 1 --docente paired
ensenar-ecosistema equilibra -1 --docente paired
palabra-ecosistema equilibra --retorno omit
```

Son ejemplos de sintaxis, no una recomendación de repetir la enseñanza o reinicializar el taller de MAIN. `ecosistema-iniciar` modifica la preparación ambiental, no recrea E1. Las formas nuevas y sus soportes ya se admitieron en esta vida; no repetir una admisión P0 ni una docencia para aparentar retención. `--revision` identifica una revisión explícita de una señal.

`ecosistema-vivir` ofrece entre una y cuatro oportunidades. `--sin-lexico`, `--sensor tag_only/zero`, `--desacoplado`, `--retorno omit` y `--actuador nulled` son controles declarados; no son reparaciones automáticas. Los parámetros se fijan antes de la prueba. El supervisor transporta los campos y nunca cambia un lector al descubrir cuál acierta.

## Qué se utilizó en esta vida

El panel del corte retuvo las 16 formas heredadas, que ya incluyen `luma` y `nara`, y seis testigos MA. En estos últimos el dato pertinente es `fieldreader.formed_native_command`, no el campo `choice` de un selector.

MAIN recibió una docencia explícita de `clasifica` positiva y otra de `equilibra` negativa. Posteriormente, la primera señal se utilizó con la comparación nativa de 27 frente a 20 y una clasificación positiva. La segunda se utilizó con operaciones nativas que llevaron las cargas 3/7 a 4/6 y después a 5/5. La segunda acción alcanzó el objetivo ambiental de equilibrio.

Estos datos acreditan el uso contextual de asociaciones y herramientas preparadas. Los primarios auxiliares B positivo, B negativo y docente omitido sostienen una dependencia local de señal y contenido. No demuestran que la vida haya inventado la comparación, el movimiento de una unidad o un plan general. Tampoco se encontró una ventaja favorable de transferencia entre historia relacionada y opuesta. Los resultados de una auxiliar no se transfieren a MAIN o a su bifurcación por esta guía.

El futuro adverso incluye otro negativo preciso: una experiencia explícita A cambió la referencia relativa, recalculada desde RAW, de 20 a 21; no la llevó al criterio ambiental previsto 19. Las salidas ante 20 y 18 fueron negativas y cumplieron ese criterio en uno de dos casos. Se conserva el resultado sin reinterpretarlo como equilibrar una referencia21 o regulación P2. La autopsia sólo leyó SQLite y registros existentes; ningún acontecimiento previsto desde el desplazamiento500 llegó a enviarse.

## Sensor memoria ambiental y límites

En el sensor R03, `independent_balanced`, la propiedad elemental de objetivo entra mediante el payload de consulta y `s_reg`, no mediante una dirección dependiente del objetivo. Hay dos propiedades elementales observadas y tres señales materiales; Python no introduce su igualdad ni una recomendación de acción. El estado nativo produce la salida, pero su selección INSPECT/USE y su reajuste siguen siendo resultados parciales y cuestionados causalmente.

Los niveles 2, 5, 10 y 20 son fuentes ambientales recorridas secuencialmente mediante una vista de dos bits. No equivalen a veinte registros completos procesados simultáneamente. Un dato revelado por INSPECT puede permanecer en la caché ambiental; eso no acredita memoria numérica nativa. El objetivo, los objetos, las cargas, el cursor, los recursos, el codec y el evaluador son preparación externa declarada.

El caso de cargas ya iguales produjo NULL. No se traduce como HOLD, espera deliberada ni regulación inteligente. El pipeline preparado tampoco demuestra una secuencia descubierta. No se certifican R2 general, NSM65 ni comprensión libre de español.

La referencia operativa detallada es `contratos/APD04_TALLER_SITUADO.json`. La incorporación actual permite utilizar la función dentro de ese dominio sin esperar una promoción global. La reserva integrada, los controles causales y la extracción Full deberán actualizar este contrato con el estado realmente alcanzado, preservando los fallos y la revisión provisional.
