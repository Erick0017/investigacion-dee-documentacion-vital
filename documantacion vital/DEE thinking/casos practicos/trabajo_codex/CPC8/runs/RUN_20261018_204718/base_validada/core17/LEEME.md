# Referencia CORE17 sobre DEE thinking4.5

La adaptación reproduce recuperación funcional mediante una copia adquirida redundante y transporte. El componente preparado, relays, conversores y daño finito conservan su procedencia: no es autorregeneración local ni integración enMAIN E1.

`repair45.py` ejecuta únicamente Runtime/v27 del WHL4.5 instalado. No importa el binario legado ni resultados archivados. `ejecutar_referencia.py` coordina las cohortes y compara sus lecturas contra el primario después de ejecutarlas. `FROZEN_CONFIG.json` fija doce trayectorias: ocho replays diagnósticos con clocks históricos y cuatro adaptaciones mediante canales estándar. La segunda geometría histórica se reservó para comprobar el adaptador, no se cuenta como holdout científico nuevo.

Los replays exactos usan `ResearchStateEdit` en forks explícitos para mantener las antiguas entradas RAW/clock y el daño. Por tanto no se presentan como experiencias por las interfaces ordinarias ni como una sola vidaMAIN. En el brazo de canales las entradas usan recibos reales; sólo el daño/control de memoria requiere un fork diagnóstico. Todos pertenecen a cohortes separadas deE1.

## Corrección de etiqueta de clock

El código ejecutado conservado tiene una etiqueta instrumental que decía que una entrada de canal asignaba clock0. El contrato real de Runtime4.5 preserva el clock completo existente. La ejecución llamó ese Runtime sin modificarlo; la etiqueta no cambió la física. `CLOCK_CONTRACT_CORRECTION.json` identifica todos los campos de texto/ledger afectados. Los clocks per-input que no se capturaron no se completan retrospectivamente.

Los cuatro pares conservan RAW idéntico en las24 fronteras guardadas, pero los arrays de clocks difieren en las20 fronteras posteriores aT0. La reproducción local y funcional pasa; no se afirma identidad física completa entre ambos contratos de entrada. El primario histórico tampoco ofrece todos los arrays de clocks con los que afirmar una igualdad global frente al original.

## Resultados y reproducción

Consulte `resultados/core17_repair/CLOSURE.json`, `SUMMARY_all.json`, la corrección de clock y los `MEASUREMENTS.json`. Se conservan72 snapshots y doce comparaciones de save/load+un tick. Tratamiento y reserva recuperan la función; el sham fuera de ruta la conserva. Copia no entrenada, dirección reseteada, copia ausente y ruta cortada no la recuperan; el receptor incorrecto conserva carga pero produce otra dirección.

Para una nueva reproducción, copie el directorio de resultados a otra ubicación de salida mediante una adaptación explícita del runner: el actual protege casos completos y los reanuda sin repetirlos. El comando ejecutado, desde la raíz CPC8, fue:

```powershell
python -I -B tools/supervisor.py --name core17_repair_confirm01 --timeout 600 -- python -I -B base_validada/core17/ejecutar_referencia.py --phase all
```

En un comando nuevo use otro nombre de job. Los argv exactos constan en `jobs/core17_repair_confirm01/COMMAND.json`; el ejemplo abreviado anterior muestra la estructura, no reemplaza esos argv. No lance runners históricos de limpieza.

El error inicial de comparación de recibos `Applied` frente a `applied` se corrigió en el evaluador. Piloto y comparaciones previas permanecen. No se repitieron los dos casos ya ejecutados para aparentar nuevas réplicas.
