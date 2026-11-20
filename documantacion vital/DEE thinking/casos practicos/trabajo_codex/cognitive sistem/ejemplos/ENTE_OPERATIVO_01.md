# Usar y continuar una copia del ente EO01

El alias `ENTE_OPERATIVO` identifica un snapshot completo seleccionado al cierre. Su ficha en `entes/CATALOGO.json` declara vida, padre, tick, funciones actuales y límites. El alias no fusiona E1 con CF01 ni importa experiencias de ramas de control.

## Recorrido único

Desde la carpeta extraída completa:

```bat
INICIAR.bat catalogo
INICIAR.bat ente MI_ENTE_01 --mediciones=2:14,8:21,12:23
INICIAR.bat gestor ente-estado --vida MI_ENTE_01
INICIAR.bat gestor guardar --vida MI_ENTE_01
```

El primer uso importa explícitamente el estado completo bajo una identidad personal nueva y delega en `gestionar.py ente-servicio`. Los pares son dos mediciones públicas RAW en el dominio del contrato, no direcciones de actuación ni correcciones de memoria. El lanzador no calcula su comparación.

Después de cerrar ese proceso:

```bat
INICIAR.bat ente MI_ENTE_01 --continuar --mediciones=6:18,10:23
INICIAR.bat gestor bifurcar MI_ENTE_01 MI_ENTE_COMPARACION
INICIAR.bat gestor ente-estado --vida MI_ENTE_COMPARACION
```

`--continuar` carga esa misma vida: si no existe se informa el error, sin reconstruirla desde T0. Sin `--continuar`, un nombre ya existente se conserva y el comando se detiene. Los cambios quedan en `trabajo_personal/estado/`, incluyendo el snapshot completo y el estado operacional del entorno; una actualización normal no sobrescribe esa carpeta.

## Entorno, retorno y asistencia

EO01 distingue comando material emitido, acción realmente ejecutada y resultado observado posteriormente. El retorno táctil del modo `real` procede del contacto externo ya ocurrido y de la postura del actuador; no se suministra el antiguo primer recurso de contacto anticipado de CF01. Los recursos posteriores y el lector de dos instantes son preparación declarada, no autonomía adquirida por nombre.

Sin `--referencia-entorno` se conserva la calibración ambiental guardada. Un cambio deliberado requiere, por ejemplo, `--referencia-entorno 9 --reiniciar-entorno`: reinicia sólo el entorno, nunca la memoria DEE. No utilice cambios de calibración o fase para rescatar retrospectivamente una evaluación.

Los controles `--actuador nulled`, `--retorno omit` o `--retorno decoupled` se ejecutan sobre una copia identificada. No son resultados de aprendizaje por sí solos. Los recursos de soporte, la iniciativa del usuario al ofrecer oportunidades y la transducción fija conservan su atribución al aparato.

`gestor ente-social --vida COPIA --valor N` presenta una experiencia privada a B por la interfaz del contrato. No garantiza que cualquier dato nuevo actualice contexto ni que B conserve todos sus accesos: consulte el panel actual de esa vida. Un mensaje transportado no acredita negociación ni lenguaje general.

La revisión de válvula social añade un camino **externo preparado P0**, distinto de actualizar directamente el contexto nativo7/5. Sus flags se delegan sin política al mismo gestor:

```bat
INICIAR.bat ente MI_ENTE_01 --continuar --mediciones=4:14 --privada-B 52 --valvula-social
```

El valor RAW es privado para B. La oportunidad material de la válvula es genérica, tiene un vencimiento fijo y no se selecciona por conocer la respuesta que conviene. Un paquete de B puede accionar la válvula del entorno, cuyo cambio posterior puede producir un contacto real para A. La habilitación se conserva en el estado ambiental; no es una orden para que A consulte o recupere en cada paso.

`--actuador-B nulled` y `--corte-mensaje minus_bus|plus_bus` son controles en copias; un corte rechazado no cuenta como corte realizado. Esta interfaz no acredita por sí sola renovación autónoma del lector, negociación ni que el contexto nativo7/5 haya adquirido otro valor. La ficha final y los primarios distinguen lo observado de esos pendientes.

## Trabajos pendientes y usos repetidos

El mismo gestor ofrece una FIFO externa, sin otro cuerpo ni controlador. Sobre una copia:

```bat
INICIAR.bat gestor ente-tarea --vida MI_ENTE_COMPARACION --trabajos=3:15,4:17 --pasos 12 --referencia-entorno 12 --reiniciar-entorno
INICIAR.bat gestor guardar --vida MI_ENTE_COMPARACION
INICIAR.bat gestor ente-tarea --vida MI_ENTE_COMPARACION --pasos 4
```

El primer comando declara una nueva cola y un cambio ambiental explícito; no reinicia DEE. Después, omitir `--trabajos` y `--reiniciar-entorno` continúa la cola y calibración guardadas. El mismo trabajo queda pendiente hasta que la acción **ejecutada** lo completa, o termina el máximo de intentos fijado con `--pasos` (1..32). No se elige una salida correcta desde Python.

Esas oportunidades repetidas son calendario del entorno, **no iniciativa aprendida de reintentar**. El resultado informa trabajos completados, intentos y aciertos al primer intento por separado: completar después de un contacto y otro intento no equivale a acertar de entrada. `ente --mediciones` sigue ofreciendo cada par una sola vez; no se mezclan sus denominadores con los de la FIFO. El retorno procede del mismo core de contacto real, y `--retorno omit` es un control explícito sobre otra copia.

Los resultados acreditados, denominadores, fallos y corte final están en la guía vigente y `investigacion/ENTE_DEE_OPERATIVO_01/`. Los ejemplos anteriores son entradas modificables dentro del dominio, no promesas de acierto ni una lista de respuestas precargadas. `servicio-cf01` permanece disponible como capacidad comparativa distinta, con su retorno antiguo y su propia historia.
