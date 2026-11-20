# PI05 · F1: tránsito global, formación intermedia e interferencia

**Corte de esta síntesis:** 9 de noviembre de 2026. Incluye exclusivamente los resultados cerrados enumerados abajo: REAL, NONE, YOKED, contraste escalar b2/b3, prevención GUARD/SHAM, recuperación asistida desde el futuro fallido con espera3ticks y continuación integrada de la candidata protegida hasta824911. Es una fuente científica de la campaña para integrar en su informe y en el único Manual Maestro; no es otro manual rector. La incorporación operativa todavía no está incluida como resultado. B4 y reutilización inmediata0 no se ejecutarán en este presupuesto; sus predicciones no se presentan como datos. No se ejecutó Native desde este frente de análisis.

## Pregunta y antecedente

El panel de conservación PI04 falló en la comparación FI128 de las entradas públicas `14/3`. La interfaz fija no envía esos dos números directamente a la resta preparada: codifica dos contribuciones `14` y `20−3=17` en una arborescencia material de 128 entradas. Se trata del contrato de comparación con sesgo **20**, distinto del sesgo32 de otra operación aritmética. El ensayo anterior admitió176/176 entradas y produjo una respuesta física negativa, mientras el testigo histórico PI03 había producido una positiva con el mismo contrato. El fallo bloqueó la adopción de la candidata PI04; no se redefine su resultado como éxito.

El diagnóstico anterior situaba una diferencia en C/S:14 frente a31. Eso todavía no explicaba dónde dejaba de formarse la contribución derecha ni si había sido trasladada a otra parte. PI05 observa globalmente el universo N67, incluyendo todos los bits RAW, las posiciones con state=0 y todos los clocks, con fronteras temporales y geometría fijadas antes de la captura. Matching de carga, dirección o posición no constituye genealogía de un portador.

Fuentes del antecedente desde P5: `../PROGRESION_INTEGRADA_04/control/CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json`, `../PROGRESION_INTEGRADA_04/ensayos/PI04_MAIN_PANEL12_OP2_FIplus.json` y la réplica negativa preservada de PI04. Sus ubicaciones permanecen históricas. El extracto literal pequeño del positivo se encuentra en `fuentes/TESTIGO_HISTORICO_FI128_14_3_PI03.json` y referencia el primario original `../PROGRESION_INTEGRADA_03/ensayos/PI03_MAIN_OP3_PANEL_FIplus.json` por ruta, bytes y SHA.

## Instrumento y cobertura efectiva

El capturador externo lee `raw_copy()` y `clock_copy()` en la misma frontera del propietario y exige que el tick siga siendo el mismo. Conserva tres anclas completas y66 deltas XOR uint64LE, comprimidas sin pérdida. El lector documental reconstruyó y verificó los hashes originales de69/69 fronteras por condición. Los arrays contienen300.763 sitios cada uno. Su igualdad es igualdad de buffers físicos dentro de ese alcance, no igualdad del estado operativo completo.

Para la consulta q=817932, las fronteras densas son q−56…q+10. También se conservan q+75 y q+142. **No hay captura de cada tick de los intervalos q+11…q+74 y q+76…q+141**. Los horizontes75/142 no se declaran periodos universales. El último par está separado67 ticks y muestra una coincidencia RAW en este caso; sus clocks sí avanzan.

En el REAL observado hay309 posiciones RAW!=0 al inicio y308 al cierre. En todas las fronteras hay202 posiciones state=0 con RAW!=0. Por ello un inventario basado únicamente en state>0 habría omitido información causal potencial. El máximo s_reg global observado es4530. En la frontera crítica esto excluye el umbral de fusión19665 para el paso siguiente, dado que no se admite otra entrada en ese paso. No se extiende esa comprobación a todos los ticks no capturados ni se equipara s_reg con energía, RAM o conocimiento.

La captura no recibe objetivos ni decide una acción. Los arrays y los mapas de este análisis no se entregan al ente. La comprobación de pasividad con su comparación completa corresponde a `control/PASIVIDAD_CAPTURA_GLOBAL_FI_PI05_R02.json`; no se deriva una garantía universal de sólo haber leído los arrays. Las pruebas Fake del analizador prueban su codec/recálculo, no la pasividad material del motor.

