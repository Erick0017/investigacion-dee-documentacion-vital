# PROCESOS 02 — CONTINUIDAD CAUSAL MEDIANTE UN GRADO PREEXISTENTE

## Alcance y contrato físico

La ejecución reutilizó el aparato BA/P1/P2/P3 congelado y añadió desde `t0` un único mecanismo positivo previo: la interfaz compartida C10H03 de CORE10. Sus doce posiciones `semantic=4`, estacionarias, forman dos guards solapados; durante la preparación generan dos centros `semantic=7`, `s_reg=1`, dirección `(0,0,0)` y `state=1`.

La geometría no fue buscada por respuesta. En MAIN_S0 se fijó la única coordenada con distancia toroidal Moore máxima respecto de todo el soporte parental inicial: centro A `(37,0,38)`, distancia `19`. FRESH_V1 y FRESH_V2 utilizaron exclusivamente las transformaciones espaciales ya congeladas del aparato.

Todos los registros físicos del componente existían antes de `HOST_STOP=4`. Después, los mundos principales recibieron únicamente `tick`, lecturas, hashes y checkpoints. Las ablaciones de centros descritas más abajo se realizaron sólo en clones diagnósticos y nunca regresaron al mundo principal.

## Estado científico vigente

**Interpretación anterior:** P2 podía describirse informalmente como el elemento que globalizaba HB.

**Evidencia posterior:** Procesos 01 y el primer bloque de Procesos 02 mostraron dos realizaciones de la misma familia expansiva: HB_OMIT_P2 con `tau50=112`, `tau99=121`, y HB_FULL con `tau50=442`, `tau99=450`.

**Interpretación actual:** BA determina el acceso al régimen expansivo; P2 participa en una interacción configuracional no aditiva que modifica su latencia. La estabilización RAW posterior es relajación terminal, no una experiencia independiente.

La presente continuación añade una observación distinta: un grado físico estable y preexistente es modificado por el frente BA con el mismo tiempo relativo en la realización temprana y la tardía, pero llega a organizaciones funcionalmente diferentes.

## 1. Mecanismo previo reutilizado

Se reutilizó `CORE10_C10H03_SHARED_INTERFACE`, no una estructura diseñada para este resultado. La fuente primaria es `core10_apparatus.py` SHA-256 `6b52faf7503d39e1e281983ab371463db1e67fc89b41cbcd4b97ce112ffb3772`; su resultado C10H03 tiene SHA-256 `7d89eed97bfdd3ffb21a9a74829219e4d31a9eec805b0b8ef2d5f1ffbcf8e679`.

## 2. Perturbación del fenómeno parental

El componente no adelantó ni retrasó los landmarks expansivos:

| Rama | parent tau50/tau99 | con componente tau50/tau99 |
|---|---:|---:|
| HB_OMIT_P2 | 112 / 121 | 112 / 121 |
| HB_FULL | 442 / 450 | 442 / 450 |

H0 y HA no cruzaron ninguno de los dos landmarks hasta `512`, con o sin componente.

La igualdad microscópica global fuera del componente no permanece indefinidamente: la presencia del scaffold produce una primera diferencia externa en H0 y HB_FULL a `t=57`, y en HB_OMIT_P2 a `t=102`. Como H0 presenta este efecto sin transición y el componente local continúa inalterado, ese onset externo no se utiliza como consecuencia downstream. La afirmación de no perturbación queda limitada a lo medido: la transición expansiva parental conserva exactamente sus tiempos y el componente local permanece RAW-invariante hasta el contacto asociado al frente.

## 3. Contacto causal con el componente

El componente ocupa 14 posiciones en todo momento: 12 de scaffold y dos centros. H0 y HA mantienen exactamente los 14 registros RAW del componente hasta `512`.

En las dos ramas BA expansivas, el primer cambio local queda alineado con el evento:

| Rama | primer cambio RAW del componente | relativo a tau50 | relativo a tau99 |
|---|---:|---:|---:|
| HB_OMIT_P2 | 113 | +1 | -8 |
| HB_FULL | 442 | 0 | -8 |

