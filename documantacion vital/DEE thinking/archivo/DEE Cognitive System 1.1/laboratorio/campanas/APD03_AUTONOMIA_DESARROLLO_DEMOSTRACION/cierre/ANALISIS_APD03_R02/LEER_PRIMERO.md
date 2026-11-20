# APD03 — análisis científico esencial

Este paquete conserva ocho expedientes compactos cerrados, la comprobación Full y sus fuentes, positivos, negativos y límites. Es análisis esencial: no contiene motor ni todos los snapshots completos necesarios para continuar vidas; no sustituye al paquete operativo ni al archivo histórico íntegro.

El Full exacto fue comprobado en una extracción local separada. Su evidencia está en `VALIDACION_FULL/VERIFICACION_FULL_APD03_R02.json` y el recálculo en `VALIDACION_FULL/RECALCULO_FULL.json`. El R01 negativo previo a Native se conserva con su nombre y causa, no se borra ni se presenta como prueba funcional fallida. No se trató de otro investigador ni otra computadora.

El Word 1.17 tiene comprobación editorial estructural, no validación visual: el render disponible falló por ausencia de LibreOffice. Su alcance se conserva explícito en `MANUAL/EDICION_MANUAL_APD03.json`.

`CANDIDATO_NO_SELLADO.json` documenta el precursor de ensamblado y sus revisiones. Después del sellado manda `MANIFIESTO_FINAL_ANALISIS.json` para los miembros del paquete; el hash y la verificación del ZIP exacto se comunican fuera del contenedor. El informe original de corte y sus cuatro derivados editoriales posteriores están diferenciados en `INDICE_FUENTES_Y_OMISIONES.json` y `REVISION_EDITORIAL_FULL_R02/`.

Recálculo archivado sin motor desde cualquier ubicación: `python -I -B RECALCULO/recalcular_todo_apd03.py --out RUTA_EXTERNA_NUEVA`. Ejecuta CLIs reales y exige resultados idénticos byte a byte a referencias conservadas. No ejecuta Native, otra adquisición ni el Full.

CODIGO_DELTA es material de estudio de la capa1.1, no instalador ni kernel; no transfiere memorias. CONTINUIDAD contiene localizadores locales, no mundos completos.
