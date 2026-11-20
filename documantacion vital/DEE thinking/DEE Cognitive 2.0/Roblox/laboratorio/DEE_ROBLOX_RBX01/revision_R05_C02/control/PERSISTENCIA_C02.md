# Contrato de frontera conjunta C02

Estos archivos son instrumentación experimental de R05. No cambian el principal,
el motor ni C01. Las pruebas sintéticas de archivos no acreditan una reapertura
material; Root debe ejecutar y conservar esa comprobación antes de depender de ella.

## Archivos y despliegue

- `mundo/Config_C02.luau` se instala como ModuleScript `Config`.
- `Body_C02.luau`, `EstadoPareja_C02.luau` y `ExportarRegistros_C02.luau` conservan esos nombres de ModuleScript.
- `Controller_C02.server.luau` reemplaza el único Script de control habilitado.
- El cliente de transporte se instala como ModuleScript `Bridge`.

El modelo exige `workspace.RBX01/DEE_Body` con PrimaryPart, doce `Gates/Gate_s_p`
con `Station` y `Port` IntValue, `Pickups` con partes `Kind=KEY/RESOURCE/DELIVERY`,
y `ReplicatedStorage.RBX01Status`/`RBX01Control`. Body recoloca puertas conforme
a las aristas nuevas y pickups en1/5/0. Los caminos y rótulos visuales antiguos
deben regenerarse desde Config. Blockcast se limita a puertas: no atribuir
planificación de trayectorias ni evitación general de obstáculos.

El ScenarioFingerprint de Config empieza sin sellar. Root debe fijar un hash de
la definición del escenario que excluya el propio campo y después pinnear los
bytes finales de fuentes. No existe un hash autorreferencial del archivo.

## Bucle y frontera

El controlador secuencia Q1 → ACK → Q2 → ACK → función por contacto (si existe)
→ ACK de función → retorno. Ese orden es preparación del aparato. Sólo usa el
resultado numérico realmente producido por cada participante.

`bridge:tool(fields,onProgress)` devuelve exactamente
`accepted/nativeTick/operationId/toolResult`. Tras `Body.applyTool`, el cliente
envía `toolAck(operationId,worldTimeMs,executionStatus=APPLIED|NO_RESULT)` antes
del retorno. `feedback` devuelve `operationId`; la ausencia bloquea la frontera.
CALCB sin resultado A produce `NUMERIC_INPUT_MISSING`, ningún RPC numérico y
ningún cero sustituto. Un resultado A cero válido conserva presencia=true.

Después de16 oportunidades completas, Controller llama `/v1/suspend` y conserva
cursor17. El mismo límite máximo48 sigue vigente tras reapertura; no se reinicia
contador ni stock. `/stop` sólo cierra el horizonte final. Save-close pedido
durante procesamiento termina la oportunidad y no vuelve a enviar una acción.

## Captura y comprobación material requerida

1. Suspender en `BOUNDARY`, con Native `IDLE`, ningún tool pendiente, último
   movimiento ACK y retorno confirmado. Verificar bridge sin queued/running/
   uncertain ni ACK pendiente; guardar Native por el propietario y cerrarlo.
2. En Server, invocar `ServerStorage.RBX01Checkpoint_C02:Invoke(context)`.
   Context aporta `checkpoint_id` y un resumen exacto de bridge con
   `session_id`, `server_id`, phase, pending_count0, uncertain_count0 y ticks
   Native relativos. Controller añade su cursor, estado RNG y frontera.
3. Guardar el JSON completo como WORLD_CHECKPOINT. Sólo entonces calcular su
   SHA-256 externo. No insertarlo dentro del mismo JSON.
4. `persistencia_C02.py seal-system` copia un destino Native experimental ya
   cerrado y completo, WORLD_CHECKPOINT, SQLite de bridge sin WAL pendiente y
   comprobante de cierre. Preserva archivos y directorios vacíos; no importa
   Native. El motor oficial instalado sigue como dependencia compartida.
