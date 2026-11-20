# Caracterización mecánica de la amplificación causal HB–P2

## Alcance

Esta entrega caracteriza el aparato parental congelado de Procesos 01 / Ingeniería 06 V2. Usa `N=39`, historias H0/AB/BA, oportunidades P1/P2/P3, `HOST_STOP` parental y las transformaciones MAIN_S0, FRESH_V1 y FRESH_V2. No introduce estructuras ni intervenciones después de `HOST_STOP`. FRESH_V1/V2 son controles de covariancia espacial congelados, no muestras estadísticas independientes.

Los números siguientes proceden de `HB_P2_DENSE_TIMELINE.json`, `FIELD_DIFF_TIMELINE.json`, `HB_P2_CAUSAL_FRONT_TOPOLOGY.json`, `FIRST_DIVERGENCE_STATISTICS.json`, `PLATEAU_MASK_DYNAMICS.json`, `MATCHED_CONTROL_COMPARISON.json` y los mapas NPZ adjuntos.

## Corrección puntual causada por evidencia primaria nueva

La afirmación heredada «HB–P1 y HB–P3 no muestran una expansión comparable» sólo describe correctamente la ventana observada anteriormente, hasta `+256`. La extensión congelada hasta `+512` muestra que ambas comparaciones alcanzan media retícula en `+442` y 99 % en `+450`. HB–P2 conserva una separación temporal cuantificada: media retícula en `+112` y 99 % en `+121`, 330 y 329 ticks antes, respectivamente. No se modifica ningún otro hallazgo heredado.

## Evolución entre +64 y +144

| tick | RAW distinto | FULL ocupado | OMIT_P2 ocupado | diferencia de ocupación |
|---:|---:|---:|---:|---:|
| 64 | 406 | 311 | 360 | 385 |
| 80 | 512 | 326 | 434 | 490 |
| 96 | 1 174 | 334 | 1 041 | 1 135 |
| 100 | 2 378 | 340 | 2 242 | 2 334 |
| 103 | 4 885 | 339 | 4 749 | 4 830 |
| 108 | 15 394 | 343 | 15 273 | 15 306 |
| 112 | 32 113 | 340 | 32 043 | 31 955 |
| 113 | 37 043 | 342 | 36 979 | 36 867 |
| 116 | 50 645 | 347 | 50 638 | 50 371 |
| 120 | 58 517 | 344 | 58 544 | 58 200 |
| 121 | 58 751 | 346 | 58 772 | 58 438 |
| 128 | 58 877 | 355 | 58 903 | 58 550 |
| 144 | 58 877 | 361 | 58 903 | 58 544 |

La diferencia comienza a cambiar desde `+1`; no existe un tick de inicio único posterior. La aceleración se concentra después de `+95`: RAW y `state` superan 1 000 posiciones en `+95`, `semantic` en `+96`, y `s_reg`/`dx`/`dy`/`dz` en `+97`. La mayor razón finita entre conteos consecutivos aparece en `+103` (`1.289258...`), la mayor segunda diferencia en `+109` (`526`) y el mayor incremento absoluto en `+113` (`+4 930` posiciones RAW). La curva combina crecimiento temprano lento, aceleración entre aproximadamente `+95` y `+119`, y aproximación a una meseta desde `+121/+124`.

## Campos que transportan la diferencia

La omisión ya diferencia todos los campos RAW en `+0`, de modo que «primer campo» significa aquí primer campo cuya extensión espacial cruza una escala común. RAW y `state` cruzan 1 000 posiciones en `+95`; `semantic` en `+96`; `s_reg` y las tres direcciones en `+97`. En `+113`, el incremento máximo ocurre simultáneamente en todos ellos: RAW `+4 930`, `state` `+4 935`, `semantic` `+4 912`, `s_reg` `+4 846`, `dx` `+4 771`, `dy` `+4 617`, `dz` `+4 740`.

