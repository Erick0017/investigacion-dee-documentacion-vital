# Auditor externo — corte incremental ABCD

No modifica producto4, kernel v27, CPC4 heredado ni los MAIN experimentales.
`src/auditor/passive.py` sólo lee. Los diagnósticos se realizan en copias completas,
identificadas, que nunca regresan al MAIN. No se instaló ni se pidió GUDHI.

## Fuentes reales y alcance

`SOURCE_REVIEW.json` registra siete fuentes efectivas, hashes y copias pasivas:
I02 constructor/patrones/lector renovable; R04 recurrencia; R14 feedback; API y
implementación pertinente de producto4. Ningún main histórico fue importado o
ejecutado. El lector I02 usa una fuente semantic4 física dos sitios aguas arriba;
la invariancia de su RAW no significa inmovilidad del clock ni aprendizaje nuevo.

La regulación R14 pública es un componente finito preparado retainP/switchQ,
no una política arbitraria adquirida o renovable. Se midieron cinco preparaciones
fresh (roles P/Q×reporte ±, más reporte omitido) y un fork diagnóstico tardío.
Los cuatro casos completos emitieron la política correspondiente en10, acción
en11 e información del signo presente en14. Sin reporte o retirando sólo el
primer report ya formado en2, no se obtuvo ese readout en el panel congelado.
Las listas vacías son ausencia del readout; no se sustituyen por valor cero.
Estas seis trayectorias no se cuentan como seis individuos fresh ni como una
nueva función de la red ABCD. Evidencia: `R14_PUBLIC_COMPONENT/`.

## Nuevas ventanas de la red

Se restauraron snapshots de la realización nueva de ABCD, sin recrear historia:

- 93→94: llegada social a D.
- 160→161: primera lectura posterior de D.

La referencia heredada se reprodujo únicamente148→149, un tick desde su snapshot
anterior a la consulta. La parte física —RAW completo y clocks— coincide con el
checkpoint histórico posterior. El estado operativo completo no coincide y ese
resultado se conserva como falso. El histórico149 se
guardó después de que su runner presentara dos llamadas nuevas: recurso@149 y
suministro@155. No estaban en148 ni las genera F_v27; avanzar sólo un tick no
reproduce esas llamadas ambientales posteriores. No es pérdida de cola por
save/load. No se introdujeron inputs para forzar igualdad. Ver
`INHERITED_REFERENCE_OP_DIFF.json`. No se ejecutó la suite antigua ni se
contabiliza otra organización aprendida. Evidencia: `INHERITED_REFERENCE148_149/`.

Para cada ventana completada: observación repetida, fork operativo inicial,
save/load con cola pendiente, continuación directa y backends Lazy/Dense/Parallel
con un hilo. Coinciden RAW completo, clocks, recibos, canales, metadatos, protocolo
y resultados posteriores. Son cuatro continuaciones técnicas del mismo estado,
no cuatro experiencias independientes. Los JSON conservan las ventanas y todos
los campos observados; no son un dictamen cognitivo.

En93 D es un destino vacío. Se conservan sus26vecinos, incluidos ceros y registros
inactivos/orphan. Hay dos propuestas direccionales efectivas:58(0,+1,+1) en
(26,43,23) y16(−1,0,0) en(27,44,24). El snapshot94 muestra74(−1,+1,+1).
`D_SOCIAL_CONTEXT93_94.json` separa reconstrucción por campos de necesidad
contrafactual; esta última corresponde a los controles físicos de la red.

## Dos correcciones del instrumento, conservadas

El primer assert exigió hashes iguales de contenedores con backends distintos.
Runtime.cpp656 serializa precisamente esa opción; cambian un byte de backend y
ocho bytes de checksum, no la física ya comparada. El intento original, su código
y sus snapshots permanecen. La versión corregida conserva ambos tipos de archivo:
los originales distintos y una comparación adicional después de restablecer
únicamente scheduling en las copias técnicas, sin advance ni edición física.
Eso no significa que los contenedores originales fueran iguales.

Los primeros checks de eliminación eligieron puertos centrales vacíos y fueron
no-op. No se utilizan como prueba fuerte de aislamiento. En dos forks posteriores
sin evolución se retiraron portadores realmente presentes:58@93 y74@160. Cambia
exactamente un RAW y ningún clock; el padre operativo permanece íntegro. Ver
`NONTRIVIAL_FORK_ISOLATION.json` y `TECHNICAL_HOTFIX_AND_BYTE_DIFF.json`.

## Información y modalidades

La receta nueva usa historias/signos como condiciones de experiencia explícitas;
el futuro U/V es un acontecimiento externo fijado, no elegido leyendo una acción.
No usa `expected_evaluation_only`, utilidad ni una respuesta decodificada para
escribir memoria o encaminar materia. Los outputs se leen de RAW después de v27.
El protocolo de NetworkSession prepara una cola finita antes deT0 y el restore
no instala materia. La metadata es visible al científico, no una entrada nativa.

Limitación de observador heredado: `A_segment` en el panel de la receta sigue
una dirección positiva concreta, no ambas historias. Su vacío no puede usarse
como prueba de desaparición de un portador A de dirección negativa. El auditor
conserva campos/direcciones y contexto; no infiere identidad por proximidad o carga.

## Comandos y reproducción

Los trabajos reales fueron procesos aislados mediante `src/supervision.py`,
con timeout60s (90s para el pequeño conjunto R14) y el presupuesto compartido
inmutable. Los nombres están en jobs: auditor_sources01, auditor_R14_reference01,
auditor_ABCD_window01 (assert de formato), auditor_ABCD_window02,
auditor_ABCD_social93, auditor_ABCD_passive93 y auditor_inherited_reference01.

Ejemplo de recorrido técnico con salida NUEVA, usando el WHL4 incluido y sin
ejecutar ninguna campaña histórica:

    ..\..\.venv\Scripts\python.exe -I -B src\auditor\technical.py --snapshot resultados\red\discovery01\CENTRAL\BEFORE_D_SOCIAL.deetsnap --recipe resultados\red\discovery01\CENTRAL\MEASUREMENTS.json --end-tick 94 --output resultados\auditor\REPRODUCCION_NUEVA

El punto temporal se expresa en ticks absolutos. El helper rechaza ventanas mayores de cuatro ticks
y no sobrescribe carpetas existentes. Para nuevas reproducciones se debe usar
un proceso con timeout, no reiniciar el presupuesto original de la campaña.

Las observaciones pasivas pueden usarse directamente sobre el Runtime actual:
`capture(world, puertos, sitios_de_contexto)`; no avanzan, sondean, editan ni
calculan qué respuesta debe escribir la organización.
