# Recálculos portables del mecanismo



Ejecutar desde la raíz de esta carpeta MECANISMO. Sólo Python stdlib; cero imports del motor y cero ticks. Cada salida se compara byte por byte mediante SHA con la referencia incluida.



python -I -B "RECALCULO/recalcular_seleccion_mufi01.py" --evidencia "EVIDENCIA/seleccion" --salida "RECALCULADO/SELECCION.json"

python -I -B "RECALCULO/recalcular_main_u.py" --evidencia "EVIDENCIA/contraste_main_u/MAIN_U_COMPLETO_FINAL.json.gz" --salida "RECALCULADO/MAIN_U_A.json"

python -I -B "RECALCULO/recalcular_transferencia.py" --evidencia "EVIDENCIA/transferencia_b" --salida "RECALCULADO/TRANSFERENCIA_B.json"

python -I -B "RECALCULO/recalcular_controles_cadena.py" --evidencia "EVIDENCIA/composicion_b" --salida "RECALCULADO/COMPOSICION_B.json"

python -I -B "RECALCULO/recalcular_preparadas.py" --evidencia "EVIDENCIA/comparacion_cadena_b/MAIN_U_T31765_COMPLETO.json.gz" --salida "RECALCULADO/PREPARADAS_B.json"

python -I -B "RECALCULO/recalcular_acceso_nativo.py" --evidencia "EVIDENCIA/acceso_nativo_b" --salida "RECALCULADO/ACCESO_NATIVO_B.json"
