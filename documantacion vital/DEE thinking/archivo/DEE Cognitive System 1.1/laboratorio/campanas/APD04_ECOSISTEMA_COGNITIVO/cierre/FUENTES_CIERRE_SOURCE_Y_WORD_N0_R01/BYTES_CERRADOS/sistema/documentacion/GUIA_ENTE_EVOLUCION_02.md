# ENTE02: entradas propias y continuidad
Use CPython3.13 x64 y el motor oficial ya instalado. No hace falta volver a ejecutar las familias históricas. Desde sistema, los comandos son del gestor existente.

## Continuación compatible de EO01
~~~powershell
python -I -B gestionar.py bifurcar EO02_MAIN MI_EVOLUCION
python -I -B gestionar.py evolucion-estado --vida MI_EVOLUCION
python -I -B gestionar.py evolucion-servicio --vida MI_EVOLUCION --dominio trabajadores --observaciones '[[8,22,4,4],[9,22,4,4]]' --referencia-entorno 14 --reiniciar-entorno
python -I -B gestionar.py guardar --vida MI_EVOLUCION
~~~

Cada número llega por una entrada física fija; el anfitrión no envía su suma. El programa declara aciertos, errores, rechazo y silencio sin rellenarlos. Un nuevo uso puede enseñar y cambiar la referencia. --reiniciar-entorno reinicia sólo el fixture externo, nunca la materia DEE ni su pasado.

C2 permite una señal genérica de fase preparada:
~~~powershell
python -I -B gestionar.py evolucion-servicio --vida MI_EVOLUCION --dominio transaccion --observaciones '[[10,24]]' --referencia-entorno 14 --reiniciar-entorno --fase-visible
python -I -B gestionar.py evolucion-servicio --vida MI_EVOLUCION --dominio transaccion --observaciones '[[13,27]]' --referencia-entorno 14 --fase-visible
~~~
La segunda llamada continúa el mismo mundo. Si hubo preparación aceptada, lee el archivo anterior. El snapshot contiene los bytes ambientales indispensables para restaurar ese archivo en una copia, no la respuesta a emitir. No promete resolver todas las relaciones opuestas ni aprender cuándo cambiar de lector.

## Alternativa R10, otra vida nueva
~~~powershell
python -I -B gestionar.py bifurcar EO02_SENSORIAL_R10_T0 MI_SENSORIAL
python -I -B gestionar.py evolucion-sensorial-estado --vida MI_SENSORIAL
python -I -B gestionar.py evolucion-sensorial --vida MI_SENSORIAL --dominio trabajadores --observaciones '[[2,4,3,5,4,4,5,5],[3,5,4,6,5,6,6,6]]' --referencia-entorno 4 --reiniciar-entorno
python -I -B gestionar.py guardar --vida MI_SENSORIAL
~~~
R10 recibe8 componentes0..32. El rango aceptado no garantiza exactitud funcional en todos sus microestados. No es una ampliación de recuerdos de EO01. Se comprobó serial16 como dos tramas8 y dos actos. Los intentos32 fallaron en auxiliares R9; serial32 en R10 no se ejecutó. No se demuestra una decisión conjunta16/32. La elección de tarea y vida es explícita y del operador.

## Asistencia y archivos
A/B de servicios comparten una relación comparativa: transferencia isomorfa, no lenguaje general. Los trabajadores realizan compresión/SHA256 reales con una ley de admisión modelada. Los resultados y estados de entorno quedan en estado/servicios_locales y en snapshots completos. No modifique RAW, clocks ni copias históricas para corregir respuestas.

Cree copias con nombres nuevos. No abra el mismo mundo durante un commit de otro proceso. Si aparece INCOMPLETE_COMMIT, espere a que termine el propietario y consulte el estado; no cambie el puntero a un snapshot antiguo. El guardado y la siguiente llamada son operaciones distintas; no reinicializan la vida.

En cognitive sistem puede usar INICIAR.bat evolucion NOMBRE --observaciones "[[...]]" --dominio trabajadores y --continuar para la misma copia; --sensorial elige explícitamente R10. El lanzador conserva trabajo_personal.

