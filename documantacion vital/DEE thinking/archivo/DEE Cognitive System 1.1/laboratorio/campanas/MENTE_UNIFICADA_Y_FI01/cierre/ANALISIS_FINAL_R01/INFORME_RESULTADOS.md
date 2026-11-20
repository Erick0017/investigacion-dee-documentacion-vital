# Mente unificada y FI01: resultados científicos y uso

La opción operativa alcanzada es **MU_MAIN_FASE_R3 T104472**, después de su
preflight y de la reserva propia R17:3684.000645800042 segundos reales de modo
operativo no pausado,120/120 lecturas de asociaciones y12/12 tramas128
concordantes con el criterio fijado. La actuación simple siguió limitada:
89/215 trabajos útiles. El propietario quedó detenido, sin entradas, cadena ni
efectos externos inciertos pendientes; su epoch4 sigue abierto y ligado al
estado emparejado, no a un snapshot aislado. No hubo promoción global a ACTIVO.

R3 bifurcó el completo real **MU_MAIN T68924**, futuro R11 adverso que permanece
intacto. No restauró un prefijo favorable ni importó el control R16. Recibió una
sola experiencia B0 declarada para revisar su referencia y admitió después la
protección de calendario P0, sin edición de RAW/clocks. Su preflight terminó en
T70223 y R17 continuó esa misma vida hasta T104472. Los resultados R11 y R17 se
mantienen separados; la verificación de los ZIP finales corresponde a otros
comprobantes y no se certifica anticipadamente en este informe.

## Lo construido y cómo utilizarlo

Se amplió el mismo gestor de Cognitive 1.1, sin modificar thinking4.5 ni v27.
Una bifurcación completa de MA02_MAIN_5 conserva su propia historia en un solo
mundo N67. No es una fusión de recuerdos de R9, U0 o las ramas auxiliares.

Operaciones de bajo nivel ejecutadas desde `sistema/gestionar.py` en el
preflight R3, antes de iniciar su reserva persistente:

- `unificada-estado --vida MU_MAIN_FASE_R3`: estado y alcance del mundo seleccionado.
- `unificada-sesion --vida MU_MAIN_FASE_R3 --situaciones '[{"modo":"dato","valor":13}]'`:
  dato escalar crudo, tres pulsos genéricos y lectura física fija.
- `unificada-sesion --vida MU_MAIN_FASE_R3 --situaciones '[{"modo":"cadena-iniciar","contexto":"gamma","valores":[29,4]}]'`:
  acceso contextual asistido a una asociación y actuación real del trabajador
  seleccionado por su emisión, dejando el archivo y la transacción pendientes.
- `guardar --vida MU_MAIN_FASE_R3`, cierre del proceso y
  `unificada-sesion --vida MU_MAIN_FASE_R3 --situaciones '[{"modo":"cadena-finalizar"}]'`:
  sensado de los bytes reales del archivo y segunda actuación física.

Las consultas son materiales y cambian el estado. Para experimentar sin consumir
el corte de referencia debe abrirse una copia explícita. Las operaciones no
recrean un individuo cuando falta su estado. El activo histórico no se promovió
por obtener un resultado favorable local.

Estos ejemplos de bajo nivel fueron ejecutados antes del servicio persistente.
Una vida cuyo propietario persistente conserva un epoch abierto no debe
avanzarse a escondidas desde otro proceso del gestor: se utiliza el propietario
único o se cierra expresamente el protocolo, sin ticks ni rebobinado, con
`mente-unificada-finalizar-protocolo`. Para una copia emparejada y la interfaz
normal véase `GUIA_SERVICIO_PERSISTENTE_MU01.md`. El nombre de una vida no basta:
su mundo, FIFO, recibos, artefactos y progreso deben corresponder al mismo corte.

Con el propietario de una copia personal ya iniciado, las peticiones actuales
se envían por la misma cola. Por ejemplo, `mente-unificada-pedir --vida COPIA
--id EJ_ZETA --retorno omit --situaciones '[{"modo":"memoria","contexto":"zeta"}]'`
solicita una lectura de zeta. Una petición con modo `cadena-iniciar`, contexto
gamma y valores[21,4] prepara un artefacto; otra petición con un ID nuevo y modo
`cadena-finalizar` solicita su sensado y verificación. Son dos iniciativas
explícitas del operador, no una secuencia autónomamente planificada. Los ID de
transporte deben ser únicos: repetirlos recupera su recibo, no otra experiencia.

La frontera funcional se mantiene en cada una de esas operaciones:

