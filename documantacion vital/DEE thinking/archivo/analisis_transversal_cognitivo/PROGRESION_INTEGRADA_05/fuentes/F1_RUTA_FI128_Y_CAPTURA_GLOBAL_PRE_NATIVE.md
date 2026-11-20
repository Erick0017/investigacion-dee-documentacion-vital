# PI05 F1/E3: ruta FI128 y captura global antes de Native

Corte de lectura: 2026-11-09T16:18:32.457133-06:00. Lectura dirigida de fuentes y estados congelados; cero ticks nuevos. Esta nota no declara una trayectoria observada entre fotogramas ni identifica un portador por su valor.

## Alcance y base comprobada

El prompt PI05 completo de 35FC fue leído. Se reutilizaron la autopsia PI04, la réplica negativa y los contratos de comparación. El dominio de `acciones_nativas_apd04.balance(left,right)` es **0..20 por carga pública** y su códec es `[left,20-right,0,...]`; el límite0..32 corresponde a los componentes materiales de FI128 y NO cambia aquel sesgo20. No se reutiliza el sesgo32 de la resta aritmética.

El primer desacuerdo funcional que los registros antiguos ya muestran es C en817933:14 en vez de31. No hay fotografías globales de817878..817932 en esas fuentes; por ello el primer encuentro responsable anterior a C todavía no está localizado. La admisión de176 eventos no cubre su transporte.

## Calendario exacto y convención temporal

`Runtime::advance` aplica primero los eventos cuyo tick solicitado esT, ejecuta un paso v27 y después incrementa el tick. Por tanto el fotograma de fronteraT es **antes** de la admisión programada enT; el siguienteT+1 incorpora admisión y un paso. `effective_tick=T` acredita la admisión, no una observación independiente después de inyectar y antes de evolucionar. La API pública no expone aquí esa frontera intermedia.

| Frontera | Hecho documentado o función contractual |
|---:|---|
|817876|Corte completo físico previo; empieza la operación.|
|817878|128 muestras RAW solicitadas/aplicadas;14 y17 son los dos payloads no nulos.|
|817879|Primeros nodos nominales de las ramas; debe observarse, no inferirse su contenido.|
|817880|32 retornos/cambios de dirección genéricos de payload0.|
|817885|Nodos intermedios nominales de ambas ramas.|
|817886|8 recursos genéricos de payload0.|
|817897|Convergencias raíz nominales de ambas ramas.|
|817898|2 girosY genéricos0.|
|817915|2 girosX genéricos0.|
|817932|Salida común genérica0 y consultaMU5 con dos soportes0; q.|
|817933|C=(12,17,18), dato registrado14; positivo histórico31.|
|817935|S=(14,15,16), registrado14; E tiene la consulta5 antes de su interacción.|
|817936|E=(15,15,15), dirección(-1,+1,-1), carga5: signo material-1 en q+4.|
|817938|Lector fijado q+6 también-1.|
|818074|Fin del horizonte, incluidos2N=134 ticks posteriores al último grupo de lecturas.|

Las dos entradas materiales diferenciadas son:14 en(47,55,53), dirección(+1,-1,+1), cabeza nominal(48,54,54);20-b en(14,46,20), dirección(+1,+1,+1), cabeza nominal(15,47,21). Ambas se programan817878; sus cabezas corresponden817879 en la geometría.

| Rama | Nodos nominales de la geometría, no linaje medido |
|---|---|
|Izquierda|817879:(48,54,54) →817885:(52,48,58) →817897:(62,36,1)|
|Derecha|817879:(15,47,21) →817885:(19,53,25) →817897:(29,65,35)|

Los giros a seguir en ambas ramas, incluidos sus ceros, aparecen con sus coordenadas exactas en el anexo176. Un cero material puede crear un encuentro; no es ausencia de entrada.

## Lectura global y representación sin pérdida

`runtime.raw_copy()` y `runtime.clock_copy()` son métodosconst que devuelven copias en `runtime.hpp:154–155`. Cada vector tiene300763uint64, shape(67,67,67),2406104bytes; índice `(x*67+y)*67+z`. Dos vectores suman4812208bytes, no9624416(el contador operativo incluye buffers internos adicionales). `observe(Coordinate)` esconst en `runtime.cpp:446`; `receipt(id)` recupera el recibo. Las lecturas se hacen bajo el mismo propietario, con tick antes/después idéntico y sin avance concurrente.

Captura propuesta acotada a **817876..818074 inclusive**,199fronteras de un único usoFI. Ancla binariauint64LE de RAW+clocks en817876; deltas sin pérdida cada paso, guardando índices y nuevosuint64(incluidoRAW0 y state0/SEM4 no nulo). Anclas completas adicionales en817878/879,880/881,885/886/887,897/898/899,915/916,932..940 y818074; pueden reconstruirse de los deltas y no requieren otro ensayo. Si los clocks evolucionan exactamente+1, se permite codificar esa transformación externa verificada más excepciones; de otro modo conservar los valores completos. Nunca modificar clocksNative.

