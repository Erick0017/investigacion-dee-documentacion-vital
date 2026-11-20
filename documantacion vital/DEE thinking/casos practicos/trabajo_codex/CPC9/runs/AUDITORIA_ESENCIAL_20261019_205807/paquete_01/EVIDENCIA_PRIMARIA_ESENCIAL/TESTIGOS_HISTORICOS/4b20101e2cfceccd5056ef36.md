# Ingeniería 05 — NRD05: transformación del paisaje condicionada por historia

## Hallazgo

La misma segunda experiencia física E2=BA transforma el paisaje de manera causalmente distinta según haya ocurrido previamente E1=AB.

Clasificación promovida provisionalmente:

`DEE_NATIVE_HISTORY_CONDITIONED_TRANSFORMATION`

No se promueven RW3 ni L4.

## Diseño causal

Desde el mismo estado inicial se ejecutaron cuatro mundos:

- W00: no E1, no E2;
- W10: E1, no E2;
- W01: no E1, E2;
- W11: E1, E2.

Antes de E2 se verificó byte a byte:

- W00 = W01;
- W10 = W11;

Por tanto, E2 fue idéntica dentro de cada contrafactual y la comparación no mezcla contaminación previa entre sus pares.

El efecto sin historia se definió como W01 frente a W00. El efecto con historia se definió como W11 frente a W10. Las firmas exactas incluyeron estado público, máscaras, fields, futuros C0/C3 y respuesta C3−C0 en h=32 y h=64.

## Resultado principal y retención

En MAIN_S0 las firmas de E2 con y sin E1 fueron distintas inmediatamente después de E2 y continuaron siendo distintas tras 64 ticks sin nuevos eventos.

La diferencia no se limita a conteos. Los XOR, máscaras y hashes exactos de las transformaciones difieren. Después de la retención, la comparación de efectos produjo 2,988 diferencias RAW inmediatas; los futuros C0 continuaron separados en 12,097 posiciones RAW en h=32 y h=64.

## Exclusión de ruta directa

La segunda geometría congelada aplicó a E2 la transformación espacial V1 previamente validada. Su conjunto de entrada fue disjunto del conjunto de entrada de E1.

La historia siguió condicionando E2 en D0 y D64. En la condición separada, después de retención quedaron 104 diferencias RAW entre las dos firmas inmediatas de E2; los fingerprints diagnósticos permanecieron distintos en ambos horizontes.

Por tanto, el resultado no depende exclusivamente de reutilizar la misma coordenada o trayecto físico de entrada. Esto no demuestra una influencia global universal, pero sí supera la explicación de interacción local por ruta compartida.

## Fresh validation

El factorial completo se repitió sin retuning en V1 (N=19) y V2 (N=25). Ambas configuraciones reprodujeron:

- condicionamiento en D0;
- persistencia en D64;
- diferencias futuras bajo C0, C3 y/o C3−C0 en h=32 y h=64.

## Respuestas directas

1. **¿E2 transforma distinto con E1?** Sí.
2. **¿Persiste?** Sí, después de 64 ticks sin nuevos eventos.
3. **¿Replica fresh?** Sí, en V1 y V2.
4. **¿Sobrevive sin ruta directa compartida?** Sí, con rutas E1/E2 disjuntas bajo la transformación V1.
5. **¿Local o paisaje?** No queda explicado por una ruta local compartida. La evidencia favorece una transformación condicionada por el estado distribuido del paisaje, acotada a estos aparatos.
6. **Cambio conceptual:** la historia no sólo deja un presente distinto; modifica la transformación causada por una experiencia posterior idéntica.
7. **¿Basta `DEE_NATIVE_SEQUENTIAL_REACHABILITY_CHANGE`?** Sigue siendo cierto, pero es incompleto.
8. **Promoción:** sí, a `DEE_NATIVE_HISTORY_CONDITIONED_TRANSFORMATION` provisional.
9. **Siguiente prueba:** F3 queda científicamente autorizada como siguiente pregunta, pero no fue ejecutada aquí. Debe conservar el mismo factorial histórico y controles.
10. **¿L4/equivalente?** No. Faltan tercera transformación, competencia renovable, recursos, función autónoma y cierre ambiental.

## Límites

Las experiencias físicas fueron iniciadas por el host en límites congelados; el host no copió la configuración RAW causal. El resultado establece condicionamiento histórico de la transformación, no autonomía ambiental cerrada. Ingeniería 05 permanece abierta.