| Tramo | Qué se permite conocer y hacer | Atribución |
|---|---|---|
| Petición | El operador elige contexto, tarea y comienzo de etapa | Iniciativa asistida P0 |
| Entrada sensorial | Codec fijo introduce bytes o componentes actuales, sin calcular el signo | Transducción preparada |
| Transformación | Referencias y portadores se encuentran y producen una dirección bajo v27 | Física de la vida; depende de su historia cuando el contraste lo demuestra |
| Lectura | Las mismas clases de dirección y posición se observan, sin argumento target o respuesta esperada | Lector fijo del instrumento |
| Actuación | El signo nativo selecciona una herramienta local; no hay reemplazo por la mejor acción | Elección física y herramienta externa declarada |
| Consecuencia | Se sensan bytes reales cuando el protocolo lo pide. Con retorno real, un fracaso aporta el mismo contacto A0; `omit` no aporta ese docente | Entorno/retorno preparado; cambio posterior medido por separado |
| Transporte | FIFO, recibos, artefactos y epoch permiten continuar sin repetir efectos inciertos | Estado operativo, no facultad cognitiva |

## Bloque A: resultados en la trayectoria principal

La vida comenzó exactamente en MA02_MAIN_5 T11196, con cinco asociaciones. En
su propia continuidad adquirió zeta positiva y revisó beta de positiva a
negativa. Los paneles posteriores retuvieron las otras cinco. Son seis
correspondencias físicas opacas, no seis estrategias ni seis significados NSM.

El acceso restaurativo continúa necesitando un contexto explícito y recursos
materiales preparados. Un control sin adquisición de zeta mostró ausencia de
salida y posterior interferencia cuando se consultó primero ese contexto. Las
cinco relaciones antiguas sí eran accesibles en otra rama del mismo prefijo
antes de introducir esa consulta. Por tanto, el resultado no demuestra que
hubieran desaparecido antes de evaluarlas. Aportar indiscriminadamente recursos
a dos bancos sin señal contextual produjo0/6 accesos frente a6/6 sin ese aporte.
No se incorporó ese suministro indiscriminado como solución a la selección.

Se instaló legalmente una anatomía de referencia relativa en E=(15,15,15),
comprobando RAW completo, incluidos registros inactivos, sin transplantar
contenido aprendido. La selección usa siempre tres pulsos genéricos y un lector
espacial/direccional fijo. Una primera experiencia material produjo elecciones
positivas repetidas. Posteriormente dos oportunidades reales no completadas
devolvieron el mismo contacto periférico cero, sin transmitir la acción correcta.
La secuencia propia fue positiva, central y después negativa. Tres trabajos
reservados se completaron3/3, frente a0/3 en la rama de igual edad y retorno
omitido. Los seis accesos anteriores siguieron disponibles6/6 sin docente.

El resultado acredita una referencia y elección local condicionadas por
consecuencias, no una política reversible general, asignación autónoma de crédito
o regulación R2. Al invertir la ley en controles auxiliares, la misma preferencia
podía perjudicar. Las preparaciones, ventanas de escritura y transductor de
fracaso siguen siendo asistencia P0.

Un error del instrumento impidió lanzar el trabajador después de una consulta
nativa: se conservó ese futuro, se corrigió únicamente la autorización del mismo
argv local y no se rebobinó ni duplicó una acción externa. Otros errores de
comprobación documental se conservan como errores del instrumento, no como
fracasos cognitivos ni éxitos físicos.

El servicio persistente mantiene un único escritor, cola local acotada,
identificadores de transporte y mundo evolucionando entre solicitudes. Una
exportación emparejada incluye mundo, cola, recibos y artefactos; el snapshot
aislado no sustituye esos elementos. Las interrupciones con efecto externo
incierto no se reintentan automáticamente. El primer corte A fue T16634.

## Reserva prolongada histórica R11 de MU_MAIN

R11 conservó el protocolo prospectivo de480 oportunidades y3605.031940600136
segundos de horizonte real. Las tres pausas técnicas, incluida la recarga del
estado pendiente en otro proceso, descontaron conservadoramente27.417765s.
Un tramo suplementario separado añadió60.1862740998622s sin solicitudes
materiales ni enseñanza. El total operativo no pausado fue3637.8004496999984s,
sin afirmar un único proceso ininterrumpido ni ejecución de CPU cada instante.
El mundo pasó de T34193 a T68473 y después a T68924:34731 ticks nuevos.

Se intentaron las480 oportunidades nominales. Hubo499 intentos de admisión al
cliente, incluidos inválidos:498 materiales y un control inválido. Se encolaron
487 solicitudes materiales;485 terminaron y dos fueron rechazadas por preflight
sin sus ticks materiales. Otros nueve intentos fueron rechazados por capacidad
y tres por validación. Estos denominadores no se confunden con las4100 entradas
nativas solicitadas y aplicadas4100/4100.