## REAL: lo que se observó antes de C

La vida diagnóstica `ECI02_PI03_REPRO_PI04_PI05_REAL_GLOBAL_01` avanzó817876→818074 en el ensayo FI cerrado. Admitió176/176 entradas. No hubo cambio del lector para obtener otro signo. La respuesta temprana q+4 y la fija q+6 fueron ambas −1 material: **no NULL y no una respuesta material cero**.

La convención temporal importa: el frameT es anterior a la aplicación de las entradas programadas paraT; el frameT+1 incorpora su admisión y una actualización v27. Así, el frame817878 todavía muestra vacíos los puertos de las contribuciones que reciben entradas con recibo aplicado817878. No existe en esta captura un estado público separado entre la admisión y esa actualización.

| Frontera | Sitio/relación observada | Campos decisivos |
|---|---|---|
|817876|Fila x19,y53,z17, antes de las entradas FI|state1, s_reg0, SEM1, dirección(0,0,+1)|
|817879|Primer agregado derecho nominal (15,47,21)|state1, s_reg17, SEM1, dirección(0,+1,0)|
|817880|Sitio (15,48,21)|Mismos campos del candidato17|
|817881|Sitio (15,49,21), tras el aporte genérico de giro|state1, s_reg17, dirección(+1,+1,+1)|
|817884|Cuatro entradas dirigidas al padre derecho (19,53,25)|Una con s_reg17 y tres con s_reg0; cuatro vecinos vivos apuntan al destino|
|817884|El propio destino (19,53,25)|Ya está activo: state1, s_reg0, SEM1, dirección(0,0,+1)|
|817885|Padre derecho (19,53,25)|RAW0; no se formó allí la agregación nominal esperada|
|817885|Sitio siguiente (19,53,26)|Se observa la configuración de carga cero, dirección+Z|
|817897|Raíz derecha nominal (29,65,35)|state1, s_reg0, dirección(0,+1,0)|
|817897|Raíz izquierda nominal (62,36,1)|state1, s_reg14, dirección(0,−1,0)|
|817933|C=(12,17,18), q+1|state1, s_reg14|
|817935|S=(14,15,16), q+3|state1, s_reg14|
|817936/817938|E y lector fijo|Carga5 con dirección de respuesta negativa; −1 material|

La tabla muestra estados y relaciones de vecindad medidos. No etiqueta como el mismo objeto todo lo que tiene carga17. El recorrido propuesto por la geometría sólo ayuda a ubicar las observaciones; no sustituye al registro. El último candidato entrante nominal observado está en817884 y el primer padre nominal vacío en817885. Esto acota el fallo de formación mucho antes de la lectura final. Todavía no demuestra por sí solo que el contenido no exista bajo otra forma o en otro lugar.

## Recalcular la actualización local sin ejecutar el motor

El archivo congelado `4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp`, SHA `fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`, diferencia el destino vacío del destino material. La función `buscar_fuente_demux` puede reducir fuentes que apuntan al destino dentro de la rama de vacío. Un destino con state>0 y SEM1 entra en la regla de materia.

En817884 se exportaron completos el destino y sus26 vecinos. Hay cuatro vecinos vivos, no existe ninguna firma tetraédrica y no hay una entrada Native programada en esa frontera. La regla local selecciona T_local=2,5 y calcula:

`floor(4 × 2,5 / 26 + 0,5) = 0`.

El resultado RAW0 observado en817885 coincide exactamente con esa rama. Éste es un recálculo documental de la regla sobre datos congelados; no es otra ejecución de Runtime ni una edición de su estado. La configuración ceroZ que ocupa el destino sigue encontrándose, por sus campos exactos y posición traducida toroidalmente, en69/69 cortes. Ese ajuste no identifica su fuente única ni certifica genealogía entre objetos.

**Interpretación sostenida hasta aquí:** la comparación incorrecta final tiene un antecedente físico local verificable: el destino intermedio ya no es vacío cuando llegan las contribuciones y cambia la rama de actualización que se aplica. **Límite:** sólo con REAL no queda aislada la responsabilidad causal de ese ocupante. La intervención legal y su sham son la prueba posterior pertinente; no se declara realizada antes de sus primarios cerrados.

