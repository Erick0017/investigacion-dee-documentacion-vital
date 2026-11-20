# Consecuencia nativa, selección de regulador y acceso posterior

Una consecuencia física local modifica una política finita por R14; el producto seleccionado se desvía por seis oportunidades neutras preparadas desdeT0 y neutraliza un residuo antes de que altere una comparación posterior. No hay callback que lea la respuesta para escribir el contraflujo.

## Datos y contraste

| Mundo | Medio actual | Referencia adquirida | Ruta | Operandos exactos137 | Lectura70/137 |
|---|---:|---:|---|---|---|
| RCA_C01_OFFPATH_HIGH | 1 | 31 | offpath | 43/50 | correcta/fuera del criterio |
| RCA_C02_OFFPATH_LOW | -1 | 11 | offpath | 16/57 | correcta/fuera del criterio |
| RCA_D01_PLUS_HIGH | 1 | 31 | onpath | 36/50 | correcta/correcta |
| RCA_H01_MINUS_HIGH | -1 | 31 | onpath | 43/50 | correcta/fuera del criterio |
| RCA_H02_MINUS_LOW | -1 | 11 | onpath | 16/50 | correcta/correcta |
| RCA_H03_PLUS_LOW | 1 | 11 | onpath | 16/57 | correcta/fuera del criterio |
| RCA_R101_PLUS | 1 | 17 | onpath | 22/36 | correcta/correcta |
| RCA_R102_MINUS | -1 | 17 | onpath | 22/50 | correcta/correcta |
| RCA_R201_FUNCTION_PLUS | 1 | 31 | onpath | 36/42 | correcta/correcta |
| RCA_R202_FUNCTION_MINUS | -1 | 31 | onpath | 43/42 | correcta/fuera del criterio |
| RCAM_C01_OFFPATH_HIGH | 1 | 31 | offpath | 43/50 | correcta/fuera del criterio |
| RCAM_D02_CONTINUED_FROM4 | 1 | 31 | onpath | 36/50 | correcta/correcta |
| RCAM_H01_MINUS_HIGH | -1 | 31 | onpath | 43/50 | correcta/fuera del criterio |
| RCAM_H02_MINUS_LOW | -1 | 11 | onpath | 16/50 | correcta/correcta |
| RCAM_H03_PLUS_LOW | 1 | 11 | onpath | 16/57 | correcta/fuera del criterio |
| RCAM_R101_PLUS | 1 | 17 | onpath | 22/36 | correcta/correcta |
| RCAM_R102_MINUS | -1 | 17 | onpath | 22/50 | correcta/correcta |
| RCAM_R201_FUNCTION_PLUS | 1 | 31 | onpath | 36/42 | correcta/correcta |
| RCAM_R202_FUNCTION_MINUS | -1 | 31 | onpath | 43/42 | correcta/fuera del criterio |

Con referencia31 y primer objeto16, P conserva36/50 en la segunda comparación; Q deja43/50. Con referencia11, Q conserva16/50, mientras P deja16/57. Los shams de material y las rutas desplazadas conservan dosis y muestran que no basta añadir un portador. Las reservas precongeladas usan referencia17 y objetos nuevos: ambos contextos pertinentes conservan22 y los objetos físicos correspondientes.

El escalar de salida es7 y la segunda dirección es−X incluso en los primeros controles con operandos dañados. Los10 cortes anteriores (dentro de20 forks:10cortes+10shams) alteraron exactitud de operandos, no la dirección de respuesta137. Por eso se conservan ambos indicadores separados: respuesta direccional y estado adquirido pertinente.

### Contraste funcional posterior, congelado antes de ejecutarse

Con la misma geometría/cadencia/lector, se presentó referencia31 y un nuevo segundo objeto37: los operandos verdaderos son36 y42. P preserva36/42 y emite−X; Q deja43/42 y emite+X. Esto ocurrió tanto en AUX como en los nuevos mundos completos. Un corte selectivo del contraflujoP114@77 reproduce43/42,+X; el sham conserva36/42,−X. Aquí sí se modifica la respuesta a la misma consulta, además de las magnitudes. Son4 preparaciones focales y2forks adicionales, no reservas confirmatorias del factorial inicial; los resultados adversos previos no fueron sustituidos.

## Cadena causal y persistencia

Se registraron retorno1@4, comparación86@5, política97@9, acción114@10, desvío11, contraflujo114@77 y producto121 dirección0@78; el registro desaparece79. Las cuatro ablaciones selectivas (retorno4, política9, acción11, contraflujo77) en dos historias AUX producen8 pérdidas de exactitud137; los8 shams conservan estado físico y recibos141 completos. Los clocks de los campos intervenidos, la cola y el padre permanecen preservados.

