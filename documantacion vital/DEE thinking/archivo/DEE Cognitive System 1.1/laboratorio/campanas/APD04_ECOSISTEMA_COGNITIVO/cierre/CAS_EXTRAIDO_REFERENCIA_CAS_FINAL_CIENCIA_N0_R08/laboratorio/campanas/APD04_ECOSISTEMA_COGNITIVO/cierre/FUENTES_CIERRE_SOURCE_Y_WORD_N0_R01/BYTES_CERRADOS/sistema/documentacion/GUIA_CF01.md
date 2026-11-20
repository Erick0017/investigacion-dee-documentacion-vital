# Servicio contextual CF01: uso y continuación

Cognitive1.1.0 utiliza thinking4.5.0 con Universev27 sin cambios. CF01.R9.protocol.4 añade un servicio acotado al mismo gestor, no otro motor. El Manual Maestro1.9 es una edición documental distinta.

## Tres pasos en la distribución

1. Extraiga `cognitive_sistem_colaborador.zip` en una ruta local de Windowsx64. Lea `LEER_PRIMERO.md`. El lanzador utiliza el CPython3.13 incluido y el WHL oficial. Universe ya está integrado, no se instala como segundo motor. La primera preparación puede extraer localmente el WHL. Si Windows indica que falta VisualC++, use el redistribuible Microsoft incluido según la guía.
2. Desde esa carpeta ejecute `INICIAR.bat servicio-cf01 MI_PRIMER_CF01 --mediciones=20:28,7:13,9:18`. Se importa el alias `CF01_OPERATIVO` como una vida personal nueva desde su snapshot completo; no consume la vida distribuida. Un nombre existente requiere continuación explícita, no recreación silenciosa.
3. Cierre el proceso y continúe con `INICIAR.bat servicio-cf01 MI_PRIMER_CF01 --continuar --mediciones=18:25,6:14`. Sus snapshots y operaciones quedan en `trabajo_personal/estado/`. No los borra una actualización normal.

Estas mediciones son ejemplos de entradas nuevas dentro del contrato, no respuestas precargadas. Cada par contiene dos observaciones enteras crudas0..64; cada llamada admite1..32situaciones. La dirección y la acción proceden de DEE. El mundo tiene una ley fija de puertas: izquierda cuando `izquierda + calibración >= derecha`; derecha en otro caso. Su calibración no se entrega como respuesta a A. Las consecuencias de la acción real vuelven mediante el aparato material preparado.

## Vidas y estado real

| Vida original / alias distribuido | Corte | Uso acreditado |
|---|---:|---|
| CF01_MAIN / CF01_OPERATIVO | T67723 | Futuro real final: propia175/171, contextos7/5, B61/19, mundo calibrado8. Última secuencia4/5; el primer error enseñó delta3→4. |
| CF01_CALIBRACION7 / CF01_CALIBRACION7 | T63813 | Bifurcación anterior al cambio del mundo: propia165/162, contextos7/5, B61/19, calibración7. No es una reparación posterior. |
| CF01_PLANTILLA_R9 / CF01_PLANTILLA_R9 | T44263 | Pasado anterior al nuevo dato de B: propia116/113, contexto0/5. Útil para contrastar adquisición social; no posee por etiqueta el nuevo contexto7. |

El protegido `E1_SOCIAL_11` permanece en T3154. CF01 desciende de MI02_SOCIAL_REUSABLE_240 T15329: otra biografía R9, no E1 renombrado. No se fusionan recuerdos entre alias, controles o plantillas.

## Desde el gestor original

Use el intérprete compatible instalado y el lanzador existente. Argumentos reales:

```text
gestionar.py cf01-estado --vida CF01_MAIN
gestionar.py bifurcar CF01_MAIN MI_CF01
gestionar.py cf01-servicio --vida MI_CF01 --mediciones=20:28,7:13,9:18
gestionar.py guardar --vida MI_CF01
# cerrar el proceso; la siguiente ejecución carga el snapshot completo
gestionar.py cf01-servicio --vida MI_CF01 --mediciones=18:25,6:14
```

`cf01-estado` es observación externa pasiva, cero ticks. Una experiencia o servicio sí añade materia y ticks, puede enseñar y perjudicar accesos: use una copia. Cada comando mutante guarda mediante Store el mundo completo, interfaces, entradas pendientes, progreso y estado externo. Un fallo de restauración no autoriza crear un individuo vacío.

`cf01-servicio` sin `--referencia-entorno` conserva la calibración guardada:8 en MAIN final,7 en su plantilla. Para cambiar deliberadamente la ley use, por ejemplo, `--referencia-entorno 9 --reiniciar-entorno`. Es un reset externo explícito registrado; no borra ni rebobina DEE. No cambie la ley durante una reserva para favorecer una respuesta.

`cf01-contexto --vida COPIA --valor 52` presenta una observación privada cruda a B por interfaz y fase fijadas. En el pasado ensayado, B compara con61/19 y su mensaje añade contexto izquierdo7 conservando el derecho5. No garantiza actualización arbitraria en cualquier futuro. Otros valores o fases pueden rechazarse, no transportar o producir otra transformación. No reintente en una fase favorable después de mirar el resultado.

`cf01-tarea` conserva la tarea antigua de oportunidades±1 y su lector de una sola muestra. `cf01-episodio` y `cf01-pulso` son protocolos finitos de experiencia/diagnóstico, no selección autónoma de lector. Los controles `--actuador nulled` y `--retorno omit_return` difieren: el primero cancela sólo la acción externa ya formada; el segundo omite el retorno nativo.

## Qué observar y atribuir

La salida separa testigos RAW/clocks exactos, entradas y recibos, comando nativo, comando ejecutado, consecuencia y estado ambiental. Una petición aplicada no garantiza percepción útil. Conserve rechazos, pendientes, silencio y conflicto; no reemplace una ausencia por una acción inteligente.

El lector usa los mismos contactos motores en dos ticks fijos y puede retener la salida exactamente un tick: instrumentoP0, no recuperación aprendida. En reservas18/18 hubo9 muestras actuales y9 retenidas; el panel antiguo de una muestra permanece1/4 y no se recalificó. x0 es simultáneamente izquierda por defecto y corriente de consulta, no elección exclusiva aprendida entre actuar y preguntar.

Las consecuencias modificaron una relación propia y mejoraron acciones nuevas en un cambio de calibración. También hubo una experiencia perjudicial y readquisición durante evaluación. No se garantiza estabilidad ilimitada, política general, R2, lenguaje adquirido ni65significados. Pendulum y otros perfiles mantienen sus contratos, no se suman a esta vida.

El campo histórico `service.revision` puede indicar protocol.1: no reescribe los episodios anteriores. `protocol_code_revision` identifica el código4 actual. Los contadores históricos mezclan protocolos y no son la tasa del lector nuevo ni decisiones exclusivas de preguntar.

## Fuentes y actualización

La distribución incluye primarios y recálculo CF01 en `investigacion/CF01_CIERRE_FUNCIONAL/`. Recalcular archivos no ejecuta DEE; reproducir física requiere motor y snapshots completos. Las fuentes del producto están en `fuentes/` y las de Cognitive en `sistema/`.

En la computadora fuente, después de cerrar una campaña y guardar sus estados, ejecute `ACTUALIZAR.bat` con selección y comprobante de cierre según `actualizaciones/`. `CREAR_ZIP.bat` regenera la copia local sin repetir física. No hay sincronización remota: envíe el nuevo ZIP o delta declarado. No sobrescriba trabajo personal ni memorias para insertar conocimientos.
