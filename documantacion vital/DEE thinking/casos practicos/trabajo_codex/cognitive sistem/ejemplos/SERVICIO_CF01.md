# Servicio persistente CF01: entradas propias

Este acceso utiliza el **mismo gestor Cognitive** y el corte completo identificado como `CF01_OPERATIVO` en `entes/CATALOGO.json`. No crea desde T0 una anatomía equivalente ni combina memorias de otros perfiles. Las condiciones y tasas acreditadas del corte se consultan en su ficha y en el informe CF01 distribuido; un nombre de servicio no acredita aprendizaje general.

## Tres pasos

1. Extraiga la carpeta completa y abra una consola en ella. `INICIAR.bat catalogo` muestra las vidas originales disponibles y sus límites.
2. Utilice una identidad personal nueva y ofrezca mediciones propias dentro del dominio RAW 0..64:

```bat
INICIAR.bat servicio-cf01 MI_CF01_01 --mediciones=20:28,7:13,9:18
```

El primer uso importa explícitamente el snapshot completo de `CF01_OPERATIVO` y continúa esa copia. Las salidas materiales de DEE se convierten en comandos mediante el lector fijo del contrato. No se elige un lector según qué respuesta acierte.

3. Guarde y siga con la misma vida, incluso después de cerrar la consola:

```bat
INICIAR.bat gestor guardar --vida MI_CF01_01
INICIAR.bat servicio-cf01 MI_CF01_01 --continuar --mediciones=18:25,6:14
INICIAR.bat gestor cf01-estado --vida MI_CF01_01
```

Una vida ya existente no se sobrescribe: el segundo uso exige `--continuar`. Los snapshots completos, interfaces, colas, progreso y estado del entorno se guardan en `trabajo_personal/estado/`. No borre esa carpeta al actualizar código.

## Qué puede cambiar el investigador

Los pares son dos mediciones públicas, no un signo de acción. Puede presentar otros pares admitidos, observar respuestas, bifurcar antes de una experiencia y comparar sus consecuencias. El acceso sencillo conserva la calibración externa ya almacenada con la vida (consulte `cf01-estado`): no fija 7 ni sobrescribe un contexto posterior. La calibración pertenece a la **ley del entorno**, no es un contenido aprendido por A. El contrato rechaza cambiarla silenciosamente: un cambio requiere `--referencia-entorno N --reiniciar-entorno`, que reinicia sólo ese entorno, nunca RAW, clocks ni la vida DEE.

```bat
INICIAR.bat gestor bifurcar MI_CF01_01 MI_CF01_COMPARACION
INICIAR.bat gestor cf01-servicio --vida MI_CF01_COMPARACION --mediciones=11:16,23:31
```

La transducción de salida es P0 preparada: examina dos instantes fijos, admite retención instrumental de un tick y no repara un conflicto al vencimiento usando una muestra antigua. Silencio, conflicto, rechazo y acción anulada no se convierten en una respuesta correcta. Un cambio de interfaz no es selección aprendida por el ente.

`CF01_PLANTILLA_R9`, si aparece en el catálogo, conserva un pasado funcional de comparación con el lector anterior: no es el futuro reparado de una vida adversa. Abrirla crea otra copia explícita. Las fuentes del servicio están en `sistema/capacidades/cierre_funcional_cf01.py`; no es necesario recompilar v27.

El programa `actualizaciones/verificar_decode_cf01.py` recalcula exclusivamente la independencia de la transducción usando AST/stdlib. No ejecuta DEE. La prueba nativa y sus controles son evidencia distinta.
