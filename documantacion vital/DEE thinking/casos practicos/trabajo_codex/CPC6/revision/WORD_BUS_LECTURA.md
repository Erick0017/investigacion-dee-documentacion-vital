# Reutilización de FORMA_01 después de FORMA_02

Una nueva provisión física de lector, preparada antesT0 y estimulada igual en ambos bancos candidatos, permitió consultar de nuevo el contenido de FORMA_01 después de adquirir y consultar FORMA_02. La secuencia efectiva del mismo MAIN es53→80/90→117/162: primer uso, segunda asociación/consulta, nueva solicitud del primer protocolo y respuesta tardía. No hay limpieza ni restauración favorable entre esas operaciones.

En las reservasR03, con cargas y código de fuentes variados antes de ejecutarlas, la misma carga de respuesta11 expresa contenido diferente mediante dirección: Q− produce(−1,0,−1), Q+ produce(+1,0,−1) en162. Los pares BA/Q− y BA/Q+ conservan el resultado de FORMA_02 mientras cambia el de FORMA_01; BA/Q− y AB/Q− conservan FORMA_01 mientras cambia FORMA_02. Son dos contrastes de separabilidad sobre tres celdas, no una consulta semántica conjunta nueva.

El decoder discoveryV1 utilizó−dx y leyó al revés esos vectores. Sus discrepancias se conservan. V2 utiliza dx, se congeló antes de las reservasR03 y sus resultados no sustituyen retrospectivamente los erroresV1. El primer suministro remoto no expresó la firma en95; el acceso comprobado es el segundo,162. No se infiere acceso arbitrario de un único horizonte.

## Causalidad del nuevo lector

En `WORD_BUS_CONTROLS_01`, cortar sólo el portador neutral ya emitido en160 elimina el registro de respuesta162 y conserva deltaR2=+1. El shamRAW idéntico reproduce exactamente el registro parental. Así,162 requiere una interacción física nueva: no es únicamente una lectura del campo que ya estaba emitiendo sin la nueva solicitud. El control sin repetición y el de enseñanza del primer nombre desacoplada tampoco expresan esa respuesta; en este último sigue funcionando FORMA_02.

La igualdad escalar no describe todo el mecanismo. En el otro padre, igualar solamente A.s_reg aB.s_reg en160 lleva deltaR2 a0, pero deja intacto el registro(+1,0,−1) de162. En cambio, la igualdad antes de la lectura temprana94 cambiaba la respuesta97. La necesidad causal de una coordenada depende del lector y la etapa: el uso tardío conserva información en contexto físico más rico que la sola diferencia de cargas. No se ha localizado una región única de memoria mediante este contraste.

El nuevo recurso y el transporte pertenecen a la preparación y la evolución; la asociación requiere historia. El renderer comunica el vector y el identificador del protocolo. Se sostienen dos asociaciones opacas locales y reutilización posterior de la primera, no dos primitivasNSM generales, composición gramatical o un lector renovable ilimitado.

Evidencia: `resultados/R03_WORD_BUS_V2/INDEX.json`, `resultados/B01_WORD_BUS/INDEX.json`, `resultados/WORD_BUS_CONTROLS_01/INDEX.json` y `revision/NSM65_EVIDENCIAS.json`.
