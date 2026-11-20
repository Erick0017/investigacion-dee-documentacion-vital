# Demostración SEM01

Esta aplicación experimental utiliza el WHL inmutable DEE thinking4.0.0 y v27.
No es una nueva versión del producto. Se conservan dos relaciones móviles en
un Runtime N67 y dos ocasiones de consulta físicas; no ofrece conversación
ilimitada, vocabulario humano adquirido ni una inversión automática de historia.

## Ejecutar

Instalar el WHL incluido en `runtime/` en CPython3.13 x64 de Windows. Desde la
raíz de esta sección, con ese Python:

```
python -I -B demostracion.py
python -I -B demostracion.py --eventos configuraciones/DEMO_A.txt --directorio sesiones/A
python -I -B demostracion.py --eventos configuraciones/DEMO_B.txt --directorio sesiones/B
python -I -B demostracion.py --cargar sesiones/A/EMISION1.deetsnap --directorio sesiones/reanudada
```

Si el controlador usa otro Python, indicar `--python` con el ejecutable aislado
que tenga instalado el WHL4 oficial. No se ejecutan scripts históricos ni se
importan laboratorios CPC3 anteriores para responder. La aplicación sí reutiliza
los helpers SEM01 exactos incluidos aquí, identificados por su configuración.

## Gramática real

- `crear` crea explícitamente un individuo vacío con los puertos ya declarados.
- `crear reservada` inicia otro individuo: traslación(9,-4,7), carga7 y orden S2,S1.
- `enseña zuvi U` y `enseña pako V` seleccionan experiencias en un generador externo.
- `termina enseñanza` ejecuta ambas; el sensor externo de efecto actual transmite
  la misma clase física a ambas regiones. La coincidencia local escribe la
  relación. Después se elimina el mapa del controlador operativo de consultas.
- `señal zuvi` o `señal S1` introduce sólo esa señal por su puerto fijo. Se avanza
  hasta la emisión actual y se lee RAW/dirección. No se presenta el evento futuro.
- `revelar U` introduce ahora el acontecimiento físico, posterior a la emisión;
  avanza y muestra entregas reales de función y recurso, más evaluación externa.
- `observa` lee pasivamente el presente; no reproduce una contestación guardada.
- `nombre S1 bruma` modifica sólo la etiqueta externa del puerto, no la asociación.
- `guardar "archivo.deetsnap"` conserva el snapshot operativo completo. Rutas
  relativas se resuelven dentro del directorio de sesión. No sobrescribe archivos.
- `cargar "archivo.deetsnap"` valida y restaura sin crear ni enseñar otra vez.
- `ayuda` enumera el dominio; `salir` termina. Otras órdenes se rechazan explícitamente.

Principal: enseñanza17/45, señal84/112, emisión87/115, lectura física101/129.
El orden de señales es S1,S2; la reservada invierte ese orden y mantiene las
mismas fases físicas. No se recolocan sensores ni se reinician clocks. Una
consulta transforma la continuidad y no puede repetirse indefinidamente.

## Separaciones y persistencia

`INTERFAZ` indica traducción textual/validación; `GENERADOR EXTERNO`, selección
de experiencias; `ENTE`, emisión física nativa actual admitida; `INSTRUMENTO`,
observación o evaluación realizada fuera. U/V son nombres de efectos físicos:
la ausencia de entrega la clasifica un transductor externo fijo, no un detector
nativo de ausencia. La acción útil protege la ruta y tiene coste físico sobre
un recurso opcional; la utilidad externa nunca actualiza la memoria.

El mapa elegido y la transcripción de enseñanza pueden conservarse como
evidencia externa, pero no son entradas del proceso de consulta. Este proceso
recibe un único snapshot y S1/S2. El snapshot contiene RAW, clocks, tick, canales,
cola/recibos y un cursor neutro de fases/alias; no contiene una tabla funcional
S1/S2→U/V en metadatos de aplicación. El resultado se obtiene del RAW actual.
Las fronteras públicas de esta aplicación no tienen entradas externas pendientes:
una carga con teacher/evento futuro Scheduled se rechaza, aunque su fase y RAW
parezcan válidos. También se contrastan canales, geometría y alias normalizados.
El audit de aperturas Python rechaza lecturas de resultados/mapas del workspace;
no es un sandbox del sistema operativo y no intercepta fopen de la biblioteca.

Cada orden nativa restaura el mismo MAIN en un proceso propio, guarda su estado
posterior completo y sólo entonces publica el nuevo cursor. Esto es continuidad
por snapshots, no recreación del cuerpo ni devolución de un fork a MAIN. Una
orden rechazada/timeout conserva el snapshot anterior. Guardar durante una
enseñanza externa incompleta conserva T0/alias, no ese mapa pendiente.

Las llamadas nativas tienen timeout máximo120segundos y un Job de Windows
propio con cierre de descendientes. No se enumeran ni matan procesos ajenos.
La app no depende del presupuesto temporal histórico de la campaña: su uso
posterior conserva únicamente el timeout por orden. Cada sesión conserva
TRANSCRIPCION.jsonl, llamadas/recibos/RAW, snapshots y tiempos efectivos.

## Evidencia de esta interfaz

`resultados/demostracion_A` y `demostracion_B` contienen sesiones ejecutadas:
la misma señal zuvi emitió U o V según la experiencia físicamente entregada;
las segundas señales invirtieron la respuesta. Ambas completaron129ticks,
guardaron/restauraron y obtuvieron perfiles físicos U=[1,0], V=[1,1].
`demostracion_reservada` verificó el recorrido sobre la geometría reservada ya
definida, con alias bruma/nube, orden invertido y carga7. Estas sesiones de API
reutilizan mecanismos científicos de la batería: no son réplicas independientes
adicionales de esa batería ni otra capacidad por cambiarles el nombre.

`UI_TECHNICAL02/RESULTS_REVIEWED.json` conserva21checks de continuidad, pregunta
nueva tras carga, aislamiento y admisión. El original contiene un falso positivo
instrumental: un filtro por substring confundió el nombre de una carpeta vacía
SIN_GENERADOR_NI_HISTORIAL con acceso al generador. Se corrigió leyendo los paths
ya conservados, sin repetir las trayectorias; ambos informes permanecen.
`UI_LOADER_CLOSURE` conserva5checks posteriores de carga/cola/alias.
`UI_QUEUE_HOLE_WITNESS` conserva4checks del defecto de carga corregido: el
loader anterior admitía un teacher futuro Scheduled; un bypass diagnóstico
produjo carga32/dirección0 en vez de21/[-1,+1,0]. La app final rechaza ese estado
antes de evolucionar. Ese bypass no es una señal-sola operativa ni aprendizaje
autónomo y nunca se aplicó a las sesiones MAIN de demostración.

Se conservan los primeros errores técnicos: una referencia incorrecta a
`recipe_id` en vez de `id`, y un cwd demasiado largo para CreateProcess. Ninguno
se corrigió cambiando v27, los helpers congelados o los resultados físicos.
