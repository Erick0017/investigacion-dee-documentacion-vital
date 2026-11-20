# CPC5 · arquitecturas compuestas y aprendizaje acumulativo

DEE Universe / INVESTIGACION DEE. Autor del proyecto: Ivan Erick Tlaltecatl Morales.
Instrumento: DEE thinking 4.0.0, kernel v27 congelado. No es una actualización del producto.

## Comenzar por la evidencia

Abra `revision/LEER_PRIMERO.md` y después `revision/LECTURA_PROVISIONAL.md`.
La primera lectura no necesita ejecutar todos los mundos. `INDICE_EVIDENCIA.json`
enumera casos; `OBSERVACIONES.jsonl` conserva lecturas exactas y punteros al dato
primario; `CALCULOS.json` declara fórmulas y denominadores. Los registros RAW y
clocks son cadenas exactas o datos binarios uint64, nunca coordenadas float.
`CONTEOS_RECONCILIADOS.json` separa los 101 registros primarios, 97 preparaciones,
cuatro continuaciones restauradas, forks, consultas y reproducciones técnicas.
Estas categorías no se convierten en réplicas estadísticas independientes.

El corte compara rutas acopladas, simples, mixtas y unidades de diferentes
familias. La continuidad acumulativa se mide en individuos identificados, no
sumando repertorios de mundos distintos. Las reservas, diagnósticos, reproducciones
técnicas y preparaciones nuevas se cuentan por separado. Las 65 entradas NSM
tienen una matriz de evidencia: registrar un nombre no acredita su significado.

## Instalación sin conexión

Requiere Windows x64 y CPython 3.13 de 64 bits. El ZIP no incluye Python, un
entorno virtual ni un toolchain. El wheel exacto está en `runtime/`; no requiere
DEE thinking 3.5, CPC3, CPC4, un LLM ni acceso a internet para los recorridos.

Desde la carpeta `CPC5` extraída, con la ruta de su intérprete 3.13:

```powershell
& 'C:\ruta\Python313\python.exe' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install --no-index --no-deps '.\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
& '.\.venv\Scripts\python.exe' -c "import dee_thinking as d; print(d.__version__, d.kernel_identity(), d.__file__)"
```

El wheel debe tener SHA-256
`17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623`.
La aplicación comprueba 4.0.0, v27 y el PYD oficial antes de evolucionar.
No basta que el archivo tenga el nombre correcto.

## Demostración principal: datos nuevos, no transcripción precalculada

Use un directorio de salida nuevo para conservar todas sus sesiones:

```powershell
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' demostracion --eventos '.\configuraciones\demo_integrado.json' --salida '.\sesiones\integrado_01'
```

La demostración presenta experiencias, transmite un producto entre regiones,
reutiliza físicamente P1/P2 para incorporar dos experiencias posteriores, conserva
respaldos consultables, guarda, restaura y vuelve a consultar. En su testigo se
midieron 37→44→60→76→83 y cuatro respuestas conservadas en los paneles posteriores.
Esos números describen el testigo: la aplicación genera la evolución y lee RAW,
no busca esa serie en una tabla. Cambiar experiencias puede cambiar la respuesta.

Para el recorrido anterior de dos contribuciones acopladas y cuatro respaldos:

```powershell
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' demostracion --eventos '.\configuraciones\demo_compuesto.json' --salida '.\sesiones\compuesto_01'
```

Para modo interactivo, omita `--eventos`. `ayuda` muestra la gramática vigente.
`DIALOGO.jsonl` registra solicitudes, recibos, observaciones, errores y procedencia.

## Gramática y alcance

```text
nuevo integrado | compuesto | lexical | R1 | R2 | R3 | R4 | R5
experiencia K1 +1 0
experiencia K2 +1 67
avanzar 70
comunicar 73 5
contexto recurso 7 85
observar
guardar estado.deetsnap
cargar estado.deetsnap
consultar panel 5
ayuda
salir
```

- `integrado`: seis ubicaciones funcionales y cuatro relaciones; P1/P2 se
  reutilizan mediante experiencias, sin borrar registros. Los respaldos se
  adquieren mediante entradas físicas adicionales, no por trasplantar memoria.
- `compuesto`: dos primarias acopladas; dos respaldos y dos nuevas relaciones
  independientes. No se le atribuyen retrospectivamente las capacidades del integrado.
