# Acceso nativo: selección limitada sí; iniciativa no acreditada

## R1: selección P1 sobre una consulta basal P0

Una bifurcación T/H del pasado completo de MAIN recibió nueve terminadores periféricos inactivos por interfaces legales. Ambas rutas y sus nueve suministros genéricos cero se fijaron **antes** de consultar. El mismo query de tres pulsos se dirige al selector local; el anfitrión no elige alfa, beta o gamma. El contenido se lee con un único panel fijo de los12gates, aceptando sólo un producto material con dirección mixta adecuada, enT31092.

| Vida/contraste R1 | Primer contexto propio | Consulta/perturbación | Banco observado | Signo |
| --- | --- | --- | --- | --- |
| T | referencia adquiridaD−20 | Query genérico+guías | gamma | + |
| H | referencia adquiridaD+18 | Query genérico+guías | beta | − |
| H_beta_plus | D+18, beta explícitamente revisada+ | Mismo query y guías | beta | + |
| no_query H | D+18 | Sin query, mismas guías | beta | − |
| cut_first_turn H | D+18 | Sin dos primeros recursos | beta | − |
| T_no_query | D−20 | Sin query, mismas guías | beta | − |
| T_cut_sham_dose | D−20 | Primeros recursos sustituidos por dos shams periféricos0 | beta | − |
| T_extra_sham | D−20 | Guías intactas+dos shams periféricos0 | gamma | + |
| T_gamma_minus | D−20, gamma explícitamente revisada− | Query y guías intactas | gamma | − |

La preparación genera una consulta basal aunque no se entregue el query del selector. Los dos recursos de reversa, aun con carga0, producen material−Z; al encontrarse con otro recurso (0,+Y,+Z), producen+Y0. En los frames de no_query llega a I=(33,33,33), T31088, una entrada+Y0 y se lee beta. **Cero de carga no equivale a ausencia de portador.** Por eso R1 **no demuestra iniciativa del ente**.

El efecto de T no desaparece: el primer selector aprendido produce una contribución que llega a I como+X5. Se combina allí con la contribución basal+Y0 y forma el cue diagonal(+X,+Y), que alcanza gamma. H aporta+Y y deja el acceso en beta. El corte con dosis compensada de T devuelve el resultado basal beta; el sham conserva gamma. La revisión de gamma invierte el signo de la segunda respuesta sin cambiar el lector ni la consulta. Se demuestra una selección material de acceso dependiente del estado adquirido sobre una oportunidad preparada; no una estrategia general aprendida ni P2/R2.

El coste es importante. Después del uso, el panel estándar consecutivo de T responde en2/6contextos (alfa/beta), sin producto válido en los otros cuatro. H conserva5/6respuestas, sin beta. Son pérdidas de **acceso bajo ese protocolo**; no se ha probado convergencia causal o destrucción del contenido completo. No se restaura una memoria favorable ni se oculta el futuro adverso.

Esta capacidad se conserva como mecanismo auxiliar finito de una utilización, no como nueva arquitectura estable ni habilidad sumada a MAIN. `acceso_nativo_un_uso.py` proporciona admit/state/use sin importar datos del laboratorio o evidencia. Sus hashes de compatibilidad sólo impiden utilizar otro estado: nunca se consultan para decidir el resultado. El uso material procede del mismo lector12gates y no incorpora tabla de respuestas. El dominio probado es el estado preparadoT30957 y la ventana exactaR1; no un acceso repetible indefinido.

## R2: corrección única y resultados negativos

Se probó una corrección con todos los vectores de guía de componenteY0, intentando conservar el+Y del actor como testigo necesario. Se fijaron antes del ensayo dos ventanas de lectura de los12gates (T31092/T31159); sólo se acepta un producto total, y dos se consideran ambiguos. Los terminadores de salida mixta también se prepararon antes de evaluar.

T produjo beta− en la ventana tardía. H y H_gamma_minus no produjeron lectura válida. Sin query y con corte del primer giro tampoco hubo producto. No se ajustó el lector para capturar otro resultado.

Una causa concreta limita el brazoH: el puerto `FI01.NR.plus.turn1` pretendía ingresar en(35,35,35), que ya era un soporte SEM4inactivo del coregamma. La petición fue rechazada por ocupación. El actor conservaZ+ en(35,35,33), sigue por(36,36,34) y no encuentra el soporte histórico gamma situado en(36,36,33) en esa fase. No se llamó aprendizaje fallido a ese enlace inadmisible ni se borró el soporte para forzarlo.

Además, los nuevos terminadores pos(v,5,2·z) deR2 cruzan las rutas de restauración antiguas pos(v,6,2·z)→pos(v,4,2·z). Por tanto los paneles estándar posteriores ya no son una comparación compatible e intacta de retención; su degradación no demuestra que cinco recuerdos fueran destruidos. R2 queda como candidato negativo/incompatible delimitado, sin tercera corrección ni promoción.

## Evidencia y continuidad

Se preservan14usos de ruta,14paneles posteriores, fuentes exactas deR1/R1controles/R2, entradas, recibos, frames locales+medidas globales y snapshots completos. El recálculo reproduce12gates/ventanas desde los campos registrados, coteja cada lectura con su frame y conserva los rechazos:895solicitudes,871admitidas,24rechazadas por ocupación. No suma consultas de la misma vida como individuos independientes.

Estados completos **antes** de la utilizaciónR1, todosT30957:

- T: snapshotSHA `7e4a446322036bfffae112e77548bbf097cd014178557982f06fa99d44040737`.
- H: `11b766d5d7114354fd5a84476b6fbfb7a4810bb33f949c7ed300ed9148b74b97`.
- T con gamma revisada−: `2f9ce2ba21ea3f3cb59bedaa6dc1c7266f1b59478795309997224a08784929dc`.

Se localizan desde los primarios `T_LESSON.json.gz`, `H_LESSON.json.gz` y `CONTROLES_T/T_gamma_minus_LESSON.json.gz`, bajo `evidencia/campanas/MENTE_UNIFICADA_Y_FI01/acceso_nativo_b/`; los futuros adversos están en los mismos expedientes. El módulo operativo se entrega al coordinador para su incorporación auxiliar y comprobación breve en una copia, dentro de esta campaña. No se ha escrito el activo ni ningún módulo del actor durante su ensayo de servicio en segundo plano.

No se acreditan iniciativa autónoma de consulta, acceso estable repetido, planificación, estrategia general, lenguaje nuevo ni destrucción total de información. Sí se conserva la transformación física comprobada de qué contenido se utiliza, y se conserva el fallo que impidió convertirla en un mecanismo más autónomo y compatible.
