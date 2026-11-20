# Integración mínima APD03 — propuesta para revisión Root

No se han editado `sistema/` ni el gestor. Estos archivos LAB son candidatos, no capacidades ya incorporadas o adquiridas por MAIN.

## Archivos nuevos propuestos en sistema

| Archivo LAB | Destino propuesto |
|---|---|
| `operativo/asistente_apd03.py` | `capacidades/asistente_apd03.py` |
| `operativo/entorno_compartido_apd03.py` | `capacidades/entorno_compartido_apd03.py` |
| `operativo/protocolo_apd03.py` | `app/protocolo_apd03.py` |
| `lexico_generico_apd03_r02.py` | `capacidades/lexico_generico_apd03_r02.py` |
| `mecanismo/sensor_balanceado_apd03_r02.py` | `capacidades/sensor_balanceado_apd03_r02.py` |

El entorno operativo sólo cambia la resolución de la Base APD02: usa `capacidades.entorno_objetivo_apd02`, no `vendor/` ni una ruta LAB. La semántica de consecuencia es idéntica al wrapper prospectivo a0cdef9346bbc684d188800b2a018127a188340ddc036dd921735b7ce32cc79f. La modalidad se fija una vez al admitir y se conserva en cada estado ambiental.

## Despacho MU.session

Antes de la rama `mode.startswith('apd02')`, añadir una rama `mode.startswith('apd03')`:

```python
from capacidades import asistente_apd03 as apd03
if mode == 'apd03-admitir':
    r = apd03.admit(a, consequence_mode=s.get('consecuencia','local_useful'))
elif mode == 'apd03-docencia':
    r = apd03.teach(a,s['texto'],s['senal'],revision=s.get('revision',False))
elif mode == 'apd03-panel':
    r = apd03.panel(a,new_forms=s.get('nuevas',False),
        memories=s.get('memorias',False),detailed=detailed)
elif mode == 'apd03-lenguaje':
    r = apd03.language(a,s['texto'],s['valor'],s['contexto'],detailed=detailed)
elif mode == 'apd03-tarea-iniciar':
    r = apd03.start_task(a,s['texto'],s['operandos'],s['segundo_visible'],
        Path(directory)/('apd03_goal_'+str(m['episodes']+1)),
        context=s.get('contexto_ambiente',0))
elif mode == 'apd03-paso':
    r = apd03.step(a,s['oportunidades'],
        Path(directory)/('apd03_step_'+str(m['episodes']+1)),
        feedback=feedback,detailed=detailed)
else:
    raise ValueError('Unknown declared APD03 mode')
m = get(a)
```

Rechazar `actuator != 'closed'` para estas operaciones hasta disponer de un contrato específico de acción anulada. No ignorar silenciosamente ese parámetro. `retorno='omit'` sí es una modalidad explícita del mecanismo y del control.

## Testigos de estado y errores

En `MU.state`, si existe `apd03.KEY`, añadir `result['assistant_autonomy'] = apd03.state(a)`. Ese estado público no contiene el segundo operando oculto.

En `MU.additional_operational_state`, añadir el estado ambiental completo de APD03 y `external_uncertain` cuando exista su KEY. Es una dependencia operativa opaca para guardar/continuar, no una memoria a consultar para resolver tareas. El hook `MU.external_uncertainty` debe incorporar este campo.

## Preflight de servicio y cola

1. En `app/cola_local.validate`, antes de APD02, reconocer el prefijo literal APD03 y llamar a `app.protocolo_apd03.validate_literal(row)` sin normalización semántica.
2. En `NativeWorld.validate`, reconocer APD03 y llamar a `asistente_apd03.validate(self.a,row)`. Las seis operaciones se expondrán como solicitudes separadas, no mezcladas con una evaluación material. La docencia nunca se oculta dentro de una tarea. Un panel admite hasta22interacciones internas (old14+new2+MA6) en una sola solicitud, sin ampliar el límite de situaciones del transporte; devuelve materia/recibos, no PASS.
3. En la clasificación `work` del `except BaseException` del servicio, incluir `apd03-tarea-iniciar` y `apd03-paso`; ambos pueden crear archivos operativos. Ante error se conserva el futuro y se marca incertidumbre, sin reintentar ni rebobinar. La admisión/docencia/lenguaje sólo mutan materia; siguen el guardado normal del futuro fallido.
4. Mantener el transporte, SQLite, outbox, deduplicación por ID y epoch existentes. No nueva cola ni plataforma.

## Contrato de asistencia y seguridad

La iniciativa de ofrecer oportunidades sigue en el operador. El sensor transmite `int(second is None)` del hecho actualmente público, nunca el contenido privado. La salida nativa original −1→ACT y 0/+1→QUERY se conserva. Sólo ACT con operandos ya observados y operación emitida puede llamar una vez a la aritmética Native; no hay callback externo/fallback. El evaluador y el archivo son preparados.

Un estado ambiental pendiente no se reemplaza; uno incierto no se reintenta. El método `step` restaura el estado ambiental completo en un directorio nuevo del mismo individuo y conserva hechos, contador y bytes de archivos previos; no restaura ni prepara un mundo DEE nuevo. La metadata de APD03 contiene contadores, configuración P0 y estado ambiental, no firmas aprendidas ni bancos correctos.

## Pruebas afectadas propuestas

N0: equivalencia de ambos entornos, validación literal, rechazo de targets/campos extra, estados pendientes/inciertos y serialización. Native, sólo tras GO: admitir una vez, enseñar un signo nuevo, uso, tarea con dato oculto, oportunidad, guardar/reabrir la misma vida con el dato ya observado, otra oportunidad y archivo. Panel breve anterior y conservación de originales. No repetir suites históricas.

La versión operativaR02 usa únicamente la geometríaK=(47,7,47) para los dos slots nuevos; H=(47,17,47) de compara/recuerda queda intacto. La propuestaR01 de Hcompartido fue rechazada por preflight en un auxiliar y no se incorpora a MAIN. Fuentes y futuro rechazados permanecen en sus expedientes.
