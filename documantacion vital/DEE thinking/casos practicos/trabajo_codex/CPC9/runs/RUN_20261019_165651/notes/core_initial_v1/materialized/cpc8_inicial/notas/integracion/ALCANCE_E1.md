# Integración física K65 y U0: lectura de los resultados

Este documento pertenece a CPC8. Los datos primarios están en `resultados/integracion/<caso>/MEASUREMENTS.json`; sus snapshots y cortes exactos de código quedan junto a cada registro. `INDEX_INCREMENTAL.json` y `ANALYSIS_INCREMENTAL.json` son cálculos posteriores, no entradas del participante.

## Capacidad conservada y primer acceso integrado

E1 prepara desde T0 un Runtime N131 con las 65 correspondencias inferiores y dos bancos propios adicionales. En E1_P11_AB se adquieren 32 correspondencias en T0, se consultan en T134, se adquieren otras 33 en T262 y se consultan las 65 en T396: 32/32 y 65/65 lecturas cubiertas y concordantes con las experiencias. E1_R211_BA conserva 65/65 también en T658. Ningún cuerpo entrenado se trasplanta al mundo.

La misma dinámica contiene la cadena de U0: pregunta física en T19, encuentro con información en T134, producto de acción en T136 y asociación posterior en T139. La consulta opaca posterior produce una lectura en T270. La demostración inicial acredita coexistencia con dos bancos propios; no acredita selección entre las 65 correspondencias.

La segunda y tercera preparaciones hacen que la pregunta LEFT alcance la correspondencia real L17. L17 se adquiere mediante su señal y acontecimiento en T0; no se enseña además una memoria U.left equivalente. El lector externo de L17 en T131 se omite para no duplicar esa consulta. En RL_P11_BA, la lectura física propia T134 es (-1,+1,0), la acción T136 es (-1,+1,+1), y la señal asociada conserva +1 en T270, T401 y T663. La reserva RL_R709_BA_MINUS cambia el contenido experimentado y conserva -1 en esas tres ventanas, manteniendo el mismo codificador y lector.

## Contrastes de historia, acceso y consumo

RL_N11_NO_CUE presenta el acontecimiento sin señal de asociación; RL_N13_UNPAIRED conserva las dosis de señal5 y acontecimiento11 pero los desfasa un tick. Ninguno produce la lectura opaca T270/T401. RL_H11_AB_MATCH cambia la historia del cuerpo manteniendo la señal actual +1 y no expresa esa lectura. Son distinciones entre historias y acceso, no una estimación de inteligencia.

En RL_D11_CUT se corta externamente la pregunta en un fork diagnóstico T20, conservando clocks y el MAIN padre. Desaparece la lectura opaca, pero la memoria L17 se consulta después por su puerto original en T396. El sham idéntico reproduce el padre en RAW, clocks y tick de las fronteras comunes T134/T270/T396/T401 y en los recibos pasados. El padre largo termina T663; no se compara ese final con el sham corto T401.

Un control adverso indispensable es E1_N11_UNPAIRED: RIGHT conserva una respuesta pese a la asociación desfasada. Su portador balístico vuelve tras un período toroidal y se combina con la pregunta +X, conservando el componente Y. La carga informativa es48 en ese control y53 en la experiencia emparejada. Ese resultado impide atribuir toda respuesta RIGHT a la asociación; la nueva pregunta LEFT cancela el componente X balístico y permite el contraste de adquisición de L17. No se cambió el decoder para borrar este contraejemplo.

## Geometría y recursos: tres familias, no cuatro

1. E1: 65 bancos inferiores distantes +2 propios; 67 correspondencias preparadas, 21 sitios materiales iniciales, 218 interfaces.
2. Alias directo: columna inferior cercana al cuerpo con L17=LEFT +1 propio; 66 correspondencias preparadas, mismos21 sitios materiales, 215 interfaces. Conserva61/65 consultas inferiores T396/T658 y la función derivada L17.
3. Reubicación selectiva: sólo L17 está en LEFT, los otros64 permanecen distantes; mismo inventario que el alias directo. Conserva63/65 consultas inferiores T396/T658 y la función derivada L17.

La tercera preparación recupera los accesos L18/L21 que faltaban en el alias directo, con igual número de soportes y dosis. L15 sigue sin respuesta adecuada por su interfaz original; no se ha localizado completamente su causa. L17 es consumida/transformada por su uso y su puerto original no sigue siendo un lector equivalente. Su posterior expresión opaca conserva una función derivada, no la promesa de mantener intacto cada portador.

