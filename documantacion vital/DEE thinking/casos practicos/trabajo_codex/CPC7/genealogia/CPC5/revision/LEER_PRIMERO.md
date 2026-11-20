# CPC5: leer primero

Este directorio permite revisar las observaciones y los cálculos sin instalar el
motor ni reproducir primero todas las trayectorias. Contiene 101 registros
primarios `MEASUREMENTS.json` indexados; no equivalen a 101 réplicas independientes.

1. [LECTURA_PROVISIONAL.md](LECTURA_PROVISIONAL.md): mecanismo, evidencia,
   contraejemplos y alcance de la interpretación de este corte.
2. [INDICE_EVIDENCIA.json](INDICE_EVIDENCIA.json): inventario reconciliado, tipo de
   trayectoria, archivo primario, SHA-256 y tick final. Conserva los intentos técnicos.
3. [OBSERVACIONES.jsonl](OBSERVACIONES.jsonl): selección compacta de lecturas físicas
   originales. Cada fila conserva archivo y puntero JSON. RAW y clocks de 64 bits no
   se convierten a float. La selección no sustituye las vecindades completas del origen.
4. [CALCULOS.json](CALCULOS.json): cálculos por caso, fórmulas y denominadores.
5. [COMPARACION_ARQUITECTURAS.json](COMPARACION_ARQUITECTURAS.json): recursos,
   componentes, consultas, latencias y productos por ruta; no un ranking universal.
6. [RETENCION_Y_ACCESO.json](RETENCION_Y_ACCESO.json): panel longitudinal de cada
   individuo. Separa disponibilidad, admisión, expresión y uso.
7. [NSM65_EVIDENCIAS.json](NSM65_EVIDENCIAS.json): catálogo heredado y estado de las
   pruebas nuevas. Ocho señales físicas no se convierten por conteo en ocho conceptos.

Las rutas de evidencia son relativas a la raíz CPC5 extraída. Los `MEASUREMENTS`
contienen llamadas, recibos, RAW desempaquetado, clocks exactos, ventanas, capturas
y referencias a snapshots. Las configuraciones y fuentes exactas están junto al
caso o en `configuraciones/` y `src/`; los casos conservados no se sobrescriben.

Para recalcular esta revisión sin ejecutar física:

```powershell
python src/audit.py --root .
```

Para ejecutar y usar el demostrador consulte `../LEEME.md`. El auditor no es una
parte del ente: sus métricas se calculan después y no retroalimentan MAIN.

## Unidades y separación de planos

Un tick es evolución DEE; un segundo es tiempo de ordenador. Una consulta es una
interacción, a veces consumible; una preparación, una continuación y un fork se
cuentan por separado. Los ticks sucesivos de un mundo determinista no son nuevas
réplicas. `null`, rechazo, cero físico, silencio y error conservan valores distintos.

Datos: registros físicos exactos. Cálculos: fórmulas repetibles sobre esos registros.
Lectura provisional: explicación revisable de Codex, con alternativas y dominio.
No se emite un dictamen automático sobre mente, inteligencia ni límites universales.
