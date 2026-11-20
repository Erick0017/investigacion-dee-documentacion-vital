# PI03 — Candidato de crédito temporal genérico R01

Fecha de diseño: 8 de noviembre de 2026. Estado: **borrador de ingeniería preparado; cero ejecuciones Native por el autor de esta nota**. El ejecutor principal decide y registra cualquier calibración, reserva o incorporación. Ninguna capacidad nueva queda acreditada por este diseño.

## Pregunta y diferencia respecto del antecedente

En PI02, `pi02_habitat_R04.py` usa `tr.get(a)['prefix']+'penalty'+str(act['route'])` para devolver una consecuencia negativa. La dirección de la entrada depende de la ruta anterior que conserva el anfitrión. Eso es asistencia real de atribución de crédito, aunque el cambio posterior lo produzca v27.

El candidato pregunta si una copia material de la actuación puede mantener la elegibilidad hasta una consecuencia posterior **genérica**, de modo que sea la interacción nativa con esa copia la que determine dónde cambia una referencia. El retorno no recibirá ruta, elección, respuesta esperada ni registro de actuaciones anteriores. No se pretende demostrar planificación, agencia general, exploración espontánea ni regulación general.

El antecedente `mente_unificada_01.py:job` ya tiene un retorno genérico de fallo a **un mismo puerto A**. Eso no es una novedad de PI03. La novedad propuesta es que un retorno común produzca un contacto en bancos diferentes según la historia material del efector, sin que el anfitrión escoja ese banco al devolver la consecuencia.

## Hallazgos estáticos que limitan el montaje

1. La suma direccional DEMUX de v27 compone por el signo de la suma de sus componentes (`kernel_v27.cpp:buscar_fuente_demux`). Un único vector fijo no puede permutar de manera renovable A=(1,0,0) y B=(0,1,0): transformar A en B requiere componentes opuestas a las que transformarían B en A. Por tanto, sustituir simplemente `penalty0/1` por un puerto constante en O no conserva la función.
2. La geometría R06 ya instalada en otras regiones permite una selección por referencia relativa adquirida. Sus referencias iniciales tienen seis vecinos activos de soporte y periodo de acreción 391. Un contacto material vecino añade un séptimo vecino con suma vectorial no nula y cambia el periodo a 782. En un clock local 391 módulo 782 puede suprimir el incremento que habría ocurrido sin contacto. Esto se infiere del código; se debe medir en la calibración tardía.
3. Una entrada legal sobre RAW cero conserva el clock completo existente (`runtime.cpp:apply_events_at_boundary`). Preparar el aparato en T753346 no equivale a colocarlo desde T0 con clocks cero. La comprobación de fase debe leer los clocks reales y no editarlos.
4. `semantic=4` admite preparación por interfaces ordinarias. El kernel conserva ese soporte y aumenta su clock; puede terminar un portador cuando su destino está ocupado por ese soporte. Es arquitectura preparada, no regulación adquirida.
5. `state=0` no basta para admitir una entrada ni para escoger espacio libre: el contrato rechaza `raw!=0`. Todos los exámenes de esta propuesta utilizan RAW íntegro.

## Montaje dentro de un único descendiente N67

Se instala una geometría R06 **sin historia adquirida** en un origen Q elegido antes de la reserva. No se toca el R06 heredado ni O, H, FI128, las asociaciones previas o los recursos ya consumidos. No se copia conocimiento de otro individuo. La instalación legal sucede en el mismo Runtime heredado y se declara P0.

El código borrador está en `codigo/pi03_credito_generico_R01_BORRADOR.py`. Su importación no carga DEE. `install_legal(owner,Q)` exige un propietario ya seleccionado por el ejecutor, verifica RAW y clocks mediante lectura y envía cada soporte mediante `ChannelSpec` + `InterfaceSpec` + `world.submit`. No utiliza `InitialPlacement`, `set_raw`, escritura de clocks, T0, trasplante ni limpieza. El propietario y la seguridad de destino diagnóstico corresponden al runner principal; el borrador no crea vidas ni selecciona ACTIVO.

La comprobación inicial cubre 994 sitios en el ejemplo N67/origen(33,33,33): frame, vuelta toroidal completa de elegibilidad, puertos, rutas cortas, lector, caminos del query y halo Moore. Es cobertura local explícita; no demuestra ausencia de influencias futuras desde el resto del mundo. Si hay conflicto RAW o fases distintas entre referencias, se rechaza ese montaje. La selección espacial es ingeniería de desarrollo, congelada antes de las reservas.

Referencias relativas: A=(-1,-1,0), B=(+1,-1,0). Hub de elegibilidad E=(0,-1,-2). Los elementos nuevos se expresan respecto de Q y se envuelven módulo 67.

### Eferencia preparada y persistencia

