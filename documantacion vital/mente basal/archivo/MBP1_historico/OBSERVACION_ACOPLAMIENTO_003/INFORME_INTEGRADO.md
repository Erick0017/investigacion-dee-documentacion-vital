# Informe integrado — observación relacional y acoplamiento 003

## 1. Alcance y modalidad

Se preservó el mundo principal `MENTE-BASAL-001`. Se realizaron tres clases de trabajo:

1. observación pasiva de checkpoints inmutables;
2. replay de ventanas sobre copias cargadas;
3. consultas y preparaciones diagnósticas sobre ramas completas que nunca regresaron al linaje principal.

No se modificó DEE thinking 2.2.0, el kernel v27 ni las Entregas 01/02. Después de `T64` no se registraron nuevas entradas físicas en el mundo principal; el tramo observado corresponde a evolución libre de la preparación ya existente.

## 2. Corrección instrumental de clocks

El analizador de `CUT_002` había aplicado `% 19665` al delta de clocks. Eso confundía `P_KERNEL`, que interviene en el reductor, con un módulo del clock. La comprobación corregida comparó los `2,048,383` clocks completos entre `T64` y `T134856`:

- delta esperado: `134792`;
- histograma observado: `134792` en los `2,048,383` sitios;
- anomalías: `0`.

El valor anterior `16802` es únicamente `134792 % 19665`. Los snapshots históricos no se editaron.

## 3. Observadores móviles

Se fijaron anclas externas en `T64`, sin escribir IDs en DEE:

| Identidad operacional | Origen T64 | Dirección | Carga |
|---|---|---|---:|
| linaje relacional | `(83,116,63)` | `(1,1,0)` | 4184 |
| resultado material | `(28,12,82)` | `(0,1,1)` | 68 |
| contenido contextual | `(110,27,104)` | `(1,0,1)` | 40 |

La predicción `posición(T)=posición(T64)+dirección*(T-64) mod 127` coincidió exactamente, con el mismo RAW y dirección, en `T134856`, `T193536`, `T211856` y `T214872`. En el corte final se observaron respectivamente en `(7,40,63)`, `(28,63,6)` y `(34,27,28)`. Los lectores fijos habrían informado ausencia en sus coordenadas antiguas; el lector relacional los conserva como transporte exacto en los endpoints medidos. La continuidad tick a tick no se infiere de esos endpoints cuando no existe replay intermedio.

Una prueba de pasividad comparó RAW, clocks y tick antes/después de `observe_many`: igualdad exacta, cero escrituras.

## 4. Cadencia ambiental

En los cuatro centros `(82,91,48/52/56/60)` se verificaron seis vecinos activos, suma direccional nula y ausencia de protección porque `n_active < 7`. Bajo esas premisas locales:

`period_ticks = 782 // (8 - n_active) = 391`.

Esto pertenece a la rama contextual de v27; no es una constante descubierta por la organización ni un ciclo completo del mundo. Replay Lazy desde `T193536` observó incrementos `494 -> 495` en `T193559`, `193563`, `193567` y `193571`. Dense confirmó el primer evento en `T193559`. En `T214872`, los cuatro centros tenían `s_reg=549`, exactamente 55 incrementos posteriores, sin overflow ni genesis en la ventana reproducida.

El estado completo no se repite cada 391 ticks: clocks y `s_reg` continúan cambiando. Los centros tampoco emiten un portador útil en cada incremento. Si las guardas permanecieran, el primer overflow calculado ocurriría cerca de `T7,689,029`, fuera del presupuesto principal `T900064`. Además, las órbitas actuales de 4184, 68 y 40 no atraviesan los centros de residuos. Por tanto, este montaje principal no ofrece dentro de su horizonte una vía directa desde esos incrementos locales hacia los tres portadores.

## 5. Acceso funcional al contenido 40

Desde `T193536` se aplicó en ramas diagnósticas una consulta físicamente programada para encontrar al portador móvil, con el lector congelado antes de ejecutar:

| Caso | Q, T+4 | R, T+8 | Lectura |
|---|---:|---:|---|
| intacto | 47 | 52 | `40+7`, seguido por `47+5` |
| sham temporal | 40 | 5 | la consulta 7 no coincide con 40 |
| sham de carga cero | 40 | 45 | el primer encuentro no añade carga; luego participa 40 |
| mediador ausente | 7 | 5 | consultas sin contenido 40 |

Todas las experiencias declaradas fueron admitidas. Dense reprodujo `47 -> 52`. El mismo protocolo congelado se aplicó después al checkpoint histórico `CUT_002`, con otra fase y distancia, y reprodujo `47 -> 52`; pertenece al mismo linaje, no estaba reservado antes del diseño y no es una réplica estadísticamente independiente. El campo `purpose` del JSON primario que decía lo contrario se conserva como salida original, pero queda corregido aquí y en el runner entregado.

