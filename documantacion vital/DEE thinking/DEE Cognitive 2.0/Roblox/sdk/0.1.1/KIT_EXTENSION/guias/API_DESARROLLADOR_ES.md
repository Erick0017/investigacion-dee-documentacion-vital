# API en el servidor normal

Bindables: ServerStorage/DEE_SDK_EXT_R06. El callback usa el VM normal del servidor; no depende del caché de require del plugin. No hay RemoteEvent de jugador ni elección de ruta.

Consulta sin admisión Native:

```lua
local api = game:GetService("ServerStorage"):WaitForChild("DEE_SDK_EXT_R06")
local info = api.GetCapabilitiesRO:Invoke()
```

Solicitud explícita MATERIAL, sólo tras autorización del propietario:

```lua
local accepted = api.SubmitCapability:Invoke({kind="SOLVE", form="luma", left=7, right=3})
assert(accepted.ok, "No admitido; conservar el error")
local id = accepted.result.operationId -- registrado antes del POST
-- El host no calcula una respuesta esperada.
local current = api.GetOperationRO:Invoke(id) -- sólo GET del mismo ID
local preserved = api.ReadResultRO:Invoke(id) -- registro local completo
```

GetOperationRO actualiza el registro local con el GET. Tras una espera agotada, sólo un terminal conocido COMPLETED/FAILED_KNOWN libera el bloqueo; UNCERTAIN permanece bloqueado. Nunca reenvía POST. ReadResultRO no hace HTTP. Estas consultas no añaden experiencia Native.

Cierre MATERIAL explícito:

```lua
local closing = api.CloseCapabilities:Invoke()
-- Consultar closing.result.operationId mediante GetOperationRO.
```

| kind | Campos además de kind |
|---|---|
| RECALL | form=luma/nara |
| LESSON | form, observedSign=-1/+1, revision boolean, teacherMode=paired/omitted/desync |
| NUMERIC | operation=suma/diferencia, left/right enteros 0..32 |
| SOLVE | form, left/right enteros 0..32 |
| COMPOSE | forms lista exacta de 2 formas, data lista exacta de 3 enteros 0..32 |
| COMPARE | left/right enteros 0..20 |

Rutas autenticadas: GET /v1/capabilities/handshake; POST /v1/capabilities/submit con {instanceId,sessionId,operationId,request}; GET /v1/capability-operations/ID?instanceId=ID; POST /v1/capabilities/close con los tres IDs. Respuestas {ok,result}. POST devuelve 202 rápido; GET consulta PENDING_RESOURCE/PENDING/RUNNING/COMPLETED/FAILED_KNOWN/UNCERTAIN. COMPLETED.value conserva todo el JSON Native; el cliente no lo traduce. responseRaw conserva el JSON original, incluidos null y ceros, aunque el decodificador Luau represente null como clave ausente.

## Resultados grandes

Operations contiene una carpeta por ID: POST_INTENT inmutable, Header y Chunk_00001... Cada bloque tiene hasta 16.000 bytes y termina en un límite UTF-8. Header se escribe al final e indica chunkCount, byteCount y originalTruncated=false. Puede haber bloques sobrantes de una versión previa: use sólo el número vigente.

```lua
local meta = api.GetLocalRecordInfoRO:Invoke(id).result
local chunks = {}
for n=1,meta.chunkCount do
    chunks[n] = api.ReadRawChunkRO:Invoke(id,n).result
end
local recordJson = table.concat(chunks)
assert(#recordJson == meta.byteCount)
-- Es el registro de transporte; responseRaw conserva el HTTP original.
```

ReadResultRO ofrece el objeto completo a scripts del servidor. Para exportarlo por herramientas, transfiera los bloques y verifique byteCount; no suponga que la herramienta muestra un JSON grande entero. El primario autoritativo permanece en el backend privado. Sólo la vista española recorta texto.

Se validan campos, rangos e identidad, nunca una respuesta. Instancia equivocada, entrada desconocida, concurrencia o ventana agotada se rechazan antes del POST. HttpService y las autorizaciones reales corresponden al propietario; no se eluden denegaciones.
