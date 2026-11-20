# Composición asistida: controles causales mínimos

Se ejecutaron cuatro operaciones en tres vidas de control, todas bifurcaciones exactas de snapshots completos de MAIN. El diseño se fijó en `PROTOCOLO.json` antes de los nuevos ticks. No se avanzó MAIN, no hubo edición de campos, cambio de lector ni feedback correctivo.

| Control | Prefijo completo | Intervención | Resultado físico y operación real |
| --- | --- | --- | --- |
| U1/U2, `FI01_BCOMP_U` | MAIN T17025, frontend ya preparado, antes de19experiencias | Evolución pasiva hasta31673; raw11/29/13/32; gamma[21,4] inicia cadena; guardar y finalizar en otro proceso | Cuatro respuestas+; gamma+ preparó archivo13bytes. La primera lectura del archivo en otro proceso produjo+, repitió el mismo trabajador y **no hizo commit**. Pendiente real conservado. |
| `FI01_BCOMP_noDatum` | MAIN T31832, pendiente SHA32, referencia adquiridaD−20 | Mismos tres pulsos de consulta; dato actual omitido; lector6 q+6 | Signo−; el trabajador− repitió el de preparación, verificación fallida. Pendiente32bytes conservado. |
| `FI01_BCOMP_sham` | Exactamente el mismo MAIN T31832 | Dato32dir0 en(14,15,23), fuera deS; consulta y lector idénticos | Signo−; verificación fallida, pendiente32bytes conservado. |

El contraste directo ya registrado en `B_MAIN_05_CADENA_2_FIN.json.gz` usa el mismo prefijo T31832, q31840, lectorT31846 y finalT31848, pero suministra la longitud real32enS. Produce+ y commit. Los controles cambian el acceso al dato, no seleccionan después otra lectura ni ofrecen el signo esperado. El criterio del trabajador requiere usar otro ejecutor que el de la preparación y verificar bytes reales de su artefacto; esa ley ambiental no decide la emisión de DEE.

U separa adquisición de envejecimiento: comparte el prefijo previo al currículo y la edad31673, no las19entradas docentes. El estudio T/U/H con shams y comparación RAW completa, archivado aparte en `transferencia_b`, aporta el contraste de dosis que este control de omisión no tiene por sí solo. No son réplicas independientes ni se fusionan sus experiencias.

Los cuatro procesos conservaron34/34 entradas admitidas, siete lecturas escalares válidas, una consulta de contenido circulante y cuatro operaciones reales de archivo. En los tres intentos de verificación se comprobó el artefacto de preparación, pero se utilizó el mismo trabajador y no hubo commit. La preparación U sí fue aceptada. Los fallos y las transacciones pendientes permanecen en snapshots completos; no se restauró un futuro favorable.

Esto sostiene una **composición ambiental asistida** de dos mecanismos adquiridos en una misma vida cuando el dato pertinente está disponible: contenido opaco→primera operación→archivo real→sensor fijo de longitud→comparación nativa→segunda operación. El operador todavía inicia dos etapas y elige el contexto público. No es iniciativa autónoma, planificador aprendido ni transferencia sin codec preparado.

Continuidad adversa: U quedaT31781, snapshotSHA `8db2c8c07cc119535b7196bf7f7f378b5b65154a2444ca79a8b2a8b0097ab396`; noDatumT31848 `e25e0855bd511de401af155b66563795acb54f3ba82092804c43c2be4158a695`; shamT31848 `edbf296668e2a16fb9db04a8b5da294e0be1df7a61fe0d001966ac27bf3f5a71`. Los paths completos están en los registros existentes `sistema/estado/vidas/FI01_BCOMP_*/VIDA.json`.

`recalcular_controles_cadena.py` sólo utiliza stdlib: deriva signos de paneles físicos, verifica RAW/clocks uint64, recibos, artefactos pendientes base64/hash y contenido zlib/SHA. No ejecuta el motor ni el trabajador. Los primarios completos, positivos y negativos, se conservan en `evidencia/campanas/MENTE_UNIFICADA_Y_FI01/composicion_b/`.
