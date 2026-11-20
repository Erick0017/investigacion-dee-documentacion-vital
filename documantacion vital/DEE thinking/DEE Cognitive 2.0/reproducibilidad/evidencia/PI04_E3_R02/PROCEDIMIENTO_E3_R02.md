# PI04 E3 — procedimiento preservado

La ejecución original Root Native ya terminó: real14/18 y desacoplado18/18,
90/90 entradas por brazo. La nueva receta del gestor está PREPARADA; no se
ha ejecutado nuevamente Native mediante ese CLI. No iniciar sobre ACTIVO.

Desde la raíz de Cognitive:

    motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad verificar pi04_e3_contingencia_R02
    motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad reproducir pi04_e3_contingencia_R02 --variante real --vida ECI02_PI03_REPRO_PI04_RP_REAL_01 --destino D:\DIAGNOSTICOS_DEE\E3_REAL_NUEVO
    motor\python313\python.exe -I -B -X utf8 sistema\gestionar.py reproducibilidad reproducir pi04_e3_contingencia_R02 --variante desacoplado --vida ECI02_PI03_REPRO_PI04_RP_YOKE_01 --destino D:\DIAGNOSTICOS_DEE\E3_YOKE_NUEVO

El padre del destino debe existir. Usar IDs no usados y destinos nuevos en la
misma unidad del producto. Se comparten motor/cápsula y se clona el conjunto
completo; nunca se recreaT0 ni se cambian selectores. La variante desacoplada
reproduce el plan de señales del contraste histórico; no busca un mejor plan.
Los cuatro suministros explícitos son pasos del protocolo, no autoabastecimiento.

Recálculo documental independiente del motor, desde esta misma raíz:

    motor\python313\python.exe -I -B -X utf8 reproducibilidad\evidencia\PI04_E3_R02\datos\RECALCULAR_E3.py --evidence reproducibilidad\evidencia\PI04_E3_R02\datos --out D:\DIAGNOSTICOS_DEE\RECALCULO_E3_NUEVO
    motor\python313\python.exe -I -B -X utf8 reproducibilidad\evidencia\PI04_E3_R02\RECALCULAR_ALINEACION_E3.py --recalculo D:\DIAGNOSTICOS_DEE\RECALCULO_E3_NUEVO\RECALCULO_E3.json --out D:\DIAGNOSTICOS_DEE\ALINEACION_E3_NUEVA.json

Estas órdenes sólo leen registros y escriben resultados nuevos, sin importar
DEE ni abrir un mundo. Las rutas históricas que aparecen en PROCEDENCIA y
registros son procedencia, nunca requisitos del recálculo o del runner.

El control recibió cuatro fallos falsos antes de las inversiones de conexión;
no se atribuye su18/18 a anticipación autónoma. La regla descriptiva mantener/
cambiar según señal recibida coincide con las18acciones de ambos brazos.
R01 conserva el fallo técnico de cuota y su mundo adverso permanece aparte;
la adaptación R03_R02 mantiene el límite Native1MiB, los seis antecedentes y
la fuente actual completa, archivando sólo nuevas duplicaciones por hash.

Los materiales grandes quedan en reproducibilidad/materiales: el prefijo
PI03_FINAL_T775355 y el estado real posterior PI03_PI04_POST_E3_T789431.
Son cortes reproducibles, no dos principales ni una fusión de memorias.
