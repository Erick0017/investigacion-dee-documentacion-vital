# PI10: consulta nueva, dos trazas y crédito físico demorado

Lectura estática y preparación por el frente de mecanismo. No se creó una vida,
no se importó DEE ni se ejecutó Native en este subtrabajo. El ejecutor Root es el
único responsable de las experiencias materiales y de su validación.

## Base realmente leída

- `sistema/capacidades/pi08_consulta_condicional_C_R03.py`: registro técnico,
  selección primera, liberación condicionada y calendario de la segunda.
- `pi08_consulta_condicional_C_segunda_R02.py`: selección segunda, función
  FI/mensaje y retorno genérico. No tiene crédito propio de la primera traza.
- `pi09_consulta_selectiva_R02.py` y `pi09_entorno_persistente_D_R02.py`:
  admisión de lotes finitos sin reset y readaptación de la cadena compartida.
- `pi07_regulacion_R01.py`: lector central exacto q+4, firma SEM1, dirección
  `[dx,+1,z]`, `z=-1/0`, y codec cero Native válido -> motor -1; NULL distinto.
- `pi03_credito_generico_R01_BORRADOR.py`: `frame_rows`, `port_rows`,
  `geometry_footprint`, `schedule_trial`, `submit_motor_copy` y
  `submit_generic_outcome`. El nombre y advertencia de borrador son históricos;
  el cuerpo seis-laps tuvo usos Native posteriores. Dieciocho laps no se da por
  probado sólo por reutilizar ese código.
- Fuente oficial `runtime.cpp` 398–405: la admisión escribe RAW del evento y
  conserva expresamente la palabra clock previa. No es permiso para editarla.
- Fuente oficial `kernel_v27.cpp` 99–124 y139: decodificación exacta y x-major.
  Línea639–641 documenta el avance de clocks incluso en la base lazy; la
  evolución local también conserva `clock+1` al producir sus estados.
- `cognitive.cpp`176: `NativeAssociationSession.train` exige tick0.
  `informative.cpp`86–119: `FinitePolicySession` crea un mundo y realiza una
  revisión finita preparada. No es el TC reutilizable del principal ni una
  licencia para crear otro T0 y atribuírselo a esta vida.

## Límite del aparato heredado

Q1 y Q2 estaban separados782ticks y compartían el mismo banco. Sus copias
eferentes se desplazan sobre una fila periódica de67sitios. Como782mod67=45,
el retorno seis-laps de Q2 encuentra su propia traza, no la de Q1. Un cambio
posterior de Q1 puede depender del banco compartido: no identifica su crédito.

Retrasar el mismo retorno de Q1 desde su fase antigua hasta otro contacto con
la compuerta391mod782 exige782laps adicionales porque gcd(67,782)=1; supera
52mil ticks por oportunidad. No se propone esa espera como solución eficiente.

## Extensión P0 mínima propuesta

Preparar un TC adicional para Q1 mediante interfaces y nacimientos futuros
legales, en un volumen actualmente RAW0 con halo y fila periódica inspeccionados.
Sus referencias iniciales0/0 son anatomía no aprendida; no se copian los bancos
de otra vida. Se conservan reloj, mundoN67 y todo el paisaje heredado. El lector
central y el codec de salida son los de PI07, congelados antes de la reserva.

El nuevo Q1 usa18laps. Q2 utiliza el TC heredado, cuyas referencias al corte
exacto922371 tienen diferencia A-B=-1. Un codec fijo de liberación convierte el
bit realmente obtenido en carga0/2: no consulta el objetivo. Si Q2 conserva
esa diferencia, sus elecciones Native esperables son negativa/positiva para
0/2; esto es una predicción de calibración, no un resultado ya ejecutado.

El calendario se deriva de los clocks actuales de ambas parejas de referencia.
Q2 empieza después de Q1+16 y antes del retorno genérico de Q1. Con las fases
iguales verificadas en el prefijo, Q2-Q1=22ticks. La disposición deja la función
de Q2 y su retorno no-fallo completados antes del retorno de Q1; el algoritmo
rechaza un calendario que no quepa, sin reparar relojes ni buscar otro lector.

