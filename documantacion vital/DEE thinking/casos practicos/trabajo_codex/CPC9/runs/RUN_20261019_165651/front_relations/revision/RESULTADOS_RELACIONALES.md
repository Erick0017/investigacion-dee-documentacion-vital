# Resultado del frente auxiliar: contacto, orden y adquisición receptora

## Capacidad observada

Se obtuvieron dos reparaciones físicas útiles y una extensión de comunicación: un acceso remoto a la historia de contacto que antes se perdía por ocupación de ruta; una nueva adquisición sensible al orden de dos acontecimientos físicos actuales; y transmisión de su contenido hacia una región receptora que lo utiliza después. Las preparaciones son auxiliaresN67 y no se atribuyen por suma documental a E1. El ejecutor principal conserva por separado su integración real.

Cada afirmación remite a `resultados/<caso>/MEASUREMENTS.json`; los índices, firmas y localizadores se recalculan en `revision/CONTACT_ACCESS_RECALCULO.json` y `RELACIONES_RECALCULO.json`. Los scripts de cálculo no son importados por el participante.

## Contacto: conservación frente a ocupación

La historia tardía produce en340 un portador distinto en condiciones de contacto o trayectoria libre. Un acceso nuevo343 intenta conservarlo sin usar el hub antiguo344. El acceso nuevo sin protección falla: el portador de memoria22 llega a su siguiente destino350 cuando ese sitio estaba ocupado en349 por un recurso antiguo7 de otro uso. La rama de material ocupado tiene precedencia; no se aplica el DEMUX de destino vacío y apareceRAW0.

El métodoG introduce cuatro contraflujos fijos de carga0. Uno encuentra el recurso antiguo7 en348 y deja una configuración estacionaria que desaparece349. El destino está vacío para recibir la nueva memoria350. Son oportunidades preparadas iguales en todos los bancos, no una decisión de regulación aprendida.

Datos principales:

-`RC_G01_FREE_ONPATH`: memoria343(0,1,-1),22; consulta410(-1,1,-1),27; uso416(0,1,-1),34.
-Historia de contacto: mismo protocolo y recursos, pero componenteZ0 en esas firmas.
-Contraflujos fuera de ruta: sólo lector5 en410 y recurso7 en416; no recupera el contenido.
-Reservas: libre con dosis23 produce28→33→40; contacto con dosis11 produce16→21→28; orden inicial cambiado conserva22→27→34. Cada reserva es una vida nueva con su propia asociación.
-Omitir la señal, desacoplarla o cortar sólo la memoria adquirida343 elimina la lectura y uso calificados; el sham y restauración en otro proceso a partir de343 conservan RAW/clocks completos en616.

Límite: la segunda renovación477/483 no quedó cerrada. EnG la firma recibe además un resto de señal antiguo y pierde un componente direccional. El tercer métodoH, guardas materiales preparadas, mejora un lector477 en la condición libre, pero no restaura el uso483 ni ambas historias. G es la solución parsimoniosa para una lectura y un uso en la ventana comprobada. No se anuncia acceso ilimitado ni atención adquirida.

## Orden: tres familias y una corrección mecánica

### F1: exportar el transitorio tardío

El cuerpo heredado distingue momentáneamenteAB/BA en470 y colapsa en471. La intervención de exportación separa la corriente del cuerpo, pero no obtiene una relación de orden completa: omitir el segundo acontecimiento todavía produce la señal e incluso un uso favorable. Además, los positivosF1 perturban la antigua entrega616: las salidas esperadas115 cambian a7 o43. Se conserva este fallo de integración, no se adoptaF1.

### F2: encuentros contrapropagantes

Dos acontecimientos con direcciones+X/−X y una oportunidad+Z de carga0 producen en477 un resultado móvil6+Z en un lugar diferente según su orden. Una señalposterior481 conserva11+Y; consulta548 produce18(X+,Y+); recurso554 produce29(X+,Y+,Z+). Las dos historias y nuevas dosis reproducen la distinción; omitir un acontecimiento o sustituir ambos por un solo portador de igual carga no produce la firma completa.

El fondo de un banco sin información es5→12→23 y puede conservar las mismas direcciones. No es silencio ni éxito: la firma exige carga y dirección completas. El intervalo3 con la geometría y oportunidad del intervalo5 falla; es un límite de la preparación, no del kernel. Cortar sólo la memoria481 elimina el uso29, manteniendo al resto del aparato capaz de responder. Sham y restauración481→616 producen RAW/clocks completos idénticos al positivo.

### F3v1: forma física multicomponente

Una forma actualA de un portador y una formaB de seis portadores reales permiten que el lugar de encuentro cambie con los intervalos1/3/5 sin retimar geometría, señal482 ni lectores549. La adquisición482 tiene la firma correcta en las variantes, pero algunos lectores y recursos se bloquean entre bancos adyacentes. Ejemplo: ABintervalo3 adquiere11 en482 y no puede leerlo549; BAintervalo1 lee18 pero falla el uso555. No se informa como olvido.

### F3v2: lectores paralelos

