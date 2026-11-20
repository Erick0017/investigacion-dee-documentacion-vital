# Ejecutar SEM01

Esta sección amplía CPC3 con DEE thinking4.0.0/v27. Requiere Windows x64,
CPython3.13 estándar x64 y el runtime C++ que utiliza el WHL oficial. No requiere
internet, LLM, scripts CPC3 anteriores ni instalar dee_universe_v27.

Desde PowerShell en esta carpeta, usando un CPython3.13 disponible:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -I -m pip install --no-index --no-deps .\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe -I -B .\demostracion.py --eventos .\configuraciones\DEMO_A.txt --directorio .\sesiones\A_nueva
.\.venv\Scripts\python.exe -I -B .\demostracion.py --eventos .\configuraciones\DEMO_B.txt --directorio .\sesiones\B_nueva
.\.venv\Scripts\python.exe -I -B .\demostracion.py --eventos .\configuraciones\DEMO_A_CON_REVISION.txt --directorio .\sesiones\A_revision
.\.venv\Scripts\python.exe -I -B .\demostracion.py --directorio .\sesiones\interactiva
```

Utilizar directorios nuevos: no se sobrescriben snapshots previos. Las entradas
enseña/termina enseñanza controlan un generador de experiencias externo, no
una tabla que resuelva las consultas. La respuesta lee RAW actual. Consulte
[README_GRAMATICA.md](README_GRAMATICA.md) y
[GUIA_DEMOSTRACION.md](GUIA_DEMOSTRACION.md) para la gramática y sus límites.

## Reproducir una trayectoria completa

Este comando **crea, enseña, evoluciona y usa** una preparación; no carga una
respuesta terminal. El resultado debe ir a una carpeta inexistente.

```powershell
.\.venv\Scripts\python.exe -I -B .\ejecutar.py --child .\configuraciones\casos\A_future_UV.json --output .\sesiones\reproduccion_A --wheel .\runtime\dee_thinking-4.0.0-cp313-cp313-win_amd64.whl
.\.venv\Scripts\python.exe -I -B .\demostracion.py --cargar .\sesiones\A_nueva\EMISION1.deetsnap --directorio .\sesiones\continuacion
```

Después de cargar esa emisión: `revelar U`, `señal pako`, `revelar V`. No vuelve
a enseñar ni reconstruye el individuo. Los archivos completos de evidencia ya
están en resultados; reproducirlos no añade muestras independientes.

`ejecutar.py --freeze` comprueba los hashes congelados. `--run --python <python>`
es la cola histórica reanudable: verifica y omite lo ya terminado. Conserva el
deadline original y no inicia nuevos trabajos fuera del presupuesto. Para uso
posterior utilice `--child` o el demostrador, ambos con límites finitos explícitos;
no altere BUDGET para fingir una continuación de la campaña original.

## Localizar la evidencia

- `resultados/CONFIRMATORY_SUMMARY.json`:14 casos y sus28 puestos de consulta.
- `resultados/confirmacion/<ID>/`:configuración, experiencias, predicciones,
  recibos, usos y snapshots completos. No se duplican en una carpeta checkpoints.
- `resultados/causal_memory02/`:lesión selectiva, sham, desafío directo y reservas.
- `resultados/reversal01/` y `reversal02_phase/`:cinco continuaciones del mismo
  padre usado, fuentes exactas por fase y límites de atribución.
- `resultados/repertorio4/`:cuatro señales, asignaciones no globalmente inversas,
  control desacoplado, reserva y restauración.
- `resultados/technical_checks01/`:observación pasiva, backends, cola pendiente
  y ventanas de la cadena causal.
- `resultados/demostracion_*/`:sesiones reales del UI; los tests UI conservan
  también intentos técnicos anteriores y correcciones.
- `resultados/UI_REVISION_QUALIFICATION/`:revisión finita desde el mismo MAIN129,
  equivalencia física con la extensión y consulta posterior sin mapa en otro proceso.
- `resultados/reproduccion_limpia/`:instalación desde extracción candidata,
  nueva trayectoria y nueva consulta tras restauración.
- `PREDICCIONES.jsonl`, `EXPERIENCIAS.jsonl`, `DIALOGOS.jsonl`:índices agregados
  con rutas de origen; no son nuevas ejecuciones ni evidencia duplicada independiente.
- `fuentes/`:selección pasiva de fuentes y procedencia, sin ejecutar campañas antiguas.

## Verificar el contenedor acumulativo

El manifiesto/HASHES de esta sección tienen alcance local. Los de la raíz CPC3
son históricos y se preservaron. Para comprobar publicación y1563 miembros
anteriores se necesita la copia sellada del padre, que no se anida en el ZIP:

```powershell
python -I -B .\src\verify_append.py --parent <CPC3_padre_sellado.zip> --candidate <CPC3_actualizado.zip> --parent-sha256 75ab357f41f6214c1798efbf69bd0708ab891038d30d770fdfe4a379208f793e
```

`src/package_append.py` sólo permite publicar el nombre oficial con
`--publish-atomic`. No vuelva a anexar SEM01 sobre un padre que ya la contiene.
Reempaquetar utiliza el corte sellado y el padre anterior, no repite experimentos.

El hash final del ZIP se informa fuera del contenedor para evitar circularidad.
Los hashes de fuente y del instrumento sí se conservan dentro. Las rutas privadas
en los logs son procedencia histórica; los comandos públicos usan rutas relativas.
