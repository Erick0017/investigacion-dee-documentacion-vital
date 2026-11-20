# Informe técnico de validación — Entrega 01

## Estado de este registro

Este informe separa aceptación técnica de interpretación científica. No emite
un juicio sobre consciencia, autonomía indefinida ni universalidad de DEE.

## Plataforma y compilación

- Windows 10 x64.
- Visual Studio 2022 Community 17.14.25.
- MSVC 19.44.35222.0, toolset 14.44.35207.
- Windows SDK 10.0.26100.0.
- CMake 4.2.3-msvc3 y Ninja 1.12.1.
- Configuración Release, C++20, biblioteca estática `dee_thinking.lib`.
- Compilación final del árbol de trabajo: código de salida 0.

La primera invocación del generador multi-configuración desde un PowerShell sin
entorno de desarrollo no encontró el compilador. No era un fallo del source. Se
congeló `tools/build_windows.cmd`, que inicializa explícitamente el entorno x64
de VS 2022 y ejecuta CMake/Ninja. Ese camino compiló biblioteca, tests, demo y
consumidor.

## Identidad del kernel y del oráculo

- Source canónico ejecutado: SHA-256
  `44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab`.
- WHL oficial: SHA-256
  `69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939`.
- Binario `.pyd`: SHA-256
  `0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff`.
- Paquete `__init__.py`: SHA-256
  `7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4`.

`src/kernel_v27.cpp` fue extraído mecánicamente del source por hash. Se retiró
la frontera pybind y se añadió una frontera C++ de vectores; constantes, tablas,
transición, DEMUX y copy-back permanecen en el orden canónico.

## Comparación diferencial contra el WHL

`tools/generate_whl_fixtures.py` cargó el `.pyd` oficial después de verificar
los tres hashes. Los datos esperados no fueron generados por la biblioteca nueva.
Diez fixtures compararon RAW y clock completos, bit a bit, durante uno o varios
ticks:

1. vacío durante tres ticks;
2. transporte con wrapping toroidal;
3. registro RAW no nulo con `state=0`;
4. semántica 4 y overflow modular del clock;
5. destino ocupado;
6. integración simultánea XNOR de ocho propuestas;
7. integración simultánea no-XNOR;
8. composición direccional por etapas;
9. clocks no uniformes y direcciones límite `[-8,7]`;
10. overflow material con DEMUX alcanzable.

Resultado observado: `WHL_DIFFERENTIAL_CASES=10 ALL_EXACT=true`.
Este dominio finito no constituye una prueba universal de equivalencia.

## Suite ejecutada

CTest ejecutó cinco targets, todos con código 0:

| Target | Resultado | Tiempo observado |
|---|---:|---:|
| `kernel_whl_differential` | aprobado | 0.07 s |
| `runtime_contract` | 84 comprobaciones, 0 fallos | 0.14 s |
| `reference_organizations` | 44 comprobaciones, 0 fallos | 132.75 s |
| `independent_consumer_e2e` | aprobado | 1.56 s |
| `examples_smoke` | aprobado | 0.07 s |

Resultado CTest: 5/5, 100 %, 0 fallos; tiempo total 134.62 s. La salida
literal está en `ctest_release.log`.

La suite del runtime cubre fronteras temporales, `advance(0)`, ejecución por
bloques, pausa, observación pasiva, admisión diferida, clock preservado,
conflictos, lote atómico, tardíos, probe, `state=0`, forks, mundos aislados,
snapshot con evento pendiente, igualdad del futuro restaurado y fallo
transaccional ante corrupción.

Los ejemplos E1–E4 cubren transporte/carga cero/destino ocupado; C6H01 de
reprogramación con teacher y control; HA/HB/H0 a edad común; y la cadena
multicanal AB/ABC con corte causal. Sus salidas funcionales coinciden con las
referencias históricas declaradas.

## Consumidor independiente y ausencia de Python

El consumidor incluye sólo headers públicos y enlaza `dee_thinking.lib`.
Ejecutó crear → experiencia → evolución → observación → pausa → snapshot →
restore → fork → continuación, además del control sin teacher. Resultado:

- respuesta entrenada: `state=1, s_reg=23, dir=(-1,1,0)`;
- control distinto;
- continuación fork/restaurada exacta en RAW y clock;
- código de salida 0.

`dumpbin /DEPENDENTS` sólo mostró runtime de MSVC/UCRT y `KERNEL32.dll`; no
aparece Python ni el `.pyd`.

## Defectos/correcciones durante el ciclo

- Se corrigió una expectativa de prueba: un registro direccional con `state=0`
  no está ocupado en t0, pero sigue siendo causal y produce un destino ocupado
  en t1. La prueba ahora verifica esa transición en vez de tratarlo como inerte.
- Se reforzó el lector de snapshots contra underflow de cursor, enums inválidos,
  eventos pendientes tardíos, fronteras incoherentes, coordenadas fuera de
  rango y payloads incompletos.
- Se fijó el ejemplo E2 a la geometría/agenda CORE06 C6H01 F0_T0 en vez de un
  sustituto aproximado.
- No se relajó ninguna comparación exacta y no se deshabilitó ningún test.

## Límites y pendientes no bloqueantes de Entrega 01

- Sólo se probó Windows x64/MSVC; no se afirma ABI o portabilidad no medida.
- El kernel nativo entregado es el camino denso determinista de un hilo; no se
  afirma aceleración respecto del WHL lazy/paralelo.
- Los ejemplos contienen geometría, suministro y recursos preparados y tienen
  el alcance finito de sus campañas de origen.
- Gestión prolongada de capacidad, catálogo ampliado y adaptadores pertenecen a
  Entregas 02/03 y no se exportan como funciones ficticias.
- La regeneración de fixtures requiere externamente CPython 3.13, NumPy y el WHL;
  el uso nativo no.

La reconstrucción y ejecución desde una extracción limpia del ZIP se registra
por separado en `VALIDATION_STATUS.json` antes del empaquetado final.