Las cuatro interfaces neutras de actualización L01 constituyen una revisión del protocolo de la tercera familia, sin nueva materia inicial ni una cuarta familia física. El piloto UP_P11_M1 conserva los estados físicos completos de RL_P11_BA hasta T401, adquiere una consecuencia opuesta para L01 mediante el protocolo M1 explícito en T524 y la consulta en T658. Los controles y la reserva de ese protocolo están especificados en REVISION_L01_FROZEN.json y sus resultados se contabilizan separadamente; no se atribuye al ente la elección de qué o cuándo revisar.

## Revisión posterior sin perder otros usos

Los cinco casos de REVISION_L01_FROZEN finalizaron T663. UP_P11_M1 cambia L01 de +1 (T134/T396) a -1 (T658); UP_R811_OPPOSITE conserva el mismo método y cambia -1 a +1, con una historia reservada. En ambos, se cubren63/65 interfaces inferiores en T658: L01 revisada y62de64 restantes. La función derivada de L17 conserva su signo anterior en T663, sin reenseñarla. No se cuenta dos veces L17 por estar también representada en la lectura opaca.

UP_C12_NO_UPDATE conserva L01=+1. La nueva pareja ordinaria sin segundo docente (UP_C13_ORDINARY), y la misma dosis con ese docente fuera de la ruta (UP_C11_OFFPATH), dejan un registro activo de dirección(-1,0,0) y carga50; la entrada de consulta655 resulta `rejected_occupied`. No se convierten esos estados en respuesta cero ni en una inversión correcta. Estos brazos separan la conservación sin nueva experiencia, la interferencia por enseñanza ordinaria y el método M1 situado físicamente. Los estados completos hasta T401 coinciden con el padre de referencia para los brazos emparejados de semilla11.

## Control específico de la asociación opaca

RN_C11_NAME_OMITTED y RN_C12_NAME_UNPAIRED conservan la misma adquisición de L17, pregunta y acción física T136 que RL_P11_BA. El primer caso no presenta las cuatro señales de enseñanza del nombre. El segundo conserva cuatro cargas5 y puertos idénticos, pero aplica las entradas en T137 para su contacto nominal T140, en vez de T136→139.

Ninguno obtiene una lectura cubierta por el decoder congelado en T270/T401. Es importante conservar la distinción: el caso desfasado **no está vacío**. En el sitio `left.plus` aparece en T270 un producto(-1,+1,+1), carga69, y en T401 carga78, clasificado `OUTSIDE_DIRECTIONAL_DECODER`. El caso emparejado había normalizado el componente Z y producido un lector(-1,+1,0) utilizable. La diferencia temporal cambia una función concreta; no se presenta el retorno balístico del control como palabra aprendida ni se oculta su actividad física.

## Reconciliación del corte E1, antes de la continuación desde T690

La línea de integración cierra27 registros científicos:21 preparaciones independientes y6 forks diagnósticos, además de1 reproducción técnica desde el snapshot inicial E1. Las dos colas supervisadas A/B finalizaron y no quedaron procesos propios. El replay técnico reproduce RAW, clocks y tick en T0/T20/T134/T270/T396 y todos los campos de recibo y ticks de llamada; no añade una réplica científica independiente. La restauración y reproducción de la aplicación desde UP_P11_M1/T401 son tareas del cierre general, no otros aprendizajes atribuidos a esta cohorte.

La extensión posterior autorizada desde SOC_I21/T690 se conserva aparte en `LONGITUDINAL_690.md`: añade4 continuaciones controladas y1 replay técnico, sin sumar preparaciones independientes ni una cuarta geometría.

## Observación y atribución

Todas las respuestas anteriores proceden de la evolución del motor oficial4.5 y lectores nativos en sitios e interfaces declarados. El laboratorio prepara currículos, calcula coberturas después de evolucionar y presenta las lecturas; no lee targets ni un mapa de enseñanza para responder por el participante. Los estados completos se guardan en fronteras causales, los vecindarios Moore27 cubren ventanas declaradas y no justifican genealogías fuera de esas ventanas.

Las 65 correspondencias inferiores utilizan dos clases direccionales. No son65 significados NSM,65 relaciones abstractas ni un selector general de conocimientos. La asociación opaca posterior conserva un contenido local y una ventana de uso específicos; su ampliación lingüística requiere controles propios.