Después de observar una actuación binaria efectivamente formada, una transducción fija copia esa actuación como un portador de carga cero en E: elección −1 → dirección +X; elección +1 → dirección −X. Esta inversión es una propiedad preparada del aparato aversivo. No es descubrimiento del cuerpo por DEE y no debe ocultarse. El retorno posterior no consulta este dato.

El portador da vueltas por una fila X. No hay acceso desde DEE al diario de decisiones ni al historial del evaluador. La capacidad inicial es **una sola actuación pendiente**, sin atribución de crédito a varias actuaciones superpuestas. No se crea una memoria cognitiva de acciones en Python para ayudar al retorno.

La elección física cero no es NULL. El borrador rechaza crear una eferencia a partir de ambos. Si el runner decide que una salida cero acciona una opción fija de arranque, esa es una convención P0 del actuador, se declara antes y se usa en todos los controles. El silencio nunca se sustituye por una acción conveniente.

### Retorno de fallo y contacto específico nativo

Un fallo ambiental real devuelve **un único puerto genérico**: dirección +Z, carga cero, origen E−Z, un tick antes de la llegada al hub. El API `submit_generic_outcome(world,failed,tick)` no admite ruta ni elección anterior. Cuando alcanza E y el portador de elegibilidad vuelve a E, DEMUX compone (±X,0,+Z). El banco alcanzado depende de la dirección material anterior.

Un tick después, el portador compuesto ocupa (+1,-1,-1) o (−1,-1,-1), vecino a distancia Moore 1 de una sola referencia y a distancia 2 de la otra. Al tick siguiente intenta entrar en (±2,-1,0), ocupado por un soporte SEM4 del R06 original: termina por la dinámica del montaje, sin borrado del anfitrión.

La predicción de polaridad es que un contacto R06 favorece la selección del banco contactado: al reducirse su acreción relativa, el gradiente de query apunta hacia ese lado. Por eso se usa la copia motora inversa: un fallo en una acción debería favorecer el otro banco. Esta polaridad es **inferencia estática, no resultado Native**; se debe calibrar antes de la reserva. Si es incorrecta, se conserva el negativo y se registra otra variante; no se cambia el decoder después de evaluar.

### Retorno sin castigo y consumo de la elegibilidad

Una consecuencia no fallida usa un segundo puerto **también genérico**, E+Y con dirección −Y, carga cero. La composición produce (±X,−Y,0), lejos de las referencias plásticas. Dos soportes adicionales SEM4, state0/carga0, situados en (±2,−3,−2), terminan esa ruta. No son campos vacíos: su RAW tiene semántica de soporte y deben conservarse como anatomía.

Esta ruta evita que una eferencia anterior se reutilice indefinidamente y evita el puerto +Z común sin eferencia como supuesto control nulo. La comparación de fallo y no fallo iguala número de entradas y carga, pero **no** dirección ni contactos; esos contactos son el mecanismo que se estudia.

## Fase, demora y observación fijadas

Las dos referencias nuevas deben tener clocks congruentes módulo 782. Se elige un contacto cuando sus clocks sean 391 módulo 782, siguiendo la ventana anatómica de escritura que ya usa MUFI01. No se resetea un clock ni se busca un tick que acierte una respuesta. El calendario preparado se informa como asistencia.

La eferencia entra **un tick después** de leer/aplicar la actuación y vuelve a E después de 67·k ticks. Se usa siempre una frontera futura aunque `Runtime::schedule` sólo rechaza fronteras estrictamente pasadas: evitar la ambigüedad entre observación del límite actual y admisión posterior es una decisión operativa preparada. El retorno genérico entra en su sitio de origen en `contact_tick−2`, llega al hub en `contact_tick−1` y contacta el banco en `contact_tick`. Desarrollo sugerido: k=1 y2; reserva de demora k=3 o4. La demora actuación→hub es 67·k+1; k=0 exigiría inyectar la consecuencia antes de la actuación y se rechaza. El query se programa en `seed_tick−7` y se lee seis ticks después, en `seed_tick−1`.

El query R06 consta siempre de las mismas tres entradas materiales de carga cero. Se lee exactamente q+6 en los tres sitios (−2,2,0), (0,2,0), (+2,2,0), con firma activa SEM1 y dirección[signo,1,0]. No se buscan lectores alternativos tras ver la respuesta. Consultar cambia la historia aunque la carga sea cero; no es observación pasiva. El código conserva cero y NULL separados.

El registro pasivo de calibración debe guardar, sin nuevas sondas: recibos; RAW/clocks exactos en ambas referencias, E y los dos vecinos de contacto; recorrido de eferencia en varios puntos; condición física al llegar el retorno; soportes de consumo; y métricas globales. Los relojes se serializan como enteros/cadenas exactas, sin floats. La comparación con/sin registro del observador existente puede reutilizarse sólo dentro de su alcance validado.