5. Iniciar una escena fresca idéntica y con AutoStart NONE. Invocar
   `RBX01Restore_C02:Invoke(state,expected)`, donde expected contiene world_id,
   scenario_sha256, native_life_id, native_tick, owner_closed=true,
   bridge_quiescent=true y checkpoint_id/checkpoint_sha256 externos.
6. apply no ejecuta una acción. Retorna el cursor, RNG y
   `bridge.resumeTransport={checkpointId,checkpointSha256,sessionId,serverInstanceId}`.
   El cliente reutiliza esa identidad lógica y el servidor registra el nuevo
   proceso/segmento. El binding del bridge se realiza fuera del JSON guardado.
7. Volver a capturar sin actuar y usar `compare_world_semantics`: S/inventario/
   números/cursor/deduplicación/eventos/RNG deben coincidir exactamente. Sólo
   geometría admite tolerancia absoluta1e-5 predeclarada; UI mode/reason/latency,
   close_requested y segmento de observación son excepciones documentales.
8. Reabrir el MISMO estado Native coherente, sin ticks ni reenseñanza. Cotejar
   N/tick/RAW/clocks y colas. Armado explícito del bridge contra SHA de pareja;
   `/resume` conserva contadores/ACKs, no crea otra sesión. La siguiente
   oportunidad debe ser17 y una operación completada no debe ejecutarse otra vez.

Si el estado se importa bajo otro ID, hace falta una correspondencia explícita
de identidad de transporte y verificación física. `stage-restore` no implementa
esa migración ni autoriza copiar sólo RAW/clocks. Primera prueba recomendada:
cerrar y reabrir el mismo destino, con copia completa preservada fuera.

## Comandos stdlib reales (sin motor)

```text
python -I -B control/persistencia_C02.py seal-system --native-root native/DESTINO --world-file evidencia/WORLD_CHECKPOINT.json --bridge-database configuracion_privada/bridge.sqlite3 --close-proof evidencia/OWNER_CLOSED.json --destination pares/CORTE_01
python -I -B control/persistencia_C02.py verify --pair pares/CORTE_01
python -I -B control/persistencia_C02.py stage-restore --pair pares/CORTE_01 --destination pares/RESTAURACION_DIAGNOSTICA_01
```

Todos los destinos deben ser nuevos y estar en R05. Nunca se copian bases vivas.
El presupuesto global acumulado no se restaura hacia atrás al abrir una pareja.
Existe además `seal --native-export ...` para un export oficial completo: permite
sólo la fila processing del propio export identificado y su outbox exacto, para
conciliación oficial sin replay. No permite otro pendiente ni incertidumbre.

## Evidencia visual

Body registra poses observadas durante `advanceTime` a un máximo de20Hz de pared,
con ciclo/acción/tiempo lógico/UTC y segmento. No inventa posiciones durante la
espera Native. La reapertura conserva el origen UTC y aumenta segmento; no borra
el tiempo de cierre. El límite es25000 muestras. El render posterior debe
identificarse como reproducción visual si no procede de captura original.

Export auditor por chunks sin consultas Native:

```luau
local E=require(game.ServerScriptService.RBX01Server.ExportarRegistros_C02)
return E.chunk("poses",1,100) -- También events. No más de100 por RPC.
```

`E.geometry()` exporta partes/propiedades registradas del mundo. La traza y el
estado completo son del auditor y no se entregan a las políticas comparadas.

## Cobertura de prueba

Los fixtures crean bytes de snapshot falsos, SQLite falsos y JSON sintético;
prueban integridad, fronteras, diferencia cero/ausencia, RNG, rechazo de ACK,
WAL, tick o estado desconocido y preservación de directorios vacíos. No importan
DEE, no llaman MCP, no abren bases vivas ni prueban la compilación Luau.
Los informes de `pruebas/PERSISTENCIA_SINTETICA_*.json` distinguen esos alcances.