La separación absoluta entre respuestas es `329` ticks, exactamente la separación entre ambos `tau99`. Esto no usa clock absoluto como señal: el clock residual de las 14 posiciones es idéntico en los checkpoints pre/post medidos.

## 4. Transformación física observada

El scaffold de 12 posiciones permanece RAW-invariante. Sólo cambian los dos centros.

En EARLY/HB_OMIT_P2, el centro A permanece en `state=1` hasta `112` y cambia a `state=2` desde `113`; el centro B cambia de `state=1` a `state=2` entre `113` y `114`. Ambos conservan `s_reg=1`, dirección cero y `semantic=7`. La organización local queda RAW-estable desde `114` hasta `512`.

En LATE/HB_FULL, ambos centros permanecen en `state=1` hasta `441` y pasan a `state=2` en `442`. El centro B pasa a `state=3` en `446` y el centro A en `449`. Conservan `s_reg=1`, dirección cero y `semantic=7`. La organización local queda RAW-estable desde `449` hasta `512`.

Por tanto, LATE contiene una segunda transformación nativa del mismo grado: `1→2→3`. EARLY termina en `1→2`. Python no introduce ninguna de esas transiciones.

## 5. Relación con tau99

La primera modificación física tiene latencia relativa idéntica: `tau99−8` en EARLY y LATE. El estado estable aparece en `tau99−7` para EARLY y `tau99−1` para LATE. El primer enlace causal se alinea con la transición; la relajación interna posterior depende de la trayectoria.

## 6. Controles H0/HA

H0 y HA conservan 14 posiciones ocupadas, 12 posiciones `semantic=4`, dos centros `state=1` y dirección cero en todo el componente. No se observó en ellos la transformación `state 1→2` o `state 1→2→3` hasta `512`.

## 7. Persistencia

EARLY conserva ambos centros en `state=2` desde `114` hasta `512`. LATE conserva ambos centros en `state=3` desde `449` hasta `512`. La persistencia no depende de crecimiento del soporte: ocupación, geometría del componente, semántica y dirección permanecen constantes.

## 8. Consecuencia posterior y futuros

Se reutilizó el readout funcional nativo de CORE10 únicamente en clones: se eliminan los dos centros y se ejecuta un tick para preguntar si la interfaz compartida los reinstancia.

| Organización del snapshot | centros reinstanciados tras 1 tick |
|---|---:|
| baseline HOST_STOP | 2 |
| EARLY estable, t=127 | 0 |
| LATE estable, t=458 | 2 |

MAIN_S0, FRESH_V1 y FRESH_V2 reproducen exactamente esta relación `2 / 0 / 2`.

En MAIN_S0 existe información temporal adicional: EARLY reinstancia 2 centros en `t=96`, 1 en `t=112` y 0 en `t=121/127`; LATE reinstancia 2 en `t=420`, 0 en `t=442` y 2 en `t=450/458`.

El observer funcional detecta en EARLY un cambio en `t=112`, un tick antes del primer cambio RAW de los centros. Por tanto, los dos registros locales no son estado suficiente: el contexto circundante ya había cambiado su futuro. En LATE, la capacidad desaparece transitoriamente cuando los centros pasan a `state=2` y reaparece cuando la organización llega a `state=3`; la evidencia no aísla si la recuperación está mediada sólo por esos dos estados o por la configuración contextual simultánea.

La consecuencia downstream demostrada es future-relevant: organizaciones con idénticos conteos locales y el mismo scaffold producen distinta reinstanciación. En LATE, una segunda modificación física nativa coexiste temporalmente con la recuperación del futuro funcional.

## 9. Observers

| Observer | Medición |
|---|---|
| X_FULL | Ve las transiciones RAW de los centros y el contexto completo. |
| configuration | Si se reduce a conteos, fusiona pre/post: siempre 14 ocupadas, 12 `semantic=4`, 2 centros. |
| geometry | Fusiona las organizaciones: las mismas 14 coordenadas permanecen ocupadas. |
| relation | Separa baseline, EARLY y LATE mediante la relación guard-centros. |
| phase/clock residual | No separa los checkpoints del componente; el vector residual permanece igual. |
| history | Distingue finales `state=2` y `state=3` producidos por EARLY/LATE. |
| function | Separa `2 / 0 / 2` centros reinstanciados. |
| competence | EARLY pierde la reinstanciación; LATE la recupera. |
| resource | El soporte constante de 14 posiciones oculta la transformación. |
| reachability | El challenge congelado separa los futuros en un tick. |
| R0 | Fuera del dominio exacto validado de R0; no se generaliza. |
| R1 | Registra first passage: primer cambio a `tau99−8` en ambas realizaciones. |
| R2 | La función de interfaz separa las organizaciones resultantes. |
| R3 | La ocupación gruesa no distingue la nueva historia. |