## Orden mínimo de calibración y evaluación

1. Clon diagnóstico del estado completo preservado. Instalación tardía legal; comprobar todos los recibos. Un fallo de instalación conserva su futuro y no se reintenta sobre el mismo material.
2. Prefijo del aparato preparado antes de aprender. Dos eferencias opuestas con **el mismo retorno genérico**, en copias de ese mismo prefijo: deben contactar bancos opuestos. Demostrar persistencia de elegibilidad en una y dos vueltas, su consumo y la independencia del API de retorno respecto de la actuación previa. Es una comprobación mecánica, no aprendizaje útil todavía.
3. Medir la polaridad fija de la referencia y del lector, además de una condición sin contacto específico. Si el query carece de salida, diagnosticar admisión, fase o geometría; no sustituirlo por comparación escalar de referencias en Python.
4. Congelar candidato, contingencia y lector. La candidata continua debe actuar en una tarea segura binaria con consecuencias ambientales reales y después recibir el retorno genérico a la demora fijada. El efecto útil no es el propio valor de la referencia: debe ser un trabajo realizado, acceso conservado o recurso material del entorno efectivamente disponible.
5. Reserva con demora nueva y cambio de contingencia. La historia no se reinicia entre adquisición, reserva y cambio. Un panel heredado proporcional y guardado/reapertura precede cualquier adopción.

Controles decisivos: (a) mismo prefijo sin eferencia; (b) eferencia pero retorno temporalmente desacoplado, manteniendo la misma dosis; (c) retorno no fallido/disposal en lugar del castigo real; (d) actuación anulada después de formar salida, sin inventar éxito; (e) referencia externa sencilla mantener tras acierto/cambiar tras fallo, nunca controlando DEE. No hace falta un factorial de todos ellos. Las copias comparten prefijo y no son individuos independientes.

El control sin eferencia no es automáticamente inerte: +Z solo pasa por el punto central vecino a **ambas** referencias. Debe observarse su efecto y no denominarlo ausencia de experiencia. Un retorno fuera de fase puede dejar un portador propio circulando; no se permite limpiar ese futuro. El sham se verifica espacialmente y se informa su dosis y recorrido.

## Qué podría demostrarse y qué no

Si la elegibilidad nativa selecciona el banco al retorno, se demuestra una reducción concreta de asistencia: el anfitrión ya no asigna la consecuencia al puerto de la acción anterior. El cuerpo de copia, inversión, query, momento de escritura, interfaz de consecuencia y ley ambiental siguen preparados.

Si la modificación cambia actuaciones posteriores útiles frente a controles, se puede reconocer selección adquirida de alcance local por consecuencias diferidas. El resultado se conserva en la misma genealogía candidata y no se mezcla con memorias de controles. Una selección contraria sin utilidad sólo demuestra una modificación física, no una política competente.

La recurrencia de elegibilidad no es iniciativa: el momento de ofrecer una oportunidad y el calendario de query siguen siendo del anfitrión en esta versión. Tampoco demuestra exploración aprendida, contexto general, dolor consciente, alivio subjetivo ni un plan autogenerado. El resultado puede ser útil y limitado sin esas atribuciones.

## Fuentes inspeccionadas para este diseño

Lectura completa dirigida: `sistema/capacidades/pi02_habitat_R04.py`; `pi01_traza_legal_base.py`; `selector_acrecion_nativo.py`; PI02 `lecturas/MECANISMOS/RETORNO_DIRECTO_Y_FRONTERA_API.md`.

Lectura parcial explícita: `sistema/capacidades/mente_unificada_01.py` (preparación, next_contact, uso y job); fuente oficial Thinking `source/src/kernel_v27.cpp` (DEMUX y actualización de materia); `source/src/runtime.cpp` (admisión, conservación del clock y avance); `source/src/organizational.cpp` (interfaces); `motor/python313/site-packages/dee_thinking/experimental_regulation.py` (CPC5/finitez del aparato); PI01 `lecturas/CPC_Y_CAMPAÑAS/RECALCULO_DOCUMENTAL_AA33.json`; PI02 `lecturas/CONTRASTES/AFIRMACIONES_Y_FUENTES.json` (extractos iniciales, no lectura integral).

La identidad del motor instalado y del principal se verifica por el ejecutor de PI03; esta nota no importó DEE para certificarla. No se relee a ciegas el corpus ni se atribuye lectura completa a los extractos.

Revisión operativa estática posterior: el primer helper se conservó íntegro como `codigo/pi03_credito_generico_R01_PRE_REVIEW.py`, sin ejecución Native. El borrador revisado tiene eferencia futura de un tick. `codigo/progresion_integrada_03_R01.py` implementa `eci01-pi03-preparar`, `eci01-pi03-calibrar` y `eci01-pi03-estado`, con avance exclusivamente por `a.run_until`. `PROTOCOLO_PI03_R01.json` está deliberadamente `DRAFT_NOT_EXECUTABLE`, sin Q: sólo el ejecutor principal puede sellarlo tras escoger geometría por lectura pasiva. Acepta vidas diagnósticas `ECI02_PI03_*`, exige pausa explícita del puente PI02 y rechaza el principal seleccionado al despachar. No se editó el propietario instalado ni archivos del producto.

