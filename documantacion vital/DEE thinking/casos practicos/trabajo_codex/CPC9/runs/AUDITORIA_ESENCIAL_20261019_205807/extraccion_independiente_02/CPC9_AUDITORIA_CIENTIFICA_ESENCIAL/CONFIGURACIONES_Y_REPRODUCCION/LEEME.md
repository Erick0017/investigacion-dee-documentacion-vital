# Revisión sin ejecutar el motor

Las herramientas de esta carpeta usan la biblioteca estándar de Python.
No importan DEE, no ejecutan los programas experimentales conservados y no
reanudan el presupuesto ni la vida de CPC9. Use siempre una salida nueva.

Desde la raíz del ZIP extraído:

```text
python CONFIGURACIONES_Y_REPRODUCCION/recalcular_esencial.py --root . --out ../RECALCULO_NUEVO
python CONFIGURACIONES_Y_REPRODUCCION/codec.py --verify-all
python CONFIGURACIONES_Y_REPRODUCCION/codec.py --id D00030 --out ../K65_ORIGINAL_VALORES.json
python CONFIGURACIONES_Y_REPRODUCCION/campos_guardados.py --verify-only --out EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS
python CONFIGURACIONES_Y_REPRODUCCION/verificar_paquete.py --root . --out ../VERIFICACION_NUEVA
```

`codec.py` reconstruye todos los valores JSON y comprueba su SHA canónico.
Las operaciones `=` reemplazan un valor y `-` retiran una clave respecto de
una base incluida. Las bases son documentos identificados; no se evalúa código.
Conserva listas/enteros/campos, no el formato textual original. El SHA de origen
permite localizar los bytes originales cuando éstos sean necesarios.

Los campos completos se codifican como `base64(zlib(uint64 little-endian))`.
Cuando conviene, se conserva una base incluida y un residual XOR o una diferencia
uint64 modular con desplazamiento declarado. `array_bytes(documento, 'RAW', carpeta)`
y `array_bytes(documento, 'CLOCKS', carpeta)` los decodifican con límites y hashes.
Es compresión de archivo, no regulación ni modificación de los clocks de E1.
Una base de otra historia sólo es una referencia de almacenamiento: al decodificar
se recuperan los bytes de cada individuo, no se trasplantan memorias en un Runtime.
Esto no implementa la transición v27.
Se excluye metadata operativa: no es una función de restauración del individuo.

`contrastar_historicos.py` vuelve a comparar huellas registradas vinculando
el ID del caso a un componente exacto de la ruta del archivo, sin unir datos
de otros individuos. Las actas antiguas y la nueva comparación son capas
distintas. Si un formato no ofrece esas huellas, no lo certifica automáticamente.

`FUENTES_EXPERIMENTALES/` contiene constructores, generadores y lectores
seleccionados para inspección. No es una instalación del motor ni una promesa
de que esos runners puedan ejecutarse autónomamente desde esta entrega reducida.
Sus dependencias operativas completas están en los ZIP originales.

## Obtener de nuevo las extracciones

Los scripts `extraer.py`, `anexar_testigos.py`, `documentacion_historica.py` y
`campos_guardados.py` documentan la selección, la procedencia por hash y el
procedimiento exacto de lectura de ZIP/almacén/arrays. `PLAN_EXTRACCION.json`
identifica los insumos y las exclusiones finales. No descargan nada.
`juntar_datos.py` coloca los registros codificados en un JSONL indexado por
posición/longitud; `optimizar_campos.py` aplica sólo la recodificación sin pérdida
de arrays. Ambos verifican hashes y conservan todos los valores originales.

Para comprobar nuevamente contra los originales, utilice el verificador con
los dos ZIP canónicos y, si se quieren comprobar sus bytes de origen, los
archivos externos y el directorio de la recuperación limpia ya realizada.
Los valores de estos últimos están incluidos aquí: no se necesita ese
directorio privado para el recálculo ni para leer los datos de la auditoría.

El CSV de origen indexa los datos JSON y las extracciones físicas. Los testigos
textuales y las variantes de código tienen además sus propios índices por hash
en `TESTIGOS_HISTORICOS/` y `FUENTES_POR_HASH.json`. Una referencia a código no
implica que todos esos módulos se importaran en cada participante.

## Qué queda exclusivamente en los originales

- WHL/PYD, C++/headers del producto y kernel; toolchains/entornos.
- Snapshots operativos completos, colas/canales y estados intermedios no
  seleccionados. Las extracciones de 13 campos físicos no los reemplazan.
- Corpus documental íntegro y todas las versiones de código no seleccionadas.
- El formato textual original de los JSON reducidos; sus valores y SHA de
  bytes de origen permanecen incluidos/referenciados.

Para una nueva evolución nativa se requieren el Core/producto/estados originales
y una ejecución autorizada; no debe confundirse con repetir las métricas aquí.