En `+128` la firma nombrada es:

- RAW: 58 877;
- `state`: 58 877;
- `semantic`: 58 561;
- `s_reg`: 57 325;
- `dx`: 55 752;
- `dy`: 55 671;
- `dz`: 55 794.

La firma parental anónima ordenaba los tres conteos direccionales y, por ello, no preservaba el nombre del eje. `RAW_SIGNATURE_SCHEMA.json` registra esa limitación y la nueva medición conserva `dx/dy/dz` explícitamente.

La diferencia de `clock_a` permanece en 13 posiciones durante toda la trayectoria medida. Lo mismo ocurre para clock absoluto, residual, mod 391, mod 782 y mod 304980. El crecimiento RAW no es crecimiento de una diferencia clock; los datos no determinan si los valores clock constantes participan internamente en la regla local.

## Ocupación y extensión contrafactual

En `+128`, `HB_FULL` sigue disperso (355 ocupadas), mientras `HB_OMIT_P2` contiene 58 903. De las 58 877 posiciones RAW diferentes:

- 58 549 están ocupadas sólo en `OMIT_P2`;
- 1 está ocupada sólo en `FULL`;
- 327 están ocupadas en ambos pero tienen RAW diferente.

Las 442 posiciones RAW iguales se dividen en 415 ceros compartidos y 27 posiciones ocupadas iguales. Por tanto, la separación entre soporte visible de `FULL` y extensión contrafactual es real, pero su mecanismo medido no es una influencia sin soporte en ambas ramas: la rama `OMIT_P2` se densifica. La cantidad casi global describe la divergencia entre dos trayectorias, no una capa material adicional dentro de `FULL`.

`HB_FULL` permanece entre 340–373 posiciones ocupadas desde `+112` hasta `+391`. Después también se densifica: cruza media retícula en `+442` y 99 % en `+450`. `OMIT_P2` ya había cruzado esas escalas en `+112/+121`. En `+512` ambos mundos son densos (`58 889` y `58 903`), pero 58 540 posiciones aún tienen RAW diferente.

## Topología, cono causal y toro

La máscara comienza con 19 posiciones en 4 componentes Moore-26 (6 Moore-6). No crece como un frente único compacto. En `+96` tiene 316 componentes Moore-26 y 619 Moore-6; en `+103`, 366 y 934. Durante la aceleración las ramas se unen: 179/949 componentes en `+112`, 120/790 en `+113`, y una sola componente bajo ambas conectividades en `+120`.

La distancia usada es Chebyshev toroidal desde el soporte `D_0`, compatible con self+Moore-26. Entre 59 319 posiciones:

- ninguna primera divergencia RAW ocurre antes de su distancia mínima;
- 126 ocurren exactamente en el límite de distancia;
- la distancia toroidal máxima observada es 19;
- una posición de ese shell diverge por primera vez en `+101`;
- ninguna aparición RAW nueva carece de al menos un antecedente posible RAW/clock en self+Moore-26 del tick previo.

Esto sustenta propagación compatible con la localidad pública del kernel. La multiplicidad de componentes se explica por ramas nacidas del soporte inicial distribuido y su interacción con trayectorias ya presentes. Alcanzar el shell toroidal máximo y fusionarse en una componente es compatible con cobertura y reencuentro sobre el toro; el grafo de ascendencia registra padres posibles, no una asignación causal única, de modo que no identifica un frente único ni una ruta exclusiva.

## Intervalo alrededor de +112

La cantidad de posiciones RAW nuevas por tick aumenta de 783 en `95→96` a 6 103 en `112→113`; después cae a 315 en `119→120`, 145 en `120→121`, 50 en `121→122`, 22 en `122→123` y 9 en `123→124`. Al mismo tiempo, el número de componentes Moore-26 cae de 366 en `+103` a 179 en `+112`, 120 en `+113` y 1 en `+120`. Los datos describen coalescencia acelerada de muchas ramas locales, no un salto simultáneo no local.