Las memorias produjeron120/120 lecturas físicas únicas:40/40 en cada régimen,
sumando102 consultas directas y18 accesos utilizados para iniciar cadenas.
La petición de revisión de beta es enseñanza, no una lectura adicional. Llegó
entre T52465 y T52531, con3/3 entradas docentes aplicadas. Beta pasó
explícitamente a positiva; las otras cinco conservaron sus signos sin docente.
El último panel histórico quedó alfa−,beta+,gamma+,delta−,epsilon−,zeta+ en
T67004..67540. Ese panel no se presenta como una nueva consulta tras el idle final.

Los71 datos escalares dieron una salida única:13− en18 usos,11− en18,32+ en18 y
29+ en17. Las tramas128 no fueron12/12: los dos primeros regímenes dieron4/4 y
4/4, y el tercero2/4. `fi60_00422` y `fi60_00458` tenían cero candidatos y RAW0
en las seis posiciones del lector congelado, no múltiples respuestas ni un
rechazo de los176 inputs. No se rellenaron ni se repitieron para ocultarlas.

Se ejecutaron252 trabajos reales:216 actuaciones simples y36 etapas de cadena.
Las simples eligieron siempre negativa:89 fueron útiles y127 no, bajo la ley
mixta fijada; esto no constituye una política competente nueva. Las18
preparaciones admitidas y sus18 verificaciones hicieron commit18/18. De19
oportunidades nominales de cadena, una preparación fue rechazada por capacidad y
su finalización posterior fue rechazada sin un archivo preparado:18/19 si se
cuentan todas las oportunidades. Los125 trabajos aceptados globales incluyen
89 simples y36 etapas de cadena; no son125 aprendizajes independientes.

La vida final conserva su estado adverso parcial, no fue sustituida por T34193.
No quedaron solicitudes en FIFO, cadena, artefacto de protocolo o efecto externo
incierto pendientes. Esto no significa un mundo vacío ni ausencia de actividad.
Los archivos históricos de los trabajos permanecen como efectos
reales, no como una tabla consultada por el participante. El ensayo de
interrupción destructiva de trabajador ocurrió en copias: un archivo escrito
antes del corte quedó incierto, se guardó y no se reejecutó automáticamente.

## Reserva final propia R17 de MU_MAIN_FASE_R3

El protocolo R04 fijó480 oportunidades nominales y3720 segundos de horizonte;
el intervalo registrado fue3720.048378800042s. Se descontaron conservadoramente
36.047733s de tres pausas completas, incluida la recarga en otro proceso:
**3684.000645800042s** operativos no pausados. No es tiempo de CPU continua.
La misma vida pasó de T70223 a T104472,34249 ticks nuevos; el incremento del
contador de ocio fue22743, no sus46086 ticks acumulados con el pasado heredado.
Los ID nuevos llevan prefijo `fi60r3_`; no se reutilizaron ni sumaron los R11.

Hubo499 intentos de admisión:498 con payload material, incluidos inválidos, y un
control inválido. De ellos486 se encolaron;484 solicitudes materiales
terminaron y dos fueron rechazadas por preflight sin entradas nativas. Otros
10 intentos fueron rechazados por capacidad y3 por validación de esquema.
Son denominadores de transporte, distintos de **4097 entradas nativas
solicitadas y aplicadas4097/4097**, todas localizadas en los recibos del ensayo.
Los dos preflight fueron `fi60r3_invalid_3`, contexto fuera de dominio, y
`fi60r3_00268`, finalización sin preparación admitida. No se ocultaron como
ausencias ni se incorporaron como errores de decisión del ente.

Las asociaciones dieron **120/120 lecturas físicas**,40/40 en cada uno de los
tres regímenes:102 consultas directas y18 usos de memoria para iniciar cadenas.
La revisión docente de beta entre T88074 y T88108 aplicó3/3 entradas y cambió
explícitamente su signo de+ a−; no fue otra lectura ni regulación autónoma.
El último panel observado fue alfa−,beta−,gamma+,delta−,epsilon−,zeta+,
con lecturas entre T102313 y T102782. Se preservaron los otros cinco signos sin
reenseñarlos. Ese panel precede al ocio final: no se presenta como una consulta
nueva en T104472.

