# Utilizar y continuar las capacidades MI02

El motor sigue siendo DEE thinking 4.5.0 y v27. Se usa el gestor existente. No reinstale el entorno ni cree otra vida cuando quiera continuar una ya aprendida.

El predeterminado protegido permanece en `E1_SOCIAL_11`, T3154. MAIN de investigación es `D1_MI02_MAIN`, T81207, arquitectura R6. La alternativa R9 tiene `MI02_SOCIAL_REUSABLE_240`, T15329, y su continuación operativa `MI02_R9_OPERATIVA47`, T20021. No son la misma biografía ni una promoción del activo.

La [ficha vigente](CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json) contiene rutas, hashes y colas. El [Manual Maestro 1.8](MANUAL_MAESTRO_1_8_MI02_SIN_VALIDACION_VISUAL.docx) fue actualizado realmente, sin validación visual: el renderizador no encontró `soffice.exe`.

## Iniciar desde lo que existe

Desde la raíz de Cognitive System 1.1, en PowerShell:

```powershell
$deePy = (Get-Content -LiteralPath '.\CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json' -Raw | ConvertFrom-Json).python
& $deePy '.\sistema\gestionar.py' mi02-estado --vida MI02_SOCIAL_REUSABLE_240
& $deePy '.\sistema\gestionar.py' bifurcar MI02_SOCIAL_REUSABLE_240 MI02_MI_CONTINUACION
& $deePy '.\sistema\gestionar.py' mi02-vivir --vida MI02_MI_CONTINUACION --condiciones=1,1,-1,-1
& $deePy '.\sistema\gestionar.py' guardar --vida MI02_MI_CONTINUACION
& $deePy '.\sistema\gestionar.py' mi02-estado --vida MI02_MI_CONTINUACION
```

Use un nombre nuevo para la bifurcación; uno existente no se sobrescribe. Cada oportunidad ofrece una condición ambiental, no una acción calculada para el participante. `1` significa que está disponible la alternativa izquierda y `-1` la derecha. Los contactos, retornos y solicitudes se producen dentro del mundo. La regla ambiental y sus suministros siguen preparados.

`mi02-vivir` ejecuta oportunidades con el estado real de la vida: no escoge un checkpoint o un especialista distinto según la respuesta correcta. La asistencia del operador al cambiar de bloque o de entorno no se cuenta como iniciativa nativa.

## Qué puede utilizarse y dónde

| Perfil o vida | Función comprobada | Límite importante |
|---|---|---|
| `MI02_CONTROLADOR_90` | Selección local modificada por consecuencias, uso repetido | Preparación N17 y fase declaradas; no regulación general |
| `E1_MI02_HEREDADA_R8` | Ese mecanismo en una región añadida a un pasado MI01 real | No se acreditó uso del conocimiento antiguo por la región nueva |
| `D1_MI02_MAIN` y sus ramas R6 | Historia local, solicitud nativa, información privada y uso externo en la misma trayectoria | Fallos de acceso, asistencia P0 y pérdida de discriminación de señales al revisar la actuación |
| `MI02_SOCIAL_REUSABLE_240` y `MI02_R9_OPERATIVA47` | Solicitud nativa, respuesta privada, liberación y reutilización del lector | Primer contexto persistente; sin actualización arbitraria de mensajes |
| `MI02_EFIMERO_210/212/213` | Lectura relativa reutilizable, con campos adquiridos conservados | Perfil auxiliar, sonda iniciada por operador; no habilidad de MAIN |

Los contratos están en `contratos/MI02_*.json`. R7 y R8 sociales conservan sus fracasos como variantes experimentales; su existencia en el código no acredita liberación del lector ni superioridad frente a R6.

## Crear una preparación nueva no es recuperar una vida

```powershell
& $deePy '.\sistema\gestionar.py' mi02-crear --vida MI02_MI_VIDA_NUEVA --variante unificada-r9
& $deePy '.\sistema\gestionar.py' mi02-adquirir --vida MI02_MI_VIDA_NUEVA --propias 13,13 --privadas 91,29
& $deePy '.\sistema\gestionar.py' mi02-vivir --vida MI02_MI_VIDA_NUEVA --condiciones=-1,-1,-1
```

La primera llamada guarda anatomía T0 sin contenido entrenado. La segunda presenta experiencias crudas, no resultados correctos. La tercera utiliza esa nueva historia. Este recorrido se comprobó mediante el constructor normal y coincidió físicamente con su referencia técnica; no se cuenta como aprendizaje de E1 ni como otra réplica independiente.

## Puente externo

```powershell
& $deePy '.\sistema\gestionar.py' mi02-externo --vida MI02_R9_OPERATIVA47 --pasos 1
& $deePy '.\sistema\gestionar.py' guardar --vida MI02_R9_OPERATIVA47
```

Continúa el episodio externo persistido y el mismo estado DEE. El límite del episodio es200pasos. Cuando sea necesario, `--reiniciar-entorno --semilla NUMERO` inicia explícitamente otro episodio, no otro DEE. No se reinicia automáticamente para mejorar el resultado.

El codec fijo usa seno/coseno y descarta velocidad angular; una dirección calificada produce torque firmado, y una salida inválida produce el cero obligatorio del puente. No hay control competente aprendido ni política externa que lo sustituya. Cambiar de entorno es decisión del operador. R9 se probó con16pasos entre procesos y volvió a utilizar la tarea nativa; no se promete estabilidad ilimitada.

## Lectura auxiliar

```powershell
& $deePy '.\sistema\gestionar.py' bifurcar MI02_EFIMERO_210 MI02_MI_LECTURA
& $deePy '.\sistema\gestionar.py' mi02-comparar-efimero --vida MI02_MI_LECTURA --objetos 22,24,26,None
```

El `0` nativo de balance es una respuesta válida, distinta de `None`. Una lectura indeterminada o un dato ausente no se traduce como negación. Existe un sesgo preparado y un cono de salida limitado. No es comparación imparcial ni adquisición NSM. El anfitrión no calcula qué clase emitir; presenta el dato actual y una sonda genérica. El lector se libera por evolución nativa, sin limpieza.

## Recuperación asistida y señales

`mi02-recurso-fase --vida UNA_BIFURCACION_R6 --modo treatment` aplica el procedimiento genérico del contrato de fase. Es P0 iniciado por operador; no se usa indiscriminadamente ni se ofrece como reparación universal. R9 no se acepta silenciosamente como si fuera el mismo dominio.

`mi02-orden --vida UNA_BIFURCACION_R6 izquierda derecha` sólo transporta dos señales fijas y muestra una emisión física nueva. El control desacoplado impide acreditar significados específicos aprendidos. `mi02-ensenar` presenta lecciones explícitas; no se debe usar para aparentar retención. No hay lenguaje libre.

## Integridad y privacidad

La operación normal no importa laboratorio, evidencia o entregas ni consulta targets históricos para responder. Guardar y cargar conserva el mundo, interfaces, pendientes y puente. Una sonda material puede modificar la vida; use copias de evaluación si necesita protegerla.

Los snapshots completos y el estado operativo permanecen localmente. El ZIP de análisis no incluye el motor, toda la instalación ni todos los checkpoints. No es un respaldo completo. Los cortes microscópicos capturados dentro de un protocolo son diagnósticos, no puntos de continuidad automática.