La admisibilidad de state0/SEM4 se confirmó también en `kernel_v27.cpp:pack_record`, `organizational.hpp:InputCodec` y `organizational.cpp:InputCodec::encode_integer`: el códec por defecto admite cero, `pack_record` conserva state0/SEM4, `register_channel` no exige state positivo y la frontera sólo exige RAW cero de destino. Esto acredita que la API expresa el montaje, no que sus 27 entradas serán admitidas en el futuro Native concreto.

Comprobación efectuada aquí: el helper se ejecutó con Python de Miniconda en `--self-check`. Verifica sólo geometría, separación Moore y aritmética de fase (incluidos enteros >2^53). **No es una reproducción Native ni un experimento.** La invocación `py -3.12` falló por acceso al ejecutable de WindowsApps; no se instaló nada y se usó el intérprete ya disponible.

## Revisión estática posterior ante NULL del panel combinado

Esta sección responde a un fallo comunicado por el ejecutor en una continuación diagnóstica: fuente T768317 con referencias aproximadamente37; doce usos anteriores y dos trabajos protegidos hasta T771503; posterior lector R06 q+6 sin firma en T771955. Son referencias del ejecutor, no una ejecución realizada por el autor de esta nota. La causa concreta requiere sus snapshots/recibos y no queda demostrada por esta lectura estática.

**La magnitud45 no explica una cristalización escalar.** En el C++ congelado, `UMBRAL_CRISTALIZACION=int(9.887^3)=966` y la condición es `grad_mag/19665>=966`, por lo que exige `grad_mag>=18.996.390`. Cada carga es uint16, como máximo65.535; con26 vecinos Moore y tres componentes de gradiente, incluso el límite superior deliberadamente holgado `3·26·65.535=5.111.730` es menor. Esa rama de cristalización no puede explicar el caso con estos campos representables. La génesis XNOR es otra condición: ocho vecinos activos y simetría de trece pares, y no se descarta por este cálculo. Tampoco debe confundirse con acreción, regla de densidad, encuentros o fusión a19.665.

En el aparato aislado, aumentar ambas referencias conservando su diferencia mantiene los signos básicos del gradiente de consulta. No hay un umbral40 explícito. Puede importar la fase de acreción, un campo adicional, cambios de ocupación/dirección, un soporte, un rechazo o una trayectoria entrante: la ausencia de salida por sí sola no identifica cuál. Primero se deben leer los tres recibos del query y su contexto completo; no mover el lector para obtener una firma favorable.

**Pausa del hábitat heredado:** `pi02_habitat_R04.set_enabled` rechaza ya una transacción activa o incierta. La receta del panel usa ese método para `legacy_pause`. Si ese paso terminó correctamente, no debe describirse un FI job activo como algo que sobrevivió silenciosamente a esa pausa. `_start_event` exige `job.end_tick<feedback_tick−2`; el retorno negativo es q+670 y el cierre/busy es q+710. El cierre conserva recibos terminales antes de poner `active=None`. El avance pausado sí continúa el mundo Native y no consume callbacks de un trabajo hipotéticamente pendiente, de modo que saltarse esa guarda sería peligroso; no es lo que hace el handler publicado. Confirmar la agenda concreta sigue siendo necesario.

La pausa no borra portadores materiales ya formados por FI, avisos, normalizadores o consultas. Un ciclo de1800 ticks tampoco demuestra que toda contribución haya desaparecido. Esas influencias físicas siguen siendo antecedentes legítimos y no basura que pueda limpiarse.

El `FileNotFound` posterior de `inflight_silence` es una deficiencia independiente del contenedor externo: un exportador que preserva archivos puede omitir directorios vacíos. Restaurar exclusivamente esos directorios estructurales no inserta memoria ni modifica Native, pero no convierte el NULL previo en respuesta válida. Deben conservarse ambos hechos y el futuro adverso, sin volver a lanzar solicitudes inciertas.

Si el registro identifica una ruta residual concreta, una variante acotada podría instalar legalmente un terminador SEM4/state0/carga0 **antes** de su encuentro, en RAW íntegramente cero y fuera de rutas necesarias, siguiendo los antecedentes de guardas selectivas. Sería protección P0 preparada, no aprendizaje ni limpieza. Sólo tendría sentido después de localizar una contribución causal y de comprobar que conserva las funciones heredadas y el nuevo crédito. No se propone instalar guardas a ciegas ni resetear referencias.