Los71 sensores escalares produjeron18 lecturas13−,18 de11−,18 de32+ y17 de29+.
Las **12/12 tramas128** coincidieron con el criterio reservado,4/4 por régimen:
baseline19 negativo y variantes con2 adicional en los índices3,64 o126,
positivas. El lector y los128 canales siguieron fijos; no se atribuyen128
conceptos o aprendizajes independientes. El calendario P0 se utilizó101 veces;
99 no requirieron espera y dos desplazaron conjuntamente las entradas8y4ticks,
sin consultar su contenido ni el signo esperado.101 usos no significan101
reparaciones ni101 decisiones aprendidas.

Se ejecutaron251 etapas reales:215 trabajos simples y36 etapas de cadena.
Los trabajos simples eligieron siempre negativa:89 fueron útiles y126 no
bajo la ley ambiental fijada. No se acredita una política competente nueva.
Las18 preparaciones y18 verificaciones efectivamente realizadas cerraron18
transacciones. El denominador nominal permanece **18/19**: la preparación
`fi60r3_00265` fue rechazada por capacidad; su finalización00268 no tenía
artefacto pendiente. Los125 trabajos aceptados globales incluyen89 simples y36
etapas de cadena, no125 aprendizajes distintos. La cadena fija utilizó archivos
reales, sus bytes y la emisión nativa; sus dos iniciativas siguieron siendo del
operador. El retorno docente de trabajo estaba omitido para aislar conservación
operativa; el sensado del artefacto real sí permaneció activo.

R17 no es un control con agenda, entradas y edad idénticas a R11. Además del
calendario y la B0 explícita, cambian la continuación, la disposición de las
reservas y la admisión efectiva. Su12/12 frente a10/12 R11 no basta, aislado,
para atribuir toda la diferencia a la protección. La evidencia causal acotada
de la transformación y su prevención procede de los contrastes emparejados
R15/R16; R17 demuestra utilización prolongada de la variante en su dominio.

Las primeras tablas `PANELES_Y_FUNCIONES_R01_ERROR_PREFIJO.json` y
`CORTE_PARA_MANUAL_R01_ERROR_HEREDADO.json`, junto a sus fuentes, se conservaron
como errores instrumentales de filtrado de IDs heredados. No son resultados
físicos negativos ni fueron usados para declarar las métricas finales. Los
archivos canónicos sin ese sufijo y sus recálculos proceden sólo de R17.

El completo actual es
`sistema/estado/checkpoints/MU_MAIN_FASE_R3.T104472.cb632d5d0e08.deetsnap.gz`,
SHA256 `f389f64325390daa31b8f684ac14e0a0c4c75a65e4713af4c861effd9e38a97a`.
El par postSTOP, distinto de una exportación anterior al cierre, se localiza en
`servicio/SERVICIO_60MIN_FASE_R17/PAQUETE_FINAL_POSTSTOP/` bajo la evidencia;
su manifiesto tiene SHA256
`4f9949bf12207136f8d9a569ec334688fbdbfb42cbfc6ce49d23ee53aeba4f75`.
No quedan pendientes nativos, de FIFO, de trabajador o incertidumbre externa.
El epoch4 está abierto: se continúa por el propietario persistente sobre una
copia emparejada exacta. Una mutación material CLI ordinaria exige antes el
cierre explícito del epoch por el procedimiento existente. No se permite
descartar SQLite, reintentar acciones inciertas ni mezclar snapshots favorables.

## Causa delimitada del deterioro tardío y protección preparada

La extracción retrospectiva R14 localizó el primer cambio D−20→−21 en
`fi60_00413`, cuyo dato era29, no13. El trabajo anterior412 había omitido retorno.
La localización no se tomó por sí sola como causa. R15 conservó el snapshot
completo anterior T62525 y el posterior original T62564, junto con sus agendas,
interfaces, recibos y RAW/clocks completos. La ventana crítica fue62560:
el cambio aparece en62561, no en la foto de62560.

Cuatro copias diagnósticas, con protocolo fijado antes de los nuevos ticks,
compararon consulta+dato29, consulta sin dato, el mismo dato en un sitio sham y
dato sin consulta. Sólo la combinación real terminó con A104/B125 y D−21;
los otros tres conservaron A105/B125 y D−20. La reproducción real coincidió
exactamente con los RAW, clocks y recibos nativos del tramo original413. La
interfaz sham adicional era común y se declaró: no se afirma que todo el
contenedor documental fuese idéntico. Se ejecutaron1484 ticks diagnósticos
nuevos en cuatro mundos; no son cálculos retrospectivos de cero ticks ni
experiencias de MAIN.

