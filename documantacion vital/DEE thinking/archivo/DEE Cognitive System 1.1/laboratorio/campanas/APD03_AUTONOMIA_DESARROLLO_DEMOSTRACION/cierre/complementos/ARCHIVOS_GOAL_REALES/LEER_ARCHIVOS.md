# Ocho archivos de objetivo reales — desnormalización N0

Los ocho JSON de `FILES/` son copias byte por byte del par completo final APD03_MAIN T604825. Suman1.195bytes. No fueron recreados desde objetivos, veredictos, valores esperados o `json.dumps`.

Estos bytes **ya estaban preservados** como base64 en los primarios cerrados de MAIN. Se separan aquí para lectura cómoda, no como descubrimiento ni evidencia previamente ausente. No se duplican sus trazas completas.

`INDICE_Y_EXTRACCIONES_PRIMARIAS.json` vincula cada archivo con su miembro y hash del par final, el archivo primario original y su SHA256, localizador, payload base64 original y el testigo RAW numérico. Los testigos son extracciones JSON decodificadas: su serialización no se presenta como los bytes originales de la trayectoria. Las trayectorias completas están en el cierre MAIN indicado por los localizadores.

El extractor contrastó cada copia con el miembro físico del par, su manifiesto y el base64 del primario; no tocó Native, S, colas ni estados. El recálculo portátil vuelve a comprobar los ocho bytes/payloads/hashes, decodifica el testigo RAW C, contrasta el resultado nativo y verifica la aritmética del archivo como auditor posterior.

Desde esta carpeta, con Python estándar:

```powershell
python -I -B .\desnormalizar_goal_archivos_apd03_n0.py recalcular --evidence . --out .\RECALCULO_NUEVO.json
```

Se exige nombre de salida nuevo para no sobrescribir evidencia. El recálculo usa sólo esta carpeta y no requiere motor, snapshots ni rutas originales. La extracción inicial sí requiere el par final y primarios existentes. Este complemento no permite continuar la vida por sí solo.
