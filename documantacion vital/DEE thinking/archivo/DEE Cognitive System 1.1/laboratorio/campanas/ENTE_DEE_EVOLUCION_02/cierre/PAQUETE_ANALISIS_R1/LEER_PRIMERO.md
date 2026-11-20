# ENTE02 — análisis científico

Comience por INFORME_CIENTIFICO.md, CAPACIDAD_POR_NIVEL.csv y CAPACIDADES_POR_VIDA.csv. Las correcciones de alcance de serialización están en CODIGO_Y_PROTOCOLOS/capacidad/ACLARACION_ALCANCE_SERIAL32.md: R10 ensayó 16 como dos ventanas de ocho, no 32; R9 sí conservó intentos adversos de 32.

EVIDENCIA_CAUSAL contiene los primarios exactos positivos y negativos, código ejecutado y los archivos reales producidos por los servicios locales. No son réplicas independientes las consultas o las bifurcaciones de un mismo prefijo.

Para recalcular sin motor ni simulaciones: `python RECALCULO/verificar_analisis_final.py`. Opcionalmente, añada `--prohibir-raiz RUTA` para bloquear expresamente cualquier instalación original; la verificación de entrega bloquea ambas raíces reales. Python 3.10 o posterior, biblioteca estándar. La prueba reconstruye lecturas desde RAW, comprueba recibos y bytes de workers, y compara los tres cálculos con sus referencias archivadas. No importa DEE, no ejecuta trabajadores y no añade ticks.

El manual 1.11 R1 tiene comprobación estructural; no se obtuvo validación visual por falta del renderizador autorizado. DELTA_OPERATIVO no es una instalación autónoma. Los estados completos permanecen localmente y en la distribución operativa seleccionada, no en este ZIP reducido. Sus localizadores y SHA-256 figuran en INDICE_FUENTES_Y_OMISIONES.json.