Después de2N ticks y de la misma trama128 con19+2 en el índice2, cada contraste
completo difería del real en un único RAW, A, y en cero clocks. Las interfaces
y entradas pendientes coincidían; las identidades, historiales y recibos
legítimamente no. El real produjo dirección E=(0,+1,−1) y cero candidatos en
las seis puertas; los controles E=(+1,+1,−1) y positiva. Esto explica ese cambio
de referencia y ese fallo de acceso. No prueba pérdida global de información,
linaje único de cada portador, retorno toroidal o una causa de todos los fallos.
La edad sola, el dato solo y la consulta sola no explicaron el contraste.

R16 probó una única corrección de calendario P0, sin reenseñar ni editar
contenido: antes de enviar cualquier entrada sensorial desplaza el protocolo
completo0..10 ticks para que la ventana query−1..query+8 no cruce el límite391
pertinente al dominio admitido. El código no mira el valor, target, signo ni
lector. Conserva geometría, dosis, transducción y lector fijo. En el contraste
emparejado, R3 y el control se compararon en el mismo T62570; el control recibió
seis ticks pasivos adicionales, no otra repetición de la enseñanza.

La protección dejó A105/B125 frente a A104/B125. Tras2N y el mismo dato21,
produjo positiva frente a ausencia de candidato; ambos paneles antiguos dieron
6/6 con42/42 entradas cada uno. En cuatro cortes globales sólo difería A, con
cero clocks distintos. Es evidencia causal acotada de prevención de una
transformación dañina por temporización preparada. No es una regulación
aprendida ni demuestra que toda fase problemática quede resuelta.

Para hacer utilizable el futuro R11 ya alcanzado, se creó MU_MAIN_FASE_R3 desde
su paquete completo T68924. El epoch heredado se cerró expresamente en esa
copia, con cero ticks; no se modificó el padre R11. Una
única experiencia B0 llegó en69207 y terminó en69209, revisando D−21→−20.
Esto es reenseñanza explícita de referencia, no recuperación sin docente. Se
admitió después la protección P0 sin alterar RAW ni clocks. No se mezclaron
campos de un control favorable ni se borró el futuro R11.

En la misma candidata, las seis asociaciones dieron−,+,+,−,−,+ antes y después
del bloque:12/12 lecturas, sin docente de esas asociaciones. Los datos13 y32
produjeron− y+; una trama12819+2 en el índice4 produjo+. Gamma positiva
seleccionó una compresión real de[29,4]; se guardó su artefacto pendiente de13
bytes, otro proceso lo cargó, su medida cruda produjo negativa y la verificación
hizo commit. El corte previo fue T70223, sin cadena, efecto incierto o artefacto
de protocolo pendiente. Es una comprobación operativa limitada, anterior a la
reserva propia R17 descrita arriba; no se contó dos veces como adquisición nueva.

## Bloque B: acceso escalar reutilizable y nueva aplicación

El primer datum estacionario en E-X permitía una lectura puntual, pero quedaba
ocupado e impedía una entrada posterior: no se declaró una interfaz repetible.
Una variante de ruta cruzaba un registro SEM4 inactivo preparado y no transportó
el dato; ese registro no se borró para obtener un acierto.

Un sensor transitorio en S=(14,15,16), con terminadores legales iguales para las
salidas, produjo0/2/0/2→negativa/positiva/negativa/positiva y volvió a RAW0 por
su dinámica. El lector comprende seis clases fijas de posición y dirección y no
recibe valor, target, contexto, historia ni plano favorable. Los controles sin
consulta, sin dato y sham delimitan el aporte. La preparación del sensor no es
una anatomía aprendida.

En MAIN se aplicaron exactamente19 contactos docentes A, sin reajustar su número
para forzar un campo. La diferencia entre las dos referencias cambió a−20 por
evolución v27. Con el mismo lector, los nuevos datos11/29/13/32 produjeron
−/+ /−/+. Los valores entran íntegros; Python no calcula el signo o la comparación.

Tres secuencias nuevas combinaron dos funciones de la misma vida mediante un
entorno real de archivos. Primero, gamma/epsilon/zeta seleccionaron físicamente
los trabajadores +/−/+. Éstos comprimieron o calcularon SHA sobre datos
sintéticos y conservaron el artefacto real. Después de guardar y cargar en otro
proceso, el tamaño real13/32/13 entró sin clasificación al sensor. La referencia
adquirida emitió−/+ /− y los trabajadores verificaron y cerraron3/3 transacciones.
El panel final fue alfa−,beta−,gamma+,delta−,epsilon−,zeta+:6/6 antes y después.

La composición es útil y operativa, pero asistida: el operador elige el contexto
inicial y solicita las dos etapas. No se le atribuye planificación autónoma,
elección aprendida del banco ni iniciativa de consulta. Los algoritmos de archivo
pertenecen a las herramientas. La medición de tamaño es transducción preparada;
la referencia y las emisiones pertenecen a la evolución física de esta vida.