## REAL frente a ausencia de retorno: diferencia histórica delimitada

Los prefijos cerrados REAL y NONE alcanzaron817876 con las mismas1857 actualizaciones,407/407 entradas aplicadas, dos productos y cinco usos de palabras correctos en cada historia. Los snapshots inmutables referidos por los primarios fueron leídos sin SQLite ni VIDA actual; sus SHA se verificaron antes/después.

Antes del FI sólo difiere un sitio RAW entre ambos universos: el banco R06 B=(20,53,5), estacionario, s_reg156 en REAL y157 en NONE. Los demás300.762 RAW y todos los clocks son idénticos; también las1056 interfaces y las agendas vacías. Ocho recibos históricos y siete claves de metadata difieren, por lo que no hay identidad causal u operativa completa. La configuración ceroZ anterior al choque es igual en ambos.

El FI NONE también cerró con176/176 entradas y −1 material en q+4/q+6. La comparación global de69 pares de fronteras demuestra que **sólo persiste la diferencia del banco B**, que termina157 frente a158. Todo el resto de RAW y todos los clocks siguen coincidiendo. Las176 solicitudes actuales y sus176 resultados de admisión son iguales. No aparece otra diferencia global atribuible a esa diferencia de historia dentro de la ventana capturada. Ambas condiciones presentan la misma interferencia y C/S14.

Esto no demuestra que la historia sea irrelevante en general. Tampoco prueba que las historias completas hayan convergido: recibos, metadata y entornos siguen distintos. Delimita un negativo concreto: la variación histórica entre estos brazos no explica por sí sola la recuperación de FI en esta ventana, y no elimina el mecanismo anterior de selección aprendido en otro dominio.

La continuación YOKED también produjo −1 material en ambos lectores con176/176 entradas. Su captura reconstruida es **RAW/clocks globalmente idéntica a REAL en69/69 fronteras**: D(T) vacío. Se trata de equivalencia física observada ante esta oportunidad posterior, no de igualdad de recibos, metadata o productos ambientales de sus pasados. No demuestra ventaja de contingencia propia ni convierte las ramas de prefijo compartido en réplicas independientes.

## Control de contenido b2/b3: convergencia física localizada

El ensayo b2 cambia la entrada pública14/3 por14/2. Bajo el codec fijo, sólo cambia el payload17→18 del puerto `MU.raw.L128.right.root.0.0.raw.0`, sitio(14,46,20), tick817878. Las otras175 solicitudes, sus tiempos y los176 resultados de admisión son iguales. El lector sigue devolviendo−1.

La diferencia global RAW aparece por primera vez en817879, afecta exactamente un sitio en cada una de seis fronteras817879…817884 y desaparece en817885. **Desde817885 hasta818074 todos los RAW y clocks de los300.763 sitios son idénticos en cada frontera capturada.** Así se descarta, en esos buffers y en la cobertura temporal efectiva, que la diferencia de payload simplemente se encuentre fuera de la ruta nominal. No se convierte esta igualdad en un certificado del estado operativo completo.

El snapshot final completo permite precisar dónde queda un registro de la distinción. El prefijo causal serializado de Runtime es idéntico: RAW, clocks, interfaces, agenda e historial de126.659 recibos. Los recibos Native no contienen un campo payload. Sin embargo, tres claves de metadata difieren y el registro organizacional conserva exactamente una operación distinta, índice127604: `EXPERIENCE_PROTOCOL interface=MU.raw.L128.right.root.0.0.raw.0 at=817878 load=17 receipt=126548` frente a `load=18`. Las secciones de receta, protocolos, ediciones diagnósticas, decodificadores y traza organizacional son iguales. El metadata de servicio también registra hashes diferentes de literal/resultado, identidades y revisiones de instrumentación/puentes. Se conservan esas diferencias; no se afirma identidad binaria del paquete completo.

