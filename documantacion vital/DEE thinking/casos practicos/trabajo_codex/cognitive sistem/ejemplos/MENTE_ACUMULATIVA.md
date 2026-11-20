# Sesión continua de investigación

Esta entrada usa el mismo gestor de Cognitive. No es conversación libre ni un asistente general. El catálogo identifica el corte completo que se importa con el alias `MENTE_ACUMULATIVA`; no se recrea desde T0 ni se mezclan recuerdos con U0 o R10.

Abra una consola en la carpeta extraída y consulte primero:

```bat
INICIAR.bat catalogo
INICIAR.bat gestor --help
```

Para una identidad personal nueva, el lanzador importa explícitamente una copia completa del corte seleccionado. Al volver a indicar esa identidad en el comando es obligatorio usar `--continuar`; nunca se sustituye esa vida por otra para responder. Sus estados y archivos de prueba quedan en `trabajo_personal/` y el actualizador no los borra.

La entrada predeterminada es `INICIAR.bat mente`. Si aún no hay una vida personal activa, anuncia e importa el snapshot completo de la continuación seleccionada con una identidad `COLAB_MENTE_...`; no crea una anatomía T0. Sin situaciones sólo muestra el estado, sin ticks. En usos posteriores abre la misma vida personal activa. Si ésta pertenece a un perfil no admitido, informa fuera de dominio y la conserva: no busca otra rama para responder ni la reemplaza.

El comando es:

```text
INICIAR.bat mente MI_MENTE_01 --situaciones JSON
INICIAR.bat mente MI_MENTE_01 --continuar --situaciones JSON
INICIAR.bat gestor mente-estado --vida MI_MENTE_01
INICIAR.bat gestor guardar --vida MI_MENTE_01
```

`JSON` es una lista literal de situaciones del contrato instalado. Ejemplo de contenido, no una respuesta precalculada:

```json
[{"contexto":"c2","valores":[7,25],"herramienta":"trabajadores"},
 {"contexto":"c1","valores":[12,21],"regimen":"revisado"}]
```

Las reglas de comillas varían entre `cmd` y PowerShell. Para evitar transformar el JSON en la consola, puede ejecutar este fragmento con el Python incluido desde la raíz; modifique los datos y la identidad, no un target ni un lector:

```python
import json, subprocess
from pathlib import Path
root = Path.cwd()
requests = [{"contexto": "c2", "valores": [7, 25], "herramienta": "trabajadores"}]
subprocess.run([str(root / "motor/python313/python.exe"), "-I", "-B", "-X", "utf8",
                str(root / "actualizaciones/arrancar.py"), "mente", "MI_MENTE_01",
                "--situaciones", json.dumps(requests)], check=True)
```

En una segunda ejecución añada `"--continuar"` al argumento de la misma vida. El código de arriba sólo transporta la petición al gestor; no calcula un signo, no elige una memoria y no modifica RAW ni clocks. `mente-estado` es observación pasiva; presentar una situación introduce material y puede cambiar el estado.

Los contextos `c1..c4` y su sensor son preparación del aparato. No prueban cuatro significados aprendidos ni cuatro políticas retenidas. El estado de la referencia cambia por experiencias y sus consecuencias en el dominio declarado. Una primera respuesta incorrecta y una posterior mejoría no se renombran retención intacta. Consulte el Manual Maestro y el informe del corte para la cobertura real, incluyendo regresiones.

`trabajadores` limita las acciones a archivos de prueba locales: una salida DEE selecciona una operación fija de compresión o SHA-256 y su resultado vuelve como experiencia según el contrato. Los algoritmos pertenecen a las herramientas, no a un conocimiento de criptografía adquirido por DEE. `puertas` es una ley ambiental modelada; elegir explícitamente la tarea pertenece al operador. No hay LLM ni un controlador externo que resuelva las decisiones.

La misma vida R9 también puede utilizar el servicio transaccional EO02 ya incorporado, sin cambiar de perfil ni importar otro corte:

```bat
INICIAR.bat evolucion MI_MENTE_01 --continuar --observaciones "[[7,21]]" --dominio transaccion --referencia-entorno 14 --reiniciar-entorno
INICIAR.bat gestor guardar --vida MI_MENTE_01
INICIAR.bat evolucion MI_MENTE_01 --continuar --observaciones "[[11,25]]" --dominio transaccion
```

El primer comando reinicia explícitamente sólo el fixture transaccional externo; no DEE. Este ejemplo no entrega la fase: las oportunidades y el convertidor de acciones son preparados, y las consultas las inicia el operador. La consecuencia real, y no un target anticipado, puede cambiar la referencia compartida. Estos usos pueden producir errores y readquisición: el servicio no promete dos políticas conservadas ni reintentos autónomos. La variante EO02 `--fase-visible` es un sensor adicional preparado y debe declararse aparte, no atribuirse como aprendizaje de fase en esta campaña. Un archivo pendiente y sus bytes pertenecen al estado del entorno externo; conservarlos para continuar una transacción no los convierte en una memoria cognitiva del puente.

`--retorno omit`, `--retorno decoupled` y `--actuador nulled` son controles explícitos. No son reparaciones, no deben elegirse mirando la respuesta favorable y sus resultados no se mezclan con la vida sin ese control.

## Vida complementaria U0, no memorias de MAIN

El alias `U0_ACUMULATIVO_MA` contiene el estado completo T740 de una vida distinta. Puede abrirla con otra identidad y consultar las cinco correspondencias opacas mediante el gestor oficial, sin reenseñarlas:

```bat
INICIAR.bat abrir U0_ACUMULATIVO_MA MI_U0_01
INICIAR.bat gestor consultar --vida MI_U0_01 L07 L03 L06 L04 L05 --tick 804
INICIAR.bat gestor guardar --vida MI_U0_01
INICIAR.bat gestor consultar --vida MI_U0_01 L04 L06 L05 L03 L07 --tick 871
```

Las entradas804/871 respetan la fase oficial de esta preparación y se leen tres ticks después. No son ticks universales para cualquier vida: continúe desde el tick real y el contrato instalado. Son consultas dirigidas por operador, no elección autónoma de qué memoria utilizar. Su acumulación y revisión selectiva pertenecen a U0 y no solucionan por etiqueta la pérdida contextual de MAIN. Si esa vida queda activa, `mente` informa fuera del contrato R9 y no la sustituye; active explícitamente su copia R9 cuando quiera regresar.

La distribución no sincroniza automáticamente con otro equipo. Tras una campaña cerrada en el origen, use el `ACTUALIZAR.bat` existente y envíe el ZIP nuevo o su actualización incremental por un medio autorizado. No se publica ni sube a una nube por ejecutar estos ejemplos.