Resultado: 40 no sólo conserva estructura; permanece causalmente accesible y se utiliza en dos transformaciones sucesivas bajo este protocolo. Esto cierra una lectura funcional pendiente, pero no constituye aprendizaje nuevo del mundo principal.

## 6. Acoplamiento ambiental diagnóstico

Se buscó primero una vía ya presente. No se encontró acceso directo desde los cuatro residuos a los portadores dentro del horizonte autorizado. En consecuencia se creó una rama completa y separada desde `T193536`. El investigador instaló seis soportes `semantic=4`, participantes genéricos y un sesgo declarado; no reinició clocks ni escribió el resultado final.

En el tratamiento, el móvil 40 y el sesgo 19624 alcanzaron un sitio ambiental en una fase que produjo `s_reg=19664`. El siguiente evento nativo generó un overflow DEMUX y modificó un portador independiente `23 -> 24`. Ese portador se utilizó después en una cadena de encuentros:

`24 -> 55 -> 62 -> 62 -> 67`.

Controles Lazy:

| Caso | estado ambiental | DEMUX | cadena posterior | overflow |
|---|---:|---:|---|---:|
| intacto | 19664 | 24 | 55,62,62,67 | 1 |
| subumbral, sesgo 19623 | 19663 | 23 | 54,61,61,66 | 0 |
| query sham | 19664 | 0 | 31,7,0,5 | 1 |
| corte de un soporte | 19664 | 23 | 54,61,61,66 | 0 |

Dense reprodujo las lecturas funcionales del tratamiento completo; no se guardó una comparación integral de RAW+clock entre backends. La aplicación posterior del protocolo al checkpoint histórico `CUT_002` reprodujo tratamiento y subumbral con una demora distinta.

La fila subumbral registra el sitio en el tick causal: después alcanza 19664, pero no cruza el umbral de fusión 19665 y no produce overflow. En `query sham`, el registro de carga cero sigue físicamente ocupado; cero no se trató como ausencia.

Resultado: existe una mediación causal finita y preparada en la que actividad ambiental modifica un portador y la diferencia se utiliza después. La especificidad del sesgo y la interfaz fueron instaladas por el investigador. No se observó que el mundo principal adquiriera esa interfaz, ni autoenseñanza general, ni sostenibilidad indefinida.

## 7. Estado del mundo principal al corte final

- Corte: `OBS_003_FINAL`, `T214872`, 2026-10-05 09:39:02.276 UTC / 03:39:02.276 -06:00.
- Intervalo nuevo desde la referencia: 21,336 ticks, formado por 2,667 bloques contiguos de 8.
- Estado: 37 sitios ocupados, 23 recibos aplicados, 0 rechazados.
- Entradas físicas nuevas: 0.
- RAW modificados en el intervalo: únicamente los cuatro residuos, `s_reg 494 -> 549`; ocupación y soporte RAW permanecieron en 37.
- Clocks: delta exacto `21336` en los `2,048,383` sitios.
- Checkpoint: `tick_000000214872_collect_OBS_003_FINAL_3babbbcd.deetsnap`.
- El corte no detuvo el worker y abrió un segmento nuevo.

Se dejó un seguidor pasivo independiente que sólo abre checkpoints publicados. No toca arrays vivos y no presenta entradas. Los experimentos de acoplamiento quedaron guardados, no corriendo como un segundo mundo persistente.

El seguidor inició con PID 17484 y sobrevivió al cierre de su proceso lanzador. Muestreó los checkpoints `T211856` y `T214872`; entre ambos los tres portadores siguieron apareciendo en sus posiciones predichas y los residuos pasaron de 541 a 549. Su campo `world_tick` es un heartbeat operativo leído de `status.json`, no una observación física del estado mutable. Las comprobaciones exactas de pasividad son los recorridos one-shot en `T193536` y `T214872`, ambos con `passivity_exact=true`.

El worker principal conservó PID 16864, sesión y world_id. Después del corte se observó progreso al menos hasta `T215312`, sin reinicio ni cambio de deadline. El límite seguía siendo `2026-10-05T19:57:45.761Z` y `tick_budget_end=900064`.

## 8. Límites explícitos

- Los endpoints respaldan transporte exacto; no documentan cada microinteracción entre cortes.
- La cadencia 391 depende de la vecindad, supervivencia y guardas observadas.
- El crecimiento local no fue una emisión útil hacia la organización principal dentro del horizonte.
- La función 40 fue probada con consultas diagnósticas externas en ramas.
- El acoplamiento demuestra mediación preparada, no adquisición espontánea de la interfaz.
- Las confirmaciones Dense conservan las lecturas y trazas declaradas; no se obtuvo igualdad microscópica RAW+clock completa entre backends para estos paneles.
- No se demostró aprendizaje nuevo, anticipación, fan-out, autonomía científica ni un ciclo exacto del mundo completo.
