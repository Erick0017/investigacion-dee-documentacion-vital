# CPC4 · ampliación acumulativa 02

Aprendizaje continuo, regulación nativa y red A/B/C/D. Autor del proyecto: Ivan Erick Tlaltecatl Morales. Instrumento: DEE thinking 4.0.0; kernel v27 congelado.

Esta carpeta añade evidencia al CPC4 anterior; no lo sustituye. El ZIP completo conserva su motor, fuentes pertinentes, estados y manifiestos históricos. No copie esta ampliación sola: sus rutas relativas apuntan al `CPC4/runtime` y a la evidencia heredada del mismo contenedor, nunca a una instalación privada del laboratorio.

## Iniciar

Requiere Windows x64 y CPython 3.13 estándar x64. No necesita compilar, Internet, un LLM ni documentos Word. Desde esta carpeta:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_cpc4.ps1 -Salida .\mi_sesion
```

El lanzador comprueba el WHL oficial, crea un entorno local e instala sin red la copia incluida. No incluye un entorno virtual en la entrega. No reemplaza otro Python ni modifica el producto. La sesión tiene un proceso propio y timeout por operación; `salir` lo termina. El renderer muestra sólo datos producidos por esa ejecución.

Si CPython3.13 no está registrado en `py`, indique su instalación externa con `-Python "RUTA\python.exe"`. No se utilizará silenciosamente Python3.11/3.12 ni se descargará un toolchain. La reproducción limpia de esta ejecución ejercitó esa opción con un intérprete3.13 x64, creando e instalando desde cero el entorno del lanzador.

Para reproducir el recorrido central con un archivo de eventos:

```powershell
.\iniciar_cpc4.ps1 -Eventos .\configuraciones\DEMO_CENTRAL_V3.eventos -Salida .\sesion_central
```

Tarda aproximadamente un minuto en la máquina de esta ejecución, no es una garantía de rendimiento. Crea cuatro regiones en un Runtime N67 y continúa 0→431→931→1431; después enseña dos formas y consulta la primera en1501. Guarda la misma sesión. Para continuar en otro proceso:

```text
cargar "RUTA_ABSOLUTA_A_SESION_CENTRAL\RED_LENGUAJE_T1501.deetsnap"
consultar MALO
guardar RED_T1529.deetsnap
direcciones
guardar RED_T1634.deetsnap
salir
```

`direcciones` ejecuta dos experiencias y dos consultas físicas adicionales, no imprime una respuesta almacenada. El panel intermedio conserva el resultado adverso de las formas anteriores. La preparación nueva no es el individuo histórico de CPC4 ni cuatro cuerpos basales renovables completos.

Para ver los dos contextos con neutralización nativa de interferencia:

```powershell
.\iniciar_cpc4.ps1 -Eventos .\configuraciones\DEMO_REGULADA.eventos -Salida .\sesion_regulada
```

Ese recorrido muestra0→437→937 en un mismo mundo. La salida Flat del primer contexto y la salida N del segundo se generan físicamente; los bancos miden suministro y coste. La orden `nueva-regulada SEMILLA mas sin` permite comparar la interferencia residual; `sham` conserva el portador de carga0 fuera de su encuentro causal. Son preparaciones distintas, no se cambian controles dentro de MAIN. El regulador es fijo, no una política aprendida. Este recorrido y el lingüístico v3 son realizaciones distintas, no una única fusión atribuida por compartir interfaz.

## Gramática real

- `nueva SEMILLA roles menos v3`: preparación explícita nueva. La semilla uint32 selecciona sólo una traslación toroidal de la geometría. `mas` cambia la experiencia física declarada de C, no la respuesta del decoder. También existen `basica` y el testigo `v2`.
- `nueva-regulada SEMILLA mas|menos normal|sin|sham`: nueva realización con ambos bancos preparados. `renovar-contexto` sólo en437 con Cmas y regulador normal introduce el segundo bloque de experiencias Cmenos hasta937, sin recrear el mundo. No se habilita enseñanza lingüística sobre este perfil no validado para ella.
- `avanzar T`: tick absoluto creciente, dominio interactivo0..2048. No se permite avance arbitrario mientras el protocolo lingüístico finito está activo.
- `observar`, `respuesta`, `experiencias`: panel pasivo actual, registros activos y recibos reales, respectivamente. Silencio no se convierte en cero.
- `entrada PUERTO CARGA T`, `sonda PUERTO CARGA T`: experiencia externa o sonda física; carga0..19664, interfaz ya declarada. Inspeccione el recibo después de avanzar: Scheduled no equivale a Applied.
- `currículo`: sólo en la frontera v3 sin lenguaje431. Continúa el mismo objeto hasta1431 con nuevas experiencias; no restaura materia favorable.
- `lenguaje normal|intercambiado|desacoplado`: vista inerte en431/1431; luego `enseñar` dos veces. No introduce directamente una relación aprendida.
- `consultar BUENO|MALO|L1|L2`: sonda consumible finita. Las palabras son formas fijas L1/L2; intercambiar la enseñanza puede cambiar lo que expresan, no cambia el decoder.
- `reconocer rol|episodio`: panel físico común situación→forma. Es una alternativa de consulta, no una conversación ilimitada.
- `direcciones`: tras las dos consultas anteriores, enseña las dos formas espaciales y mide su expresión y el acceso a las formas antiguas en la misma continuidad.
- `guardar ARCHIVO`, `cargar ARCHIVO`: persistencia física y operativa integral, sin sobrescribir archivos existentes. Se pueden continuar estados posteriores al protocolo terminado; sus metadatos históricos no reactivan un lector pasado.
- `ayuda`, `salir`. Toda entrada fuera de esta gramática se rechaza explícitamente.

Durante `lenguaje`, use el orden finito del protocolo. No se despejan puertos ni se reinician clocks para aceptar una orden. Una consulta puede consumir o transformar su soporte.

## Reproducción dirigida y verificación

Después de instalar el motor con el lanzador:

```powershell
.\.venv\Scripts\python.exe -I -B .\ejecutar.py identidad
.\.venv\Scripts\python.exe -I -B .\ejecutar.py verificar
.\.venv\Scripts\python.exe -I -B .\ejecutar.py reproducir --tipo red-v3 --caso .\resultados\red\confirmacion03\casos\FULL_U.json --salida .\repro_red
.\.venv\Scripts\python.exe -I -B .\ejecutar.py reproducir --tipo regulacion --caso .\resultados\regulacion\DUAL_CONFIRMATION\AB_AB\CONFIG.json --salida .\repro_retencion
```

Cada salida nueva debe tener un nombre libre. `red-v3` reproduce el testigo de comunicación, no el hábitat dual posterior. Las recetas, configs y runners específicos de los otros contrastes están indexados en `CAPACIDADES.json` y `resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json`; sus métricas no son intercambiables.

La prueba nueva principal del regulador también puede reproducirse directamente, sin abrir el modo interactivo:

```powershell
.\.venv\Scripts\python.exe -I -B .\src\red\regulated_habitat.py --case .\resultados\red\fixed_counterflow01\casos\FILTER_FLAT.json --output .\repro_regulada
.\.venv\Scripts\python.exe -I -B .\src\red\regulated_curriculum.py --parent .\repro_regulada\T437.deetsnap --output .\repro_regulada_continuacion
```

Los helpers son componentes del mismo ejecutor y usan la instalación4.0 incluida. `src/red/LEEME_RED.md` distingue sus configs y formatos de sesión. El snapshot937 conservó RAW/clocks, recibos y progreso después de restaurar; guardar no reinstala una historia.

`ejecutar.py reproducir --tipo acceso-heredado --caso CONFIG --id ID --salida DIR` continúa una frontera histórica real con el nuevo protocolo temporal. El config se localiza en `resultados/continuidad` mediante el índice. `ejecutar.py estado` describe estados guardados y tareas abiertas. `confirmar-regulacion` verifica y salta los casos completos, sin reiniciar el presupuesto histórico ni sobrescribirlos.

Las reproducciones futuras son operaciones explícitas del usuario: no hay trabajo indefinido en segundo plano. La campaña original conserva un único presupuesto monotónico de14400s; los comandos interactivos futuros tienen su propio timeout, no fingen continuar ese presupuesto vencido.

## Encontrar evidencia

`INFORME.md` expone mecanismos, resultados y límites concretos. `CAPACIDADES.json` enlaza cada objetivo; `RETENCION.json` separa memoria y expresión. `NSM65_EVOLUCION.json` remite a la matriz completa sin duplicarla. `MENSAJES.jsonl` indexa recorridos certificados y límites de atribución. `DIALOGOS.jsonl` remite a sesiones realmente ejecutadas. `checkpoints/INDEX.json` identifica fronteras sin duplicar los snapshots.

Los informes históricos mantienen su alcance anterior. `PARENT_MEMBERS.json` contiene las1289 identidades heredadas; `MANIFEST.json` y `HASHES.sha256` cubren esta ampliación. El índice y manifiesto nuevos en la raíz del ZIP añaden navegación sin reescribir los antiguos. El SHA del ZIP final se comunica fuera del archivo.

Modalidades de salida: ENTE = registro o emisión física; INSTRUMENTO = preparación, sensor, medición o sonda externa; INTERPRETACIÓN = inferencia causal posterior del auditor. Los modelos del auditor, si los hay, no escriben una política o significado resuelto en MAIN.