Por ello el resultado es **convergencia de la influencia física del contraste dentro de RAW/clocks**, con un registro explícito de las operaciones que sigue distinguible. No demuestra borrado de toda información ni memoria funcional del diario. No se probó ni se proporcionó al participante acceso a ese registro para resolver FI. Los primarios conservan además los payloads exactos y las solicitudes públicas.

## Intervención legal y control de dosis: prevención local demostrada

Desde el mismo prefijo estable817876 se ejecutaron dos condiciones preparadas. GUARD admite en817878 una entrada adicional de carga0, state0, SEM4 y dirección estacionaria en(19,53,20), antes del paso de la configuración ceroZ. SHAM admite la misma clase de entrada, dosis y calendario en(21,53,20), fuera de la ruta examinada. Ambos admiten177/177 eventos: los176 del FI son idénticos por canal, tick, carga y campos registrados; sólo se añade el soporte específico. Los IDs Native se desplazan por la entrada extra y no se cuentan como nuevas experiencias independientes. No hubo escritura de RAW/clocks por Python, restauración de un futuro favorable ni cambio del codec o los lectores.

En817878 los buffers todavía son idénticos. La primera diferencia global aparece en817879: la guarda es SEM4/state0 y absorbe la configuración entrante en su propio sitio. En817884, GUARD mantiene vacío el destino(19,53,25), mientras SHAM conserva el ocupante ceroZ activo. **Los26 vecinos y las cuatro entradas dirigidas de ese destino son exactamente iguales en ambos brazos.** Lo que cambia la actualización es el estado propio del destino, como predice la distinción de ramas del kernel: GUARD forma17 y dirección(0,+1,0) en817885; SHAM produceRAW0. El agregado derecho vuelve a alcanzar la raíz; C/S contienen31 enGUARD frente a14 enSHAM. Los lectores originales q+4/q+6 producen+1 frente a−1.

La comparación completa no sólo escogió la región favorable. GUARD/REAL conserva clocks iguales en69/69 fronteras y sus diferencias RAW afectan como máximo cinco sitios por frontera. Al cierre818074 sólo difieren dos: el soporteSEM4 instalado y la ausencia de la configuración ceroZ en su posición tardía. SHAM/REAL sólo añade su soporte fijo en las fronteras posteriores al nacimiento y mantiene el desenlace erróneo. Los bancos A/B del selectorR06 y A/B de MU tienen RAW/clocks idénticos entre GUARD/SHAM en69/69 fronteras. Este último dato es conservación física acotada; no sustituye al panel material de capacidades.

Este contraste apoya causalmente el mecanismo específico de interferencia y una protección local **P0 preparada**: un soporte legal intercepta una configuración antes de que cambie la rama de actualización de una unión funcional. No demuestra que DEE haya aprendido a instalarlo, elegido cuándo protegerse o iniciado una recuperación. No certifica que el soporte sea inocuo ante todos los usos futuros. La evaluación de conservación y la adopción permanecen separadas.

Posteriormente, la misma vida `ECI02_PI03_REPRO_PI04_PI05_GUARD_01` continuó818074→819484 y utilizó correctamente12/12 funciones del panel: palabras aprendidas, accesoalfa, comparaciones positiva/negativa/cero, números13/8 y accesos posteriores aalfa/luma. Fueron929/929 entradas Native aplicadas, sin rechazos; son entradas, no929aciertos ni conceptos. No se reinyectó la guarda. La orden externa `habitat_off` fue de cero ticks y no constituye un decimotercer test. La secuencia de ventanas la coordinó el operador; no es un plan autogenerado. Este panel material sí aporta conservación de uso en esa candidata hasta su corte probado. No se extiende automáticamente al último estado futuro ni equivale a adopción del principal.

## Continuación funcional de esa misma candidata hasta824911

Los seis primarios de integración están cerrados y enlazados por el hash de la fase anterior. Después del panel, la misma vida probó20/7→+1,4/16→−1 y13/13→0 material:3/3,528/528 entradas,819484→820078. Son reservas de comparación dentro de su contrato; el cero no se reemplazó por ausencia de respuesta.

Luego conservó el estado entre tres fases/procesos y realizó seis trabajos C2C adicionales. Las primeras elecciones Native fueron signos−/+ definidos; no se observó allí un silencio ni se sustituyó por una solución. La operación seleccionada produjo un número real y ese número fue la entrada de otra comparación Native que determinó la ruta externa. Los valores de referencia se calcularon después para evaluar, no para responder por DEE.

