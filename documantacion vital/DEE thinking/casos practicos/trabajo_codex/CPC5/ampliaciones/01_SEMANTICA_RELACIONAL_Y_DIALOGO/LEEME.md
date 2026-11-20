# CPC5 · ampliación 01: semántica relacional y diálogo

Proyecto DEE Universe / INVESTIGACION DEE. Autor: Ivan Erick Tlaltecatl Morales.
Instrumento oficial DEE thinking4.0.0, kernelv27 congelado. Esta carpeta amplía el
expediente; no actualiza el producto. El corte anterior conserva sus archivos y
manifiestos byte por byte. Empiece por `revision/LEER_PRIMERO.md` y
`revision/LECTURA_PROVISIONAL.md` para revisar los datos sin ejecutar mundos.

## Instalar y comenzar

Se requiere Windowsx64 y CPython3.13 de64bits. El wheel está una sola vez en
`CPC5/runtime/`, dos carpetas por encima de esta ampliación. No necesita CPC3,
CPC4, un LLM, internet, un compilador ni los documentos históricos externos.
Desde la raíz CPC5 extraída:

```powershell
& 'C:\ruta\Python313\python.exe' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install --no-index --no-deps '.\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
cd '.\ampliaciones\01_SEMANTICA_RELACIONAL_Y_DIALOGO'
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_longitudinal.json --salida sesiones/nueva_01
```

También puede usar `iniciar_ampliacion.ps1 -Python313 'C:\ruta\Python313\python.exe'`.
El hash del wheel debe ser
`17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623`.
La aplicación comprueba versión, kernel, módulo nativo y procedencia de importación.

El recorrido principal recibe una relación contextual, la consulta, adquiere
otra relación más tarde, solicita información nativamente, utiliza el retorno,
recibe después una forma opaca y la consulta. Guarda y restaura sin rearmar al
individuo. La evidencia central está en `resultados/dialogue_longitudinal/` y
`resultados/demo_longitudinal_01/`; los nombres exactos constan en el índice.

## Otros recorridos

```powershell
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_orden.json --salida sesiones/orden_01
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_dialogo.json --salida sesiones/dialogo_01
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_red3.json --salida sesiones/red3_01
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --salida sesiones/interactiva_01
```

`ayuda` muestra la gramática. No hay conversación libre. Las etiquetas U1/U2,
N0/NORD y A/B son identificadores del aparato, no significados de YO/TÚ.

```text
nuevo orden | dialogo | A1 | A2 | A3 | A4 | red1 | red2 | red3 | red4
evento A|B carga tick
leer_orden carga tick
experiencia U1|U2 cue reporte signo tick
relay turn1|turn2 [tick]
experiencia etapa indice cue reporte tick
solicitar carga tick
ensenar N0|NORD carga tick
consultar N0|NORD carga tick
contexto signo carga tick
recurso carga tick
soporte U1|U2 carga tick
avanzar tick_absoluto
observar
recibos
guardar archivo.deetsnap
reiniciar CONFIRMO
cargar archivo.deetsnap
salir
```

Las operaciones dependen de la preparación. `orden` ofrece A/B, NORD y contexto.
`dialogo` ofrece U1/U2, relays, dos bancos, N0 y soportes. A1–A4 son las rutas
finitas de12 componentes con1–4 agrupaciones físicas, no cuerpos universales.
Sus experiencias se presentan por `experiencia etapa i cue reporte tick`.
`red1`–`red4` ofrecen1–4 conjuntos de roles distribuidos y6–24 componentes,
con interfaces de ida/vuelta físicamente preparadas. No son el contraste
de12 componentes a inventario fijo. Para la red se añaden estos comandos:

```text
experiencia Ui memoria|contexto cue reporte signo tick
relay Ui turn1|turn2 tick
solicitar Ui carga tick
recurso Ui carga tick
soporte Ui memoria|contexto carga tick
ensenar Ui N0 carga tick
consultar Ui N0 carga tick
```

