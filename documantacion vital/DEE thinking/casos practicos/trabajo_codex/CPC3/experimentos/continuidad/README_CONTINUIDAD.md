# Continuidad nativa MAIN

Se prepararon mundos H0 nuevos con la receta pública `relational.v1`, N47,
tick absoluto32 y clocks locales260. No se restauró un preset AB/BA aprendido:
dos resultados pasados del hábitat externo independiente se codificaron como
acontecimientos físicos de carga cero en32/33. La primera consulta física,
también de carga cero, entró en34. Las siguientes predicciones leyeron el
comparador nativo actual, sin forks operativos ni consultas desde una caché.

`EXPERIMENT_CONFIG.json` se congeló antes de los ocho casos. El conjunto incluye
dos controles de entrada, una intervención diagnóstica de memoria, otra historia
y tres realizaciones reservadas (dos BA y una AB). Cada caso es un mundo, no
cientos de réplicas por contar sus ticks. Se conservaron los recibos rechazados.

## Qué muestran los datos

- En BA, la escritura inicial deja delta−1 y la lectura37 tiene dx−1.
- Sin nuevas entradas, A escribe en164 y delta pasa a0. En FULL, el evento A
  en163 eleva el conteo local: reloj391 satisface el periodo391 con seis vecinos,
  pero no el periodo782 con siete. La escritura de A se retrasa hasta555.
- Después de555 ambos brazos tienen delta0; FULL expresa dx+1 en813/946,
  mientras el control sin entradas termina con dx0. La historia posterior
  influye en el contexto de expresión además de modular la escritura relativa.
- Las dos reservas BA reproducen ese contraste temporal, manteniendo centros
  y soporte. No se atribuye la salida positiva final únicamente a delta.
- FULL admite las observaciones163/292/554, pero rechaza812/945 por ocupación.
  La historia AB tampoco admite las nuevas observaciones del otro tipo.
- Por tanto existe continuidad de escritura/lectura/evolución/experiencia y
  cambio de expresión en MAIN dentro de este dominio; no un lector ilimitado
  que garantice incorporar cualquier secuencia ni una asociación arbitraria.

El decoder fijo usa sólo la dirección actual. Los pronósticos37→67 son
prospectivos. Tras el cambio ambiental80, se conservan los pronósticos erróneos
anteriores; no se reemplazan por los corregidos. La ausencia/llegada pasada
procede de una ley externa declarada, no de un timeout nativo. La evaluación
del error es externa y jamás se suministra de vuelta al cuerpo.

## Alternativas finitas conservadas

`DISCOVERY_READER.json`: siete de nueve geometrías completadas antes del timeout
de180s del proceso; no se presentan las dos restantes como terminadas. Varios lectores
fuera del centro mueren; el central puede cerrar los puertos posteriores.

`DISCOVERY_OFFAXIS.json` y `OFFAXIS_SELECTIVE.json`: un soporte adicional fuera
del vecindario A/B mantiene una lectura con componente y no nula, útil para el
acoplamiento físico, pero sus corrientes terminan ocupando las entradas.

`absorber/` y `ABSORBER_SELECTIVE.json`: absorbedores semantic4 preparados antes
deT0 modifican la recirculación y en un caso admiten cinco eventos posteriores.
No proporcionaron una reescritura relacional selectiva seguida de lectura nueva
mejor que el candidato central; se preservó esa limitación, no se amplió la búsqueda.

## Reproducción

Con CPython3.13 x64 y el wheel oficial instalado, desde cualquier carpeta:

```
python -I -B CPC3/experimentos/continuidad/run_entity.py --root CPC3 --case BA_FULL
python -I -B CPC3/experimentos/continuidad/technical_checks.py CPC3
python -I -B CPC3/experimentos/continuidad/analyze.py CPC3
```

Utilice una extracción nueva si quiere conservar byte-exactos los resultados
medidos: el runner escribe dentro de `--root`. Las llamadas nativas deben
ejecutarse en un proceso supervisado, como los registros `supervision` incluidos.

`entity_before_metadata_audit.py` conserva el helper usado en la confirmación.
`entity.py` añade únicamente auditoría de escritura de metadata/persistencia y
estado de alcance del observador; no altera el cuerpo ni la evolución. Los
hashes de archivo snapshot pueden cambiar por metadata; la igualdad física se
comprueba por RAW, clocks y tick. Ningún cambio del auditor debe atribuirse a DEE.