En los dos nuevos mundos completos seleccionados para diagnóstico inicial, cortar el contraflujo77 también cambia causalmente los operandos137; sus shams son exactos. En el contraste funcional posterior cambia además la dirección. A616 los tres cortes de contraflujo de los mundos completos vuelven a coincidir con todo el RAW/clocks/tick y recibos de su respectivo padre, pese a la diferencia intermedia. Las cuatro restauraciones técnicas (dos AUX y dos completas) continúan sin nuevas entradas y conservan estado final y recibos. No se devolvió ningún fork al MAIN.

## Candidato compuesto y continuidad separada

El candidato añade37 materiales y7 interfaces a la receta MCTS35, siempre antesT0:72 materiales/138 interfaces, un RuntimeN67,179 solicitudes. El regulador protege el NUEVO comparador R.quantity centrado en(2,12,36), con su propia referencia adquirida; no se demostró regulación porV2 del comparador cuantitativo originalMCTS. Es otra genealogía, no una mejora retroactiva del individuo seleccionado MCTS_P01_SOURCE31. Se midieron nueve historias completas, incluidas dos del par focal posterior; una fue recuperada del snapshot4 tras un fallo de metadatos y no cuenta como otra preparación.

Las39 firmas publicadas de orden, consultas/contactos pertinentes, composición206/281/348/415/549/616, cantidad principal, MODE428, solicitud/retorno temprano, comunicación554/uso559/entrega563 y transferencia de magnitud son39/39 iguales por candidato en sus campos y ventanas. Existen diferencias físicas intermedias reales en registros residuales de contacto/joint; no se sustituyen por una afirmación de igualdad global. La variante offpath además cambia una lectura pasiva de iniciativa428, fuera de la ventana de uso86/89. El archivo conserva los valores exactos y sus localizadores.

La continuidad operativa tampoco se declara idéntica a la preparación menor:179 solicitudes producen152Applied/27Occupied. La solicitud originalID123, contact.renew.left.changed@477, pasa deRejectedOccupied aApplied en los candidatos completos, incluidooffpath. Las ocho solicitudesR.quantity producen7Applied/1Occupied. La mejora de esa admisión antigua se registra como interacción compartida de la preparación, no como efecto demostrado de selección por consecuencia.

## Preparación, experiencia y contratos

El medio actual se distingue por su dirección física a igual inventario; la referencia cuantitativa procede de entradas reales cue5+valor. El esquema R14, la expectativa, los seis recorridos y las oportunidades son diseño preparado. La consecuencia física recibida modifica la selecciónP/Q posterior y, por ella, qué contraflujo protege el acceso137: selección local dependiente de consecuencia, con evidencia positiva finita. El cruce de contextos delimita que no aprende cuál selección resulta útil ni reajusta la regla por la utilidad posterior137. Esa frontera no elimina la selección causal efectivamente observada. No se añaden significadosNSM acreditados por este aparato.

El desvío11 sustituye el contrato de entrega originalV2@15: aquí los cuatro registros de entrega son0, no3. La referencia literalV2 y su coexistenciaCMCTS continúan documentadas por separado. El lector69 es admitido; el segundo intento136 es rechazado por ocupación. El uso137 acredita acceso posterior con lector persistente, no dos lectores renovados.

## Intentos y reproducción

Se cuentan10 preparacionesAUX y9 historias completas recuperadas/terminadas, más1 Runtime construido y descartadoT0 por un nombre de canal duplicado:20 intentos de preparación física. Este último no recibió currículo ni avanzó. El fallo posterior de metadatos conservó una preparación0→76, snapshots0/4 y código exacto; la continuación4→616 corresponde al mismo individuo. Se repararon sólo nombres de canal y almacenamiento de una traza opcional, nunca física. Los frames completos permanecen en JSON; no se duplican en los metadatos operativos acotados.

El JSON reconcilia22 forks(11cortes/11shams),4 restauraciones,1 continuación de recuperación y2 avances4→9 de padres instrumentales; no son réplicas independientes. Hay22 contenedores primarios finales y2 directorios de intentos. Los procesos propios terminaron y cerraron sus jobs. Fuentes exactas, configuraciones previas, estados indispensables y comandos están enlazados conSHA-256.

Desde una extracción independiente, el worker `tools/reproducir_regulacion_acoplada.py` acepta `--condition plus` o `minus`, `--reference` al primario correspondiente y `--out` externo nuevo. La referencia se lee sólo después de construir/evolucionar el mundo y restaurar77→616. No usa un resultado guardado como respuesta. El trabajador de validación limpia registrará su ejecución por separado.