|Ordinal|Contexto ofrecido|Primera elección|Operación y resultado Native|Segunda elección/ruta|Consecuencia registrada|
|---|---|---|---|---|---|
|22|2|−1|29−4=25|+1|Producto64B|
|23|6|+1|6+5=11|−1|Producto64B|
|24|3|−1|26−4=22|+1|Producto64B|
|25|7|+1|7+6=13|−1|Producto64B|
|26|1|−1|12−3=9|−1|Producto64B|
|27|8|+1|16+11=27|+1|Producto64B|

El balance registrado es6/6 productos,384bytes y1116/1116 entradas Native, sin rechazos, hasta824621. Es una extensión de uso integrado y conservación local del selector contextual previamente adquirido. No demuestra adquisición nueva de una política, superioridad sobre una alternancia en este orden de casos, iniciativa para abrir los episodios ni planificación de la cadena. El operador ofreció los trabajos, coordinó las ventanas y el pipeline; DEE seleccionó los signos y produjo los números dentro del aparato declarado. La crítica histórica de PI04 —YOKED20/20 frente a REAL19/20 y ausencia de ventaja de contingencia propia— sigue vigente; estos seis trabajos no la anulan.

Tras otra fase, la candidata produjo FI14/3→+1, luma→+1 y alfa→−1,3/3 con190/190 entradas, y cerró en824911. **El último panel completo12/12 corresponde a819484; el último corte824911 sólo tiene esos tres testigos posteriores**, además de los seis trabajos intermedios registrados. No se vuelve a etiquetar el último corte como si hubiera recibido otro panel completo. Todas las fases declaran cero reinyecciones de guarda. No hay un merge entre futuros ni un segundo aprendizaje importado por función.

El paquete `fuentes/RECALCULO_GLOBAL_PORTABLE_PI05_R01/` deja seis contrastes documentales reproducibles sin originales y conserva también la comparación de una reproducción fría Native efectivamente ejecutada localmente desde prefijo completo:198ticks,177/177entradas, mismos69hashes y lectores. Esa reproducción en copia no se suma a la vida candidata. El comando del paquete sólo recalcula registros; no ejecuta el motor, la adquisición ni otra reapertura Native.

## La configuración ceroZ es anterior a C2C

Se inspeccionaron literalmente los67 sitios de la fila x19,y53 en dos pares estables de reproducibilidad:

|Corte estable|Observación de la fila|Alcance|
|---|---|---|
|PI03_FINAL_T775355|Ningún sitio de la fila con state1/SEM1/s_reg0/dirección+Z; hub real(19,53,3) RAW0|No es ausencia global de configuraciones+Z en otras filas|
|PI03_PI04_C2B_STOP_T800379|Un sitio coincidente en(19,53,7), RAW1224979098644774913; hub real(19,53,3) RAW0|Ya existe antes de los nuevos ensayos C2C|

La fase7+17497 mod67=17 es compatible con la observación preFI en817876. La compatibilidad no enlaza genealógicamente los dos cortes. La observación anterior a C2C sí debilita una explicación de aparición exclusiva durante el reajuste C2C. El origen queda acotado como desconocido; no se reconstruye un evento fundador a partir del valor cero o de que la fila también cruce el hubR06.

La revisión del journal C2B añade un testigo anterior: línea30 registra el hub real(19,53,3) en800375 con state1/s_reg0/SEM1/+Z, antes de aplicar el retorno programado800375. Las líneas31/32 registran ese hub RAW0 en800376/377. El último ensayo C2B tenía query800101/read800107 y respuesta+1;800377 era contacto del retorno, no q+4 de aquella decisión. No hay registro local de(19,53,5)en800377 en ese journal. Por tanto el último retorno no queda identificado como origen único; ya existía una configuración coincidente antes de su aplicación. El enlace hasta z7 en800379 sigue siendo compatibilidad de etapas, no genealogía resuelta.