El recálculo anterior a las tramas128 reconstruye57855 observaciones RAW exactas,
22 lectores,6 comprobaciones de artefactos y6 actuaciones. Su ampliación con las
tramas y la cuarta cadena reconstruye96724 RAW,45 lectores,8 comprobaciones de
artefactos y8 actuaciones, sin discrepancias en ambos cortes.
Es recálculo archivado, no una reproducción nativa de la física.

Los controles de aplicación preservaron su futuro adverso. Una bifurcación del
prefijo anterior a las19 experiencias, igualada en edad y con los mismos cuatro
datos posteriores, emitió positiva ante el archivo comprimido de13 bytes y no
cerró la transacción; el archivo pendiente no se eliminó. Antes de esa decisión,
MAIN y U tenían el mismo tick31765, clocks completos iguales, interfaces y
protocolos iguales y cero entradas nativas pendientes. Los arrays RAW completos
diferían en un único sitio, la referencia A. El artefacto pendiente y el progreso
de la cadena eran exactamente iguales. Los recibos y metadatos de historia e
identidad difieren legítimamente: no se afirma identidad causal total.

Las revisiones completas del adaptador tampoco eran byteidénticas: entre
algunos tramos se añadió el modo de entradas crudas, ajeno a esas cadenas.
Las funciones efectivamente usadas de sensor, cadena y trabajador se
conservaron idénticas. Se archivan las dos fuentes exactas y ese límite; una
igualdad de funciones ejecutadas no se presenta como igualdad de todo el ZIP.

En el segundo contraste, un archivo SHA real de32 bytes ya estaba pendiente en
el mismo prefijo adquirido. Omitir su dato o presentarlo en el sitio sham produjo
negativa y falló la verificación; el dato32 medido del archivo SHA e introducido
en el sensor real había producido positiva y commit. El retorno docente estaba
omitido: no era una corrección que proporcionara la acción correcta.
Los34 inputs de estos controles fueron admitidos. Así se delimitan tanto
el aporte del contenido adquirido como el del sensado actual, sin reenseñar la
respuesta en el destino.

## Entradas conjuntas y conservación después de la carga

Se ejecutaron8/16/32/64/128 entradas simultáneas mediante árboles de encuentros
nativos. Los portadores constantes que redirigen no cuentan como variables. En
la variante B05, cada uno de los128 componentes cambió individualmente la salida
al pasar de0 a2, manteniendo los otros127 en0. El baseline emitió negativa y los
128 contrastes emitieron positiva. Sólo126 índices eran nuevos reservados;0 y127
eran repeticiones técnicas. Todos los casos aplicaron176/176 inputs y después de
2N ticks conservaron6/6 accesos anteriores:768 consultas correlacionadas, no768
adquisiciones independientes.

La referencia adquirida participó materialmente: la historia alternativa cambió
el resultado del mismo dato; igualar externamente las referencias en una copia
produjo la dirección central en vez de silenciar el mundo. Cortar sólo la carga
del producto formado en la convergencia o en el sensor retiró el efecto, mientras
los sham lo conservaron y las seis memorias seguían accesibles. Esas ediciones
son intervenciones diagnósticas, no mantenimiento autónomo.

Las rutas importan. El primer acoplamiento podía transportar una suma correcta
pero perturbar el comparador y perder accesos antiguos; una reconexión cruzó un
SEM4 inactivo y falló. B05 no borró ese soporte: cambió la conexión preparada.
En dos vidas N67, con árboles de8 y128 variables respectivamente, cuatro tramas
0/2/0/2 con guardado y carga entre usos,
2N ticks y seis consultas antiguas intercaladas conservaron24/24 accesos en cada
vida. No se atribuye automáticamente esa conservación sólo al frontal nuevo:
también cambió la fase de preparación. El control específico B04D8+6 añadió sólo
seis ticks pasivos al frontal antiguo: admitió16/16 inputs, produjo positiva y
conservó6/6 accesos. Por tanto, ese caso no demuestra una ventaja de retención
causada exclusivamente por trasladar el dato de D a S. El reuso de S a lo largo
de cuatro tramas128 se comprobó por separado.

Finalmente se incorporó el árbol a MAIN sin copiar campos adquiridos. Sus tres
tramas128 con componente0=19 y suma material adicional2 en el índice1 o127
produjeron negativa, positiva y positiva. Las528 entradas solicitadas fueron
admitidas. Los seis accesos antiguos se utilizaron entre todas las tramas18/18 y
una cuarta cadena real de preparación y verificación se completó después de la
carga. El corte fue MU_MAIN T34193. La relevancia individual exhaustiva pertenece
a los controles del prefijo A; MAIN recibió tres tramas y posteriormente su
reserva continua, no128 aprendizajes separados.

