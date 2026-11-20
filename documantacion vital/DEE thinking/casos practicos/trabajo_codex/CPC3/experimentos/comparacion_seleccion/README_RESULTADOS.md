# Comparación física y acceso condicionado: alcance ejecutado

Se conservaron dos familias distintas; no se fusionaron sus individuos.

## Familia direccional y cuerpo con lector lateral

`src/core/comparison.py` codifica independientemente un valor binario de
expectativa y otro de consecuencia por sus direcciones. La reducción v27
produce un eje x nulo para coincidencia y no nulo para discrepancia. Las
cargas son transporte: **no se afirma comparar aritméticamente 30 con100**.
La suma130 puede acompañar códigos de coincidencia o discrepancia. Trece
preparaciones incluyen omisiones, desfase y dos reservas.

`src/habitat/selection.py` conserva ese producto hasta una consulta física
posterior. La consulta cancela dos ejes y el eje restante ejecuta una ruta P/Q.
Trece preparaciones incluyen cambio de utilidad de P/Q, cortes y reservas.
La ruta responde al estado adquirido, pero la asociación ruta–utilidad está
diseñada. Invertir las fuentes útiles deja la selección igual: **no se midió
aprendizaje de una política informativa arbitraria**. No se ejecutaron aquí
recorridos físicos separados de P fija, Q fija y alternancia; no se presentan
como controles nativos realizados.

`OPEN_POLICY_RETROSPECTIVE.json` añade la comparación **ANÁLISIS EXTERNO**
solicitada: sobre los cuatro contextos equilibrados ya guardados, encaminador
nativo, P fija, Q fija y las dos alternancias acceden a la fuente informativa
en dos de cuatro oportunidades. Las políticas no consultan el contexto oculto:
usan un nombre fijo o el índice visible del ensayo. El evaluador utiliza el
contexto sólo después para puntuar. Es lectura retrospectiva de disponibilidad;
no son nuevos mundos ni mediciones de coste físico de esas políticas.

`src/habitat/native_loop.py` conecta un cuerpo H0 real, instalado antes de T0,
con ese adaptador. Introduce A/B o B/A mediante eventos en32/33. El primer
frente del lector lateral se emite en37 y se conserva por propagación hasta47.
La consecuencia es un informe externo explícito de una de dos clases
presentes, nunca un timeout que escriba ausencia ni un error calculado por el
auditor. Se envía la misma consecuencia a ambos hubs posibles; Python no
elige el hub que coincide con la predicción. Sólo el frente realmente emitido
completa el código de comparación.

En AB con cambio, la cadena observada fue:

| Tick | Producto físico |
| --- | --- |
|37| expectativa de carga7, dirección(1,1,0) |
|47| encuentro con informe17: carga24, dirección(1,1,1) |
|51| consulta común13: carga37, dirección(1,0,0) |
|56| acceso a Q con informe23: carga60, dirección(1,1,0) |
|64| sonda posterior7: carga67, dirección(1,0,1) |

BA produce la cadena opuesta hacia P. El frente reservado conserva cada
registro y su dirección por la ruta37–46; en el contexto completo del hub en46
aparecen exactamente los dos contribuyentes direccionales que realizan el
encuentro siguiente. No se asignan padres sólo por igualdad de carga.

Se ejecutaron cuatro discovery y nueve confirmaciones nuevas, incluidas dos
reservas. Los cortes tardíos en37 y47 modificaron exactamente un sitio RAW y
ningún clock; quitaron el producto informativo60 en56. La copia idéntica sham
no modificó sitios y conservó el producto. Cortar la fuente seleccionada deja
la acción37 sin información23; cortar la otra fuente conserva60. Intercambiar
utilidad mantiene la selección y obtiene el valor constante5, producto42.

La única extensión posterior reutiliza el producto56 mediante otra sonda
común:67 en AB/BA y85 cuando el informe reservado vale41. El corte tardío del
producto56 deja únicamente la sonda7, sin componente de acción en x. La copia
idéntica conserva67. Guardar56, cargar y ejecutar realmente la consulta61–64
reproduce RAW y clocks, sin leer una respuesta de archivo. Es uso posterior
de información móvil; **no es reescritura de la relación basal A/B**.

`NativeLoopSession` ofrece create, advance, run_until, observe, save y load.
Es un episodio finito con recursos explícitos. No usa forks operativos, no
reinstala cuerpos y no ofrece reutilización indefinida. Los forks de cortes
son exclusivamente diagnósticos y no regresan a MAIN.

## Familia central sobre el MAIN de lectura cero

`src/core/central_comparison.py` declara antes de la experiencia dos entradas
inertes. Una observación real presente de la barrera se codifica con carga1 en
la diagonal(±1,0,±1), con dirección(0,0,±1). El código depende únicamente de la
observación actual; no recibe predicción, delta, etiqueta de error ni futuro.

El cuerpo adquiere su historia de paquetes reales en32/33. Emite su pronóstico
en37 para el resultado83. En83 se observa y codifica ese resultado. El
gradiente v27 en84 integra la relación A/B retenida con la presencia física
del informe:

| Historia y consecuencia | Dirección nativa en84 |
| --- | --- |
| abierta → abierta | (0,0,-1) |
| cerrada → cerrada | (0,0,1) |
| abierta → cerrada | (1,0,1) |
| cerrada → abierta | (-1,0,-1) |

La rama de anclaje de momento importa: H0 con dirección previa nula no produce
marcador aunque la entrada se aplica. No se le asigna una expectativa falsa.
Omitir el informe conserva el eje x previo sin marcador z. Dos reservas de
origen/estado reproducen las discrepancias. Un intercambio diagnóstico de A/B
en dos sitios, con clocks conservados, cambia discrepancia a coincidencia;
el sham idéntico la conserva. Igualar A modifica un sitio pero conserva el signo
del producto discrepante: ese control no demuestra una codificación escalar
lineal de error.

La comparación altera el contexto lector. La relación A/B se conserva, pero
el marcador puede persistir y no debe leerse como un nuevo pronóstico. En las
continuaciones con informe, los cinco intentos de nueva observación fueron
rechazados por ocupación hasta1000. Las trayectorias sin informe mostraron
asimetría de admisión y expresión. No se repararon ni despejaron puertos. Esta
integración demuestra un encuentro comparativo finito, **no el ciclo completo
de comparación, selección útil aprendida y nueva adquisición continuada**.

## Evidencia y reproducción

- `resultados/`: trece comparadores físicos.
- `seleccion/`: trece casos de encaminamiento y acceso.
- `native_discovery/`, `native_confirmation/`: cuerpos laterales y reservas.
- `late_controls/`: cortes selectivos tardíos y sham.
- `post_information/`: uso posterior, cortes y continuidad.
- `central_discovery/`, `central_confirmation/`: comparación en MAIN central.
- `central_followup/`: controles de historia y continuación hasta1000.
- `technical/TECHNICAL_CHECKS.json`: observación, Dense/Lazy/Parallel, save/load
  y ausencia de efecto físico de la futura consecuencia antes de presentarla.
- `TECHNICAL_NOTES.md`: errores instrumentales y sus correcciones preservadas.

Los runners aceptan `--root` explícito. Se ejecutan con el WHL3.5.0 en procesos
supervisados por `compartido/supervise.py`. Las métricas y clasificaciones
externas nunca se realimentan al controlador.