## Meseta y residuo igual

Entre `+128` y `+391` el conteo oscila sólo entre 58 876 y 58 881. La máscara también es casi fija: entre checkpoints consecutivos su Jaccard es al menos `0.999915`, con 1–5 cambios por intervalo. No es sólo un conteo constante. Entre todos los checkpoints de meseta registrados, 58 129 posiciones permanecen siempre diferentes y 32 siempre iguales.

En `+128`, las 442 posiciones iguales no forman una frontera compacta: son 390 componentes Moore-6 (máximo 3) y 149 Moore-26 (máximo 15). Las 415 posiciones cero compartidas dominan el residuo; las 27 ocupadas iguales poseen `semantic=4`, nueve valores `state` repetidos tres veces y `s_reg=0` en 24 casos, `s_reg=7` en 3. Esta estructura pequeña está dispersa, no constituye por sí sola una superficie continua.

La meseta no es indefinida. Entre `+391` y `+512`, cuando `HB_FULL` también se densifica, el Jaccard baja a `0.980552`, con 406 posiciones que entran y 747 que salen de la máscara. En `+512` el residuo igual es 779 posiciones: 5 ceros compartidos y 774 ocupadas iguales. Cambia, por tanto, la composición del residuo aunque la diferencia RAW continúe casi global.

## Controles e identidad BA/P2

H0–P2 y HA–P2 nunca alcanzan media retícula hasta `+512`; sus máximos RAW son 337 y 280. El contexto BA es necesario en este aparato. P2 determina la latencia dentro de BA, no una capacidad exclusiva de expansión:

- HB–P2: media retícula `+112`, 99 % `+121`;
- HB–P1: media `+442`, 99 % `+450`;
- HB–P3: media `+442`, 99 % `+450`.

La dirección contrafactual también importa. En HB–P2 la rama `OMIT_P2` se densifica primero. En HB–P1/HB–P3, la rama común `HB_FULL` se densifica tarde mientras las ramas omitidas permanecen dispersas. P2, por tanto, participa en una interacción no aditiva que modifica fuertemente el tiempo de acceso al régimen denso.

En `HOST_STOP+0`, HA y HB no difieren dentro de radios Chebyshev 0–4 alrededor del centro de P2; la diferencia HA/HB más próxima está a distancia 12. En `+64`, las diferencias históricas ya alcanzan distancia 1 del centro de P2 (9 posiciones distintas en radio 2). No existe una diferencia local inicial alrededor de P2 que explique por sí sola la separación; la trayectoria BA modifica posteriormente ese contexto. Esto no localiza la condición suficiente ni demuestra que toda la causa sea global.

## Semántica temporal de observers

- `M_relation`/`R2_RELATIONAL`/`M_function`, al usar h32/h64, distinguen la trayectoria HB–P2 desde `+0`; anticipan mediante futuros diagnósticos, no muestran materialización near-global presente.
- La máscara contrafactual exacta de X_FULL para HB–P2 deja de coincidir con cada control emparejado en `+7`; los resúmenes R0, configuración, geometría y recurso usados aquí también separan en `+7`.
- `M_history` identifica BA en `+0`, pero la etiqueta BA sola no identifica qué oportunidad tendrá latencia temprana.
- `M_phase` permanece ciego bajo las proyecciones de clock emparejadas: las cinco comparaciones retienen 13 posiciones clock diferentes sin expansión.
- La geometría de `HB_FULL` es una sombra especialmente pobre para la amplificación temprana: ve 355 ocupadas en `+128`, mientras la máscara contrafactual tiene 58 877. Esto no la invalida para describir el mundo FULL; sólo muestra que no representa el efecto FULL/OMIT.

Entre descripciones presentes heredadas, la combinación mínima observada que anticipa el caso es la máscara contrafactual X_FULL de FULL/OMIT, distinguible de todos los controles en `+7`. Entre descripciones future-informed, el vector h0/h32/h64 ya lo separa en `+0`. Los conteos iniciales aislados (19 RAW; 13 clock) no bastan.

