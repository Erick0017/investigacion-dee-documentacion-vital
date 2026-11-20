# F1 — una huella física de salidas recientes, con uso perjudicial ya demostrado

Inspección: 9 de noviembre de 2026, America/Mexico_City. Análisis retrospectivo de PI03; cero ticks nuevos, ningún módulo DEE importado y ningún archivo operativo modificado. No se hicieron inventarios generales. Este resultado corresponde a un observador del investigador, no a una nueva capacidad adquirida por MAIN.

## Resultado concreto

La fila toroidal **x=19, z=5, Y=0…66** del aparato R06 sin la guarda OP3 conserva información específica sobre salidas materiales recientes. En **42 snapshots** R02 —catorce oportunidades en cada una de tres historias emparejadas— la ocupación de Y60, Y38 y Y16 coincide exactamente con cuáles de las tres últimas respuestas fueron **cero material**, frente a +1. No se leyó el diario para obtener esos tres estados: se extrajeron RAW y clocks de los snapshots completos ya existentes. Los primarios se utilizaron después para contrastar el contenido histórico propuesto.

Es una huella de **respuestas físicas anteriores**, no de los recursos obtenidos, la conexión correcta del dispositivo, el significado de una palabra ni las respuestas aritméticas 8/13. El cero Native no era ausencia: su portador tiene RAW `1157425104234217473`, state=1, SEM1, s_reg=0 y dirección (0,+1,0). La traducción posterior cero→motor−1 pertenece al codec preparado.

En los tres finales R02 de igual edad T764407:

| Historia | Fila Y con ese portador | Bancos s_reg | Diferencias RAW globales respecto al real |
|---|---|---|---:|
| real | ninguna | 28/27 | — |
| retorno constante de no fallo | 16, 38, 60 | 29/29 | 5 sitios |
| actuación anulada después de producir/copiar salida | 38 | 22/22 | 3 sitios |

Las cinco y tres diferencias se localizan exclusivamente en los dos bancos y en esa fila. En **las 28 comparaciones globales por oportunidad**, ninguna diferencia RAW queda fuera de esa región. Los hashes globales de clocks son iguales entre los tres brazos en los catorce cortes de edad emparejada. Esto delimita diferencias físicas concretas; no acredita igualdad de todo el estado causal, sus recibos, metadata o entorno externo.

La fila **no identifica unívocamente la historia completa ni el brazo experimental**. Por ejemplo, durante varias oportunidades la condición real y el retorno constante tienen las mismas tres colas, aunque sus bancos y consecuencias anteriores difieran. La huella observada sólo concuerda con una ventana de salidas recientes dentro del calendario ensayado. No se ajustó un clasificador de nombres de casos ni se calculó una política para el ente.

En los 42 cortes aparecen las ocho configuraciones de ocupación de esas tres posiciones: ninguna; cada una de las tres aislada; cada uno de los tres pares; y las tres juntas. No es sólo un contraste entre «muchas» y «pocas» colas. Esas ocho configuraciones no son ocho conceptos, aprendizajes independientes ni una medición de entropía uniforme; son patrones físicos distinguibles en esta muestra y este observador.

## Cómo se obtiene y qué se contrastó

El lector original fijo detecta el cero en (19,56,5), en q+6. En estos protocolos el corte posterior satisface:

`T_corte − T_lectura = 67 × vueltas_de_demora + 4`.

Una traslación recta del portador hasta el corte lo sitúa en Y60. Entre cierres sucesivos transcurren 782 ticks, con `782 mod 67 = 45`: las posiciones siguientes compatibles son Y38 y Y16. El observador exploratorio toma las tres últimas respuestas cero y calcula:

`Y_predicha = (56 + T_corte − T_lectura_anterior) mod 67`.

Se comparó el conjunto completo predicho con **todos los RAW de los 67 sitios**, incluyendo las posiciones vacías; no sólo se buscó una señal favorable. La coincidencia exacta se obtiene en 42/42 cortes R02. La representación conserva los 67 RAW y clocks, los tres sitios del lector al corte, el lector original registrado en q+6, los dos bancos y los hashes globales. No se copian de nuevo los snapshots: el resultado contiene su ruta, tamaño y hash exactos.

Los 42 cortes no son 42 individuos ni 42 aprendizajes independientes. Las tres historias comparten prefijo y cada una es continua. El observador se propuso después de conocer los resultados R02; sus ocho oportunidades originalmente reservadas **no son una reserva independiente para este lector nuevo**. El tamaño de ventana tres se identificó retrospectivamente. La regla describe los cortes observados, no simula encuentros no registrados ni demuestra por sí sola cómo desaparece cada portador más antiguo.

## Extensión existente R04: cinco cortes más, con límite de cegamiento

La misma regla, sin modificarla, coincide con **5/5** cortes R04: T765189, T765971, T766753, T767535 y T768317. Sus salidas fueron +1,+1,+1,0,0; las filas resultantes son vacía, vacía, vacía, Y60 y Y38/Y60.

Los dos intervalos aritméticos intercalados duraron 396 ticks cada uno. Se usaron los tiempos reales de cada consulta y corte, no un desplazamiento aproximado: las demoras lectura→corte son 205,205,272,272,272 ticks. Los cierres de oportunidad siguen separados por 782 ticks; por ello esta extensión no rompe la relación temporal preparada ni demuestra generalidad frente a calendarios arbitrarios.

