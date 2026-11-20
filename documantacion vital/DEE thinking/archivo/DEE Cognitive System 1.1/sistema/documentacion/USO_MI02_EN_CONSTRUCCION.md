# Corte histórico de construcción MI02

Este documento conserva la incorporación inicial de R8. La guía vigente es [GUIA_MI02.md](GUIA_MI02.md), con R6, la alternativa R9, los perfiles auxiliares y las pérdidas observadas. No utilice este corte temprano como descripción del estado final.

El motor sigue siendo DEE thinking 4.5.0 y v27. No se cambió el predeterminado E1_SOCIAL_11. Las vidas N17 nuevas no heredan conocimiento de E1.

El retorno exterior R8 ya está incorporado. Su contrato es `contratos/MI02_RETORNO_EXTERIOR.json`. En una continuidad de24oportunidades se observaron cambios locales de elección por consecuencias. Las18posteriores dieron16acciones materiales útiles frente a7sin retorno y7con corte del retorno. Las reservas nuevas dieron13/19con retorno intacto y13/19con sham,0/19con corte de acción, y15/20en otra historia ambiental. Son trayectorias deterministas dependientes, no cientos de réplicas independientes ni un resultado de mente general.

Desde el intérprete compatible ya instalado:

```
python sistema/gestionar.py mi02-estado --vida MI02_CONTROLADOR_90
python sistema/gestionar.py bifurcar MI02_CONTROLADOR_90 MI02_MI_PRUEBA
python sistema/gestionar.py mi02-vivir --vida MI02_MI_PRUEBA --condiciones=-1,1,1
python sistema/gestionar.py guardar --vida MI02_MI_PRUEBA
python sistema/gestionar.py mi02-estado --vida MI02_MI_PRUEBA
```

Los comandos normales se probaron en procesos distintos con `MI02_OPERATIVO_RETORNO_15`; no leen laboratorio ni evidencia para decidir. La bifurcación permite proteger el estado de referencia, pero su futuro ya no es el del padre.

El dominio R8 exige la preparación espacial correspondiente y oportunidades391mod782. Los suministros legales siguen una regla ambiental recurrente; no son generación autónoma de recursos. El cero de carga es materia válida, no silencio. El fondo inerte preparado tiene RAW no nulo y no constituye espacio libre utilizable.

Las variantes unificadas R1–R5 siguen siendo candidatas. La activación nativa de B mediante una solicitud dependiente de historia ya tiene contrastes; no implica por sí sola actuación útil, comunicación renovable completa o una política general de consulta. Las pérdidas de las variantes anteriores se preservan. El manual final distinguirá la capacidad instalada del conocimiento actual de cada vida.