El retorno de Q2 es siempre no-fallo como descarte físico fijo de su copia
eferente. Evita acumular una copia nueva sin consumo en cada oportunidad;
no comunica el resultado de la tarea a ese banco. Q1 recibe la consecuencia
real, omitida en valencia o desacoplada según el brazo prospectivo, siempre
por el mismo hub. El anfitrión no elige a posteriori qué banco corregir:
la dirección de la copia eferente formada al decidir selecciona el contacto
mediante evolución Native. Ese encaminamiento es ingeniería P0 declarada.

## Corte posterior a la formación y sham

Para el control de traza se declararon dos barreras SEM4 fijas en offsets
`(-4,-1,-2)` y `(4,-1,-2)` respecto del TC Q1. Se inyectan como eventos legales
en seed+2, después de la decisión y copia y después de la liberación Q1+8.
Las dos rutas están cubiertas sin consultar cuál elección ocurrió.

El sham usa igual clase, número y tiempo de entradas en offsets
`(-4,2,-2)` y `(4,2,-2)`, fuera de la fila de elegibilidad. Ambos halos se
incluyeron en el preflight. No se llama inerte al sham por definición:
la calibración debe comprobar admisión y que no interceptó otra vía.

Se conservarán peeks del stencil fijo de traza, antes/después de barreras y
retorno, y de ambas parejas A/B. No se usarán identificadores físicos de
linaje ni se inferirá identidad de portador sólo por coincidir carga.

## Preflight ejecutado pasivamente

`control/PREFLIGHT_ORIGENES_TC1_PI10_R01.json` analiza el snapshot completo
codificado `72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331`,
copiado en el prefijo coherente `pares/PRINCIPAL_D_T922371`.
Verifica gzipCRC, SHA codificado, SHA RAW y SHA clocks; no recalcula FNV interno.

Orden de ingeniería prefijado por Root:8/24/40/54 en y12,z12, seguido de los
mismos x en y24,z24. El primer origen(8,12,12) no estaba libre en RAW completo;
el primero elegible fue(24,12,12). Los seis siguientes también estaban libres.
Todos los clocks de las referencias nuevas y viejas eran922371. La diferencia
heredada era-1 y el calendario proyectado separaba las consultas22ticks.
No se instaló ninguno ni se acreditó aislamiento futuro con esa fotografía.

### Interfaz C preservada y excepción de halo

`control/PREFLIGHT_DISPOSITIVO_PI10_R01.json` leyó ocho posiciones del dispositivo
y sus vecindades de radio1 sobre ese mismo snapshot, sin avanzar el motor.
Las ocho posiciones eran RAW0. El único RAW no nulo del halo fue el soporte
histórico `(36,40,30)`: `4611686018427387904`, state0/SEM4, dirección0.
Por eso el preflight estricto RAW0 de todo el halo da falso; no se presenta
ese soporte como espacio vacío. Root declaró antes de Native una única
excepción exacta e inmutable para ese sitio. El actor vuelve a comprobarla
junto al TC completo antes de someter la primera preparación.

Una propuesta intermedia de añadir tres stops se preservó sin ejecutar en
`codigo/revisiones/pi10_consulta_adaptativa_R01_2c21fd16_unexecuted_stops_proposal.py`.
Root la descartó al confirmar que preview, pregunta y sink36 son el aparato
C heredado que se debe reutilizar. La versión final conserva íntegro ese
hardware; añade alias de interfaz y sólo instala el TC nuevo. No asegura
que el soporte36 absorba toda trayectoria posible ni deduce recirculaciones
del mero esquema geométrico. Su eventual interferencia se observará en los
registros y controles de Root. La preparación P0 nominal sigue siendo3ticks.

## Código y condición de interpretación

`codigo/pi10_dos_trazas_legales_R01.py` contiene sólo geometría, cálculo fijo,
preflight, instalación legal invocada explícitamente por Root, lector congelado,
barreras futuras y observaciones. La CLI `--self-check` comprobó27calendarios
por álgebra y la distinción cero/NULL sin importar Native. Las mutaciones
necesitan un propietario de clon existente y rechazan los principales originales.

