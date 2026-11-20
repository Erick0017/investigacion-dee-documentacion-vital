# Mente acumulativa R02: análisis privado

Comience por [INFORME_RESULTADOS.md](INFORME_RESULTADOS.md), [CAPACIDADES_ANTES_DESPUES.json](CAPACIDADES_ANTES_DESPUES.json) y [DECISIONES_INCORPORACIONES.md](DECISIONES_INCORPORACIONES.md). [ENSAYOS_Y_CONTROLES.json](ENSAYOS_Y_CONTROLES.json) identifica las operaciones, controles y denominadores sin sumar bifurcaciones como una sola vida.

## Recalcular desde este ZIP

Extraiga todo el archivo en una carpeta nueva. Desde esa carpeta, con Python estándar, ejecute:

```powershell
python -I -B RECALCULO/verificar_analisis_final.py
```

El verificador usa [PLAN_RECALCULO.json](PLAN_RECALCULO.json), recalcula los catorce conjuntos desde los primarios exportados y compara exactamente los bytes de sus salidas con las referencias. No necesita instalar DEE, no ejecuta trabajadores y bloquea importaciones del motor, procesos y red. Es un control Python de acceso a archivos, no una sandbox del sistema operativo. Los resultados quedan en `RECALCULADO_DESDE_ZIP/`.

Se distinguen tres operaciones:

- **Recálculo archivado:** examina RAW, recibos, geometría, métricas y archivos de trabajo ya producidos. No genera ticks.
- **Reproducción nativa:** requiere motor oficial, preparaciones y snapshots completos; no está incluida en esta prueba ni es una nueva adquisición.
- **Comprobación operativa:** carga una copia completa desde el ZIP de colaboración, utiliza una entrada nueva y guarda/continúa entre procesos. Su prueba y hash del ZIP exacto se entregan externamente. No debe confundirse con los recálculos de este paquete.

Los diez accesos del perfil de cinco contextos son preparados; los primeros protocolos de cuatro contextos tenían ocho. El lector inspecciona todas las compuertas correspondientes, no sólo la favorable. El contenido de cada signo procede de la historia física. No se acredita P2 ni una política útil aprendida por consecuencias.

Los primarios positivos, adversos e instrumentales están identificados. Los snapshots completos, motor y WHL no viajan aquí. Este análisis no es un respaldo operativo completo: los localizadores y hashes de lo omitido constan en `INDICE_FUENTES_Y_OMISIONES.json`. El selector P1 auxiliar es otra vida, no una capacidad añadida retrospectivamente a MAIN.
