# Mecanismo U0 y límites del enrutador común

Corte experimental: 25-10-2026, seguido de incorporación operativa a T740. No modifica el E1 protegido,
EO02_MAIN, ni la línea principal R9 de esta ejecución. Todas las preparaciones
U0 y de enrutado son vidas nuevas declaradas, sin trasplantes aprendidos.

## Resultado utilizable: U0 oficial, adquisición acumulativa asistida

`MA_U0_SEL_BA_PLUS` es una sola vida N67, perfil oficial
`u0_integrado_4_5`, ahora T673. Su estado completo es
`evidencia/campanas/MENTE_ACUMULATIVA/mecanismo/MA_U0_SEL_BA_PLUS.T673.deetsnap.gz`.

SHA-256: `74ccd5b2fc884a3867b6453d9164ac09d5cf8868cf906b6b7516342f458c129f`.
Tamaño: 17.698 bytes comprimidos, 4.909.822 bytes decodificados.

Secuencia efectivamente vivida:

- Adquisición por encuentros de L01+/L02− y de L03+, L04−, L05− en T0.
- Primer uso de las tres formas inferiores en T137: 3/3 admitidas y correctas.
- Adquisición de L06+ en T201; primer panel posterior en T271: 4/4, sin volver
  a enseñar L03–L05.
- Revisión física dirigida L03− en T402; primer panel en T472: L03 cambia y
  las otras tres conservan sus signos, 4/4.
- Desde ese mismo estado, sin restaurar una plantilla favorable, adquisición
  de L07− en T536; primer panel T606: 5/5.
- Guardar, terminar proceso, cargar el estado T606 en otro proceso y presentar
  el panel en orden diferente: T673, 5/5; ningún nuevo docente.

Los nombres L03–L07 designan correspondencias físicas opacas, no cinco
significados NSM ni cinco procedimientos funcionalmente diversos. Las consultas
inferiores son peticiones del operador dirigidas a interfaces preparadas. Su
conservación física y actualización son reales; la elección autónoma de cuál de
esas cinco memorias utilizar **no está demostrada**.

La reserva U0 con contenidos opuestos (`MA_U0_RES_AB` y `MA_U0_RES_BA`)
también produjo 3/3 → 4/4 → revisión 4/4. Sin experiencias de contenido,
los paneles iniciales fueron 0/3 y 0/4, con entradas rechazadas, no respuestas
inventadas. El sham de revisión conservó las otras tres, pero L03 quedó
inaccesible/rechazada; no se computa como una revisión exitosa.

## Composición nativa genuina, alcance finito

El U0 incluye una cadena conectada distinta de sus paneles inferiores:
orden adquirido → comparación con acontecimiento actual → petición horizontal
material → memoria propia adquirida → uso junto con recursos de acción.

`MA_U0_SEL_BA_PLUS` recibió orden BA y acontecimiento actual +. El kernel
produjo petición izquierda `[-1,0,0]`, carga 37, en T19; llegó a L01 en T70,
generando `[-1,+1,0]`, carga 53; con recursos genéricos en ambas oportunidades,
la acción plus en T72 fue `[-1,+1,+1]`, carga 60. El operador no escogió la
pregunta, el banco que respondería ni un subconjunto favorable de suministros.

Controles decisivos:

- Mismo acontecimiento actual + y mismos contenidos propios, pero historia AB:
  no apareció petición horizontal diferencial ni acción transformada en T72.
- Historia AB con acontecimiento −: petición derecha, acceso a L02− y acción
  `+1,−1,+1`, carga 60.
- Mismo BA/+ y banco propio adquirido con signo contrario: la acción pasa a
  minus `−1,−1,+1`, carga 60. El contenido de la memoria, no el signo de la
  consulta, determina ese componente de la acción.
- Sin adquirir los bancos altos: la petición material existe, pero ambas
  oportunidades de acción quedan en el recurso genérico `[0,0,+1]`, carga 7.
- Corte diagnóstico del mensaje **ya formado** en T20, sitio (18,10,46),
  conservando clock y futuras colas: desaparece la acción transformada, aunque
  llegan ambos recursos genéricos. Sham exacto preserva la acción plus.

Esto confirma dependencia de historia, petición condicionada y uso nativo de
contenido propio. El circuito de consulta y los recursos son preparados: no
es una política de consulta adquirida, P2/R2 ni un asistente general.

La API oficial restringe `experience_order` a T0, `consequence` a T11,
`action` a T69 y `teach_form` a T72. Este frente **no** acreditó el reuso de toda
esa cadena desde T472 o T673. Su dominio operativo probado es la cadena inicial
finita y, separadamente, la ampliación y consulta continuada de asociaciones.

