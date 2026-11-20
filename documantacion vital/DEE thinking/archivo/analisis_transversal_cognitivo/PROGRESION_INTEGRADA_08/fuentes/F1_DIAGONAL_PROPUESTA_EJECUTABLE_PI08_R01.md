# F1 opcional — corte diagnóstico del producto diagonal ya formado

Estado: PREPARADO, NO INSTALADO Y NO EJECUTADO EN NATIVE. No es un gate de consolidación A ni sustituye la prioridad B. Todo dato futuro permanece pendiente.

## Pregunta y dominio

¿La continuación del producto diagonal formado por el actuador lateral contribuye a la comparación útil inmediata o a una actuación posterior? La necesidad del actuador ya fue contrastada en PI07; no se repite como si faltara. El corte posterior separa esa cuestión de la necesidad de toda su cola después del encuentro. Que ambos brazos conserven FI+ sería un negativo informativo sobre mediación tardía, no evidencia de que el actuador inicial fuera innecesario.

Se proponen dos importaciones completas del mismo prefijo POST4 T849645, manifiesto06c0bd42cf408933955743465eae357a74658e8d68521da24c400a6ebe7b8575 y código R03 literal40648fd8…/protocolo f69e8558…. Se reutilizan como referencias intactas los primarios reales ya ejecutados RP_A01_OP04 y A2_PREVIAS_EP05, cuyas rutas y hashes están en el protocolo. No se abre un tercer replay intacto. La coincidencia posterior con esas referencias debe medirse; no se presume igualdad causal operacional completa a partir de RAW/clocks.

El primer episodio es ordinal4, q850015. En q+8 se registra antes de intervenir el sitio fijo (52,48,56). Sólo si tiene la firma previamente fijada —SEM1, carga0, estado positivo, dirección[-1,0,+1]— se realiza un fork diagnóstico profundo. En el brazo raw_cut se asigna RAW=0 y clock=None; en identity_sham se asigna el RAW observado en ese mismo sitio y clock=None mediante la misma API. Si no existe la firma, se registra NO_FIXED_TARGET_NO_SEARCH_NO_EDIT y se continúa sin buscar otro sitio ni inventar un producto. No se borra el padre.

La continuación prevista tiene registros q+9 en (51,48,57) y q+10 en (50,48,58), pero la identidad de un portador no se deduce de su carga. Los buffers y snapshots permiten comprobar qué ocurre realmente. Después se ejecuta ordinal5 en la MISMA trayectoria de cada brazo, sin otro fork ni reinicio, y se observan mensaje, selección, FI y retorno reales. No se exige que la respuesta sea favorable.

## API y límites

La API oficial leída es OrganizationalWorld.diagnostic_fork(edits, authorize=True), con ResearchStateEdit.raw y clock opcionales. `runtime.hpp:77–86,127`, `runtime.cpp:diagnostic_fork` y `organizational.cpp:217–218` establecen que la copia conserva canales, agenda, recibos, metadatos y fase antes de aplicar el edit; la segunda añade el registro diagnóstico organizacional. El binding está en `bindings/organizational_pybind.cpp:140` y ResearchStateEdit en `bindings/dee_thinking_pybind.cpp`. No cambia el kernel ni se utiliza import_research_state para reconstruir desde arrays.

Un pulso de carga0 o un nacimiento en una celda RAW0 NO son un borrador. Aquí el tratamiento se llama explícitamente edición diagnóstica externa, no una acción aprendida, una protección nativa ni una reparación hecha por DEE. Ninguna vida editada de F1 puede promoverse.

El propietario real entrega un HabitatAdapter de sólo lectura sobre app.lives.WorldAdapter. El wrapper preparado conserva HabitatAdapter y sustituye únicamente su base.world asignable por el resultado del fork. Exige el hábitat heredado pausado y cierto. No utiliza un setter arbitrario ni quita el entorno. Su bookkeeping de segmentos y los metadatos diagnósticos pueden diferir del intacto; no deben presentarse como igualdad global.

