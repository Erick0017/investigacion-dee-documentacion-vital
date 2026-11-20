# Revisión finita de acceso a fuentes, derivada de R14

La regla del controlador está preparada: conservar P si su informe coincide
con una consecuencia real y cambiar a Q si discrepa. No se aprendió esa regla
general, no se descubrió por sí sola la fiabilidad de una fuente arbitraria y
no se demostró una segunda reversión Q→P sobre el mismo individuo.

Sí se ejecutó físicamente esta cadena sobre un único Runtime nuevo N67:

```
política inicial P → acción1 → informe de P2
→ comparación con consecuencia real6 → política P/Q10
→ nueva acción11 → información de la fuente seleccionada14
```

Los normalizadores espaciales de las cuatro ramas alcanzables, las consultas
simétricas y los datos de P/Q se preparan antes deT0. La consecuencia actual se
codifica en2 por dos vías fijas; representan una observación duplicada, no dos
experiencias independientes. El host no lee la expectativa, no calcula el
error y no escoge P o Q. Los reductores y las trayectorias v27 producen la
comparación, el estado de política y la acción posterior.

## Mediciones

Cuatro tratamientos discovery cubren ambos signos y roles intercambiados:
cuando P coincide con la clase real, la acción posterior usa P; cuando P no
coincide y Q sí, usa Q. Las dos realizaciones reservadas, congeladas antes de
ejecutarlas, reproducen una situación de cada tipo. En los seis mundos llega
después un informe nativo concordante con la clase real.

Retirar exactamente la primera acción ya emitida en1, en una rama diagnóstica,
elimina los productos admisibles de política/acción/información. Omitir la
consecuencia real produce el mismo corte funcional. No se cuentan consultas
preparadas ni cada tick como una réplica independiente.

Esta realización restringe Q al complemento de P y la condición ambiental
permanece estable durante el episodio. Saber qué hacer tras una discrepancia
lo aporta la geometría diseñada; la experiencia selecciona físicamente el
estado pertinente de esa regla. Los datos no acreditan exploración óptima,
utilidad arbitraria, recursos infinitos ni integración con el MAIN basal1000.

El análisis externo compara las mismas situaciones: fuentes P y Q fijas
coinciden en2/4 discovery y1/2 reservas cada una; el controlador nativo obtiene
4/4 y2/2 respectivamente. Una regla convencional comparar-y-cambiar también
resuelve los seis. No se afirma una ventaja de rendimiento frente a esa regla.
La alternancia ilustrativa usa el orden del catálogo congelado, no un orden
alfabético seleccionado por el analizador; la primera lectura equivocada de
ese orden se conserva en `RESULTADOS_ANALYSIS_ATTEMPT1.json`.

## API y conversación

`core.policy_session.FinitePolicySession` instala este individuo finito distinto.
No cambia el perfil de continuidad ni el perfil de comparación central.

```python
from core.policy_session import FinitePolicySession
s = FinitePolicySession.create()  # política P; entorno inicial Q informativa
s.sense()                        # acontecimiento externo actual2, aplicado3
s.compare()                      # producto de comparación actual6
chosen = s.source()               # acción física actual11, no consulta de roles
received = s.sense()              # informe físico actual14
s.save('politica.deetsnap')
restored = FinitePolicySession.load('politica.deetsnap')
restored.observe()                # lectura actual, no una tabla de resultados
```

`source()` fuera de11 no devuelve una elección desde el historial. El perfil
rechaza preguntas de pronóstico o experiencias arbitrarias no implementadas.
Guardar conserva Runtime, tick, canales, recibos, cola pendiente y progreso del
protocolo; cargar no prepara otra vez la materia. La normalización de tuples a
listas JSON es exclusivamente metadata de interfaz; el intento técnico inicial
con esa diferencia de tipo está conservado y la corrección no cambia RAW/clocks.

## Fuente y verificación

Se recuperaron tres archivos concretos de I01 con sus hashes de manifiesto,
sin importar ni ejecutar sus campañas. La primera referencia R14 normalizó
estados positivos de fuentes a1, manteniendo posiciones/direcciones. La prueba
posterior `TECHNICAL_CHECKS.json` utiliza los campos originales1001…1005,
clocks0 y política clock11. No se anuncia identidad RAW de la primera referencia.

Los controles técnicos verifican lectura pasiva, primer acto igual antes de la
experiencia diferencial, forks de auditoría aislados, snapshot con inputs aún
pendientes y equivalencia Dense/Lazy/Parallel. `session/VALIDATION.json` añade
persistencia de sesión, consulta actual y ausencia de respuesta ficticia fuera
de ventana. Son comprobaciones técnicas, no nuevas capacidades independientes.

Para reproducir una reserva por evolución nueva, desde cualquier carpeta:

```
python -I -B CPC3/experimentos/seleccion_revisable/reproduce.py --package-root CPC3 --case R_TRANSLATED_BAD --output SALIDA_NUEVA
```

La referencia guardada sólo se abre después de terminar la nueva evolución.
Se comparan trazas y RAW/clocks completos, no se usa un snapshot terminal como
respuesta. No escriba la reproducción encima de la evidencia original.
