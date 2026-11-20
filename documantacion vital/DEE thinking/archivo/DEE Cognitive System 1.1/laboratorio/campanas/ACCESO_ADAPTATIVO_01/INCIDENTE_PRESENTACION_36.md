# Resumen de consola posterior a la trayectoria

`main_confirmatorio_36.py` terminó sus 35 comandos del gestor con código 0, guardó el snapshot completo final y escribió `PRIMARIOS.json.gz`. Después falló el `print` de resumen: trataba la preparación del episodio como si fuese una etapa de avance y esperaba un campo `stage` que esa preparación no tiene.

El código de salida 1 del supervisor se conserva. No es un resultado cognitivo ni borra los fallos reales de recuperación tardía, cuyas emisiones vacías permanecen en los primarios. Se corrigió únicamente el filtro del resumen, preservando los bytes ejecutados en `versiones_codigo/main_confirmatorio_36_ejecutado.py` y el objeto SHA del supervisor. No se repite MAIN para reparar la presentación. El recálculo lee los datos ya guardados.
