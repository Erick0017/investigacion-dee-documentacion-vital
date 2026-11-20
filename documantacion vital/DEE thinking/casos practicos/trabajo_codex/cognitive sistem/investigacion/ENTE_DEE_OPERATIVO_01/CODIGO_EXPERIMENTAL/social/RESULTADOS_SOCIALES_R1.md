# EO01: reutilización de B y límite de su receptor actual

Se ejecutaron ocho ensayos auxiliares acotados sobre bifurcaciones completas del mismo padre CF01_MAIN T67723, SHA-256 `205a34e3b0925fe6d9631d4934aaf29c427171f123d4176adf68bf44d76e07bb`. No se modificó CF01_MAIN, el predeterminado ni EO01_MAIN. Cada rama conserva su mundo completo mediante Store y no devuelve memorias a MAIN. Son controles y continuaciones del mismo prefijo, no ocho adquisiciones independientes.

## Resultado utilizable y límite

El lector de B puede renovarse dos veces por peticiones materiales de A en la misma vida auxiliar: ante las oportunidades fijas 10/18, A emite x0; B nace en T68439 y T70003. Los datos privados nuevos 52 y 36, admitidos en T68438 y T70002, producen respectivamente B− en T68440 y B+ en T70004. Las referencias privadas heredadas61/19 permanecen: no se adquirió una nueva memoria privada persistente de B.

Eso no demostró una nueva actualización social útil en el padre final de CF01. El receptor de A ya conservaba7/5. El primer mensaje nuevo cambió durante un tick la dirección del soporte izquierdo, sin cambiar su carga7; A mantuvo su dirección y el uso posterior común10/20 produjo−1. El segundo mensaje tampoco modificó permanentemente7/5 y el segundo uso común produjo−1. Por tanto, reutilizar B no equivale a readquirir otro contenido social persistente ni a mejorar una acción posterior.

## Ensayos y controles

| Caso | Preparación y entradas | Resultado observado |
|---|---|---|
| EO01_SOC_AUX_52 | B_incoming52 enT67724, horizonte80 | Entrada aplicada, B ausente durante la ventana; contexto7/5 sin cambio. |
| EO01_SOC_AUX_50 | B_incoming50, mismo calendario | Mismo límite del lector ausente. No es dosis emparejada con52. |
| EO01_SOC_AUX_36 | B_incoming36, mismo calendario | Mismo límite. No demuestra incapacidad de B cuando hay lector. |
| EO01_SOC_AUX_QUERY | Par público10/18, sin retorno nativo antiguo | A x0 enT68409; B se renueva enT68439 y emite+ enT68440; se libera enT68441. |
| EO01_SOC_AUX_INTACT | Query10/18, dato52 encritical+13; segundaquery10/25 según hipótesis de suma | B− formadoT68440; receptorizquierdo cambia direcciónT68462 y vuelve enT68463. La hipótesis7→14 fue falsa; segundaquery no renovóB. Usos10/20 y10/27:−1/−1. |
| EO01_SOC_AUX_CUT | Mismo prefijo, dato52; barreraSEM4 busminus encritical+19 | Primer corte aplicadoT68444, después de formarse B−; elimina el cambio de direcciónT68462. No cambia las actuaciones posteriores respecto del intacto. |
| EO01_SOC_AUX_SHAM | Igual aporteSEM4 en busplus | Primer sham aplicadoT68444; conserva el cambio localizado del receptor. Actuaciones posteriores−1/−1. No es garantía de que ese sitio sea siempre inerte. |
| EO01_SOC_AUX_REPEAT | Dosqueries10/18 fijas; datos52 y36; usos10/20 después de cada una | B−T68440 y B+T70004 en una vida. Contexto final7/5, actuaciones−1/−1. Final realT70851. |

El planR2 anticipaba que la segunda entrada podría sumar7→14. Esa predicción fracasó y no se reparó durante los tres brazos. En el octavo ensayo se fijó prospectivamente otraquery10/18, conservando la hipótesis fallida anterior como evidencia. No se cambió el criterio del octavo ensayo tras observarlo.

Las49 peticiones de los ocho ensayos incluyen datos privados, medidas públicas y cortes/sham:47 aplicadas y2 rechazadas por ocupación (segundo aporteSEM4 enCUT ySHAM). No se cuentan como dos cortes nuevos realizados. El propio175/171 no permanece numéricamente idéntico: QUERY termina177/173, y las secuencias de cuatro episodios183/179, manteniendo su diferencia4. Ese crecimiento equilibrado ocurre también sin el retorno antiguo y no constituye aquí aprendizaje de una consecuencia externa. B conserva61/19 en todas las ramas; los contextos terminan7/5.