En q+8 se guardan tres snapshots explícitos: padre antes, rama después y padre después. Se verifican globalmente el único parche RAW esperado y la igualdad de clocks, identidad secuencial Native, interfaces, agenda pendiente, recibos, fase, backend e hilos. El prefijo causal Native del padre debe permanecer igual. Los snapshots son evidencia diagnóstica, no pares operativos completos para continuar una vida. El lector verifica gzip/parse completo; no afirma recalcular por separado el FNV interno.

La captura global usa18 ticks fijados por episodio y tres anclas. q+8 es PRE-edit; el estado posedit al mismo tick viaja en su snapshot independiente, y q+9 en adelante registra la continuación. Los huecos no se interpolan. No se alimenta al actor con estas capturas ni con las expectativas intactas.

Dos importaciones más dos forks reales consumen conservadoramente CUATRO slots de mundo. Dos episodios por brazo tienen cota prospectiva1300 cada uno:5200ticks máximos ambos; el calendario conocido sugiere1564porbrazo, sin prometerlo. Las copias transitorias internas del serializador no se hacen avanzar como otras historias. Root debe vigilar RAM y respetar el límite existente512MiB, sin rebajarlo ni desactivarlo. Un exceso o fallo conserva el futuro; no habilita reintentos hasta acertar.

## Integración ROOT-ONLY en sistemas diagnósticos

Archivos preparados: `codigo/pi08_diagnostico_cola_diagonal_R01.py` y `codigo/PROTOCOLO_F1_DIAGONAL_PI08_R01.json`. El protocolo rechaza Native mientras su status sea PREPARED_REQUIRES_ROOT_SEAL_NOT_EXECUTABLE_YET. Tras revisión y presupuestos actuales, Root puede sellarlo como SEALED_FOR_OPTIONAL_F1_NATIVE con fecha real y verificar su wrapper_sha256. La fuente y el protocolo R03, el codec y las dependencias completas CPC se mantienen literales en la cápsula RP anterior a A1; no se instala sobre producto ni sobre el sistema de la candidata en uso.

El modo nuevo es `eci01-pi08-f1-diagonal`, con literal exacto `{modo,arm,stage}`: arm=raw_cut|identity_sham y stage=first|next. No admite coordenadas, relojes, fuerzas ni targets ajustables. `eci01-pi08-f1-estado` es lectura administrativa sin avance.

Como el prefijo nuevo no existe en el dispatcher anterior, Root debe añadir el reenvío acotado a este módulo en la cola y en validate/execute de GenesisNativeWorld de CADA sistema F1, con `before_mutation` etiquetado DIAGNOSTIC_FORK_EXTERNAL_NOT_LEARNED. La forma de retorno es `{version:F1.VERSION,rows:[F1.dispatch(...)]}`. Debe añadir code_files, operational_dependencies y uncertain del módulo al inventario del propietario, conservando los manejadores anteriores. Este reenvío es instrumentación localizada; no se ejecutó ni se aplicó por el subagente. No usar un supuesto comando que el front-end todavía no admite.

Las identidades propuestas son ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_F1_CUT_01 y …_SHAM_01. El código rechaza cualquier principal seleccionado y cualquier instalación fuera de P8/estados. Primero cada vida ejecuta stage=first y sólo después stage=next; si el primer futuro queda incierto, no se admite el siguiente. El padre de ambas se obtiene mediante importación completa existente y manifiesto comprobado; no desde un snapshot aislado con archivos ambientales de otro corte.

## Comprobación realmente hecha

`codigo/probar_F1_diagonal_PI08_R01.py` ejecutó cinco pruebas puras: cut/sham en WorldAdapter envuelto con world readonly; un solo fork y padre detenido; firma ausente sin búsqueda/edición; rechazo de un adaptador desconocido; y lectura del formato Native v2 contra un snapshot congelado real ya inspeccionado por otro lector pasivo. La prueba se hizo extrayendo sólo definiciones AST, sin importar capacidades ni DEE. El checksum del wrapper figura en `codigo/pruebas/F1_FLUJO_Y_PARSER_R01/PRUEBA.json`, SHA6c1cb04523b376ec6d6f8a163769d8df93ae3dd2f1d1bb2933c6b328f9e89d7e.

Son pruebas de control de flujo y formato, no validación física de la intervención. Cero Native, cero forks Native y ningún cambio en producto. Root conserva la decisión de ejecutar F1 sólo después de A y de la prioridad B.
