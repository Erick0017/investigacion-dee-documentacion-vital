# EO02: entradas propias, servicios locales y continuidad

`EVOLUCION_OPERATIVA`, cuando figura en el catálogo del corte cerrado, corresponde a una continuación completa de EO02_MAIN. Su ficha identifica el estado realmente seleccionado y las funciones acreditadas; el código instalado no transfiere a esa vida todas las capacidades de la biblioteca. EO01, CF01 y el protegido E1 siguen disponibles por separado.

## 1. Cuatro observaciones y dos servicios reales

```bat
INICIAR.bat evolucion MI_EO02_01 --observaciones "[[2,14,1,3],[8,21,0,2]]" --dominio puertas
INICIAR.bat gestor guardar --vida MI_EO02_01
INICIAR.bat evolucion MI_EO02_01 --continuar --observaciones "[[3,16,2,4],[7,20,1,2]]" --dominio trabajadores
INICIAR.bat gestor evolucion-estado --vida MI_EO02_01
```

El primer comando importa explícitamente el snapshot completo bajo una identidad nueva. Los siguientes cargan esa misma vida; no la reconstruyen ni seleccionan una rama favorable por tarea. La cadena JSON se transporta íntegra al mismo gestor, sin sumarla, clasificarla ni convertirla en una respuesta en el lanzador. El contrato decide si admite dos o cuatro valores RAW individuales0..64 y cuál es su dominio físico; no se promete capacidad sobre16/32 variables por aceptar una lista.

`--dominio` es una elección de tarea del operador, no selección autónoma de especialista. Puertas y trabajadores comparten una correspondencia formal de representación y admisión: sus resultados deben interpretarse como reutilización bajo esa correspondencia, no abstracción general. Los trabajadores sí ejecutan operaciones locales inocuas, con archivos, lectura posterior y hashes. Su ley de admisión es modelada, no una medida del rendimiento de hardware ni un robot.

Los productos de servicios y snapshots personales se guardan bajo `trabajo_personal/estado/`; los diarios no son una memoria externa que el ente consulte para decidir. El proceso trabajador tiene un argv exacto autorizado por el guard y no recibe acceso al mundo nativo para escoger otra acción.

## 2. Una transacción con fase observable

Sobre la misma vida, o sobre una bifurcación explícita:

```bat
INICIAR.bat gestor bifurcar MI_EO02_01 MI_EO02_C
INICIAR.bat evolucion MI_EO02_C --continuar --observaciones "[[2,14],[8,21]]" --dominio transaccion --fase-visible
INICIAR.bat gestor guardar --vida MI_EO02_C
```

Después de cerrar el proceso, otra solicitud con `--continuar --dominio transaccion --fase-visible` recupera también el estado ambiental guardado. La fase preparada informa sólo si hay una transacción pendiente; no entrega el trabajador anterior ni la acción correcta. No acredita por sí sola una política contextual aprendida.

El control `--fase-cero` mantiene canales, conteo de entradas y cadencia, pero no conserva la dosis numérica de una fase1: no se presenta como un control de valor/dosis idénticos.

En C2, un estado pendiente conserva nombre relativo, bytes exactos y SHA del artefacto preparado. En una carpeta nueva el trabajador puede rehidratar esos bytes, leer el archivo y verificar contenido antes de confirmar. Esto es restauración explícita del estado externo, no reconstrucción del contenido desde el target ni recuerdo nativo. Un pendiente histórico C1 que sólo conserve el modelo no se convierte silenciosamente en C2: el gestor informa la incompatibilidad. Si se desea empezar otra preparación ambiental, `--reiniciar-entorno` es una decisión externa declarada que no borra DEE.

No se garantiza que toda transacción se complete con cualquier entrada. Conserve también intentos, rechazos, archivos producidos, pendientes y fallos. Consultar o presentar experiencias puede cambiar la vida: las comparaciones deben usar bifurcaciones identificadas, sin copiar sus aprendizajes a MAIN.

## Qué comparar y dónde mirar

Cambie valores admitidos, compare `--retorno real` con controles explícitos `omit`/`decoupled` en copias, y vuelva al dominio anterior sin restaurar otra memoria. Los resultados distinguen actuación, consecuencia real posterior y transformación adquirida. La calibración externa guardada se conserva si se omite `--referencia-entorno`; cambiarla requiere un reset ambiental explícito, no se ajusta para acertar.

Las capacidades finales, reservas y estados están en la guía vigente, las fichas y `investigacion/ENTE_DEE_EVOLUCION_02/`. Las fuentes principales son `sistema/capacidades/ente_evolucion_02.py`, `ente_evolucion_02_core.py`, `eo02_sensor_periferico.py` y `eo02_trabajador_local.py`.

## Otro perfil: ocho entradas en R10

Si aparece `SENSORIAL_R10` en el catálogo, es una arquitectura sensorial nueva desde T0, no la biografía EO02 ni un trasplante de sus aprendizajes. Se elige explícitamente con `--sensorial`; nunca se detecta la respuesta esperada para escoger ese perfil:

```bat
INICIAR.bat evolucion MI_R10_01 --sensorial --observaciones "[[2,7,1,3,4,2,3,2]]" --dominio puertas
INICIAR.bat evolucion MI_R10_01 --sensorial --continuar --observaciones "[[3,6,2,4,1,2,3,1]]" --dominio trabajadores
INICIAR.bat gestor evolucion-sensorial-estado --vida MI_R10_01
```

Cada lista mantiene ocho valores separados RAW0..32. El rango admitido no equivale a acierto exhaustivo sobre él. El contrato R10 no admite el modo transaccional/fase de R9, y las dos biografías no se intercambian silenciosamente. Sus resultados no se suman ficticiamente a la vida heredada. Toda actualización conserva `trabajo_personal/`; recibir un paquete nuevo no equivale a sincronización remota automática.
