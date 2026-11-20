# CORE09 — informe final

## Preguntas y adjudicación

1. **¿Existe una Rosetta externa validada?** No bajo R09_01. El fingerprint D09F01 fue congelado antes de mirar valores, el dataset USGS se dividió por evento y se abrió una sola vez. Muestra final: 6505 picks / 468 eventos. P medAPE=0.1027, S=0.5015; ambos exceden 0.05 y el competidor phase-specific es mucho mejor. El FAIL descarta el mapa `t=alpha·d` de una sola velocidad para P+S, no toda Rosetta.

2. **¿Estaba A6 oculta en CORE05–08?** No. El reanálisis encontró plasticidad, un loop A3 y homeostasis fija, pero no evidencia retrospectiva capaz de promover A6. C9H02 creó y confirmó el mecanismo que faltaba: consecuencia contingente→colisión con la traza que retorna→cambio persistente de direction→política futura diferente.

3. **¿Aprende a evitar daño?** Sí, en el dominio binario probado. Hay dos errores inevitables de información —primera adquisición y primera reversal— y conducta correcta posteriormente, incluida generalización. La ablación de memoria elimina la ventaja. El ambiente aplica una regla fija a puertos de acción y nunca lee el estado oculto para seleccionar la conducta.

4. **¿Se adapta la reparación?** No. El fast loop XNOR permanece fijo y ya ocupa la latencia mínima de un tick. Lo aprendido es evitación, no reparación más rápida o barata.

5. **¿Existe memoria simbólica resiliente grande?** Sí, causal y acotada. La curva limpia fue 40:1.000, 100:1.000, 250:1.000, 500:1.000, 1000:0.998; la muestra final limpia fue 1.000. El estado aprendido ocupa 15649 bits activos / 64000 bytes en la matriz observadora. Bajo borrado aleatorio la accuracy fue 0.990, 0.970, 0.930, 0.870 y 0.700 para 5–30%.

6. **¿Corrige typos DEE?** No de forma incremental respecto al encoder. En corrupción mixta, DEE=0.955, feature-kNN=0.955, Levenshtein=1.000. La robustez proviene de la representación de caracteres. El daño de rutas derrumba la lectura incluso sin borrar bits: relación/routing y contenido son causalmente distintos.

7. **¿Regenera memoria aprendida?** No en los scaffolds probados. El scaffold universal llenó direcciones no entrenadas y perdió selectividad; el selectivo codificó desde t0 qué direcciones debían restaurarse. El FAIL permanece.

8. **¿Existe un subsistema superior?** Existe un cociente de tarea exacto pero conocido, no superior. `G_sub(query,z)=argmax_l Σ_{f∈encoder(query)} z[l,f]` coincidió exactamente con las reducciones de F_DEE en 100/100 pruebas. Supera exact lookup bajo typos, pero empata con el mismo kNN del encoder y pierde contra Levenshtein. En el probe de clases semánticas obtuvo 0.150; no demuestra comprensión.

## Arquitectura transversal actualizada

El menor conjunto explicativo de CORE09 es: (i) propuesta dirigida; (ii) fibra de destino y reductor guardado; (iii) lineage que retorna y conserva historia; (iv) observer relativo a tarea; (v) rama XNOR fija para homeostasis. Los tres primeros explican plasticidad contingente, memoria one-shot y scoring efectivo. XNOR se compone con ellos, pero no aprende. No se ha obtenido Q4 global.

## Frontera

Las preguntas internas centrales quedaron adjudicadas con los aparatos actuales. Una Rosetta externa nueva requiere otro fingerprint congelado y un protocolo verdaderamente independiente; no se justifica ajustar R09_01. Reparación adaptativa de memoria requiere un scaffold que descubra qué restaurar sin contenerlo de antemano. Una entidad integrada más fuerte requiere cerrar recursos y fronteras internas sin decisiones post-t0 del host.
