# CORE06/CORE07 recuperados mediante 4.5 oficial

Se ejecutaron completos ambos paneles históricos desde miembros materializados
del Core, sin abrir sus ZIP originales. El trabajador V2 queda congelado con
SHA-256 `7d1ea228fff920c61de1e1e1dd164ef152eb285e95d558134622f8201185086b`.

CORE06: 134/134 casos coinciden exactamente en todos los registros locales,
puertos, resultados y resúmenes disponibles. Hay 25/25 transferencias positivas
a direcciones no enseñadas y 100/100 controles neutrales. Los otros 9 casos
preservan extinción del canal anterior, reversión y readquisición, junto con sus
controles. Son 2208 transiciones; 94.06 segundos efectivos y 47.6 MB de pico del
trabajo supervisado. No hubo lecturas externas denegadas. Evidencia:
`resultados/CORE06_FULL134/{OBSERVED,PRIMARY_TRANSITIONS,RECOVERY}.json`.

CORE07: 144/144 casos coinciden exactamente, en 4 tamaños/geometrías y 12
consultas. 48/48 positivos conservan la función reprogramada y los registros
intermedios; 96/96 negativos no la reproducen. Los 144 puertos de consulta estaban
vacíos. Las reparaciones genéricas demoradas de ruta, carga y soporte conservan
sus resultados negativos originales. Son 4896 transiciones; 1385.40 segundos
efectivos y 118.3 MB de pico supervisado. No hubo lecturas externas denegadas.
Evidencia: `resultados/CORE07_FROZEN144/{OBSERVED,PRIMARY_TRANSITIONS,RECOVERY}.json`.

La extinción de CORE06 se refiere a pérdida de una respuesta por su canal
anterior, no a destrucción total demostrada de la historia. CORE07 muestra una
transformación aditiva externamente programada del linaje funcional: no una
política autónoma aprendida ni reparación general. La insensibilidad a ciertos
cambios de state/clock en ese aparato no se extiende a otros aparatos de fase.

La evolución usa exclusivamente el módulo nativo oficial 4.5, PYD
`17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d`
y fuente v27 identificada por el producto como
`fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31`.
La adaptación declarada admite los estados de arrays del protocolo original,
conservando tick y clocks; no presume que existieran colas históricas de sesiones.

Dos comparaciones diferentes deben mantenerse separadas:

1. **Histórica:** igualdad exacta de las observaciones locales originales y de
   los controles. No se dispone de hashes globales finales originales.
2. **Publicación 4.5:** los nuevos estados completos finales se identifican por
   hashes RAW/clocks y pueden regenerarse y compararse durante la extracción
   limpia. Eso no crea retrospectivamente evidencia global histórica.

Todos estos casos son reproducciones técnicas deterministas de los paneles
anteriores, no nuevos individuos semánticos de E1. El piloto y su repetición no
se suman a 134 ni 144 como nuevas réplicas científicas independientes. El primer
exportador falló por memoria después de cinco trayectorias; el código, datos
parciales y registro de la corrección quedan preservados. Dos intentos de cola
sin Runtime no se cuentan como preparaciones. No quedan trabajadores propios
activos después del cierre de estos dos paneles.
