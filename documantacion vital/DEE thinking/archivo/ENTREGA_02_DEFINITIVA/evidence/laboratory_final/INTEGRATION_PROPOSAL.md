# Propuesta para revisión posterior

Esta propuesta no modifica la Entrega 02 estable.

## Candidato F1

Nombre provisional: `reusable_lineage_revision.c7h03.lab.v1`.

Contrato candidato: linaje C7H03 móvil, dos puertos de revisión física y tres
consultas transformativas en el dominio N=127/t≤60. Debe declarar que los
teachers son externos, que s_reg se acumula con cap y que el orden sólo fue
distinguible antes de completar ambas revisiones.

Antes de una eventual integración se debe decidir si el producto necesita un
constructor genérico o sólo un ejemplo experimental. La regresión mínima sería
el panel 11→13, 13→11, sham y no-teacher, con igualdad RAW+clock Lazy/Dense.

## Candidato F2

Nombre provisional: `environmental_demux_return.lab.v1`.

Contrato candidato: una respuesta C7H03 alcanza un receptor soportado, activa
un overflow condicionado por fase, DEMUX actualiza un portador independiente y
la diferencia se usa en dos encuentros posteriores. Dominio reejecutado:
N=127, t≤56, cargas y geometría de `CAMPAIGN_CONFIG.json`.

No debe exportarse como teacher endógeno genérico. El +1 está fijado por DEMUX
y el soporte ambiental está preparado. Una eventual integración requeriría
API experimental explícita, documentación de los seis soportes, control
subumbral y regresión de corte/no-query/sham.

## Fan-out

No integrar. El aparato saturante colapsó 4149 y 4151 a la misma salida y no
conservó una segunda expresión del contenido. Otras arquitecturas permanecen
abiertas, pero este montaje no las respalda.

## Decisiones necesarias

1. Revisar si F1 se publica como composición acotada o permanece sólo como
   laboratorio de actualización externa.
2. Revisar si F2 merece un contrato experimental versionado sin promesa de
   autoenseñanza.
3. Definir una campaña separada, si se autoriza, para procedencia de contenido
   y replicación en un receptor genérico.
4. Sólo después de esas decisiones autorizar cambios en Entrega 02 y ejecutar
   su suite completa. Esta campaña no autoriza Entrega 03.

