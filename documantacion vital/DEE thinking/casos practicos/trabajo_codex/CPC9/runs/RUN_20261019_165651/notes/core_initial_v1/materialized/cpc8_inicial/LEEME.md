# CPC8 — ejecución privada

Requiere Windowsx64, CPython3.13x64 y espacio para una extracción independiente. Se utilizó4.5.0/v27 oficial; no hay que compilar el motor. El entorno se instala offline en una ruta temporal corta y no se incluye en el ZIP.

Desde PowerShell:

```powershell
.\iniciar_cpc8.ps1
.\iniciar_cpc8.ps1 -Modo eventos -Archivo configuraciones/demo/vida_integrada.json
```

Si `python` en PATH no es CPython3.13x64, añada `-Python313 'RUTA\python.exe'`. El lanzador verifica WHL, extensión importada y versión; no instala otra versión de Python ni modifica productos existentes.

La gramática es estructurada, no conversación libre. Ejemplos interactivos: `crear social`, `orden BA`, `experiencia L17 1 0`, `avanzar 5`, `consecuencia 1`, `observar`, `guardar mi_estado.deetsnap.gz`, `cargar mi_estado.deetsnap.gz`, `ayuda`. Para el recorrido completo use el archivo de eventos: dar sólo esas líneas de ejemplo no prepara todo el ensayo.

El recorrido `vida_integrada.json` enseña32correspondencias, utilizaL17 mediante una pregunta física, enseña al receptorB, añade33experiencias, vuelve a usarB, revisaL01 mediante un protocolo docente explícito y vuelve a comprobar accesos. `vida_control.json` desplaza sólo la señal deL17: mismos recursos y dosis. Los rechazos e indeterminaciones se muestran, no se sustituyen por cero.

`configuraciones/demo/reservada.json` y `desacoplada.json` recorren la variante de signo local, separada del receptor social porque enseñar aquel signo consume el mismo producto. No concatenar ambos archivos como si sus preparaciones fuesen un solo individuo.

Con el Python del entorno aislado, también puede ejecutar:

```powershell
python -I -B ejecutar.py verificar-datos
python -I -B ejecutar.py referencias --salida MIS_REFERENCIAS_NUEVAS
python -I -B ejecutar.py regresion --salida MI_REGRESION_NUEVA
python -I -B ejecutar.py eventos configuraciones/demo/vida_integrada.json --salida MI_SESION.jsonl
```

Las salidas y snapshots existentes se protegen contra sobrescritura. `referencias` vuelve a ejecutar código seleccionado original deCP01/CP02/SEM01 sobre4.5; `regresion` ejecuta82pruebas del producto. Son reproducciones técnicas, no nuevas réplicas independientes.

La geometría y las ventanas pertenecen a cada receta. El demostrador limita sus operaciones a un horizonte finito; esto no restringe el Runtime directo del instrumento. No se cambiaN durante una vida, no se limpian celdas ni se reinician clocks.

Empiece la revisión científica en `LEER_PRIMERO.md`, `revision/LECTURA_PROVISIONAL.md` y `revision/INDICE_EVIDENCIA.json`. Las fórmulas se recalculan sin motor; la reproducción física requiere el WHL incluido. El comprobante del ZIP exacto y, cuando procedan, las dos partes binarias se entregan fuera del contenedor.

El recorrido principal no incorpora todos los experimentos semánticos. Los dos aparatos separados se encuentran en `src/relaciones/temporal_roles.py` y `contact_consequence.py`, con ejecutores por caso y configuraciones congeladas en `configuraciones/semantica/`. Sus resultados y límites están en `revision/NSM65_EVIDENCIAS.json`. No se suman como significados de E1.