## Atribución causal

El primer contraste intacto/corte/sham comparte el mismo pasado, par público y dato privado. En los tres se forma la misma emisión B−. La barrera legalSEM4 se aplica enT68444 al bus[12,19,9], cuatro ticks después; el sham usa[0,19,9], misma carga0 y semantic4. EnT68462 el RAW del receptor izquierdo difiere entre intacto/sham y corte. EnT68463 vuelve al RAW anterior. La dirección de A en el intervalo y las actuaciones posteriores coinciden. Esto demuestra un efecto local del mensaje y su interrupción selectiva, no necesidad social para una nueva decisión útil.

En la segunda emisión positiva del ensayoREPEAT se observa también un cambio transitorio del receptor izquierdo. No se le atribuye un linaje único «mensaje positivo→soporte izquierdo»: no existe aquí el corte emparejado de esa segunda ventana y hay recursos y rutas previos. Las trazas de waypoints se incluyen para investigarlo sin inventar identidad por carga coincidente.

La carga del portador emitido en B es0 en ambos signos. En el primer relay se combina con un recurso genérico5 preparado; los buses y trayectos siguientes transportan5, no52/36 ni una referencia numérica nueva. El primero recorre[12,19,9]T68455,[9,19,9]T68458 y[6,16,12]T68461; el segundo[0,19,9]T70019,[3,19,9]T70022 y[6,16,12]T70025. Sus direcciones son distintas hasta ese último testigo. El7 del contexto izquierdo ya existía y permanece; no se atribuye a una nueva carga7 llegada deB. A está activo y conserva exactamente el mismoRAW x+1 desde dos ticks antes hasta cinco después del cambio de contexto en ambas ventanas. No se observó una decisión momentánea diferente en1–3ticks que el lector tardío hubiera omitido.

## Asistencia y alcance

Las oportunidades públicas, fase de los datos y cortes son programación del investigador. La creación de las solicitudes, renovación del lector, emisión y transformación material proceden de v27. El contenido52/36 es una observación privada actual, no la solución futura. Los cortes son diagnósticos en ramas, no actos autónomos de E1. El lector motor sigue siendo el CF01 de dos muestras con máximo un tick de retención; no se amplió ni se seleccionó según el acierto.

En todas las oportunidades de estos ocho ensayos se omitió el retorno nativo antiguo (`mode=omit_return`). Este subestudio no ejecutó el nuevo bucle de consecuencia externa y no lo acredita. Las etiquetas `availability/useful/wrong` internas de cf.episode son metadatos del auditor en esta modalidad y no se usan como prueba de utilidad externa. Se informan comandos físicos y cambios de receptores.

## Evidencia y reproducción

Primarios completos de la familia: `evidencia/campanas/ENTE_DEE_OPERATIVO_01/social/EO01_SOC_AUX_*.json.gz`. Cada uno incluye configuración, código ejecutado por hash, recibos, testigosRAW/clocks exactos, ambos estados y localizador/hash del snapshot completo.

El recálculo puro `recalcular_social.py` no importa el motor ni ejecuta ticks. Verifica35.340 observaciones decodificandoRAW, vuelve a calcular el lector fijo y comprueba el contraste localizado. Comando desde la raíz de Cognitive:

```
python laboratorio/campanas/ENTE_DEE_OPERATIVO_01/social/recalcular_social.py evidencia/campanas/ENTE_DEE_OPERATIVO_01/social --output evidencia/campanas/ENTE_DEE_OPERATIVO_01/social/RECALCULO_SOCIAL.json
```

`RECALCULO_SOCIAL.json` enumera SHA-256, tamaños, denominadores y snapshots de los ocho casos. Para repetir física se requiere CPython3.13x64, el motor oficial, el sistema y el padre completo indicado; no basta este informe ni las extracciones. Los guiones de ejecución y planesR1–R3 permanecen en `laboratorio/campanas/ENTE_DEE_OPERATIVO_01/social/`; cada revisión efectivamente ejecutada quedó archivada por contenido en la evidencia. No se propone promover estas ramas: no mejoraron la función social operativa del padre.