## Covariancia fresh

FRESH_V1 y FRESH_V2 reproducen exactamente la curva de 513 puntos. Tras canonicalización reproducen exactamente el mapa de primera divergencia RAW, el mapa clock y todas las máscaras muestreadas; los hashes nativos cambian sólo conforme a la transformación espacial congelada. Esto verifica covariancia geométrica del aparato, no frecuencia poblacional.

## Relación con evidencia anterior

NRD04 comparte dependencia configuracional, no aditividad y sensibilidad valor/posición. HB–P2 añade una trayectoria temporal casi global y una reconstrucción del cono causal. No se demuestra identidad microscópica entre ambos.

POST-04.5 midió expansión visible de un mundo. HB–P2 mide una diferencia entre mundos y separa la geometría de cada rama. En la ventana temprana, `FULL` sigue disperso y `OMIT_P2` se expande; por ello ambas campañas pueden compartir una clase descriptiva de reorganización extensa, pero no la misma cantidad observada ni necesariamente el mismo mecanismo.

## Mecanismos compatibles con las mediciones

1. **Modulación histórica de latencia de un régimen expansivo.** BA permite densificación; la presencia/ausencia de P2 cambia su tiempo de acceso de aproximadamente `+442` a `+112` en la rama omitida.
2. **Interacción configuracional no aditiva entre BA y el conjunto P1/P2/P3.** P2 no es un emisor suficiente: retirarlo adelanta una trayectoria, mientras retirarlo bajo AB o H0 no produce la expansión.
3. **Ramificación local seguida de coalescencia toroidal.** La diferencia avanza mediante múltiples ramas compatibles con self+Moore-26, alcanza el shell toroidal máximo y se fusiona en una máscara conectada.

Estos mecanismos no son excluyentes y los datos actuales los sostienen conjuntamente. Sigue ambiguo qué microconfiguración local inicia la aceleración entre `+95` y `+103`, si el clock residual constante es requisito de la regla aunque no se expanda, y qué papel funcional cumplen las 27 posiciones ocupadas iguales del residuo.

## A) WHAT_IS_DIRECTLY_MEASURED

Estados públicos completos emparejados, diferencias por campo, ocupación de cada rama, máscaras espaciales comprimidas, primera divergencia de cada vóxel, topología Moore-6/Moore-26, distancia toroidal, ascendencia local potencial, dinámica del residuo, latencia de observers y covariancia exacta bajo dos transformaciones espaciales congeladas.

## B) WHAT_MECHANISM_IS_SUPPORTED_BY_THE_MEASUREMENTS

Una historia BA y la configuración de oportunidades modulan la latencia de una reorganización expansiva. La omisión de P2 adelanta la densificación de la rama contrafactual; la diferencia se ramifica localmente, acelera, coalesce sobre el toro y permanece casi fija durante cientos de ticks. P2 no actúa como fuente global aislada.

## C) WHAT_REMAINS_AMBIGUOUS_WITHIN_THIS_MECHANISM

La condición microscópica suficiente que inicia la aceleración, la asignación única de ascendencia, el papel necesario o meramente acompañante del clock residual, la función del residuo estructurado y la identidad o no con los mecanismos de NRD04/POST-04.5.

## D) WHAT_DATA_ARE_NOW_AVAILABLE_FOR_THE_NEXT EXPERIMENT

Curvas tick a tick hasta `+512`, checkpoints completos seleccionados, máscaras espaciales, mapas de primera divergencia, grafo de ascendencia potencial, topología del frente, residuo, separación FULL/OMIT, controles H0/HA/HB–P1/P2/P3, transformaciones fresh canonicalizadas y semántica temporal de observers. Esta entrega no diseña ni ejecuta el experimento posterior.

