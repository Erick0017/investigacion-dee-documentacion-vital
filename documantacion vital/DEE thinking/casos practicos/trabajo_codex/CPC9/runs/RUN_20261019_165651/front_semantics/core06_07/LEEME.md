# Recuperación CORE06/CORE07 desde el contenido deduplicado

El trabajador `worker_recover.py` no consulta ZIP históricos. Recibe una carpeta
materializada y verifica la fuente exacta antes de ejecutarla. Necesita CPython
3.13 x64, DEE thinking 4.5.0 oficial y, **sólo para estas dos familias**, NumPy
2.2.6 como dependencia externa declarada (`--numpy-root`). No instala ni modifica
NumPy ni el producto. La verificación de procedencia registra sus rutas y hashes.

La lógica científica de los dos runners y los helpers se carga byte por byte.
Únicamente se sustituye la carga del binario histórico por un adaptador de
transiciones que utiliza `Runtime.import_research_state` y `advance` LAZY del
producto oficial. Los runners originales disponían de arrays RAW/clocks
directamente escribibles: no tenían la cola de entradas de una sesión thinking.
Por eso esta recuperación **no** acredita compatibilidad de colas históricas.

El adaptador mantiene el Runtime entre pasos sin escrituras externas. Cuando el
runner introduce un portador por puerto vacío o aplica una intervención
diagnóstica explícita, importa exactamente el estado continuado, conservando
tick y clocks. No restaura un estado favorable ni modifica una respuesta. Es un
portado técnico del contrato de arrays, no un nuevo individuo MAIN de CPC9.

Atribución: la transición y los encuentros pertenecen al motor nativo; la
preparación, admisión de portadores con clocks históricos y daños de control son
intervenciones instrumentales explícitas; la comparación con referencias es del
auditor y se realiza después. La importación fiel de estado es una adaptación
técnica declarada, no se anuncia como una nueva API ordinaria de enseñanza ni
como iniciativa o política adquirida.

Los resultados de referencia sólo se leen después de completar la evolución.
Se comparan literalmente registros físicos locales, condiciones, controles y
resúmenes. Los originales no conservan hashes de cada estado global final: no se
afirma igualdad global histórica cuando falta ese dato. La nueva ejecución sí
conserva el estado inicial disperso, hashes completos finales y cada escritura
externa. Los clocks de sitios vacíos también evolucionan: expandirlos como
diccionarios no es compresión dispersa. El primer exportador lo intentó y falló
por memoria después de cinco trayectorias completas; se conserva el código V1,
sus lecturas y el log. La corrección no cambia la física. El estado completo se
regenera mediante las mismas entradas y su hash permite comprobarlo. Enteros
RAW/clocks exportados se representan mediante cadenas decimales exactas.

CORE06 cubre transferencia a 25 direcciones no utilizadas para enseñar, extinción
de un canal, reversión y readquisición mediante entradas ordinarias, con controles
de exposición, orden y ausencia. CORE07 repite su reserva congelada de 4
geometrías/tamaños y 12 consultas: programación aditiva externa de una relación
adquirida, redirección y controles de daño/reparación limitada. Una programación
positiva no se denomina política reguladora autónoma. Las intervenciones de daño
pertenecen a controles diagnósticos, no a una operación MAIN autorreparada.

Una repetición determinista acredita recuperación técnica, no una nueva muestra
independiente ni una reserva CPC9 inédita.

Ejemplo (rutas proporcionadas por el lanzador limpio):

```text
python -I -B worker_recover.py --materialized RECUPERADO --out NUEVA_SALIDA --numpy-root NUMPY_SITE_PACKAGES --family core06
python -I -B worker_recover.py --materialized RECUPERADO --out OTRA_SALIDA --numpy-root NUMPY_SITE_PACKAGES --family core07
```

Cada salida nueva contiene `IDENTITY.json`, `OBSERVED.json`,
`PRIMARY_TRANSITIONS.json` y `RECOVERY.json`. Un corte inconcluso o un error
conserva su salida parcial y el log supervisado; no se convierte en un éxito.
