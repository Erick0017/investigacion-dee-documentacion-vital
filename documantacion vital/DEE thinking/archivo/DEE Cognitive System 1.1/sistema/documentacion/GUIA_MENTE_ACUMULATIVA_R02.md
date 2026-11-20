# Uso operativo acotado de MA02

Requiere el entorno compatible existente CPython3.13 x64 y el motor oficial congelado. No instala otro motor ni recrea una vida desde una receta. La selección de desarrollo es `MA02_MAIN_5` T11196, no una promoción del activo global `MA_MAIN_R9`.

Desde `sistema/`, con el intérprete del entorno existente:

```text
python gestionar.py mente2-estado --vida MA02_MAIN_5
python gestionar.py bifurcar MA02_MAIN_5 MI_MA02 --modalidad CANDIDATE
python gestionar.py mente2-sesion --vida MI_MA02 --situaciones '[{"contexto":"epsilon","modo":"usar"},{"contexto":"gamma","modo":"usar"}]'
python gestionar.py guardar --vida MI_MA02
python gestionar.py mente2-estado --vida MI_MA02
```

`--situaciones` recibe JSON literal. El ejemplo de comillas simples se comprobó en PowerShell7.6.5; Windows PowerShell5.1 puede cambiar las comillas al invocar programas nativos. En ese caso use `INICIAR.bat mente2` y el ejemplo de la distribución, sin copiar una línea JSON que su shell altere. No introduzca un target en consultas de uso. El contexto identifica una señal física preparada, no la respuesta. Epsilon−, alfa−, beta+, gamma+ y delta− son las adquisiciones comprobadas del corte final; esa lista documental no alimenta al decodificador.

El modo `trabajo` utiliza los campos `"dominio":"transaccion","valores":[9,9]` en el mismo objeto JSON, no un subobjeto trabajo, para un trabajador real; su fase y sus valores son entorno externo. `ensenar` y `revisar` requieren `"senal":1` o `"senal":-1` docente explícita y son enseñanza, no retención. Consulte `contratos/MENTE_ACUMULATIVA_R02.json` y la ayuda del gestor para límites. `componer` exige `aceptar_consumo:true`: consume acceso individual y no debe usarse como una consulta inocua. No use `mente2-extender` en una vida que ya admite epsilon.

En `cognitive sistem`, el acceso preparado es `INICIAR.bat mente2`; crea/importa sólo una copia personal declarada la primera vez y conserva esa vida en usos posteriores. La distribución final incluye los estados completos seleccionados. El ZIP científico reducido no basta para continuarlos.

La composición requiere contenidos concordantes en esa vida. MAIN_5 tiene alfa−/beta+ y no emite un resultado conjunto válido. Bifurque explícitamente `MA02_MEMORIA_SEPARADA` (−/−) o `MA02_COMPOSICION_PLUS_LISTA` (+/+) para ese uso; son pasados o ramas alternativas, no conocimientos simultáneamente presentes en MAIN_5. La copia de uso conserva el coste: no restaure el estado listo después para aparentar composición no destructiva.

## Selector de historia P1: otro perfil, primer uso finito

```text
python gestionar.py bifurcar MA02_SELECTOR_P1_H1 P1_MI_PRUEBA --modalidad DIAGNOSTIC_COPY
python gestionar.py mente2-p1-estado --vida P1_MI_PRUEBA
python gestionar.py mente2-p1-usar --vida P1_MI_PRUEBA --detalle
python gestionar.py guardar --vida P1_MI_PRUEBA
```

No consuma directamente los originales H1/H0 T129. Su consulta y recursos futuros están en el snapshot completo. El primer uso acabaT212; el segundo se rechaza, no restaura ni crea otro mundo. Un fork nuevo desde T129 es otra trayectoria, no continuación de la copia ya usada. No atribuya sus contenidos a MAIN_5 ni a E1.

## Errores y límites

Una entrada rechazada permanece rechazada. El sistema no sobrescribe la celda ni elige otra ruta porque conozca el resultado esperado. Lectura vacía, ambigua, fuera de dominio y error de proceso se distinguen. Las consultas transforman la materia. Para continuar hacen falta snapshot completo, ficha, interfaces, colas y estado del protocolo; arrays RAW/clocks y el informe no los sustituyen.
