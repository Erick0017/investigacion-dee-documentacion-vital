# Red nativa ABCD — uso y reproducción

Instrumento: WHL oficial DEE thinking 4.0.0, kernel v27. No se modifica el producto.
Estas clases son herramientas experimentales, no una nueva versión de la biblioteca.

La API operativa de la preparación V3 es `red.session_v3.NetworkSession`:

```python
from red.session_v3 import NetworkSession
s = NetworkSession.create({"roles": True, "A_history": 1, "B_history": 1,
                           "C_history": -1, "D_history": 1, "event": "U"})
s.run_until(161)          # Tick absoluto; observa el estado actual.
s.save("estado161.deetsnap")
t = NetworkSession.load("estado161.deetsnap")
t.run_until(431)          # Continúa RAW, clocks, cola, recibos y puertos.
print(t.observe())        # Lectura pasiva, no respuesta de una tabla.
```

`create` prepara una sola vez y programa un protocolo externo finito en la cola
nativa. No contiene memoria aprendida en RAW inicial: los acontecimientos se
aplican en sus tiempos efectivos y sus recibos deben comprobarse. Los metadatos
conservan condiciones externas y progreso, no respuestas esperadas ni utilidad.

Para la continuación posterior, sin cargar/recrear otra organización:

```python
from red.curriculum_v3 import continue_session
t, episodios = continue_session(t, "continuacion_nueva")  # 431 -> 1431
```

El currículo presenta nuevas experiencias sintéticas mediante los mismos puertos.
No borra portadores anteriores, no cambia clocks, no repara admisiones rechazadas
y no mezcla un fork de regreso a MAIN. Puede mostrar readquisición en una región
cuyo portador anterior se consumió; no se presume sobreescritura de ese portador.

Reproducción de un caso, desde la carpeta de la ampliación y con el CPython3.13 que
tenga instalado el WHL oficial incluido por el expediente:

```powershell
& RUTA_PYTHON -I -B src/red/run_roles_v3.py --case resultados/red/confirmacion03/casos/FULL_U.json --output reproduccion_red_nueva
& RUTA_PYTHON -I -B src/red/curriculum_v3.py --parent reproduccion_red_nueva/T431.deetsnap --output reproduccion_curriculo_nueva
```

Usar siempre una salida nueva. Los supervisores de campaña son
`src/supervision.py` y conservan el presupuesto original de la ampliación; el
reproductor posterior no declara que una trayectoria repetida sea otra réplica
científica independiente.

Las versiones no se intercambian silenciosamente:

- `session.py`: V2; dos consultas +Z. Sus controles unpaired conservan utilidad.
- `session_v3.py`: V3; panel físico alternante +X / -X para D. El contexto C
  opuesto conserva otra vía útil de B en el banco original. No se borra ese dato.
- `selective_session.py`: pregunta nueva con consulta de B -Z y otro banco
  preparado físicamente. No corrige las métricas ni los archivos de V3.
- `dual_session.py`: dos bancos físicos distintos. La calibración vacía muestra
  que ninguna de las cuatro políticas fijas ensayadas es la mejor en todos los
  contextos. La red integrada original conserva el banco N pero falla en Flat:
  un relay no consumido vuelve después de dos vueltas y desvía la respuesta.
- `regulated_session.py`: otra preparación versionada con un contraflujo físico
  fijo de carga cero. Su encuentro nativo cancela la dirección del relay residual
  y éste desaparece por la rama material sin vecinos. No es regulación aprendida
  ni una eliminación desde Python. None y sham conservan la interferencia Flat.

La consulta -Z es un contexto solicitado por el experimentador, no una decisión
de atención aprendida. En el banco +Z de V3, el contexto C opuesto puede conservar
otra función útil de B; el contexto -Z distingue esa alternativa de la trayectoria
que incorpora D. La igualdad de una puntuación no equivale a igualdad de memoria.

Los resultados anteriores permanecen intactos. El diagnóstico
`residual425_diagnostic01` es una excepción explícita: un replay intacto reproduce
el checkpoint canónico y un **fork diagnóstico** retira exactamente un RAW, sin
editar clocks. El rescate sólo establece suficiencia/efecto condicionado en ese
fondo; nunca se incorpora a MAIN ni se presenta como reparación autónoma.

Para reproducir los contextos nuevos sin cargar resultados terminales como
respuesta:

```powershell
& RUTA_PYTHON -I -B src/red/run_selective.py --case resultados/red/selective_negative01/casos/FULL.json --output reproduccion_selectiva_nueva
& RUTA_PYTHON -I -B src/red/dual_habitat.py --case resultados/red/dual_habitat01/casos/A_PLUS_C_PLUS_FLAT.json --output reproduccion_dual_nueva
& RUTA_PYTHON -I -B src/red/regulated_habitat.py --case resultados/red/fixed_counterflow01/casos/FILTER_FLAT.json --output reproduccion_contraflujo_nueva
& RUTA_PYTHON -I -B src/red/regulated_curriculum.py --parent reproduccion_contraflujo_nueva/T437.deetsnap --output reproduccion_continuacion_contraflujo_nueva
```

El último recorrido restaura el estado operativo completo una vez y continúa
437→937, con una segunda experiencia externa C- y los mismos puertos. No vuelve
a crear el individuo entre ambas experiencias. Los snapshots conservan RAW,
clocks, tick, cola, recibos y metadatos de ambos protocolos; los perfiles de
sesión no se sustituyen silenciosamente al cargar.

El primer resultado central, sus controles y las fuentes ejecutadas exactas están
en sus respectivas carpetas de resultados. `NETWORK_MEASUREMENTS_SUMMARY.json`
resume sólo la red; las pruebas de lenguaje y observación se cuentan aparte.

Alcance: cuatro regiones funcionales móviles finitas, no cuatro cuerpos basales
plenamente renovables. La topología y el relay se prepararon; las relaciones y los
productos se adquieren por encuentros nativos. Las sondas cambian el estado. La
utilidad `2*F+R` es evaluación externa y nunca un reward enviado a DEE.