Cada frontera conserva tick, hashes de ambos buffers, dimensión, tamaño, max_s_reg global, soporteRAW(no sólostate>0), contador de overflow/genesis/backend y recibos nuevos. Guardar telemetría en archivos externos comprimidos, no en metadatosNative. Reconstruir todos los buffers y verificar cada hash. El flujo bruto199×4812208=957629392bytes no se materializa como duplicados; se comprimen las diferencias y se conserva un par anterior/actual en memoria. Medir coste y memoria bajo el límite512MB sin deshabilitarlo.

La inspección contempla TODO N67: fases, configuraciones inmóviles, direcciones, semántica y RAW no nulo con state0. F1Y60/Y38/Y16 es sólo un antecedente; no se restringe la búsqueda a esa fila ni se retira la guardaOP3 del principal.

## Dependencia causal derivada del kernel

Las reglas ordinarias, XNOR, firma tetraédrica y búsqueda de fuentes leen la vecindadMoore1 y el reloj local. La rama `prov_total>=UMBRAL_FUSION=19665` cuenta vecinos de vecinos, y su DEMUX se aplica en un vecino mediante el segundo pase. Por ello una cota conservadora de dependencia RAW del paso completo es radioChebyshev3 toroidal, no una supuesta velocidad universal1. Si el máximo global de s_reg antes de un paso es≤19663, el incremento de provisión(como máximo1) no alcanza aquella rama y la actualización de ese paso se acota a Moore1. Registrar los máximos y contadores permite precisar la cota observada; no asumir esa exclusión a partir de dos extremos.

Para el primer desacuerdo de tránsito encontrado, inspeccionarT−1/T/T+1 y la vecindad causal derivada, incluidos aportes de otras regiones. Si el camino nominal no contiene la influencia, continuar con diferencias globales, sin rellenar trayectorias a partir de una carga coincidente.

## Contrastes mínimos prospectivos

1. Obtener un prefijo operativo completo y coherente817876. Existe su snapshot físico, pero no debe tratarse como par completo por sí solo. Si no se preservó el par, alcanzarlo en una copia desde816019 con los dos trabajos y los cinco usos originales, y exportar0ticks mediante contrato; no ensamblar snapshot con una SQLite posterior. La candidata de recuperación puede continuar el futuro ya fallido; este prefijo diagnóstico no sustituye su historia.

2. Ejecutar el mismo FI14/3 con captura, conservando las176 entradas y los lectoresq+4/q+6. Comparar su final con el brazo sin captura ya reproducido desde el mismo prefijo: buffers completos, interfaces, agenda, recibos y estado operativo pertinente, excluyendo sólo identidad/diarios declarados. Si la captura divide `run_until` en pasos, conservar los eventos/calendario exactos y cotejar además el avance sin captura. Una variante compact con la misma granularidad y sin copias globales separa lectura de división temporal si aparece una discrepancia. No retirar la consulta funcional y llamarlo ausencia de observador.

3. En clones completos del MISMO prefijo,14/2,14/3,14/4 modifican sólo el payload18/17/16 de `MU.raw.L128.right.root.0.0.raw.0` en(14,46,20)817878. Todos los otros175 eventos/calendario permanecen iguales. El dominio es legal y el signo útil es positivo en los tres; la discriminación principal es el conjuntoglobalD(T) de diferenciasRAW/clocks, el primer contacto y su transformación, no únicamente el signo. Mantener todos los rechazos si la evolución cambia la admisión posterior.

4. Si hace falta, comparar omitir aquella entrada(175eventos) con payload0 material(176eventos; b=20 legal). Ambos difieren de17; no son equivalentes entre sí ni un sham automáticamente equiparable. Consultar ausente o cortar un portador son intervenciones materiales adicionales que requieren motivo y controles propios; no se añaden de rutina.

5. Antes del contraste de rescate, fijar encuentro/condición sospechosa, predicción, intervención legal y sham, lectores, horizonte y conservación. Ningún atlas/delta o resultado esperado se entrega al ente. Una huella externamente distinguible sólo es capacidad del observador hasta demostrar usoNative.

## Prefijos REAL/NONE/YOKED T816019: lectura pasiva exacta

REAL yYOKED tienen RAW/clocks byteidénticos, interfaces y agenda iguales; sus recibos/prefijos causales y ambientes difieren. NONE difiere de REAL en un soloRAW: B=(20,53,5), s_reg153 frente152; clocks e interfaces/agenda coinciden. No se concluye igualdad de mundos completos.

El contrato YOKED deC2C está agotado tras20slots: `validate` rechaza una continuaciónordinal20 que invente señales futuras. Para repetir los dos trabajos en ese brazo hace falta una extensiónPI05 explícita que preserve el plan/historia20 y declare sus retornos nuevos(por ejemplo los dos retornos reales ya registrados, ambosFalse). No editar calladamente el pasado, ni contar una modificación administrativa de plan como aprendizaje. No se ejecutó tal extensión en esta lectura.