Corrección de instrumentación documental: el primer testigo de fila R01 había llamado «hub» al puntoz5, aunque sus67 lecturas eran literales y correctas. El hub declarado es Q+(0,−1,−2)=(19,53,3). Se preservó R01, se documentó el error de etiqueta y R02 utiliza z3. El hallazgo de z7 y el contraste guarda/sham no dependen de esa etiqueta.

## Reproducción documental transportable

`codigo/analizar_influencia_global_PI05_R01.py` lee el codec completo, reconstruye los buffers y exporta todos los RAW!=0, todos los nodos nominales y D(T) global a iguales ticks. Conserva las diferencias iniciales; no las elimina para buscar un resultado favorable. La ventana±1 informa los ticks que faltan.

El recálculo adicional `codigo/recalcular_inventarios_globales_PI05_R02.py` permite transportar inventarios pequeños sin los archivos de origen: reconstruye los300.763 RAW con los valores exactos exportados y ceros en las demás posiciones y exige el SHA original de cada buffer. Reconstruye clocks uniformes y exige también su SHA original. Si no son uniformes, rechaza esta receta compacta y exige el codec completo. No adivina clocks omitidos. La igualdad de D(T), sus índices y los hashes originales coincide69/69 con el segundo método que leyó íntegramente los XOR. No son réplicas Native independientes. R02 añade el emparejamiento documental por canal+tick para contar eventos comunes/extra sin confundir el desplazamiento de lista causado por el soporte; D(T) es idéntico al de R01, que permanece preservado.

Comando real, sin motor:

```text
python recalcular_inventarios_globales_PI05_R02.py --inventario-a INVENTARIO_A --inventario-b INVENTARIO_B --destino NUEVO
```

No abre las rutas históricas que permanecen en las procedencias. Requiere los miembros de inventario y su manifiesto. El destino debe ser nuevo. No funciona como sensor cognitivo ni da estos mapas al participante.

## Primarios, controles y localizadores decisivos

Todos los siguientes localizadores son relativos a P5 salvo que indiquen una campaña anterior:

- `control/PI05_REAL_FI_GLOBAL_R01.json`: operación real, propietario cerrado,176/176,198 ticks y localizador de captura. Primario material: `ensayos/PI05_REAL_FI_GLOBAL_R01_FI.json`, pointer `/result/result/rows/0`; `result` exterior puede estar serializado como JSON-string.
- `control/PI05_NONE_FI_GLOBAL_R01.json`: condición histórica NONE con igual FI; no es otra experiencia de MAIN.
- `control/PI05_YOKE_FI_GLOBAL_R01.json`: condición histórica desacoplada con FI erróneo e igualdad física completa con REAL en la ventana observada.
- `control/PI05_GUARD_FI_GLOBAL_R01.json` y `control/PI05_SHAM_FI_GLOBAL_R01.json`:177/177 en cada brazo y resultados opuestos con lectores intactos.
- `control/PI05_INTEGRACION_PANEL_R01.json`: misma candidata protegida818074→819484,12/12usos,929/929entradas y guarda persistente sin reinyección. No hubo C2C en esta fase del panel.
- `control/PI05_INTEGRACION_COMPARACIONES_R01.json`, `PI05_INTEGRACION_RESERVA_R01.json`, `PI05_INTEGRACION_RETENCION_R01.json`, `PI05_INTEGRACION_REAPERTURA_R01.json` y `PI05_INTEGRACION_FINAL_R01.json`: mismo estado continuado, reservas de comparación, seis trabajos y testigos finales hasta824911. Cada fase contiene sus primarios y el hash de la anterior.
- `control/INVENTARIO_REAL_FI_GLOBAL_R01/` y `control/INVENTARIO_NONE_FI_GLOBAL_R01/`: `RESUMEN_GLOBAL.json`, RAW exactos no nulos, nodos nominales y manifiestos.
- `control/AUTOPSIA_TRANSITO_REAL_GLOBAL_R01.json`: Moore26, estados/RAW/clocks, candidatos de traslación, regla local y límites. SHA `13abf8f92a48aac434b09be0bcc862d5d5b5110fcda81fc9bc1d98c546355bbe`.
- `control/CONTRASTE_PREFI_REAL_NONE_GLOBAL_R01.json`: comparación integral de snapshots817876 y preservación antes/después. SHA `affd39666ae4a1e396d1fca163dfc83ff701423f8fa18fac977681a5b238442b`.
- `control/CONTRASTE_GLOBAL_REAL_NONE_FI_R01/RESUMEN_INFLUENCIA.json`: D(T) completo con lectura XOR. SHA `20d243c18d14eb42329891f1f2c18c1f65fa596ac71e2c832c4fc12b30ae3d27`.
- `control/RECALCULO_PORTABLE_REAL_NONE_R01/RECALCULO_GLOBAL_PORTABLE.json`: reconstrucción hash-verificada compacta. SHA `27559105ad274175ffd82262100418594165d3fccdc4b1d4a4d206c525f38e78`.
- `control/ACUERDO_DOS_RECALCULOS_REAL_NONE_R01.json`: coincidencia de ambos métodos69/69. SHA `fb0d43dd644858062fd91a1ac27db8d243fd603db4f20bfebbdcff41532f8019`.
- `control/CONTRASTE_CAUSAL_GUARD_SHAM_PI05_R01.json`: alineación de eventos, vecindario crítico completo, predicciones de ambas ramas, estados y límites. SHA `6a530b4cbcbbdd1be760f1923392f5cd90a84f1a168c8cd5a78004f8ef5481eb`.
- `control/RECALCULO_PORTABLE_REAL_YOKE_R01/RECALCULO_GLOBAL_PORTABLE.json`: D(T) global vacío69/69, SHA `17360dc2584909a67234be36679f54ced7e17235948f5a253393c88aff24cd0f`.
- `control/RECALCULO_PORTABLE_GUARD_SHAM_R02/RECALCULO_GLOBAL_PORTABLE.json`: diferencias globales y176 eventos comunes/soporte propio por brazo, SHA `d2e1d702869ab44ed064a10e9f7975675f56a037d9e5e8f622b6ceb35876be83`.
- `fuentes/KERNEL_V27_EXTRACTO_ACTUALIZACION_185_352.txt`: extractos literales de constantes/firmas25–172 y reglas185–352, con hash del archivo fuente completo. SHA `47c1dc38138da399d859733765e2913acdddbf9da96165eda7925e6ed0d8494a`.
- `control/FILA_ZERO_Z_ANTERIOR_A_C2C_PI05_R01.json`: filas históricas completas, pares, hashes y ausencia de asignación de linaje. SHA `6ea5be3d0a2a8c04fe7c61c151e06f032606134c277ffd200c5378ec88d14985`.
- `control/FILA_ZERO_Z_ANTERIOR_A_C2C_PI05_R02.json`: mismos67datos por corte y etiqueta de hub corregida a z3; no es otra ejecución Native.
- `fuentes/ORIGEN_ACOTADO_ZEROZ_C2B_EXTRACTO_PI05_R01.json`: líneas30–33 literales, último calendario y corrección de etiqueta. SHA `31e921624755c7db190bb0bc88aa76ee9ccfc5ffab6eacfc588657cda60f9064`.
- `control/RECALCULO_PORTABLE_REAL_B3_B2_R02/RECALCULO_GLOBAL_PORTABLE.json`: seis fronteras diferentes y convergencia global desde817885, SHA `8e087835d04c4e02d29f9e7ad1c1f0eaeb1ebead86bf3f660741c0311483ce62`.
- `control/CONTRASTE_SNAPSHOT_COMPLETO_B3_B2_PI05_R01.json`: prefijo Runtime exacto,126.659recibos, tres clavesmetadata distintas, SHA `aaba4213009996b8e533d99d30d21a754f01651717f074a6f15fe78545dfc423`.
- `control/CONTRASTE_ORGANIZATIONAL_B3_B2_PI05_R01.json`: operación literal load17/18 y secciones del serializador organizacional, SHA `14b69a8932e1f4037e8d5260b3fc179466935ea03c4c7c8869dd7b1a640f7430`.
- `fuentes/TESTIGO_HISTORICO_FI128_14_3_PI03.json`: extracción literal de C/S31, referencias y lectores positivos. SHA `6362673ee924a6e9578f0685f9829ded5c8687aecfbd2112f80a24daae404ef9`.
- `fuentes/F1_RUTA_FI128_Y_CAPTURA_GLOBAL_PRE_NATIVE.md` y `fuentes/F1_HIPOTESIS_GLOBALES_PRE_DATOS_R01.json`: contratos/176entradas y las hipótesis anteriores a las capturas. CORE09 y CPC9 no se tratan como el mismo expediente.
- `fuentes/RECALCULO_GLOBAL_PORTABLE_PI05_R01/`:37archivos totales,36contenidos hash-verificados más un manifiesto; tres condiciones principales y tres controles adicionales, sin motor. `control/PRUEBA_BUNDLE_GLOBAL_REUBICADO_PI05_R01/VERIFICACION_REUBICADA_SIN_ORIGINALES.json` verifica seis comparaciones desde una copia nueva con acceso a originales prohibido durante la ejecución, SHA `1932face2e260ac9096e0456e84f40d828905751ae6ac18cf30fbb4812c4cdbf`.