## Transferencia: alcance y límites

Las ramas T/U/H conservan un prefijo común y no se suman a MAIN. Tras19 contactos,
T reutilizó la referencia cuantitativa adquirida en el primer destino sin
feedback:4/4 emisiones concordantes con la ley fijada, frente a2/4 en U y H.
Con la ley contraria T obtuvo0/4. La comparación de snapshots completos mostró
un único RAW distinto en cada contraste relevante y clocks iguales; interfaces
e historiales legítimamente difieren. No se declaró identidad causal total.

Una segunda familia fue la revisión de una asociación arbitraria y su uso en un
header digital. Es reutilización mediante una representación compartida P0,
no abstracción universal ni descubrimiento de una equivalencia desconocida.
H tuvo una entrada docente rechazada:3 solicitadas,2 admitidas. No se lo trató
como una historia de dosis efectiva perfectamente igual. La exportación de
headers sufrió una colisión de nombres entre brazos: los primarios conservan
hexadecimal y hash, y los bytes regenerados se identifican como tales, no como
archivos históricos intactos. La dinámica del participante no leyó esos headers.

La extensión B14 partió de los tres finales propios T/U/H en T31631, sin repetir
su enseñanza fuente. Ocho oportunidades C2 por vida intercalaron cuatro usos
cuantitativos y cuatro de gamma. Las24 emisiones accionaron trabajadores reales
sobre fixtures iguales; las148 entradas nativas se aplicaron148/148. T hizo
commit8/8 sin nuevos contactos de retorno de fracaso; U y H hicieron0/8. Sus ocho fracasos
regresaron por el mismo contacto A0, cambiando D de−1 a−9 y de+18 a+10,
respectivamente, pero sus acciones continuaron positivas. T mantuvo D−20 y
acciones negativas. Los tres finales fueron T43403, con sus propios futuros.

El coste de adaptación útil de U/H queda censurado por encima de ocho
oportunidades, no se estima como ocho ni se acredita una política nueva. La
ventaja T procede de lo adquirido antes del destino. La ley contraria sólo se
evaluó analíticamente sobre los mismos actos:0/8 en T y8/8 en U/H; no hubo
trabajadores falsos ni feedback físico contrario. No se ejecutó otro control
omit-return nuevo en B14: el efecto de sus consecuencias sobre las referencias
queda observado, mientras la atribución causal más fuerte proviene de los
controles anteriores. El recálculo verifica74932 observaciones exactas y todos
los archivos reales, sin discrepancias.

## Cadencia, perturbación y tamaño del dominio

El contraste B06 mantuvo dos tramas128, los mismos352 inputs y un horizonte
común. Con separación de dos ticks se admitieron352/352, la primera lectura fue
nula y la segunda positiva; después fallaron los seis accesos antiguos:0/6.
Ese panel posterior solicitó42 entradas: sólo3 fueron aplicadas y39 rechazadas;
las demás cadencias admitieron42/42. El0/6 mide acceso fallido bajo ese bloqueo,
no demuestra destrucción física de las seis memorias.
Con separaciones16/67/200, la pareja produjo negativa/positiva y el panel antiguo
conservó6/6. Una admisión completa no implica acceso preservado ni ausencia de
interferencia. La ocupación pasiva en T17038 fue283382 sitios para Δ2 y24 para
las demás cadencias. El snapshot final de Δ2 es posterior al panel, T17427 y
297621 sitios activos: no se confunde esa foto posterior con la medida pasiva.
No se conservó un snapshot completo exactamente en T17038 y no se inventa.

Un único pulso legal en la ruta precursora cambió una respuesta positiva a
negativa tanto con carga0 como2 o32; el sham de carga32 fuera del encuentro la
conservó. Cada caso admitió177/177 inputs y mantuvo6/6 accesos antiguos. Incluso
un portador de carga cero puede intervenir materialmente. Son cuatro contrastes
de ubicación y carga, no una curva general de resistencia al ruido.

B07 comparó cuatro vidas auxiliares nuevas desde T0, una por combinación de
N67/N101 e historia A/B; no amplió MAIN ni heredó sus recuerdos. Cada vida
adquirió sus referencias mediante su
propia experiencia. En el régimen nominal de cuatro tramas0/2/0/2, la historia A
produjo−/+ /−/+ y la historia opuesta B produjo+/+/+/+ en ambos tamaños, con
705/705 inputs aplicados por vida: un contacto docente y704 entradas para las
cuatro tramas, no705 por trama. El mayor dominio no mejoró esa función disponible.