Ui es U1..Um. El vecino y el acceso por rol se fijan en la preparación;
Python no busca quién sabe la respuesta. La copia de respaldo se enseña mediante
otras entradas físicas, no mediante copia de memoria. `demo_red3.json` recorre
comunicación, enseñanza posterior de N0, consulta y seis respaldos. Su continuación:

```powershell
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_red3_continuacion.json --checkpoint sesiones/red3_01/RED3_T204.deetsnap --salida sesiones/red3_continuada_01
```

Los tiempos son absolutos; no se retrocede ni se selecciona una fase según el
resultado correcto. Las cargas son enteros uint16 representables. Las preparaciones
publicadas tienen dominios adicionales; representable no significa funcional.

`observar` lee pasivamente. `consultar` y `leer_orden` son interacciones físicas:
pueden transformar o consumir portadores. Un recibo Scheduled aún no es Applied.
`recibos` conserva rechazos, incluidos occupied y late. Ausencia no se decodifica
como cero. El renderer muestra campos medidos, sin completar una respuesta humana.

## Continuar en otro proceso

Después de la demostración longitudinal:

```powershell
& '..\..\.venv\Scripts\python.exe' ejecutar.py demostracion --eventos configuraciones/demo_longitudinal_continuacion.json --checkpoint sesiones/nueva_01/LONGITUDINAL_T338.deetsnap --salida sesiones/continuada_01
```

`--checkpoint` sustituye únicamente una ruta en la plantilla, no un significado
ni una respuesta. El snapshot conserva materia, clocks, tick, puertos, cola,
recibos y estado de sesión. Cargar no vuelve a enseñar ni libera automáticamente
puertos ocupados. Los forks diagnósticos nunca regresan a MAIN.

## Reproducir y examinar

El ejecutor tiene además modos `orden`, `dialogo`, `capacidad` y `arquitectura`:
consulte `python ejecutar.py --help`. Los dos primeros reciben `--config` con
una batería; los otros `--caso` con una receta finita. Cada salida debe ser nueva.
No cambie una configuración y reutilice la etiqueta de reserva de la anterior.

Los comandos exactos, timeouts y salidas están en `jobs/`. El presupuesto histórico
de cuatro horas es `BUDGET.json`; no se reinicia al reanudar. El ejecutor público
ofrece timeouts locales para nuevas ejecuciones explícitas, no un trabajo de fondo.
Cada worker es propietario único de su Runtime; el supervisor sólo termina hijos
propios. `REANUDACION.json` describe el punto real del corte y las tareas pendientes.

`src/audit_extension.py` recalcula índices, observaciones, admisión y retención
desde los primarios. Es un instrumento externo: no lo importa el participante.
Los apuntadores JSON y hashes permiten localizar la lectura original.
`src/analyze_semantic.py` y los resúmenes de capacidad/composición muestran fórmulas
y contrastes. No convierten ticks en réplicas ni65 puertos en65 significados.

## Fuentes e integridad

`PARENT_MEMBERS.json` y `historial/corte_01/` conservan identidades y manifiestos
del padre. El nuevo manifiesto tiene un alcance propio; no reemplaza el anterior.
Las versiones de código que produjeron intentos anteriores permanecen incluidas.
Los fallos de fase, acceso, interferencia y comparación de metadatos no se borran.

El reporte limpio identifica el candidato que realmente se extrajo e instaló.
La comprobación final del ZIP y su SHA se publican fuera del contenedor para
evitar una identidad circular. Si supera20MiB comprimidos habrá exactamente dos
segmentos binarios, no dos ZIP independientes, con reunión y hashes comprobados.

El tamaño expandido puede ser considerable por los estados completos preservados.
No se incluyen entornos virtuales, cachés, toolchains ni ZIP históricos anidados.

## Atribuciones

ENTE: producto físico nativo medido. INSTRUMENTO: preparación, experiencia, sonda,
avance u observación. INTERPRETACIÓN: cálculo o explicación del auditor.
Los nombres españoles pertenecen a la interfaz. La relación que se afirma adquirida
debe sostenerse en el estado físico, sus controles y su uso posterior.