Datos recalculados de los snapshots(los hashes completos de las fuentes quedan abajo):
```json
{
  "prefixes": {
    "REAL": {
      "source": "D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\PI04_C2C_REAL_RES_R01.json",
      "source_sha256": "7d876fe82f44e40c834ae08ae2684c2a322ad7b7e3bee8b8aea9d93928c7ac6c",
      "snapshot_sha256": "ef9869aece0641db17f14934415f560563c32405d4799fa3ae4a644a55b57a70",
      "physical": {
        "N": 67,
        "tick": 816019,
        "RAW_sha256": "3ecd4014307de5dab012307b10e92aad5538d05ac5703566fa9f9408fbdcc472",
        "clocks_sha256": "d26c51ff0bd4cb74aea483b89a893a2d121d9750115f64ddb5d1b2b5a2b9939e"
      },
      "interfaces": 1056,
      "pending": 0,
      "receipts": 126076,
      "causal_prefix_sha256": "d8372e75768b5930b3b2ba3084ce7ee03414bd35b1fce44123998f5e8d986c89"
    },
    "NONE": {
      "source": "D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\PI04_C2C_NONE20_R01.json",
      "source_sha256": "027cfadcbd96405908c7a1f00692f00527d59ecaa77eb46265a257bd509912cc",
      "snapshot_sha256": "8a2e95c080cbce0c64384508475d5ef4638f13e665413919a825745fa800b4ce",
      "physical": {
        "N": 67,
        "tick": 816019,
        "RAW_sha256": "f078a7d563959b384fae83aff2a22d6d9cdbdc6badc3eb71def638d4b099039a",
        "clocks_sha256": "d26c51ff0bd4cb74aea483b89a893a2d121d9750115f64ddb5d1b2b5a2b9939e"
      },
      "interfaces": 1056,
      "pending": 0,
      "receipts": 126076,
      "causal_prefix_sha256": "d1bd1b96c6bb424e087c4ccae6a5ecb0c791162fc29ab6dd55f08f5b88995060"
    },
    "YOKED": {
      "source": "D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\PI04_C2C_YOKE20_R01.json",
      "source_sha256": "30f64ce429ed4cf77201ff2e2414fc9ea66653616ea74c0a1f77359b14a11f18",
      "snapshot_sha256": "e9627eab31989f076b4af973658f2aed250f030176613e0061f0eebca1c820a3",
      "physical": {
        "N": 67,
        "tick": 816019,
        "RAW_sha256": "3ecd4014307de5dab012307b10e92aad5538d05ac5703566fa9f9408fbdcc472",
        "clocks_sha256": "d26c51ff0bd4cb74aea483b89a893a2d121d9750115f64ddb5d1b2b5a2b9939e"
      },
      "interfaces": 1056,
      "pending": 0,
      "receipts": 126076,
      "causal_prefix_sha256": "be459c5b525c9b4a3292563c1650a9a364f17c4d677263831eb44210b1ac5c45"
    }
  },
  "REAL_vs_others": {
    "NONE": {
      "RAW_differences": [
        {
          "site": [
            20,
            53,
            5
          ],
          "REAL": {
            "RAW": "1152922157441875969",
            "state": 1,
            "s_reg": 152,
            "semantic": 1,
            "direction": [
              0,
              0,
              0
            ]
          },
          "NONE": {
            "RAW": "1152922161736843265",
            "state": 1,
            "s_reg": 153,
            "semantic": 1,
            "direction": [
              0,
              0,
              0
            ]
          }
        }
      ],
      "clocks_bytes_equal": true,
      "interfaces_equal": true,
      "pending_equal": true,
      "receipt_history_equal": false
    },
    "YOKED": {
      "RAW_differences": [],
      "clocks_bytes_equal": true,
      "interfaces_equal": true,
      "pending_equal": true,
      "receipt_history_equal": false
    }
  }
}
```

## API real disponible para Root

La petición utilizada y preservada es `Owner.material(ID_NUEVO,{"modo":"eci01-balance","izquierda":14,"derecha":3},feedback="omit")` sobre un propietario aislado ya abierto. El propietario dePI05 elegirá sólo prefijos completos y nuevosID. Para captura, un wrapper que delegueworld/tick y haga los mismos avances con eventos previamente fijados puede leer `a.world.runtime.raw_copy()`, `clock_copy()`, `current_tick`, `last_tick_info` y `receipt(id)`; debe contrastarse con la continuación sin captura. No usar `diagnostic_fork`, ediciones, `--nueva` ni save deCognitiveSession como supuesta lectura pasiva: ese save actualiza metadatos operativos.

## Fuentes leídas/cotejadas en este bloque

Lectura completa del promptPI05; lectura dirigida del código geométrico, comparación, calendario/lector, Runtime y reglas v27; recálculo pasivo de176recibos y de tres snapshotsT816019. No se declaran releídos íntegramente los manuales ni todos los expedientes. No se ejecutó Native, no se escribió el producto ni se incorporó una solución.

