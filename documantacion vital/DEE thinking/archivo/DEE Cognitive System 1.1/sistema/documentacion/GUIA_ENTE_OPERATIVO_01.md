# Ente operativo EO01: uso acotado y continuidad

Esta aplicación utiliza una vida real de R9, derivada por bifurcación completa de CF01_MAIN T67723. No reconstruye desde T0 ni renombra al E1 histórico. La vida seleccionable EO01_MAIN quedó en T121681; el predeterminado E1_SOCIAL_11 T3154 sigue protegido.

## Comenzar en la distribución para colaboradores

Desde la carpeta cognitive sistem:

~~~bat
INICIAR.bat ente MI_ENTE --mediciones=23:35,11:24
INICIAR.bat ente MI_ENTE --continuar --mediciones=6:18,10:23
~~~

La primera operación crea explícitamente una copia de ENTE_OPERATIVO. La segunda continúa esa copia; no crea otro universo ni restaura el pasado. Los nombres son identidades del usuario, no respuestas. El lanzador guarda el trabajo del colaborador en trabajo_personal.

Cada par son dos observaciones escalares crudas, no las palabras “izquierda/derecha” ni una orden correcta. La calibración del mundo guardado es 12. El contenido actual de A es referencia propia304/296, contexto7/5; B conserva61/19. Es una relación numérica funcional interpretada por el auditor, no comprensión de la palabra «doce».

## Mismo gestor, sin lanzador

Con CPython3.13 x64 y el motor oficial ya disponible, desde sistema:

~~~powershell
python -I -B gestionar.py bifurcar EO01_MAIN MI_ENTE
python -I -B gestionar.py ente-estado --vida MI_ENTE
python -I -B gestionar.py ente-servicio --vida MI_ENTE --mediciones=23:35,11:24
python -I -B gestionar.py guardar --vida MI_ENTE
python -I -B gestionar.py ente-servicio --vida MI_ENTE --mediciones=6:18,10:23
~~~

Use el intérprete compatible declarado por su instalación, no otro Python que encuentre por nombre. No es necesario reinstalar el sistema original. El estado completo contiene materia, clocks, interfaces, agenda, recibos, progreso y mundo externo; un resumen RAW no lo sustituye.

## Dos modalidades distintas

ente-servicio presenta una oportunidad por par y avanza aunque ese trabajo falle. Informa silencio, conflicto y acciones incorrectas; no los rellena con respuestas.

ente-tarea ofrece una FIFO: un trabajo pendiente se repite por una regla ambiental fija hasta que la acción efectivamente ejecutada lo completa. Esto no acredita iniciativa nativa de reintentar. Ejemplo sobre una copia propia:

~~~bat
INICIAR.bat gestor ente-tarea --vida MI_ENTE --trabajos=3:15,4:17,6:17,9:23,12:24,16:31 --pasos12 --referencia-entorno12 --reiniciar-entorno
INICIAR.bat gestor ente-tarea --vida MI_ENTE --pasos4
~~~

--reiniciar-entorno crea otra cola/fixture externos, nunca reinicia DEE. Sólo se necesita al declarar deliberadamente una cola nueva. No usarlo para ocultar un futuro adverso. La cola completada y el historial de intentos fallidos son campos diferentes: backlog no es el contador de trabajos pendientes.

## Retorno de consecuencias

La salida de A se lee en dos muestras fijas, con retención instrumental máxima de un tick. El comando se ejecuta antes de observar el resultado. Sólo un contacto realmente producido genera el pulso táctil posterior; no se programa el retorno j0 antiguo. Todos los cambios de los soportes adquiridos proceden de encuentros v27.

Los recursos y calendarios preparados no se denominan aprendizaje ni autorrenovación. El operador ofrece situaciones, pero no necesita indicar qué acción es correcta o elegir un lector según el acierto.

## B e interacción ambiental opcional

Una observación privada puede entregarse a B durante la oportunidad:

~~~bat
INICIAR.bat ente MI_ENTE --continuar --mediciones=10:22 --privada-B=50 --valvula-social
~~~

No garantiza activar su lector: debe alcanzarlo la petición material nativa. El ejemplo ilustra la interfaz; no promete un acierto en todo estado posterior.

La válvula es un instrumento EXTERNO P0. Una vez habilitada en el fixture, el lector fijo de los buses en crítico+30 traduce un único paquete de carga5 y dirección horizontal a un paso mecánico ±1 de calibración. Cada solicitud privada aporta una sola oportunidad mecánica, independiente del valor, la admisión y el resultado; expira en su ventana. Sin ese recurso puede existir comando de B y no ejecutarse movimiento.

A sólo aprende del contacto real de sus acciones posteriores. No se copia el dato privado de B ni se calcula una corrección de A desde Python. Esto no reparó la actualización directa de los contextos nativos7/5, que continúa sin demostrarse. Tampoco demuestra negociación, consulta exclusiva aprendida o comunicación cerrada puramente v27.

El último fixture FIFO está sin válvula habilitada; puede instalarse explícitamente mediante --valvula-social. Otro reset externo crea otro fixture: declare otra vez el equipo opcional que desea instalar. No es un cambio de memoria DEE.

## Controles y límites

--actuador=nulled anula A después de emitir; --retorno=omit omite la transducción; --retorno=decoupled desacopla la postura táctil. --actuador-B=nulled y --corte-mensaje son controles, no reparaciones. Ejecútelos en bifurcaciones identificadas. Un corte rechazado no cuenta como ablación.

Se conservaron reservas originales5/8,6/8,5/8 y otras sociales4/6 cada una; no se sustituyeron por el resultado de cola6/6 en8intentos. No se acredita control general, estabilidad ilimitada, NSM65 o lenguaje humano. Una experiencia nueva puede modificar la referencia y perjudicar un uso anterior.

EO01_CORTE_R02 conserva el corte previo a la válvula en T95093. Sus conocimientos y los de controles no se fusionan con MAIN. El Manual1.10 y CONTINUIDAD_ENTE_DEE_OPERATIVO_01.json localizan el corte, asistencia y evidencia.