## Candidatos de entrada común: negativos conservados

Se probaron cuatro revisiones acotadas, todas nuevas T0. Ninguna se promociona.

1. R01, N31: cuatro señales tipadas en un sitio sensorial común y recursos
   genéricos que intentaban reunir respuestas en dos salidas. Sólo una salida
   inequívoca admitida por historia en siete consultas. Los encuentros podían
   anular dirección o interferir con adquisiciones posteriores.
2. R02, N31: retirar los giros y observar los cuatro bancos con un lector fijo.
   Dos de siete consultas se admitieron; el lector veía después una firma que
   no acreditaba una respuesta nueva. Las cinco rechazadas no se contabilizan.
3. R03, N67 y direcciones no opuestas: cinco de siete admitidas, una respuesta
   inequívoca y cuatro ambiguas; dos entradas finales rechazadas.
4. R04, nueva reserva con lector de ventana RAW pre/post en todos los bancos,
   sin conocer token ni target: mismo 1 inequívoco / 5 admitidos / 7 solicitados
   en ambas historias opuestas. No resolvió la ambigüedad.

El contraste R04 corrige una interpretación fácil: no eran únicamente bits
`active` antiguos. En q268, bancos 0 y 2 pasan ambos RAW0 a una firma de carga21
en T271: uno responde a la nueva petición y otro reaparece por recurrencia.
Observar un cambio RAW reciente tampoco identifica por sí solo el linaje ni
selecciona la respuesta pertinente. El lector de ventana es un instrumento del
investigador y nunca alimentó decisiones del participante.

Estos resultados no demuestran imposibilidad general de un selector común.
Delimitan estas rutas, dosis, calendarios y lectores concretos. No se borraron
sus futuros adversos ni se reetiquetaron como una mente acumulativa exitosa.

## Uso e incorporación

El cargador ya existe: `IntegratedSession.load_snapshot(path)`, que conserva
Runtime, agenda, recibos, interfaces y progreso de protocolo. El gestor admite
`u0_integrado_4_5` en `app/lives.py`, `Store.import_state`, `fork`, `mutate`,
`experiencia`, `consultar`, `revisar` y guardado. No hace falta otro gestor.

La importación operativa debe declararse como continuidad importada de esta
vida nueva, no como recuerdos heredados de EO02. La línea R9 principal no se
sustituye automáticamente. La siguiente consulta inferior T737, lectura T740,
se ejecutó después de este corte científico: importación por el gestor existente,
consulta 5/5 admitidas/correctas, recarga desde otro proceso y guardado.

Vida incorporada: **MA_U0_ACUMULATIVO_AUX**, perfil `u0_integrado_4_5`, T740.
Estado operativo en `sistema/estado/checkpoints/MA_U0_ACUMULATIVO_AUX.T740.268a60a86d99.deetsnap.gz`.
SHA-256 `5e3fad7704919631528148ff6201acc619fb40f39d0e0778085c363c2b3e5412`.
El contrato `sistema/contratos/U0_ACUMULACION_ASISTIDA_MA.json` y una entrada única
en el catálogo ya la admiten como vida complementaria ejecutable. La consulta,
recarga y guardado preservaron los mismos hashes RAW/clocks en T740. Se conserva
también el intento inicial U0_50_IMPORT fallido por ruta relativa del instrumento;
no había importado ni avanzado el participante. El intento U0_50B_IMPORT usó
la ruta absoluta verificada y terminó correctamente.

## Verificación y fuentes

`recalcular_mecanismo.py` sólo utiliza la biblioteca estándar. Recalcula signos
desde RAW decodificado, direcciones, cargas y recibos; no importa DEE ni da
ticks. `RECALCULO_MECANISMO_FINAL.json` contiene 26 primarios más cinco registros
operativos, hashes y cero discrepancias del decodificador. Incluye todos los
negativos de enrutado y comprueba identidad física query→reload→save. El archivo
anterior sin operaciones se conserva como corte parcial, no como autoridad final.

La identidad instrumental se reutilizó del entorno oficial vigente; se leyó
el código instalado de `IntegratedSession`, `RepertoireSession` y
`ConsolidatedSession`. Se consultaron de forma dirigida los originales locales
CPC7 `src/selective_native.py` e `src/integrated_revision.py` para identificar
el enlace de bancos propios que faltaba en el primer piloto. No se atribuye una
lectura nueva de todo CPC7 ni de toda la biblioteca a este frente.
