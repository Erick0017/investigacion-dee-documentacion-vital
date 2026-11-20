# Coste registrado del acumulador adquirido — APD01 N0

Extracción retrospectiva de P16/P17 y seis controles existentes; cero ticks nuevos. No se estima una ventaja de CPU ni se equipara el acumulador a SUM genérica.

## MAIN

| Fase | Tick inicial→final | Ticks | Entradas físicas | Calculadora externa | Tiempo host registrado |
|---|---|---:|---:|---:|---:|
| P16 enseñanza |112220→112227|7|2 solicitadas/aplicadas|1 docente inline|9.449938999954611 s|
| P17 cinco usos |112227→112269|42|10 solicitadas/aplicadas|0 en evaluación|7.4815540998242795 s|

La preparación de interfaces avanza0 ticks y no inserta contenido adquirido. La enseñanza recibe x=7 y el resultado17 de la calculadora externa para SUM[7,10]; se forma la diferencia física10. Los incrementos posteriores1,4,0,7,2 producen11,15,15,22,24. Son acumulación contextual y cinco oportunidades preparadas, no cinco llamadas independientes n+δ ni un operador binario aprendido. Cada uso requiere2 entradas (incremento y giro genérico): primer uso10 ticks después de enseñanza; siguientes8 ticks cada uno. La evaluación no vuelve a invocar la calculadora docente.

Los tiempos son dos comandos supervisados completos: importación, carga, observación, guardado e I/O incluidos. No son tiempos puros de cálculo. Su suma16.93149309977889 s no es una sesión continua ni una medición de CPU. La única llamada docente registra además1.6998965293169022e-06 s de pared interna; no debe usarse para extrapolar rendimiento.

## Controles

Cada rama empieza enT104472, termina enseñanzaT104479, cinco usosT104521 y panel antiguoT104929:7+42+408=457 ticks por rama. No se suman como una vida ni se consideran réplicas independientes.

| Historia | Entradas enseñanza | Entradas cinco usos | Entradas panel antiguo | Total |
|---|---:|---:|---:|---:|
| T emparejada |2|10|42|54|
| U sin docente |1|10|42|53|
| D desacoplada |2|10|42|54|
| H historia opuesta |2|10|42|54|
| CUT |3|10|42|55|
| SHAM |3|10|42|55|

Total325 entradas. En los recibos tempranos CUT y SHAM conservan cada uno una entrada scheduled, sin reescritura retrospectiva. El testigo completo posterior acredita325/325 aplicadas y ninguna pendiente. Los pares docentes de los controles son entradas preparadas declaradas, no llamadas a la calculadora externa de P16. Todos sus usos posteriores omiten nuevas referencias docentes. El supervisor conjunto de seis ramas registra62.80290630017407 s incluyendo sus paneles y guardados; no existen tiempos separados exactos por fase/control en esos primarios.

T/SHAM producen4,8,8,15,17; H produce−2,2,2,9,11; U/D/CUT emiten cinco abstenciones. El alcance de esas diferencias está en sus primarios originales; este informe sólo añade contabilidad del coste observado.

## Lo que no se concluye

El ahorro amortizado es indeterminado: no hay comparación de dominio y recursos equivalente. El SUM preparado procesa dos operandos; el acumulador conserva una diferencia adquirida y suma incrementos en una trayectoria finita. Cinco usos ensayados no demuestran borrado físico, un máximo universal de cinco, un sexto uso ni reutilización indefinida. No se miden energía ni metabolismo.

REFERENCIAS/COSTE_ACUMULADOR.json conserva cada fuente/SHA256 y sus localizadores JSON. PLAN_RECALCULO.json repite sólo esta extracción stdlib desde los primarios incluidos, sin importar el motor. Los snapshots completos quedan en las ubicaciones ya indexadas por las dos campañas de origen; este stage no los sustituye.