## 10. Covariancia espacial fresh

FRESH_V1 y FRESH_V2 reproducen sin retuning `tau50/tau99`, respuesta EARLY `113`, respuesta LATE `442`, secuencias exactas de estados, estabilización `114/449`, readout `2/0/2` y hashes terminales canonicalizados de las cuatro ramas. Son comprobaciones de covariancia espacial del mismo aparato, no muestras poblacionales independientes.

## 11. Qué procede del corpus y qué es nuevo

Ya existían la interfaz compartida y su reinstanciación task-relative en CORE10; historia BA, equivalence breaking y transición expansiva en Ingeniería 06/Procesos 01; dependencia configuracional en Ingeniería 05; y observers relacionales en CORE15/16.

La información nueva es:

1. un componente funcional preexistente puede ser alcanzado por las dos realizaciones de la transición BA sin cambiar sus tiempos;
2. su primera modificación RAW ocurre a `tau99−8` en ambas;
3. EARLY y LATE transforman los mismos centros en finales distintos (`2` y `3`);
4. LATE contiene una segunda actualización nativa `2→3`;
5. el readout futuro queda perdido en EARLY pero se recupera en LATE;
6. un observer future-informed detecta reorganización antes de que cambien los registros locales.

## 12. Extensión de la cadena sin host

Dentro del horizonte medido:

`BA → transición expansiva → contacto event-aligned con interfaz preexistente → cambio 1→2 de centros → organización history-conditioned`.

Para LATE continúa:

`state 2 → cambios asincrónicos de los centros → state 3 → reinstanciación funcional nuevamente accesible`.

Para EARLY termina en:

`state 2 estable → reinstanciación no accesible bajo el mismo challenge`.

La cadena alcanza una nueva organización con futuros distintos y, en LATE, una segunda transformación física nativa. No se midió otro ciclo después del estado estable ni una nueva contingencia que vuelva a iniciar el régimen expansivo.

## Incertidumbres conservadas

- El componente genera backaction microscópica externa incluso en H0; esa señal genérica fue excluida del readout downstream.
- La recuperación funcional LATE coincide con `state 2→3`, pero el experimento no aísla el estado central de su contexto denso.
- El challenge de reinstanciación demuestra future relevance en clones; no es un acontecimiento autónomo del mundo principal.
- La geometría y el soporte local son insuficientes para predecir por sí solos el futuro funcional.

## DIRECTLY_MEASURED

Tiempos de transición, tiempos de respuesta, secuencias RAW de centros, persistencia, controles H0/HA, hashes canonicalizados fresh, call ledgers post-HOST y respuestas diagnósticas de un tick.

## CAUSAL_CHAIN_SUPPORTED_BY_MEASUREMENTS

La transición BA alcanza un grado preexistente con latencia relativa reproducible, lo transforma sin host y deja organizaciones estables que producen futuros funcionales diferentes. La realización LATE incluye una segunda transformación física y recuperación funcional.

## ALTERNATIVE_MECHANISMS_STILL_COMPATIBLE

La diferencia funcional puede depender de los estados centrales, del contexto denso que rodea al scaffold o de su interacción no aditiva. Los datos muestran que los centros aislados no constituyen una descripción causal suficiente.

## NEW_INFORMATION_FOR_NEXT_STAGE

Quedan disponibles tres organizaciones frozen —baseline `state=1`, EARLY `state=2`, LATE `state=3`—, tiempos relativos exactos, transformaciones fresh y un readout funcional nativo que las separa. La pregunta posterior puede dirigirse a la mediación centro/contexto sin volver a buscar posiciones o parámetros.