| Fuente | Bytes | SHA-256 actual |
|---|---:|---|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\ensayos\PI04_MAIN_PANEL12_OP2_FIplus.json|185890|d4eb8a7aba3dd3d4aa2ed207e83adbb439af525542eaa9145c33c82d84804e3e|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\control\CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json|64225|8010b5a54d0687bc68161ef4df889d29a6ad6fa74ef7b91d4370997348310d6f|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\control\REGRESION_FIPLUS_PROTOCOLO_PRE_REPLICA_R01.json|9493|c63ebcac16093e5b18408119db76c6fd39201c6be7041d68652bfb8efca383ea|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\control\REGRESION_FIPLUS_REPLICA_CERRADA_R01.json|19797|ddf9d15041c46bfab2d8e5b4ccf7fdf9e6fc221ab662be9dfe0c6a8714ed07ca|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\estados\candidato_R02\sistema\capacidades\percepcion_cruda_fi01.py|11212|0fb2e1f88ab1a6aedea2784791509b4e0a42fb94fdf15491f7b79596af6c3390|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\estados\candidato_R02\sistema\capacidades\acciones_nativas_apd04.py|4589|f0fb1a3616c668d48bee8865956f12bd6c53367b7b2062a9a33f6ff966bf3f3a|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\estados\candidato_R02\sistema\capacidades\acceso_eci01.py|12723|33bee08fc31f30616180e0747721cd75aeaf8f6a97ec095c32eef53978000bfb|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\archivo\analisis_transversal_cognitivo\PROGRESION_INTEGRADA_04\estados\candidato_R02\sistema\capacidades\selector_acrecion_nativo.py|3751|e5e78021fc7c2218064ada2f69db6b70bc73cd40325304e1140a9e07cd9752b7|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\4.5\DEE_thinking_4_5_0\source\src\runtime.cpp|36031|5e1951b7e5b192219e6c7620c9f9c61be911ab5a7faaa6948fea32956cfaf357|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\4.5\DEE_thinking_4_5_0\source\include\dee_thinking\runtime.hpp|7085|809283b4f8e11b3e98f285b6d48f056bb0be34b55a0369d5fc9f31483d1ce1d4|
|D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking\4.5\DEE_thinking_4_5_0\source\src\kernel_v27.cpp|31596|fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31|

## Anexo:176 eventos exactos solicitados y aplicados

Coordenadas/dirección de la interfaz congelada anterior; tick y payload del primario. Las cabezas/nodos descritos arriba son derivados de la geometría, no de seguir una identidad por s_reg.

