# CPC9: auditoría científica esencial de la evidencia registrada

Proyecto DEE Universe. Autor del proyecto: Ivan Erick Tlaltecatl Morales.
Instrumento de la campaña: DEE thinking 4.5.0, kernel v27 congelado.

Esta entrega es una extracción y un recálculo posteriores al cierre de CPC9.
No se volvió a ejecutar la campaña, no se cargó un Runtime y no se modificaron
los resultados originales. «Independiente» significa que los recuentos y
contrastes indicados se obtienen de los registros, sin aceptar un PASS como
sustituto de los datos. No significa una nueva réplica física por otro laboratorio.

## 1. Qué contiene la evidencia

Se conservan los valores completos de los **281 contenedores primarios CPC9**
indexados en el ZIP canónico: experiencias, entradas/recibos, frames, campos,
vecindades, controles, reservas e intentos adversos. La compactación deduplica
documentos y expresa diferencias estructurales reversibles; no elimina campos
de esos contenedores. Las listas mantienen su orden y los uint64 no pasan por
float. No se conserva el espacio en blanco, la escritura léxica de floats ni
se promete conservar el orden de miembros de objetos JSON. El orden físico de
entradas se conserva en las listas de llamadas, eventos y recibos.

El índice también conserva 342 rutas JSON históricas referenciadas desde el Core
y 458 archivos JSON de la recuperación limpia que **ya había terminado**.
Esos archivos incluyen configuraciones y actas: no son 458 ensayos independientes.
Los duplicados exactos de valores comparten un documento y retienen sus orígenes.
Los 91 testigos textuales históricos adicionales conservan bytes exactos.

Hay extracciones completas RAW/clocks de 13 estados físicos significativos.
Se decodificó el contenedor de datos sin importar el motor y se verificaron sus
checksums, hashes de arrays y recuentos. Se excluyen las colas, interfaces y
metadata operativa de esos snapshots: **estas extracciones no sirven para
restaurar ni continuar una vida nativa**.

`AFIRMACIONES_Y_EVIDENCIAS.json` vincula cada afirmación C01–C15 con condiciones,
fuentes originales, SHA-256, localizadores y límites. `INDICE_EVIDENCIA_ORIGINAL.csv`
distingue el SHA de los bytes originales, el de los valores JSON canónicos y
el del registro reducido. El manifiesto verifica además cada archivo físico.
No deben confundirse esas identidades. Los documentos lógicos comparten un
JSONL con posiciones y longitudes verificables para reducir duplicación y
número de archivos, sin cambiar los bytes de sus registros codificados.

## 2. Continuidad y aprendizaje de E1 — C01, C04, C05, C12

E1 conserva una genealogía N67, T0–2493, con siete fases serializadas y seis
fronteras. El recálculo compara el estado final previo con el inicial siguiente,
los hashes de los padres y la conservación de IDs de recibos. Resultan seis
fronteras concordantes, 352 frames registrados y 1573 recibos únicos.

La preparación inicial contenía 107 sitios materiales y oportunidades/rutas
especializadas. Se añadieron interfaces vacías en T1220/T1907; sus registros
declaran igualdad RAW/clocks antes/después. Esto es una ampliación instrumental,
no crecimiento aprendido. No se importaron memorias de otros mundos a MAIN.

E1 adquirió contenidos y formas después de T0. Dos operandos, 36 y 16, seguían
participando en la respuesta T2283, después de adquisiciones adicionales. En
copias diagnósticas, cambiar 36 a 5 invierte +X a −X; cambiarlo a 16 produce
un portador activo de carga 7 sin dirección. El sham conserva +X y el estado
final correspondiente. Es evidencia del uso del contenido, no sólo de un RAW
antiguo presente. El corte completo de referencia altera otras funciones y no
debe utilizarse solo para localizar significado.

