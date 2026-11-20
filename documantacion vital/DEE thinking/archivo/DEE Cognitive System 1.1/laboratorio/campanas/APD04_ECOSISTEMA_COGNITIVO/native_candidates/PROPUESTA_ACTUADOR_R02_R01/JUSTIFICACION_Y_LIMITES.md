# ACTUADOR_R02: propuesta P0, no aprendizaje demostrado

La ruta nativa histórica declara que una consecuencia FAILURE inhibe A tanto para
la emisión −1 como para la emisión neutra0; +1 sigue la inhibición B. El codec
R01 traduce −1 a USE y0/+1 a INSPECT. Un cambio físico0↔+1 puede, por tanto,
no cambiar la acción externa. La alternativa única R02 fija −1/0→INSPECT,
+1→USE para hacer visible esa distinción. No calcula utilidad, igualdad, signo
correcto, acción objetivo ni reparación usando el target del auditor.

La elección de este codec es ingeniería externa P0 basada en el contrato
route.Failure, no conocimiento ni política aprendida por E1. Sólo un contraste
posterior de historias con consecuencias reales/omitidas podría acreditar un
cambio nativo condicionado, su utilidad, su conservación o sus pérdidas.

`apd04-actuador` sólo admite el enum R01/R02 y se ejecuta explícitamente antes de
evaluar. Persiste `action_codec` dentro del estado ambiental existente. No toca
RAW, clocks, cachés, recuerdos, geometría ni crea un mundo. Los snapshots antiguos
sin ese campo conservan exactamente la interpretación R01; un enum desconocido
se rechaza y no se repara. La vida y el entorno completos siguen siendo necesarios.

CLI propuesta: `configurar-actuador-ecosistema R02`. R01 permanece seleccionable.
El enum queda fijo durante cada bloque; no existe un override por oportunidad.
La ausencia de emisión sigue sin acción;0 es una emisión neutra válida, no silencio.

Dos ramas completas del mismo T639374, sensor R03 en ambas, conservarán el pasado
ambiental/cachés y recibirán diez oportunidades1+1 con cambio de goal después de5.
La única diferencia prospectiva del contraste es retorno real/omitido, con su
diferencia material declarada. No se importa R04 nuevo ni se limpia ningún futuro.

Esta carpeta es una propuesta N0. No se instaló en sistema ni se ejecutó DEE.