| ID Native | Tick solicitado/aplicado | Canal | Sitio | Dirección | Payload |
|---:|---:|---|---|---|---:|
|126484|817878|MU.raw.L128.left.root.0.0.raw.0|[47, 55, 53]|[1, -1, 1]|14|
|126485|817878|MU.raw.L128.left.root.0.0.raw.1|[49, 55, 53]|[-1, -1, 1]|0|
|126486|817878|MU.raw.L128.left.root.0.0.raw.2|[47, 55, 55]|[1, -1, -1]|0|
|126487|817878|MU.raw.L128.left.root.0.0.raw.3|[49, 55, 55]|[-1, -1, -1]|0|
|126488|817878|MU.raw.L128.left.root.0.1.raw.0|[55, 55, 53]|[1, -1, 1]|0|
|126489|817878|MU.raw.L128.left.root.0.1.raw.1|[57, 55, 53]|[-1, -1, 1]|0|
|126490|817878|MU.raw.L128.left.root.0.1.raw.2|[55, 55, 55]|[1, -1, -1]|0|
|126491|817878|MU.raw.L128.left.root.0.1.raw.3|[57, 55, 55]|[-1, -1, -1]|0|
|126492|817878|MU.raw.L128.left.root.0.2.raw.0|[47, 55, 61]|[1, -1, 1]|0|
|126493|817878|MU.raw.L128.left.root.0.2.raw.1|[49, 55, 61]|[-1, -1, 1]|0|
|126494|817878|MU.raw.L128.left.root.0.2.raw.2|[47, 55, 63]|[1, -1, -1]|0|
|126495|817878|MU.raw.L128.left.root.0.2.raw.3|[49, 55, 63]|[-1, -1, -1]|0|
|126496|817878|MU.raw.L128.left.root.0.3.raw.0|[55, 55, 61]|[1, -1, 1]|0|
|126497|817878|MU.raw.L128.left.root.0.3.raw.1|[57, 55, 61]|[-1, -1, 1]|0|
|126498|817878|MU.raw.L128.left.root.0.3.raw.2|[55, 55, 63]|[1, -1, -1]|0|
|126499|817878|MU.raw.L128.left.root.0.3.raw.3|[57, 55, 63]|[-1, -1, -1]|0|
|126500|817878|MU.raw.L128.left.root.1.0.raw.0|[0, 55, 53]|[1, -1, 1]|0|
|126501|817878|MU.raw.L128.left.root.1.0.raw.1|[2, 55, 53]|[-1, -1, 1]|0|
|126502|817878|MU.raw.L128.left.root.1.0.raw.2|[0, 55, 55]|[1, -1, -1]|0|
|126503|817878|MU.raw.L128.left.root.1.0.raw.3|[2, 55, 55]|[-1, -1, -1]|0|
|126504|817878|MU.raw.L128.left.root.1.1.raw.0|[8, 55, 53]|[1, -1, 1]|0|
|126505|817878|MU.raw.L128.left.root.1.1.raw.1|[10, 55, 53]|[-1, -1, 1]|0|
|126506|817878|MU.raw.L128.left.root.1.1.raw.2|[8, 55, 55]|[1, -1, -1]|0|
|126507|817878|MU.raw.L128.left.root.1.1.raw.3|[10, 55, 55]|[-1, -1, -1]|0|
|126508|817878|MU.raw.L128.left.root.1.2.raw.0|[0, 55, 61]|[1, -1, 1]|0|
|126509|817878|MU.raw.L128.left.root.1.2.raw.1|[2, 55, 61]|[-1, -1, 1]|0|
|126510|817878|MU.raw.L128.left.root.1.2.raw.2|[0, 55, 63]|[1, -1, -1]|0|
|126511|817878|MU.raw.L128.left.root.1.2.raw.3|[2, 55, 63]|[-1, -1, -1]|0|
|126512|817878|MU.raw.L128.left.root.1.3.raw.0|[8, 55, 61]|[1, -1, 1]|0|
|126513|817878|MU.raw.L128.left.root.1.3.raw.1|[10, 55, 61]|[-1, -1, 1]|0|
|126514|817878|MU.raw.L128.left.root.1.3.raw.2|[8, 55, 63]|[1, -1, -1]|0|
|126515|817878|MU.raw.L128.left.root.1.3.raw.3|[10, 55, 63]|[-1, -1, -1]|0|
|126516|817878|MU.raw.L128.left.root.2.0.raw.0|[47, 55, 6]|[1, -1, 1]|0|
|126517|817878|MU.raw.L128.left.root.2.0.raw.1|[49, 55, 6]|[-1, -1, 1]|0|
|126518|817878|MU.raw.L128.left.root.2.0.raw.2|[47, 55, 8]|[1, -1, -1]|0|
|126519|817878|MU.raw.L128.left.root.2.0.raw.3|[49, 55, 8]|[-1, -1, -1]|0|
|126520|817878|MU.raw.L128.left.root.2.1.raw.0|[55, 55, 6]|[1, -1, 1]|0|
|126521|817878|MU.raw.L128.left.root.2.1.raw.1|[57, 55, 6]|[-1, -1, 1]|0|
|126522|817878|MU.raw.L128.left.root.2.1.raw.2|[55, 55, 8]|[1, -1, -1]|0|
|126523|817878|MU.raw.L128.left.root.2.1.raw.3|[57, 55, 8]|[-1, -1, -1]|0|
|126524|817878|MU.raw.L128.left.root.2.2.raw.0|[47, 55, 14]|[1, -1, 1]|0|
|126525|817878|MU.raw.L128.left.root.2.2.raw.1|[49, 55, 14]|[-1, -1, 1]|0|
|126526|817878|MU.raw.L128.left.root.2.2.raw.2|[47, 55, 16]|[1, -1, -1]|0|
|126527|817878|MU.raw.L128.left.root.2.2.raw.3|[49, 55, 16]|[-1, -1, -1]|0|
|126528|817878|MU.raw.L128.left.root.2.3.raw.0|[55, 55, 14]|[1, -1, 1]|0|
|126529|817878|MU.raw.L128.left.root.2.3.raw.1|[57, 55, 14]|[-1, -1, 1]|0|
|126530|817878|MU.raw.L128.left.root.2.3.raw.2|[55, 55, 16]|[1, -1, -1]|0|
|126531|817878|MU.raw.L128.left.root.2.3.raw.3|[57, 55, 16]|[-1, -1, -1]|0|
|126532|817878|MU.raw.L128.left.root.3.0.raw.0|[0, 55, 6]|[1, -1, 1]|0|
|126533|817878|MU.raw.L128.left.root.3.0.raw.1|[2, 55, 6]|[-1, -1, 1]|0|
|126534|817878|MU.raw.L128.left.root.3.0.raw.2|[0, 55, 8]|[1, -1, -1]|0|
|126535|817878|MU.raw.L128.left.root.3.0.raw.3|[2, 55, 8]|[-1, -1, -1]|0|
|126536|817878|MU.raw.L128.left.root.3.1.raw.0|[8, 55, 6]|[1, -1, 1]|0|
|126537|817878|MU.raw.L128.left.root.3.1.raw.1|[10, 55, 6]|[-1, -1, 1]|0|
|126538|817878|MU.raw.L128.left.root.3.1.raw.2|[8, 55, 8]|[1, -1, -1]|0|
|126539|817878|MU.raw.L128.left.root.3.1.raw.3|[10, 55, 8]|[-1, -1, -1]|0|
|126540|817878|MU.raw.L128.left.root.3.2.raw.0|[0, 55, 14]|[1, -1, 1]|0|
|126541|817878|MU.raw.L128.left.root.3.2.raw.1|[2, 55, 14]|[-1, -1, 1]|0|
|126542|817878|MU.raw.L128.left.root.3.2.raw.2|[0, 55, 16]|[1, -1, -1]|0|
|126543|817878|MU.raw.L128.left.root.3.2.raw.3|[2, 55, 16]|[-1, -1, -1]|0|
|126544|817878|MU.raw.L128.left.root.3.3.raw.0|[8, 55, 14]|[1, -1, 1]|0|
|126545|817878|MU.raw.L128.left.root.3.3.raw.1|[10, 55, 14]|[-1, -1, 1]|0|
|126546|817878|MU.raw.L128.left.root.3.3.raw.2|[8, 55, 16]|[1, -1, -1]|0|
|126547|817878|MU.raw.L128.left.root.3.3.raw.3|[10, 55, 16]|[-1, -1, -1]|0|
|126548|817878|MU.raw.L128.right.root.0.0.raw.0|[14, 46, 20]|[1, 1, 1]|17|
|126549|817878|MU.raw.L128.right.root.0.0.raw.1|[16, 46, 20]|[-1, 1, 1]|0|
|126550|817878|MU.raw.L128.right.root.0.0.raw.2|[14, 46, 22]|[1, 1, -1]|0|
|126551|817878|MU.raw.L128.right.root.0.0.raw.3|[16, 46, 22]|[-1, 1, -1]|0|
|126552|817878|MU.raw.L128.right.root.0.1.raw.0|[22, 46, 20]|[1, 1, 1]|0|
|126553|817878|MU.raw.L128.right.root.0.1.raw.1|[24, 46, 20]|[-1, 1, 1]|0|
|126554|817878|MU.raw.L128.right.root.0.1.raw.2|[22, 46, 22]|[1, 1, -1]|0|
|126555|817878|MU.raw.L128.right.root.0.1.raw.3|[24, 46, 22]|[-1, 1, -1]|0|
|126556|817878|MU.raw.L128.right.root.0.2.raw.0|[14, 46, 28]|[1, 1, 1]|0|
|126557|817878|MU.raw.L128.right.root.0.2.raw.1|[16, 46, 28]|[-1, 1, 1]|0|
|126558|817878|MU.raw.L128.right.root.0.2.raw.2|[14, 46, 30]|[1, 1, -1]|0|
|126559|817878|MU.raw.L128.right.root.0.2.raw.3|[16, 46, 30]|[-1, 1, -1]|0|
|126560|817878|MU.raw.L128.right.root.0.3.raw.0|[22, 46, 28]|[1, 1, 1]|0|
|126561|817878|MU.raw.L128.right.root.0.3.raw.1|[24, 46, 28]|[-1, 1, 1]|0|
|126562|817878|MU.raw.L128.right.root.0.3.raw.2|[22, 46, 30]|[1, 1, -1]|0|
|126563|817878|MU.raw.L128.right.root.0.3.raw.3|[24, 46, 30]|[-1, 1, -1]|0|
|126564|817878|MU.raw.L128.right.root.1.0.raw.0|[34, 46, 20]|[1, 1, 1]|0|
|126565|817878|MU.raw.L128.right.root.1.0.raw.1|[36, 46, 20]|[-1, 1, 1]|0|
|126566|817878|MU.raw.L128.right.root.1.0.raw.2|[34, 46, 22]|[1, 1, -1]|0|
|126567|817878|MU.raw.L128.right.root.1.0.raw.3|[36, 46, 22]|[-1, 1, -1]|0|
|126568|817878|MU.raw.L128.right.root.1.1.raw.0|[42, 46, 20]|[1, 1, 1]|0|
|126569|817878|MU.raw.L128.right.root.1.1.raw.1|[44, 46, 20]|[-1, 1, 1]|0|
|126570|817878|MU.raw.L128.right.root.1.1.raw.2|[42, 46, 22]|[1, 1, -1]|0|
|126571|817878|MU.raw.L128.right.root.1.1.raw.3|[44, 46, 22]|[-1, 1, -1]|0|
|126572|817878|MU.raw.L128.right.root.1.2.raw.0|[34, 46, 28]|[1, 1, 1]|0|
|126573|817878|MU.raw.L128.right.root.1.2.raw.1|[36, 46, 28]|[-1, 1, 1]|0|
|126574|817878|MU.raw.L128.right.root.1.2.raw.2|[34, 46, 30]|[1, 1, -1]|0|
|126575|817878|MU.raw.L128.right.root.1.2.raw.3|[36, 46, 30]|[-1, 1, -1]|0|
|126576|817878|MU.raw.L128.right.root.1.3.raw.0|[42, 46, 28]|[1, 1, 1]|0|
|126577|817878|MU.raw.L128.right.root.1.3.raw.1|[44, 46, 28]|[-1, 1, 1]|0|
|126578|817878|MU.raw.L128.right.root.1.3.raw.2|[42, 46, 30]|[1, 1, -1]|0|
|126579|817878|MU.raw.L128.right.root.1.3.raw.3|[44, 46, 30]|[-1, 1, -1]|0|
|126580|817878|MU.raw.L128.right.root.2.0.raw.0|[14, 46, 40]|[1, 1, 1]|0|
|126581|817878|MU.raw.L128.right.root.2.0.raw.1|[16, 46, 40]|[-1, 1, 1]|0|
|126582|817878|MU.raw.L128.right.root.2.0.raw.2|[14, 46, 42]|[1, 1, -1]|0|
|126583|817878|MU.raw.L128.right.root.2.0.raw.3|[16, 46, 42]|[-1, 1, -1]|0|
|126584|817878|MU.raw.L128.right.root.2.1.raw.0|[22, 46, 40]|[1, 1, 1]|0|
|126585|817878|MU.raw.L128.right.root.2.1.raw.1|[24, 46, 40]|[-1, 1, 1]|0|
|126586|817878|MU.raw.L128.right.root.2.1.raw.2|[22, 46, 42]|[1, 1, -1]|0|
|126587|817878|MU.raw.L128.right.root.2.1.raw.3|[24, 46, 42]|[-1, 1, -1]|0|
|126588|817878|MU.raw.L128.right.root.2.2.raw.0|[14, 46, 48]|[1, 1, 1]|0|
|126589|817878|MU.raw.L128.right.root.2.2.raw.1|[16, 46, 48]|[-1, 1, 1]|0|
|126590|817878|MU.raw.L128.right.root.2.2.raw.2|[14, 46, 50]|[1, 1, -1]|0|
|126591|817878|MU.raw.L128.right.root.2.2.raw.3|[16, 46, 50]|[-1, 1, -1]|0|
|126592|817878|MU.raw.L128.right.root.2.3.raw.0|[22, 46, 48]|[1, 1, 1]|0|
|126593|817878|MU.raw.L128.right.root.2.3.raw.1|[24, 46, 48]|[-1, 1, 1]|0|
|126594|817878|MU.raw.L128.right.root.2.3.raw.2|[22, 46, 50]|[1, 1, -1]|0|
|126595|817878|MU.raw.L128.right.root.2.3.raw.3|[24, 46, 50]|[-1, 1, -1]|0|
|126596|817878|MU.raw.L128.right.root.3.0.raw.0|[34, 46, 40]|[1, 1, 1]|0|
|126597|817878|MU.raw.L128.right.root.3.0.raw.1|[36, 46, 40]|[-1, 1, 1]|0|
|126598|817878|MU.raw.L128.right.root.3.0.raw.2|[34, 46, 42]|[1, 1, -1]|0|
|126599|817878|MU.raw.L128.right.root.3.0.raw.3|[36, 46, 42]|[-1, 1, -1]|0|
|126600|817878|MU.raw.L128.right.root.3.1.raw.0|[42, 46, 40]|[1, 1, 1]|0|
|126601|817878|MU.raw.L128.right.root.3.1.raw.1|[44, 46, 40]|[-1, 1, 1]|0|
|126602|817878|MU.raw.L128.right.root.3.1.raw.2|[42, 46, 42]|[1, 1, -1]|0|
|126603|817878|MU.raw.L128.right.root.3.1.raw.3|[44, 46, 42]|[-1, 1, -1]|0|
|126604|817878|MU.raw.L128.right.root.3.2.raw.0|[34, 46, 48]|[1, 1, 1]|0|
|126605|817878|MU.raw.L128.right.root.3.2.raw.1|[36, 46, 48]|[-1, 1, 1]|0|
|126606|817878|MU.raw.L128.right.root.3.2.raw.2|[34, 46, 50]|[1, 1, -1]|0|
|126607|817878|MU.raw.L128.right.root.3.2.raw.3|[36, 46, 50]|[-1, 1, -1]|0|
|126608|817878|MU.raw.L128.right.root.3.3.raw.0|[42, 46, 48]|[1, 1, 1]|0|
|126609|817878|MU.raw.L128.right.root.3.3.raw.1|[44, 46, 48]|[-1, 1, 1]|0|
|126610|817878|MU.raw.L128.right.root.3.3.raw.2|[42, 46, 50]|[1, 1, -1]|0|
|126611|817878|MU.raw.L128.right.root.3.3.raw.3|[44, 46, 50]|[-1, 1, -1]|0|
|126612|817880|MU.raw.L128.left.root.0.turn.0|[47, 53, 53]|[1, -1, 1]|0|
|126613|817880|MU.raw.L128.left.root.0.turn.1|[57, 53, 53]|[-1, -1, 1]|0|
|126614|817880|MU.raw.L128.left.root.0.turn.2|[47, 53, 63]|[1, -1, -1]|0|
|126615|817880|MU.raw.L128.left.root.0.turn.3|[57, 53, 63]|[-1, -1, -1]|0|
|126617|817880|MU.raw.L128.left.root.1.turn.0|[0, 53, 53]|[1, -1, 1]|0|
|126618|817880|MU.raw.L128.left.root.1.turn.1|[10, 53, 53]|[-1, -1, 1]|0|
|126619|817880|MU.raw.L128.left.root.1.turn.2|[0, 53, 63]|[1, -1, -1]|0|
|126620|817880|MU.raw.L128.left.root.1.turn.3|[10, 53, 63]|[-1, -1, -1]|0|
|126622|817880|MU.raw.L128.left.root.2.turn.0|[47, 53, 6]|[1, -1, 1]|0|
|126623|817880|MU.raw.L128.left.root.2.turn.1|[57, 53, 6]|[-1, -1, 1]|0|
|126624|817880|MU.raw.L128.left.root.2.turn.2|[47, 53, 16]|[1, -1, -1]|0|
|126625|817880|MU.raw.L128.left.root.2.turn.3|[57, 53, 16]|[-1, -1, -1]|0|
|126627|817880|MU.raw.L128.left.root.3.turn.0|[0, 53, 6]|[1, -1, 1]|0|
|126628|817880|MU.raw.L128.left.root.3.turn.1|[10, 53, 6]|[-1, -1, 1]|0|
|126629|817880|MU.raw.L128.left.root.3.turn.2|[0, 53, 16]|[1, -1, -1]|0|
|126630|817880|MU.raw.L128.left.root.3.turn.3|[10, 53, 16]|[-1, -1, -1]|0|
|126632|817880|MU.raw.L128.right.root.0.turn.0|[14, 48, 20]|[1, 1, 1]|0|
|126633|817880|MU.raw.L128.right.root.0.turn.1|[24, 48, 20]|[-1, 1, 1]|0|
|126634|817880|MU.raw.L128.right.root.0.turn.2|[14, 48, 30]|[1, 1, -1]|0|
|126635|817880|MU.raw.L128.right.root.0.turn.3|[24, 48, 30]|[-1, 1, -1]|0|
|126637|817880|MU.raw.L128.right.root.1.turn.0|[34, 48, 20]|[1, 1, 1]|0|
|126638|817880|MU.raw.L128.right.root.1.turn.1|[44, 48, 20]|[-1, 1, 1]|0|
|126639|817880|MU.raw.L128.right.root.1.turn.2|[34, 48, 30]|[1, 1, -1]|0|
|126640|817880|MU.raw.L128.right.root.1.turn.3|[44, 48, 30]|[-1, 1, -1]|0|
|126642|817880|MU.raw.L128.right.root.2.turn.0|[14, 48, 40]|[1, 1, 1]|0|
|126643|817880|MU.raw.L128.right.root.2.turn.1|[24, 48, 40]|[-1, 1, 1]|0|
|126644|817880|MU.raw.L128.right.root.2.turn.2|[14, 48, 50]|[1, 1, -1]|0|
|126645|817880|MU.raw.L128.right.root.2.turn.3|[24, 48, 50]|[-1, 1, -1]|0|
|126647|817880|MU.raw.L128.right.root.3.turn.0|[34, 48, 40]|[1, 1, 1]|0|
|126648|817880|MU.raw.L128.right.root.3.turn.1|[44, 48, 40]|[-1, 1, 1]|0|
|126649|817880|MU.raw.L128.right.root.3.turn.2|[34, 48, 50]|[1, 1, -1]|0|
|126650|817880|MU.raw.L128.right.root.3.turn.3|[44, 48, 50]|[-1, 1, -1]|0|
|126616|817886|MU.raw.L128.left.root.turn.0|[51, 47, 57]|[1, -1, 1]|0|
|126621|817886|MU.raw.L128.left.root.turn.1|[6, 47, 57]|[-1, -1, 1]|0|
|126626|817886|MU.raw.L128.left.root.turn.2|[51, 47, 12]|[1, -1, -1]|0|
|126631|817886|MU.raw.L128.left.root.turn.3|[6, 47, 12]|[-1, -1, -1]|0|
|126636|817886|MU.raw.L128.right.root.turn.0|[18, 54, 24]|[1, 1, 1]|0|
|126641|817886|MU.raw.L128.right.root.turn.1|[40, 54, 24]|[-1, 1, 1]|0|
|126646|817886|MU.raw.L128.right.root.turn.2|[18, 54, 46]|[1, 1, -1]|0|
|126651|817886|MU.raw.L128.right.root.turn.3|[40, 54, 46]|[-1, 1, -1]|0|
|126652|817898|MU.raw.L128.left.root.turnY|[61, 35, 1]|[1, -1, 0]|0|
|126654|817898|MU.raw.L128.right.root.turnY|[30, 66, 35]|[-1, 1, 0]|0|
|126653|817915|MU.raw.L128.left.root.turnX|[13, 16, 0]|[-1, 1, 1]|0|
|126655|817915|MU.raw.L128.right.root.turnX|[11, 18, 36]|[1, -1, -1]|0|
|126656|817932|MU.raw.L128.remote_root.constant_exit_X_minusY_minusZ|[11, 18, 19]|[1, -1, -1]|0|
|126657|817932|MU.selector.query|[15, 15, 12]|[0, 0, 1]|5|
|126658|817932|MU.selector.support.plus|[13, 16, 13]|[1, 0, 1]|0|
|126659|817932|MU.selector.support.minus|[17, 19, 15]|[-1, -1, 0]|0|
