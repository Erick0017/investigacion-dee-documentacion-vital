# Reserva REAL R02 — cierre retrospectivo por guarda del anfitrión

Esta autopsia no añadió ticks, consultas, propietarios o reenvíos. No modificó el estado, la cola, el marcador o los originales. El componente preferente es `EV/RESERVA60_CIERRE_GUARDA_N0_R03/`,46 archivos y2943167 bytes expandidos, con manifiesto SHA `ffe419fdc4e6f1b1a21df81df8e3197fd872b42ca91e4b114bcdc19f2ebc8b26`. R01 y el intento N0 R02 quedan preservados aparte.

## Qué terminó y qué no

El wrapper terminó a5400.0135813 segundos por su guarda predeterminada, exit124 y0 procesos activos en el Job final. No hay `FIN_VENTANA.json` ni `RESULTADO.json` del driver. Esto es un cierre del anfitrión con futuro no comprometido posible, no una certificación de60 minutos del protocolo completo ni un crash cognitivo.

El plan tiene64 eventos:63 materiales con ID y un checkpoint sin ID en3570 segundos, etiqueta `actual_end_of_reserved_experiences`. Sólo10 eventos materiales llegaron a SQLite;9 completaron yuno quedó processing. Se observaron las10 marcas previas de envío ylos9 resultados completos en el diario. No apareció ningún resultado tardío completo en SQLite ausente del diario. Los53 eventos materiales restantes yel checkpoint no se ejecutaron. Las43 oportunidades previstas no equivalen a43 oportunidades realizadas.

Se completaron7 oportunidades:5 del nivel2 y2 del nivel5. La primera formó INSPECT yexpuso el hecho ambiental nuevo16 con utilidad según el evaluador preparado; las6 siguientes fueron NULL ysin acción útil. Las dos operaciones administrativas completadas, apertura yexpansión5, no añadieron entradas Native en sus resultados.

Los116 IDs Native únicos abarcan únicamente estas7 oportunidades completas:11 aplicados y105 rechazados por ocupación. La primera aportó11 aplicados+3 clear rechazados; las6 siguientes rechazaron sus17 entradas respectivas. No se asigna cero actividad Native a la octava oportunidad incierta.

La octava oportunidad está en `apd04_reserve_r01_level5_work03`, estado processing, seq1816 ypayload SHA `9b9e61790898928e59a1705081ac83eec17f73a3e46fb1a00f90c403b5099e1c`. El protocolo UI conserva ese mismo ID; no fue limpiado ni reenviado. El pendiente posventana previsto `apd04_reserve_exact_pending_r01` no llegó a SQLite. No se confunden ambos IDs.

## Último estado comprometido y límite de la observación

Último snapshot completo local: T667452, SHA `9359f2d1be677cca16c177e7cbbe92695512092ec0c2edde3ca3f1b5fb2cbdad`. El marcador separado conserva `uncommitted_native_future_possible=true`, operación `idle_continuous` yobjetivo667453. Que el campo UI `uncertain_preserved` sea false no anula ese marcador ni convierte este futuro en una vida de continuación normal válida.

El corte tiene297412/300763 sitios state no cero, máximo s_reg19664 y187 sitios state0 con RAW no nulo. Su RAW global es idéntico al de las primeras dos oportunidades, SHA `28a90f348d3e703e924a5badeb6595bd2b35cf7e558b05aa6fbd9a63faf6f0ca`; los clocks avanzaron al tick667452. Los soportes μA/μB conservan s_reg1618/1638, ambos state2 ydirección0. La diferencia externa20 es un indicio físicamente distinguible compatible con una huella; no se demostró acceso Native, recuperación funcional o conservación general de memoria. No se compararon aquí historias contrastadas envejecidas de forma emparejada. Las ramas REF21/19 son otras vidas.

El primer episodio útil tuvo categoría SUCCESS yno produjo pulsos FAILURE. Por eso no se atribuye su densificación a nuevos pulsos FAILURE de ese mismo episodio. La lectura válida de selector en656649, los rechazos clear658063 yel global densificado658068 acotan observaciones disponibles; no revelan por sí solos un nacimiento microscópico único.

## Integridad y recálculo

Se abrió SQLite mediante `mode=ro&immutable=1` sólo tras comprobar ausencia de WAL ySHM. La revisión R03 vuelve a registrar antes/después ambos sidecars inexistentes,0 bytes, yel hash de la DB intacto. No se ignoró un WAL con datos. Se concilian9 resultados completos con sus archivos de salida, sus entradas VIDA ylos hashes de sus9 snapshots completos.

El intento de conciliación R02 exigió erróneamente igualdad del archivo de salida con la envoltura SQLite entera. Los archivos originales preceden al campo administrativo `committed_snapshot` añadido en SQLite: los hashes de archivo coinciden con VIDA ytodos los demás campos coinciden. R03 verifica precisamente esa diferencia de envoltura, conserva el compromiso completo por separado yno descarta campos físicos. El fallo N0 R02 ysus bytes no se borraron.

El recálculo principal portable es byte-idéntico, SHA `3e64965c028b60cbef17a65e67cf7d033d850458bcc11bf6b28f2be2dad787fe`. El complemento de calendario yconciliación también es byte-idéntico, SHA `4f9e71501073e65c817ae4e441b1a544e7165feb5e7f4842f4c4c6aa39f66e67`.

Viaja el RAW global exacto comprimido. Todos los clocks fueron comprobados iguales a667452 en el snapshot original yse regeneran con esa receta sin pérdida, verificando su SHA. Esto reduce duplicación, no omite clocks distintos. RAW/clocks ycontexto exportado están rotulados NO_OPERATIVOS; no reemplazan el snapshot completo, sus colas yla continuidad incierta local. Las fuentes físicas del actor son únicamente las21 copias `FUENTES_ANTES_DE_NATIVE` R02 de la reserva; no se leyó el código S posterior como si hubiese producido estos resultados.