- `lexical`: ocho formas opacas L1…L8; `experiencia L1 +1` y `consultar L1 5`.
  Conserva asociaciones direccionales, no un diccionario universal NSM.
- `R1`–`R5`: grafos móviles finitos. Las etiquetas designan las preparaciones;
  no convierten un agregado en un compuesto por sí mismas. La verdadera referencia
  R0 es A/B/C/D, reproducible con el comando `referencia`, no un grafo renombrado.
- `experiencia stage0 3 9 0`: exposición de una etapa del grafo. Debe respetar
  la ventana publicada; no se reconstruye al individuo para aceptar una entrada tardía.
- `comunicar stage0 stage1`: avanza un enlace nativo ya declarado, sin callback
  que lea un Runtime y escriba la respuesta en otro.

`submit` programa y el recibo posterior distingue Applied, Rejected y otros
estados. Una consulta es una sonda física y puede transformar el estado.
`observar` es pasivo. `avanzar` usa una cantidad de ticks; los ticks de las entradas
son absolutos. La fase de acceso es pública y finita, no seleccionada por respuesta.
Sólo `reiniciar CONFIRMO` permite abandonar explícitamente una instancia activa.

Los nombres K/L y los participantes son identificadores de interfaz/investigador.
La dirección y el resultado proceden del estado adquirido. El renderer no
resuelve qué debería contestar la organización. ENTE indica una lectura de un
producto nativo; INSTRUMENTO una entrada, avance o medición; INTERPRETACIÓN el análisis.

## Reproducciones dirigidas

```powershell
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' referencia --caso ABCD_FILTER_FLAT --salida '.\sesiones\ref_abcd'
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' compuesto --caso '.\configuraciones\compound_reuse_D01.json' --salida '.\sesiones\reuso'
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' red --caso '.\configuraciones\red_R2_caso.json' --salida '.\sesiones\red'
& '.\.venv\Scripts\python.exe' '.\ejecutar.py' verificar
```

Las opciones `heterogeneo` y `puente` exponen las cohortes de tipos diferentes;
consulte `ejecutar.py --help` y sus configuraciones, sin calcular coordenadas.
Para reconstruir los índices y cálculos desde la evidencia, ejecute
`python src/audit.py`: es una herramienta externa y no escribe respuestas en MAIN.
`configuraciones/clean_reproduction_plan.json` contiene la instalación y las
reproducciones independientes comprobadas. La verificación compara trayectorias
generadas y snapshots completos después de ejecutarlos, no como ayuda al participante.

## Persistencia, fuentes y modalidades

El snapshot conserva RAW, clocks, tick, canales, recibos, cola pendiente y los
metadatos operativos de la sesión. Cargar no vuelve a preparar la historia.
Las versiones de sources que produjeron descubrimientos anteriores se conservan;
los ajustes de fase y errores técnicos no sustituyen silenciosamente los intentos.

`referencias/` contiene sólo aparato seleccionado y fuentes pertinentes con
procedencia. No hay ZIP históricos anidados ni dependencias de sus rutas privadas.
El wheel y el kernel no se recompilan. Los avisos que acompañan a las fuentes se
conservan; esta campaña no inventa ni modifica una licencia del producto.

Modalidades: experiencia externa declarada, evolución nativa, observación pasiva,
sonda física, fork diagnóstico y reproducción técnica. Los forks no vuelven a MAIN.
La fuente fija preparada, el pulso adquirido y una política adaptada por consecuencias
se distinguen: la última no se acredita por el nombre de un regulador.

## Tamaño, integridad y transporte

Los snapshots completos son grandes al expandirse y muy compresibles por su
estructura dispersa. No confunda tamaño expandido con comprimido. El manifiesto
enumera bytes y SHA-256 de cada archivo; `HASHES.sha256` incluye el manifiesto y
excluye su propia identidad para evitar circularidad.

Si el ZIP canónico supera 20 MiB comprimidos se entregan exactamente dos partes
binarias, `PARTES.json`, `REUNIR_CPC5.py` e instrucciones externas. No son dos ZIP
independientes. Su concatenación se comprueba contra el SHA-256 completo.
El ZIP original se conserva. No hay trabajo científico indefinido en segundo plano.
