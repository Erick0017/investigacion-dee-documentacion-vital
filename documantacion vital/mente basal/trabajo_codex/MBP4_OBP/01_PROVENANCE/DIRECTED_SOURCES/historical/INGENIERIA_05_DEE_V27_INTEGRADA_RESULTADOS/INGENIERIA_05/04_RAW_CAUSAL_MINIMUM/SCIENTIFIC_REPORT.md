# Ingeniería 05 — NRD04: soporte RAW causal mínimo y reescritura condicional

## Hallazgo principal

El cambio de reachability en t=4 no reside en una posición RAW aislada. Depende de configuraciones distribuidas y no aditivas.

- H1: el conjunto mínimo suficiente es R1 completo, 8 de 8 posiciones.
- H2: en discovery existe un conjunto mínimo suficiente de 5 posiciones, índices `[1,2,4,5,6]` dentro de R2.
- Ningún sitio individual ni ninguna mitad congelada reproduce el fingerprint completo.
- La superposición XOR de contribuciones individuales no reproduce el efecto de los conjuntos mínimos.
- Permutar cíclicamente el mismo multiset de valores entre las mismas posiciones cambia el fingerprint en H1 y H2: la asignación valor↔posición y su configuración importan.

Clasificación DEE-first:

`SYNERGISTIC_DISTRIBUTED_RAW_CONFIGURATION`

## Necesidad y suficiencia

### H1

R1 completo es mínimo suficiente: ningún subconjunto propio reproduce exactamente FULL_RAW en h=32 y h=64. El conjunto de eliminación mínimo que devuelve el fingerprint exactamente a BASE tiene cuatro posiciones `[0,1,5,6]`.

La regla R1 completo pasó fresh necessity/sufficiency en V1, V2 y V3.

### H2

El conjunto `[1,2,4,5,6]` es mínimo suficiente en discovery. El conjunto mínimo de eliminación que devuelve el fingerprint a BASE es `[1,5,6]`.

La regla de cinco posiciones pasó en V3, pero no reprodujo FULL_RAW en V1/V2. En los tres casos, eliminarla transformó FULL y dejó el residuo exactamente en BASE. Por tanto es necesaria bajo la regla, pero su suficiencia exacta depende del marco/contexto. No existe aún una regla mínima H2 generalizada.

## H1 frente a H2

Ambos mecanismos son distribuidos, configuracionales y no aditivos, pero no usan el mismo soporte mínimo:

- H1 requiere todo R1 y generaliza fresh.
- H2 admite compresión causal local en discovery/V3, pero esa compresión no generaliza a V1/V2.

La evidencia no demuestra que AB/BA esté almacenado literalmente. Demuestra que presentes RAW distintos crean clases distintas de respuesta futura.

## Reescritura nativa condicional

Sólo H1 abrió el gate secuencial porque su soporte R8 tenía necesidad/suficiencia clara y pasó las tres configuraciones fresh.

En un mundo continuo se compararon CONTROL, AB_ONLY y AB_THEN_BA:

1. F0: los tres mundos eran idénticos.
2. Una experiencia física AB exacta produjo F1 distinto del control.
3. Sin reset ni copia host de R8, se inició una segunda experiencia física BA mediante portadores en trayectorias entrantes vacías.
4. Después de dinámica kernel nativa, F2 de AB_THEN_BA fue distinto de AB_ONLY.

El resultado se reprodujo en N=23 y en una configuración transformada N=25, para h=32 y h=64 con el mismo panel C0/C3.

Clasificación provisional:

`DEE_NATIVE_SEQUENTIAL_REACHABILITY_CHANGE`

Esto no es todavía RW3 ni L4: sólo hay dos transiciones, las experiencias fueron iniciadas por el host como condiciones físicas y todavía faltan internalización/retención más fuerte, tercera transición, renovación de competencia y cierre ambiental.

## Respuestas directas

1. **Parte mínima RAW:** H1 necesita R1 completo (8); H2 necesita 5/7 en discovery, pero esa reducción no generaliza fresh.
2. **Necesaria:** sí configuracionalmente. Retirar subconjuntos críticos altera el fingerprint; los conjuntos destructivos mínimos son 4 posiciones para H1 y 3 para H2.
3. **Suficiente:** R1 completo sí, fresh-confirmed. H2 S5 sólo en discovery y V3; no es una regla suficiente general.
4. **Mecanismo:** distribuido y sinérgico/no aditivo, no individual ni meramente redundante.
5. **Valores/posiciones:** importa la asignación valor↔posición; el multiset de valores no basta.
6. **H1/H2:** comparten el carácter configuracional, pero sus soportes y robustez son distintos.
7. **Fresh:** H1 pasó 3/3; H2 S5 pasó 1/3.
8. **Segunda experiencia:** sí, volvió a modificar nativamente el fingerprint en dos configuraciones sin copiar manualmente el soporte.
9. **Cambio interpretativo:** el portador causal probado es una configuración RAW distribuida del presente, y al menos una segunda interacción física puede reorganizar el espacio de futuros sin construir el estado causal desde Python.
10. **Siguiente frontera:** caracterizar la segunda transición —retención, causal support y exclusión de ruta directa— antes de intentar tercera experiencia o adaptación recurrente.

Ingeniería 05 permanece abierta. No se abrió Ingeniería 06.