## Frontera actual y pruebas todavía pendientes en este corte

Ya hay un avance explicativo y causal sobre el fallo: se ubica un encuentro intermedio con la totalidad del vecindario, se recalcula su actualización y una intervención legal de dosis emparejada recupera la función, mientras el sham conserva el fallo. También hay negativos globales útiles: REAL/NONE conserva una diferencia física de historia en un banco sin cambiar el tránsito fallido; REAL/YOKED coincide físicamente en toda la ventana y tampoco lo recupera.

El presupuesto fijo de6GB llevó al responsable a omitir B4 y los dos brazos de reutilización inmediata0 antes de que existieran sus resultados; la previsión completa excedía6GB y el recorte conservaba margen para continuidad/adopción. No se borró evidencia para simular cumplimiento. Sólo b2/b3 tiene contraste global ejecutado. B4 queda como predicción deductiva no probada, no como un tercer ensayo. La guarda es una preparación física externa P0, no una regulación aprendida ni una acción iniciada por el ente. La eventual adopción pertenece a una puerta posterior; este corte no anuncia una promoción, aprendizaje nuevo de reparación, iniciativa autónoma ni recuperación general. Los futuros adversos, los silencios y las respuestas erróneas materiales permanecen como evidencia.

**Predicción exploratoria de la reutilización0, no ejecutada:** repetir inmediatamente desde el futuro fallido818074 también cambia la fase relativa. En ese corte la configuración ceroZ está en z14; su llegada a z25 no coincidiría con la misma primera unión nominal del nuevo FI. Por ello una repetición sin guarda podría recuperar una respuesta correcta sólo por fase, aunque otros encuentros todavía podrían interferir. Esta posibilidad deriva del diagnóstico abierto y no es una reserva ciega ni un resultado ejecutado; reutilización0 fue omitida.

**Recuperación efectivamente ejecutada:** el protocoloR03 prescribe esperar **3ticks**, no tres vueltas, desde el futuro fallido818074, sin entradas durante esa espera. Ambos brazos llegan818077, programan un soporte legal, ejecutan el mismo FI198ticks y cierran818275:201ticks totales y177/177 entradas en cada brazo. GUARD produce+1 en ambos lectores ySHAM−1, con propietarios cerrados. Esto respalda recuperación funcional asistidaP0 desde un estado que ya había fallado, sin reenseñar bancos ni restaurar un estado anterior. Son dos clones diagnósticos; no se fusionan con la vida preventiva que continuó hasta824911. No hay una captura global69nueva de estos brazos: esta conclusión utiliza los primarios normales y sus controles emparejados.

Corrección documental explícita: una nota anterior de este frente confundió el sufijoG3/S3 con tres vueltas y escribió201como espera. Los protocolos/primarios reales dicen`legal_wait_first_ticks=3`y`FI_only_Native_ticks=198`;201es su suma. Aquella suposición no fue un ensayo ni es su interpretación final. Fuentes: `control/PROTOCOLO_RECUPERACION_PI05_R03.json`, `control/PI05_REC_G3_R03.json` y `control/PI05_REC_S3_R03.json`.