Los cinco cortes intermedios no se utilizaron para derivar la regla de R02. Sin embargo, el extremo final R04 Y38/Y60 ya se conocía de la autopsia PI03. **No es una validación prospectiva ciega**: es una extensión retrospectiva con contaminación parcial del extremo. No se anuncian nuevas simulaciones ni una reserva creada después de ver sus respuestas.

## Relación con R05: persistencia compatible e interferencia funcional

Los dos portadores de T768317 en Y38/Y60 predicen por traslación toroidal Y8/Y30 en T771503. El snapshot posterior al panel/OH coincide con esa predicción. Los nueve fotogramas q−1…q+7 del control R05 sin consulta también coinciden exactamente con la traslación de esas dos posiciones iniciales. Esto muestra continuidad espacial observada en la ventana de nueve ticks y compatibilidad de extremos separados por muchas vueltas; no identifica partículas únicas durante todo el intervalo no observado.

En cambio, la lectura fallida con consulta T771955 **no** coincide con la continuación recta sin interacción. R05 ya había mostrado el efecto causal: a igual edad y con el lector q+6 intacto, la guarda legal después del lector produce cero material y un archivo útil de 64 bytes; el sham produce NULL, ninguna actuación y cero bytes. El control sin consulta revela material antiguo cruzando la zona antes de solicitar una nueva respuesta. El resultado respalda interferencia de retornos físicos antiguos con la consulta; no convierte sus posiciones en una memoria nativa útil ni autoriza a leer un cero antiguo como respuesta nueva.

El análisis nuevo añade procedencia histórica **de clase**: esas configuraciones son compatibles con una huella de salidas cero recientes, no sólo con «ruido» sin información. No asigna identidad microscópica a un portador ni un recuerdo semántico por igualdad de carga. El uso funcional ya probado de las colas es perjudicial para el acceso en esa condición; no se ha encontrado en estos registros una recuperación útil de su contenido por el ente.

## Alcance en el principal adoptado

El snapshot operativo explícito ECI02_PI03_MAIN N67 T775355, SHA-256 `5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b`, contiene **cero portadores cero +Y** en esta fila. Su único RAW no nulo en la fila es la guarda preparada state=0/SEM4 en (19,57,5), RAW `4611686018427387904`. No se trató state=0 como espacio sin contenido.

El registro de las tres últimas actuaciones materiales es 0,+1,+1; aun así, la fila protegida ya no conserva el patrón de la anatomía anterior. **El observador de tres salidas no se aplica al MAIN protegido.** La guarda absorbe este soporte recirculante y evita la interferencia, sin que ello pruebe borrado global de esas experiencias: los bancos, las acciones anteriores y otros componentes no se reducen a esta fila. No se quitará la protección, copiarán colas antiguas ni injertarán recuerdos para presentar la huella histórica como capacidad actual del principal.

## Qué queda incorporable y qué falta

Se puede incorporar de inmediato este recálculo como **instrumento retrospectivo**, con dominio y procedencia explícitos. No corresponde anotarlo como recuperación iniciada por el ente, selección aprendida de lectores, memoria semántica o regulación autónoma. Las capacidades ya incorporadas y la protección P0 del principal no se modifican por este dictamen.

No hace falta repetir R05 para afirmar interferencia: sus controles existentes resuelven esa pregunta. Si se quisiera demostrar un **uso positivo** de la huella, el contraste nuevo indispensable sería otro: una interacción Native fija, declarada como aparato preparado, que transporte la presencia del retorno a una consecuencia verificable, con historias 0/+1 y cortes de cola frente a sham. El diseño debe congelar geometría, fase y lector antes de una reserva nueva; el anfitrión no puede mirar el diario y convertirlo en la respuesta ni elegir el puerto según la historia. Bancos diferentes entre las historias son un factor contribuyente: habría que aislar físicamente la ruta del retorno y comprobar que el corte afecta esa ruta sin modificar bancos o el sensor requerido.

Ese contraste todavía no está ejecutado ni especificado a nivel de una geometría validada. No conviene improvisarlo como requisito de cierre de F1: probaría inicialmente un acceso preparado, no recuperación autónoma, y el principal actual elimina precisamente esta cola para proteger sus funciones. El prefijo completo estable disponible para una copia diagnóstica anterior a OP3 es `reproducibilidad/materiales/PI03_CANDIDATA_T768317`, manifiesto `0c8992b417c142357907881260950d13217bc47e45a24fde8a00f40a643ac6b5`. No debe restaurarse sobre MAIN ni confundirse con su historia posterior.

## Material y repetición pasiva

`F1_RESULTADO.json` contiene los 47 cortes R02/R04 con localizadores exactos, RAW/clocks/firmas relevantes, las 28 comparaciones globales y la extensión R05. Los estados operativos completos permanecen en sus fuentes PI03 y en los pares estables; este conjunto pequeño no es un respaldo ejecutable.

Desde la raíz tests, usando el Python oficial ya existente:

```powershell
& '.\documantacion vital\DEE thinking\DEE Cognitive 2.0\motor\python313\python.exe' -I -B -X utf8 '.\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\F1_retornos_historicos\F1_recalcular.py' --output '.\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\F1_retornos_historicos\F1_RECALCULO_NUEVO.json'
```

El destino debe ser un JSON nuevo dentro de F1. El modo por defecto no sobrescribe un resultado existente. La lectura verifica SHA-256 esperado, formato de snapshot y CRC gzip, extrae los arrays y recalcula las observaciones; no recalcula el FNV interno de DEE, no importa el motor, no abre propietario, no consulta materialmente al ente ni avanza ticks. El recálculo de archivos es distinto de una reproducción Native.
