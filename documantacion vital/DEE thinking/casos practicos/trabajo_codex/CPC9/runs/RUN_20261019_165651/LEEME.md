# CPC9 — ejecución privada y reproducción

Windows x64 y CPython3.13 x64 son requisitos externos. Se incluye el WHL oficial
4.5.0, comprobado por SHA256. No se necesita Internet, un ZIP histórico, un LLM
ni una ruta privada para ejecutar las nuevas preparaciones CPC9.

Desde una extracción nueva:

```powershell
py -3.13 tools/preparar_entorno.py
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py demo --out runs/mi_demo
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py demo --control-no-order-a --out runs/control
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py eventos --events app/ejemplo_eventos.json --out runs/eventos
.\.runtime_cpc9\Scripts\python.exe -I -B ejecutar.py interactivo --out runs/interactivo
```

La demo normal/control llega a T606. La interfaz acepta comandos JSON
estructurados, no conversación libre. Crear, presentar, avanzar, observar,
guardar/cargar e interrogar puertos ejecuta física nueva; `evidencia` es lectura
del AUDITOR y nunca memoria del ente. Se muestran rechazos, ausencia y ambigüedad.
`app/LEEME.md` documenta la gramática, ventanas, recursos y etiquetas.

El lanzador `iniciar_cpc9.ps1` tiene sintaxis validada, pero la política local
de Windows bloqueó su ejecución en este equipo. No se modificó seguridad.
La vía Python anterior fue ejecutada y verificada y no requiere habilitar PS1.
La persistencia nativa usa un temporal ASCII; `--ascii-temp` permite indicarlo.

## Revisión reproducible

Los cálculos son herramientas del auditor, no parte del participante:

```powershell
py -3.13 tools/recalcular_cpc9.py --out runs/recalculo.json
py -3.13 tools/indexar_evidencia.py --out runs/indice.json
py -3.13 tools/reconciliar_e1.py --out runs/cadena_e1.json
```

No introducen sus resultados en el Runtime. Usan enteros exactos y localizadores
de los primarios. Una copia técnica idéntica verifica reproducción, no añade
una réplica científica independiente. Las decisiones NSM fueron adjudicadas
manualmente con sus dominios; no se generan desde un único PASS.

La verificación limpia del ZIP exacto utiliza `tools/verify_cpc9_clean.py`:

```powershell
py -3.13 tools/verify_cpc9_clean.py --zip RUTA_ZIP --work CARPETA_ASCII_NUEVA --out COMPROBANTE_FUERA_ZIP.json --budget-seconds 1800 --memory-mib 512
```

El verificador crea un entorno aislado, instala el WHL local, ejecuta referencias,
controles, continuidad y recálculos y comprueba miembros sellados. Su presupuesto
es nuevo y explícito al invocarlo usted, no una reanudación automática de esta
campaña. La auditoría de accesos cubre las operaciones Python declaradas, no
promete interceptar todos los syscalls C++/OS. Las rutas de carga nativas son
explícitas y están dentro de la extracción/área limpia.

`tools/supervisor.py` conserva el presupuesto original de investigación y no es
el punto de entrada futuro. Los `src/lote_*.py` son orquestaciones históricas de
esa campaña; sus trabajadores individuales y las pruebas limpias se ofrecen
para nuevas invocaciones autorizadas. No reinicie silenciosamente su deadline.

## Capas y dependencias

`src/` y los módulos de los frentes contienen participantes y currículos.
`base_validada/cpc8/src/` conserva el mínimo heredado con hashes; no importa
código desde carpetas CPC antiguas. `resultados/` y los resultados de frentes
contienen datos primarios, snapshots y controles; no son una tabla de respuestas
del participante. `revision/` interpreta y calcula. `runtime/` guarda una sola
copia del instrumento. `DEPENDENCIAS.json` separa lo incluido de lo externo.

El paquete maestro Cognitive Core es independiente y acompañante: contiene la
recuperación histórica completa localizada y sus contratos comprobados. No es
necesario para la vida nueva. La prueba desde cero sólo autoriza declararlo
sustituto operativo de los contratos que realmente pasaron, no de todo compendio
histórico ni de una mente integrada universal.