En la revisión cuantitativa, la experiencia aporta 13 a una referencia adquirida
de 54, que pasa a 67. Cuatro objetos nuevos producen −X,+X,−X,+X; igual material
fuera de ruta produce −X,−X,−X,+X. La respuesta T941 todavía utiliza 54: no debe
atribuirse retrospectivamente al 67 que llega después. El comparador/gradiente
estaba preparado; la referencia, su revisión y sus usos dependieron de historia.
Los pronósticos previos conservados pertenecen al auditor, no a una nueva
facultad de predicción espontánea atribuida a E1.

En la última fase sólo se aplica una de 178 peticiones nuevas: 177 son rechazadas
por ocupación. Los cuatro intentos de revisión no aplicados no cuentan como
aprendizaje. La rama sin esos intentos coincide físicamente con MAIN. La
restauración registrada conserva el estado/recibos, pero la interacción posterior
tampoco resuelve por sí misma el bloqueo de acceso.

## 3. Orden, contacto y composición — C03, C09, C10

Los datos apoyan adquisiciones y usos finitos de orden/contacto dentro del
aparato. La prueba de composición conserva dos llegadas reales, carga 26 con
dirección (1,0,1) y carga 30 con dirección (0,1,0). Forman 56(1,1,1) en T206.
La consecuencia posterior es 63(1,0,1) en T210.

Retirar cualquiera de las llegadas o borrar X/Z de la composición conservando
su carga 56 elimina esa consecuencia: queda actividad 7(0,−1,0). El sham
conserva la consecuencia y reproduce el estado final T884. Por tanto, el
resultado no se reduce a sumar cargas ni a paralizar globalmente el aparato.

Esta es composición funcional en geometría y ventanas preparadas. No demuestra
una gramática abierta ni unión general de referentes y papeles. La reserva
BA3 tardía de MAIN falla; los registros permiten examinar el destino ocupado y
la precedencia de su evolución sobre el encuentro esperado. Las realizaciones
auxiliares exitosas no se convierten en transferencia semántica de E1.

También se preserva la separación entre memoria y lector: algunos accesos de
conteo fallan bajo un criterio de fase y vuelven a aparecer en T1287/T1354 sin
atribuir una nueva enseñanza. No toda consulta fallida demuestra olvido, ni
toda presencia material demuestra conocimiento accesible.

## 4. Comunicación, consulta y regulación — C06–C08

Existe un recorrido físico acotado E1→B→E1 con respaldo adquirido por entradas
propias, comparación en B, retorno, nueva asociación y uso posterior. Los
portadores viajan por v27, no mediante copiar una respuesta desde un callback.

Los controles son asimétricos y deben mantenerse: cortar el mensaje positivo
deja una respuesta negativa residual; el corte negativo conserva su dirección
pero cambia 44 a 32. Es comunicación/uso físico finito, no prueba de diálogo
lingüístico general ni de que B sea una segunda mente completa.

La recepción modifica una consulta posterior: el corte selectivo del retorno
cambia la compuerta T210 de un portador activo 28 sin dirección a la emisión
de pregunta de carga cero y dirección (1,−1,0). El cero es un portador activo,
no silencio. Otras funciones testigo permanecen. La pregunta reaparece T277;
las oportunidades periódicas y el destinatario estaban preparados. No se
demostró selección general aprendida de fuentes, curiosidad ni agotamiento.

La regulación R0 preparada y R1 dependiente del estado adquirido tienen
efectos finitos. En el contraste integrado, la salida T137 cambia −X a +X
con el aporte fuera de ruta. No se demostró en E1 regulación R2, entendida
como selección de estrategia modificada por consecuencias anteriores.
Esto no anula otras realizaciones históricas/auxiliares de diferente dominio.

## 5. Las 65 primitivas — C13, C15

El CSV contiene las 65 identidades del catálogo oficial recuperado. Separa
las dimensiones originales A–J de una lectura crítica actual. El recuento de
niveles **originalmente adjudicados** es 60 E0, cuatro E2 y un E3. No son cinco
conceptos humanos completos ni cinco relaciones disponibles al final T2493.