Con dos ticks de separación, ambos tamaños quedaron nulos al principio y
después de un horizonte común de al menos3N101:352/360 inputs aplicados y ocho
consultas finales rechazadas. La ocupación final fue297835/300763 para N67 y
1020757/1030301 para N101. No se atribuye el fallo simplemente a volumen escaso.
Con separación16, N67 conservó−/+ en las dos ventanas. N101 produjo−/+ al
principio, pero neutral/+ posteriormente: sus referencias2/3 llegaron a3/3.
El mayor tamaño tampoco garantizó conservación tardía y este contraste no
identifica por sí solo el encuentro causante ni prueba un retorno toroidal.

El recálculo ampliado B06/B07 reconstruye26 primarios,71854 observaciones RAW y
99 lectores sin discrepancias. Las medidas de ocupación y sus ticks conservan
sus propios localizadores; no se extrapolan a los otros perfiles ni a MAIN.

## Selección nativa de banco y coste de su integración

En R1 auxiliar, una referencia adquirida cambió la ruta física de una consulta
preparada: T negativo llegó a gamma positiva, H positivo llegó a beta negativa.
La revisión explícita de gamma hizo que T utilizara gamma negativa. Cortar el
primer giro y su sham delimitaron la dependencia. Sin embargo, el circuito de
guías generaba una consulta basal incluso sin la emisión selectora. Es P1 sobre
iniciativa P0, no una consulta espontánea ni una estrategia P2/R2.

La función no conservó el alcance anterior: tras un uso, T sólo permitió2/6
accesos antiguos y H5/6. La corrección R2 perdió un giro por una entrada rechazada
en un soporte SEM4 ya ocupado y afectó rutas restaurativas. Se conservan ambas
variantes y sus futuros adversos. R1 se admite únicamente como perfil auxiliar
de un uso con coste destructivo declarado; no sustituye a MAIN ni convierte sus
ventajas en conocimiento de MAIN. Los READY contienen el estado completo previo
al uso y la API impide reutilizar silenciosamente un estado ya consumido.

## Qué sigue sin acreditarse en este corte

No se acreditan mente general, nuevos significados NSM65, selección autónoma de
todos los bancos, planificación multietapa aprendida, autoabastecimiento ni
estabilidad ilimitada. Las calibraciones auxiliares de presencia y fisión
escalar que no consiguieron expresión repetible permanecen negativas/parciales;
no se transfieren sus resultados a MAIN.

La escala conjunta, ruido, rutas, variación de N y reserva continua se documentan
con sus primarios y cobertura efectiva en el cierre de este mismo informe. Una
admisión de128 portadores no equivale por sí sola a128 variables relevantes,
conceptos o estrategias. Sólo se contará la relevancia contrastada.

## Localizadores decisivos

Evidencia local: `evidencia/campanas/MENTE_UNIFICADA_Y_FI01/`.

- A03,A08,A13–A17,A22–A26: adquisición, revisión, retención e interferencia.
- A42–A49 y `contraste_main_u/`: consecuencia, uso posterior y estados completos.
- `seleccion/`: historias opuestas, cortes, sham, fase y actuador anulado.
- `servicio/`: continuidad emparejada, errores y recálculo de recibos.
- B_MAIN_01–07 y RECALCULO_APLICACION_B.json: la aplicación de la misma vida.
- `transferencia_b/`: fuentes, destinos, historias T/U/H y arrays/deltas exactos.
- `escalamiento/`: rutas, niveles y contraejemplos; no son recuerdos de MAIN.
- `servicio/AUTOPSIA_FASE_R15/` y `servicio/PROTECCION_FASE_R16/`:
  primarios de causa y prevención emparejada. Las extracciones cerradas
  `ANALISIS_AUTOPSIA_R15` y `ANALISIS_PROTECCION_FASE_R16` están en el laboratorio,
  bajo `escalamiento/`, no en ese directorio de evidencia.
- `R3_01..13` conserva la comprobación operativa.
- `servicio/SERVICIO_60MIN_FASE_R17/`: protocolo, primarios, recálculos,
  `PANELES_Y_FUNCIONES.json`, `CORTE_PARA_MANUAL.json` y par final postSTOP.
- `CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json`: identidad y dependencias del corte
  actual; `CONTINUIDAD_R11_PRESERVADA.json`: futuro adverso anterior intacto.

El paquete científico es una extracción de análisis, no un respaldo operativo
completo. Los estados completos y las colas necesarios para continuar se
mantienen localmente. La distribución operativa seleccionada y sus ZIP finales
requieren sus propios comprobantes de extracción y continuidad.