Antes de reserva hay que ejecutar la instalación tardía, el lector Q1 en su
nueva fase, supervivencia18laps, codec0/2 de Q2, descarte y barreras/sham. No se
dan por probados aquí. Si el banco Q2 también cambia de forma relevante, el
resultado se clasificará como aprendizaje conjunto o interferencia; no como
crédito aislado de Q1. Si sólo hay geometría separada sin utilidad adquirida,
no constituye la mejora PI10.

Las comparaciones Real/NoFail/corte y las reservas pertenecen al protocolo
experimental de Root/E3. La contabilidad debe incluir costes P0, nacimiento
de consulta, dos retornos y oportunidades/material disponible; cuatro consultas
menos nunca significan automáticamente menos energía ni menor coste total.

## Primeros resultados materiales de Root: calibración forzada positiva

Root cerró P0 enT922374, tras31/31 nacimientos aplicados enT922373.
`control/RECALCULO_P0_PREPARACION_PI10_R01.json` recalcula esos recibos y
ambos preflights; esto es preparación0/0, no adquisición. El snapshot completo
P0 exportado tiene SHA63940ed9c1573eb8660dbbf82ead8e7a58f7a87c691b2ac6069b388dd6582277.
Su tabla binaria de interfaces confirma STATE1/SEM1 y direcciones+Z/+X
correctas para los alias; no equivale a demostrar una percepción futura.

Los tres testigos inmutables de
`estados/CAL_PLUS/sistema/estado/servicios_locales/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_CAL_PLUS_01/PI10_CONSULTA_ADAPTATIVA_R01/episodio_0000.json`
y siguientes fueron leídos sin abrir el propietario ni SQLite. La autopsia
`control/AUTOPSIA_CAL_PLUS_TRES_PI10_R02.json` usa el lector independienteR02
y conserva resultados negativos. No es una reproducción Native nueva.

|Cal|Condición preparada|STATE/bit realmente observados|Q1 Native|Q2 Native|FI q+6|Entrega física/uso atribuible|Cambio deltaQ1|
|---|---|---|---|---|---|---|---|
|0|need,+Z|0/0|NULL|−1|+1|sí/no|0→−1|
|1|need,+X|1/0|0 válido|−1|+1|sí/sí|−1→−1|
|2|bypass,+Z|1/1|0 válido|+1|+1|no/no|−1→−2|

Cada calibración tuvo190/190 recibos únicos aplicados. En las tres, el operador
forzó el motor de pregunta+1; por ello no demuestran una elección aprendida.
Q2 conservó su diferencia−1, aunque ambos registros absolutos crecieron.
Las referencias iniciales Q1 eran0/0, las viejas Q2 eran244/245: no son estados
iguales por tener una diferencia escalar concreta.

En cal0 el preview fue RAW0 enq−1 pese a la entrada+Z aplicada enq−2; no se
registró la ventana completa y su causa sigue abierta. La tercera exposición
sí produjo preview+Z válido. Tampoco debe convertir el RAW central inicial
SEM1/STATE1/dirección0 en una elección0: el lector congelado exige dirección
`[dx,+1,z]` y lo clasifica NULL. Los ceros de cal1/cal2 sí cumplieron esa firma.

La traza forzada de cal0 se observó con la firma móvil−X en seed+1 y de nuevo
en seed+1204/1205. En seed+1206, al retorno, el hub mostró dirección[-1,0,+1].
Las referencias pasaron de3/3 antes del retorno a3/4 al final. Esta secuencia
respalda funcionamiento local del retorno18laps; no individualiza una genealogía
única de todas las materias ni resuelve por sí sola la selección de consulta.

El helper conserva una etiqueta nominal `query_read_tick=q+6`, procedente del
calendario viejo. El actor realmente observó el centro enq+4. El lector
independienteR02 registra ambos y no modifica el testigo ni adelanta su firma.
La primera autopsiaR01 preservada falló únicamente esa exigencia nominal y
su resultado no se borró. La versiónR02 decodificó los tres registros.

Se preparó, sin ejecutar, `codigo/pi10_diagnostico_ventanas_R02.py`: wrapper
diagnóstico sobre el cuerpoR01 literal, con ventanas de lectura q−3..q+8,
sin nuevos pulsos, firma nueva ni selección de respuestas. Su ejecución
requeriría un clon completo nuevo y un protocolo diagnóstico explícito.