Las cinco candidatas operacionales son DOS calibrado, ANTES, TOCAR, COMO
direccional y MÁS cuantitativo. En particular, E3 de MÁS describe uso reservado
de una referencia aprendida en un comparador preparado: no aprendizaje de la
ley comparativa ni dominio de la palabra. La composición positiva de ANTES/TOCAR
se conserva como dimensión específica, sin elevar automáticamente a E4/E5.

Catorce entradas tienen ensayos de función limitada o prerrequisitos; otras
51 no tienen adquisición semántica ejecutada. YO/TÚ sólo tienen prerrequisitos
auxiliares de participación causal, no signo deíctico aprendido con intercambio
de roles. NO no se acredita por silencio, cero ni inversión de dirección.
Ausencia de demostración no equivale a una refutación universal del kernel.

## 6. Continuidad CPC1–CPC8 — C14

Las 56 filas históricas se mantienen separadas de las doce nuevas: 39 C
(reproducción individual registrada), una B (auxiliar) y 16 D (documentadas,
sin nueva reproducción completa del dominio). La matriz total de 68 filas
conserva además ocho A, tres B en total y dos E condicionadas. Son filas de
procedencia/función, no cantidades de conceptos o de individuos.

Se incluyen los datos y actas de las 34 familias de recuperación previas, con
sus controles y adversos. El nuevo contraste genérico no acepta esos PASS
como sustitutos de datos: coteja 148 pares vinculados por identificador exacto,
con 124 pares que contienen todas las huellas históricas comparables. Suman
1071 coincidencias de RAW/clocks/tick **contabilizadas por par**, en 23 familias;
no son 1071 réplicas independientes. Los otros 24 pares no ofrecen ese formato
comparable de huella completa; no se declaran fallos físicos. Las demás familias
mantienen sus registros y comprobadores específicos para revisión, sin una
certificación genérica nueva. No se ejecutó otra reproducción física aquí.

Las 16 filas D están enumeradas en los cálculos y en la matriz, con fuentes y
límites: compendios de Ingenierías/Procesos, observadores, Física/MetaRosetta,
contrato amplio 4.0, alcance NSM histórico y CORE15–17, entre otros. Recalcular
un resultado particular no demuestra el dominio entero del compendio.

## 7. Lectura epistemológica y límites

HECHOS COMPUTACIONALES: bytes/valores identificados, recuentos y comparaciones
repetibles. MECANISMOS INTERNOS: transporte, encuentros, fase, registro,
reducer/DEMUX y precedencia de ocupación según las observaciones declaradas.
FUNCIONES: adquisición dependiente de historia, conservación/uso finitos,
revisión, composición dirigida y comunicación condicionada.

La interpretación cognitiva y las correspondencias NSM son operacionales.
Generalidad, lenguaje abierto, conciencia y equivalencia DEE–realidad no quedan
establecidos. Las analogías biológicas no son mecanismos demostrados.

La campaña es principalmente determinista. Restauraciones y reproducciones
técnicas no son individuos independientes. Los datos no justifican significación
estadística poblacional, estabilidad ilimitada ni superioridad tecnológica.

El paquete permite auditar datos y cálculos sin motor. No permite una nueva
evolución nativa autosuficiente: para ello hacen falta el instrumento oficial,
el Core completo y los estados/configuraciones operativos indicados en origen.

## 8. Cómo revisar

1. Leer `HALLAZGOS_CONFIRMADOS_Y_LIMITACIONES.md` y la auditoría de interferencias.
2. Consultar C01–C15 en `AFIRMACIONES_Y_EVIDENCIAS.json`.
3. Buscar el ID/miembro/SHA en `INDICE_EVIDENCIA_ORIGINAL.csv`.
4. Decodificar el documento con `CONFIGURACIONES_Y_REPRODUCCION/codec.py`.
5. Recalcular con `recalcular_esencial.py` en una carpeta nueva.

El manual de esa carpeta especifica los comandos, las fórmulas y las evidencias
que permanecen exclusivamente en los originales. Esta auditoría no autoriza
eliminar ninguno de ellos.
