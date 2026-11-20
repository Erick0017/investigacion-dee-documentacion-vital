# Revisión estática del cierre y plan global

Alcance: lectura dirigida de `armar_analisis.py`, `repetir_todo.py`, `extraer_revision.py` y los siete planes cerrados indicados. Cero imports DEE, cero Runtime, cero ticks y ninguna modificación de S o de los staging congelados. No se ejecutaron nuevamente los recálculos al crear este borrador: se verificaron fuentes, imports, rutas, existencia y hashes de referencias, además de consultar los comprobantes portátiles ya existentes.

## Plan preparado

`PLAN_GLOBAL_BORRADOR.json` normaliza19casos al formato `{case,base,script,args,reference}` que acepta el runner. Mantiene siete namespaces:

- MECANISMO:6casos.
- SERVICIO:7casos.
- AUXILIAR:1caso.
- ADAPTACION:1caso.
- ESCALAMIENTO_B:2casos, desde el corte `ANALISIS_B_CERRADO_R2`.
- AUTOPSIA_R15:1caso.
- PROTECCION_FASE_R16:1caso.

Las19referencias existen y coinciden exactamente con sus SHA congelados, descomprimiendo sólo las referencias `.gz`. Los20archivos de cálculo necesarios se enumeran explícitamente, con hash e imports. Todas las dependencias son stdlib salvo un import local, incluido expresamente: `recalcular_b06_b07_R2_FINAL.py` utiliza funciones de `recalcular_escalamiento_b_R3_B05_FINAL.py`. El launcher `RUN_RECALCULO_B.py` conserva ambos junto a sí y añade únicamente esa carpeta local, necesario bajo `-I`.

El borrador no está aprobado para sellado. El coordinador todavía debe incorporar sus casos de trayectoria MAIN/A/B, el cierre operativo R3/R17 posterior y el informe final. No debe presentarse19como cobertura completa de toda la campaña. El borrador no copió evidencia ni abrió otro staging.

## Requisitos concretos de empaquetado

1. Colocar `repetir_todo.py`, `extraer_revision.py` y el plan final en `RECALCULO/` del análisis. Ambos helpers resuelven la raíz como `Path(__file__).parents[1]`.
2. Copiar cada staging cerrado íntegro bajo el namespace indicado, sin aplanarlo. Los calculadores de SERVICIO leen fuentes ejecutadas y artefactos en subcarpetas exactas de EVIDENCIA; convertir esas copias en simples localizadores de objetos impediría su recálculo. La deduplicación de `CODIGO_EJECUTADO` es otra representación y no sustituye automáticamente esas dependencias locales.
3. Conservar los tres scripts vecinos del launcher de ESCALAMIENTO_B. No basta exportar sólo `RUN_RECALCULO_B.py`.
4. Ejecutar el runner con un directorio de salida nuevo fuera de todos los árboles de evidencia. Sus scanners de carpetas podrían contabilizar un recálculo añadido dentro de EVIDENCIA como si fuera otro primario. El runner ya separa el cwd de cada proceso y sustituye `--salida/--out` por un archivo propio; el operador no debe situar esa salida dentro del corpus de entrada.
5. Las rutas históricas absolutas presentes en recibos/índices son procedencia y bytes archivados. Los19casos usan únicamente rutas de entrada relativas al namespace que el runner convierte en absolutas de la extracción; no requieren abrir las carpetas históricas.

## Observaciones sobre los helpers; sin modificaciones

- No encontré un bloqueo de formato en el runner para estos19casos: acepta flags `--salida/--out`, referencias `.gz`, argumentos de selector B05/B06_B07 y directorios/archivos de evidencia existentes.
- El packer recorre todos los archivos de cada `plan.trees`, excluyendo únicamente `__pycache__`. Por tanto, el plan final debe apuntar sólo a los staging científicos cerrados, nunca a la carpeta viva completa del laboratorio, un árbol de snapshots o un directorio operativo. El límite16MB se comprueba después de producir el candidato, no evita por sí solo inclusiones indebidas.
- El packer también incorpora automáticamente los primarios raíz y todas las revisiones de `EV/codigo_ejecutado`. Hay que sellar después del cierre definitivo y conservar ese directorio; no afirma estabilidad si una revisión sigue escribiéndose durante el recorrido.
- `repetir_todo.py` comprueba los miembros declarados, pero no rechaza archivos adicionales en una extracción previamente modificada. Para la verificación final debe usarse una extracción nueva del ZIP exacto y una salida externa. Los hashes manifiestan integridad de bytes, no constituyen un sandbox del sistema operativo.
- `extraer_revision.py` sólo materializa bytes archivados y no ejecuta el código. Hay que comprobar antes el manifiesto del análisis y escoger un destino nuevo; una interrupción puede dejar una extracción parcial, que no debe sobrescribirse silenciosamente. La inclusión del script no convierte el análisis en un entorno nativo autosuficiente.
- Las guardas de rutas/integridad del packer y del extractor utilizan `assert`; no invocarlos con `python -O`. Los comandos previstos usan `-I -B`, sin `-O`.
- Las comparaciones exactas de salidas calculadas mediante zlib corresponden a la biblioteca efectivamente utilizada. Una futura diferencia de biblioteca/codec sería un problema técnico de reproducción que debe informarse, no un fallo cognitivo ni una razón para editar las referencias.

## Pérdidas y límites científicos

Los snapshots operativos completos siguen fuera del ZIP científico, con índices y hashes en sus staging. Sus arrays o las extracciones u64 no sustituyen interfaces, colas, metadatos y transporte emparejado. El plan verifica cálculos archivados; no avanza vidas, no demuestra encuentros no registrados y no sustituye la prueba independiente del paquete operativo completo. No se detectó dependencia histórica ejecutable oculta en los19calculadores revisados. No se eliminaron negativos, fuentes ni evidencia única en esta tarea.