Una corrección preparada desdeT0 cambia todos los lectores a+Z y todos los recursos de uso a−Y. Ningún banco es seleccionado según el resultado. Mantiene sin cambio acontecimientos, seis señales, fechas, cargas y materia inicial. Los intentosv1 adversos permanecen.

Seis condiciones completas resultan positivas con el mismo aparato:

-ABintervalo5: banco+5,11→18→29.
-BAintervalo5: banco−5,11→18→29.
-ABintervalo3: banco+3,11→18→29.
-BAintervalo1: banco−1,11→18→29.
-ReservaABintervalo1 con cargas13/17: banco+1,35→42→53.
-ReservaBAintervalo3 con cargas19/23: banco−3,47→54→65.

La memoria482 tiene direcciónY+, lectura549Y+Z+, uso555Z+. OmitirA, omitirB, desplazarB fuera de ruta con igual material, omitir la señal, desfasarla un tick o reemplazar todos los acontecimientos por una sola contribuciónA21 elimina la firma calificada. Cortar sólo la memoria482 produce lector7+Z y uso11−Y. Sham y restauración482→616 conservan RAW/clocks completos. En todos los casosF2/F3 que alcanzaron616, la antigua entregaplus.changed mantiene115(0,1,1); esto no sustituye una regresión de todas las capacidadesMCTS.

Alcance: robustez física del mecanismo de adquisición y acceso en esa familia de acontecimientos, con intervalos1/3/5. Cada laboratorio adquirió su propia señal. No demuestra que una palabra antigua se transfiera a otro intervalo sin nueva asociación, ni ANTES humano universal, ni selección aprendida del banco pertinente.

## Comunicación: fuente de orden → receptor nuevo

En una preparación adicional desdeT0, el portador nativo generado por la fuente555 viaja ocho pasos+Z hasta un receptor simple563. Se preparan18 interfaces receptoras sin materia inicial, señales idénticas en los seis bancos y sin callback lecturaA/escrituraB.

EnAB5 yBA5, la fuente produce29+Z; el receptor563 adquiere34+Y; su lector630 produce41(Y+,Z−); el uso636 produce52Z−. La fuente no vuelve a presentarse en630. Las reservasABintervalo1 yBAintervalo3 con cargas13/17 mantienen la dependencia de banco y producen respectivamente34/41/52 y58/65/76.

Controles:

-Sin señal receptora, el portador29 sí llega563, pero la lectura630 queda estacionaria36 y el uso636 sólo contiene11−Y. Transporte no equivale automáticamente a aprendizaje útil.
-Sin acontecimientoA, el receptor sólo produce fondos5→12→23.
-Cortar sólo el mensaje29 en555 conserva el padre y elimina la adquisición34: aparece5→12→23. El fondo23 tiene direcciónZ− y no debe contarse como la consecuencia52.
-Sham en555 y restauración en otro proceso desde555 conservan RAW/clocks completos hasta636, iguales al positivo.

Esto demuestra transmisión de contenido condicionado por acontecimientos, adquisición receptora y uso posterior dentro del dominio. No demuestra una segunda mente completa, comunicación bidireccional, deíxisYO/TÚ ni lenguaje productivo general. El diseño proporciona rutas, formatos y oportunidades; el contenido diferencial procede de encuentros físicos e historia.

## Integridad y reconstrucción causal

`PRIMARY_AUDIT.json` cubre76 contenedores:59 intentos de preparación,9 continuaciones y8 forks. No son76 réplicas científicas independientes. Incluye los fallos técnicos anteriores y las continuaciones de cobertura.

El recálculo sin motor verifica608304 camposRAW/clock exactos: cero conversiones inválidas. Todas las identidades de fuentes registradas se resuelven contra bytes actuales o versiones conservadas. Se reconstruyen1562 transiciones locales de bajo contenido con Moore27 completo y coinciden RAW/clock; cero discrepancias. El verificador declara su dominio finito, excluye ramas de alta carga y las fronterasF1 con entrada actual no capturada en el preestado. No es una demostración exhaustiva de la física ni reconstruye genealogías sólo por proximidad.

Las reparaciones técnicas del primer contacto afectan sólo buffers pasivos en metadata de snapshot; se conservan los dos intentos, sus fuentes y la reanudación del mismoT0. No se editaronRAW/clocks deMAIN. Las intervenciones selectivas son forksdiagnósticos que nunca devuelven soluciones al padre.

Los jobs `RESOURCE_BLOCKED` no crearon unRuntime y no cuentan como negativos científicos. Se preservan en el registro global; sus reintentos únicos usan el límite512MiB autorizado, con reservaRAM512MiB y concurrencia máxima2. Los workers nativos del frente quedaron terminados.

## Lectura provisional

Los resultados identifican un mecanismo de pérdida de acceso por destino ocupado, una reparación nativa fija y una adquisición temporal que ya no depende de coincidir con el intervalo5. La información actual puede conservarse mediante una señal y propagarse para formar otra relación reutilizable. Persisten las fronteras entre acceso geométrico preparado, relación adquirida, generalización de mecanismo y significado lingüístico amplio.

No hay prueba nueva de autorregulaciónR2, consulta autónoma general o comprensión de65 primitivas en este frente. Las funciones positivas se conservan con sus costes y límites, sin convertir sus límites en imposibilidades universales de v27.
