# Alcance cientifico del habitat Mente Basal

## Contrato del mundo

Mente Basal usa DEE thinking 2.2.0 y el kernel DEE v27 congelado como motor. El dominio es un cubo `N=127`; las coordenadas de la preparacion se calculan modulo N. RAW, clock, colas, recibos, canales, organizacion, materia y entorno pertenecen al mismo `Runtime`. Los nombres de regiones describen papeles operacionales y no motores separados.

X0 se guarda en tick 0 **antes** de presentar las entradas iniciales. Un segundo checkpoint de tick 0 conserva esas entradas ya programadas. Esta diferencia permite distinguir capacidad instalada, experiencia admitida y transformacion posterior sin reconstruir el mundo entre bloques.

El backend operativo es `LAZY` con un hilo. La comparacion densa es un control de implementacion en un mundo de prueba separado, no otra fisica ni una fuente de datos que se copie al linaje principal.

## Mecanismos instalados en X0

La preparacion contiene:

- un linaje relacional central con union, consecuencia, programa, redireccion, tres sitios de respuesta y dos sitios de revision;
- cuatro estaciones de coincidencia ambiental asociadas a fases sucesivas y un portador de actualizacion reutilizable;
- campos locales de soporte observacional en las estaciones y un soporte remoto para el segundo contexto;
- dos rutas de materia movil, `matter.route.alpha` y `matter.route.beta`, que convergen en un hub auxiliar inicial;
- una ruta de suministro contextual y un canal de experiencia tardia que convergen en otro hub;
- rutas explicitas de consulta y redireccion para lecturas antes y despues de los encuentros;
- un puerto generico `external.port.alpha` para experiencias externas declaradas;
- lectores pasivos de RAW, clock, ocupacion, direccion, estado y `s_reg` en sitios congelados, mas metricas agregadas del Runtime.

Estos elementos son organizaciones persistentes en el dominio declarado. No se denominan muros, espejos, fuentes infinitas o sumideros porque esos contratos funcionales no han sido establecidos. Los campos de soporte no son decorado restaurado: forman parte de X0 y despues quedan sujetos a la misma dinamica. `s_reg` es un registro del record DEE, no energia ni temperatura.

## Dos bloques sobre una sola continuidad

### Bloque 1: relacion, regularidad ambiental y encuentro material

En tick 0 se programan entradas finitas. El cue y teacher relacionales llegan a la union en tick 5; el suministro y marcador del puente, en tick 8. Los cuatro pares ambientales alcanzan sus estaciones antes de los encuentros del portador en ticks 14, 18, 22 y 26. Las dos rutas de materia alcanzan el hub inicial en tick 16; la ruta de linaje, en tick 18; y la redireccion de actualizacion, en tick 30.

La consulta basal se lee en `response1` en tick 34, antes de la lectura de revision ambiental en tick 38. El tick 40 cierra la ventana previa a la segunda experiencia. Todo avance entre admisiones se debe a v27; las entradas preparadas siguen siendo intervenciones externas registradas, no estimulos nacidos espontaneamente.

### Bloque 2: contexto tardio y comprobacion posterior

En tick 40 se programa el bloque tardio. La primera consulta posterior alcanza `response2` en tick 46, antes del encuentro contextual. El suministro y la experiencia contextual convergen en tick 48; la ruta de redireccion se observa en tick 50; y una consulta posterior alcanza `response3` en tick 58. El corte cientifico inicial esta previsto en `T_ref=64`.

El orden ofrece dos contrastes acotados: volver a leer una via asociada al primer bloque antes del nuevo encuentro, y leer otra respuesta despues del contexto tardio. No presupone una progresion `A`, `A+B`, `A+B+C`. Retencion, interferencia, sustitucion, inaccesibilidad o ausencia de respuesta siguen siendo resultados posibles.

## Que esta instalado y que tendria que adquirirse

Estan instalados desde X0 la geometria, los soportes, los canales, los lectores y la posibilidad de que los portadores coincidan. Tambien estan declaradas de antemano las cargas iniciales y sus ticks solicitados. No esta instalada como dato una respuesta nueva por episodio ni se inyectan la etiqueta del regimen, el estado global o el resultado esperado.

Una distincion adquirida durante la experiencia solo puede atribuirse si una lectura funcional cambia respecto de una referencia pertinente, sobrevive a una comprobacion posterior y supera controles de historia u orden que excluyan explicaciones triviales. Que dos estructuras coexistan, que RAW cambie o que un sitio tenga `s_reg` distinto de cero no basta. Un cambio de admision puede indicar accesibilidad diferente sin demostrar transformacion del contenido.

## Evidencia que el habitat puede sostener

Con sus registros y checkpoints se puede establecer:

- la trayectoria exacta de tick, RAW y clock en los cortes guardados;
- que una entrada fue recibida, programada, aplicada en cierto tick o rechazada con causa;
- las lecturas pasivas en los sitios y ticks cientificos predeclarados;
- persistencia o cambio entre X0, checkpoints intermedios y `T_ref`;
- reproducibilidad de una ventana cuando replay coincide exactamente con el checkpoint esperado;
- aislamiento de una rama diagnostica respecto del linaje principal;
- equivalencia del backend denso y el exploratorio solamente en el caso y corte efectivamente comparados.

Las observaciones son datos registrados o estados reconstruidos. Una explicacion causal requiere ademas un contraste que retire, reordene o simule de forma controlada el mecanismo candidato. La interpretacion debe identificar siempre cual de esas categorias respalda cada afirmacion.

## Lo que no queda demostrado automaticamente

El habitat y una evolucion exitosa no demuestran por si solos aprendizaje, memoria funcional, inteligencia, autonomia investigadora, eco, causalidad unica ni generalizacion. Tampoco convierten tiempo de pared en tiempo DEE. Mas ticks libres pueden mostrar persistencia, saturacion, congelacion o extincion, pero no implican mejora.

En particular:

- variacion de RAW, clock, direccion, ocupacion o `s_reg` es cambio fisico observado, no aprendizaje por definicion;
- mediacion ambiental F2 no prueba un eco;
- dos respuestas presentes no prueban que sus funciones se combinen;
- una diferencia entre dos mundos no prueba experiencia como causa si edad, inventario y orden no estan controlados;
- una lectura nula no establece incapacidad general de v27, solo ausencia de la respuesta medida bajo esta preparacion;
- una lectura favorable en una rama diagnostica no puede devolverse al principal ni presentarse como su historia.

Las conclusiones cientificas del primer corte deben limitarse a los valores realmente observados y a las pruebas realmente ejecutadas. Si no aparece una distincion funcional contrastada, el resultado valido es la historia experimentada y reproducible, no una afirmacion de aprendizaje.

## Observacion, diagnostico y continuidad

La telemetria periodica y los lectores congelados son pasivos. `evaluate` carga un checkpoint aparte y declara expresamente una lectura diagnostica sin afirmacion de aprendizaje. Replay reconstruye con el contexto completo del mundo y produce otro checkpoint en `analysis`; no recorta una region para tratarla como universo independiente.

Una sonda o consulta aplicada al mundo principal es transformativa y pasa a su historia. Las pruebas interventivas deben originarse en un checkpoint como rama diagnostica, registrar padre, motivo y diferencias, y nunca reemplazar ni fusionarse con el linaje principal.

Despues de agotarse las entradas finitas preparadas, la politica declarada es evolucion libre. El worker solo ejecuta v27, registra, guarda y vigila recursos. No selecciona estimulos para obtener una respuesta deseada, no restaura materia y no cambia resolucion o fisica para sostener una apariencia de aprendizaje.
