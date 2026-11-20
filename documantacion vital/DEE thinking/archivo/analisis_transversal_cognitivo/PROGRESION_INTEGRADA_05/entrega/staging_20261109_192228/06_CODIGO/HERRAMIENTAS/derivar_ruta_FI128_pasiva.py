"""Static FI128 geometry + exact recorded176-event contract; never import DEE."""
from pathlib import Path
import ast,collections,datetime,hashlib,json,runpy,struct
P5=Path(__file__).resolve().parents[1];P4=P5.parent/'PROGRESION_INTEGRADA_04';R=P5.parents[2];C=R/'DEE Cognitive 2.0';S4=P4/'estados/candidato_R02/sistema'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def primary(p):
    d=read(p);return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def geometry_from_text(path):
    nodes=[]
    for n in ast.parse(path.read_text(encoding='utf-8-sig')).body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in('N','E','S','FACTORS','VERSION')for t in n.targets):nodes.append(n)
        if isinstance(n,ast.FunctionDef)and n.name=='geometry':nodes.append(n)
    scope={};exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),scope)
    return scope['geometry'](128)
def main():
    out=P5/'fuentes/F1_RUTA_FI128_Y_CAPTURA_GLOBAL_PRE_NATIVE.md'
    if out.exists():raise FileExistsError('Preserve first targeted note')
    percept=S4/'capacidades/percepcion_cruda_fi01.py';g=geometry_from_text(percept)
    source=P4/'ensayos/PI04_MAIN_PANEL12_OP2_FIplus.json';d=primary(source);trial=d['result']['rows'][0]['original_result']['native_trial'];root=trial['input_tick']-g['raw_relative_tick']
    pg=runpy.run_path(str(P4/'codigo/contrastar_finales_E3_pasivo.py'),run_name='pure_PI05_prefix_parser');parse=pg['parse']
    before_doc=primary(P4/'ensayos/PI04_MAIN_PANEL12_OP2_alfa.json');cut=before_doc['committed_snapshot'];before=parse(S4/cut['snapshot'],cut['snapshot_sha256'])
    channels={}
    for name,hexspec in before[3]:
        x,y,z,state,dx,dy,dz,semantic,experience,probe=struct.unpack('<iiiIiiiBBB',bytes.fromhex(hexspec));channels[name]={'site':[x,y,z],'state':state,'direction':[dx,dy,dz],'semantic':semantic,'experience':bool(experience),'probe':bool(probe)}
    declared={q['id']:q for q in g['raw_sources']+g['generic_sources']}
    for request in trial['requests']:
        name=request['port'];channel=channels[name]
        if name.startswith('MU.raw.L128.'):
            item=declared[name.removeprefix('MU.raw.L128.')]
            if channel['site']!=item['site']or channel['direction']!=item['direction']or request['tick']!=root+item['injection_tick_relative']:raise ValueError('Recorded physical source differs from exact geometry')
        if request['receipt']['status']!='applied':raise ValueError('Original admission was not complete')
    if len(trial['requests'])!=176 or len(g['raw_sources'])!=128 or len(g['generic_sources'])!=45:raise ValueError('Exact FI128 contract expected')
    prefixes={};parsed={}
    for arm,name in(('REAL','PI04_C2C_REAL_RES_R01.json'),('NONE','PI04_C2C_NONE20_R01.json'),('YOKED','PI04_C2C_YOKE20_R01.json')):
        f=P4/'control'/name;v=read(f);cc=v['final']['committed_snapshot'];data=parse(S4/cc['snapshot'],cc['snapshot_sha256']);parsed[arm]=data
        prefixes[arm]={'source':str(f),'source_sha256':sha(f),'snapshot_sha256':cc['snapshot_sha256'],'physical':data[0]['physical'],'interfaces':data[0]['interfaces_count'],'pending':data[0]['pending_count'],'receipts':data[0]['receipts_count'],'causal_prefix_sha256':data[0]['causal_prefix_sha256']}
    comparisons={}
    for arm in('NONE','YOKED'):
        a=parsed['REAL'];b=parsed[arm];different=[]
        for i,(x,y)in enumerate(zip(a[1],b[1])):
            if x!=y:different.append({'site':[i//4489,(i//67)%67,i%67],'REAL':pg['decode'](x),arm:pg['decode'](y)})
        comparisons[arm]={'RAW_differences':different,'clocks_bytes_equal':a[8]==b[8],'interfaces_equal':a[3]==b[3],'pending_equal':a[4]==b[4],'receipt_history_equal':a[5]==b[5]}
    files=[source,P4/'control/CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json',P4/'control/REGRESION_FIPLUS_PROTOCOLO_PRE_REPLICA_R01.json',P4/'control/REGRESION_FIPLUS_REPLICA_CERRADA_R01.json',percept,S4/'capacidades/acciones_nativas_apd04.py',S4/'capacidades/acceso_eci01.py',S4/'capacidades/selector_acrecion_nativo.py',R/'4.5/DEE_thinking_4_5_0/source/src/runtime.cpp',R/'4.5/DEE_thinking_4_5_0/source/include/dee_thinking/runtime.hpp',R/'4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp']
    lines=['# PI05 F1/E3: ruta FI128 y captura global antes de Native','',f'Corte de lectura: {datetime.datetime.now().astimezone().isoformat()}. Lectura dirigida de fuentes y estados congelados; cero ticks nuevos. Esta nota no declara una trayectoria observada entre fotogramas ni identifica un portador por su valor.','',
      '## Alcance y base comprobada','',
      'El prompt PI05 completo de 35FC fue leído. Se reutilizaron la autopsia PI04, la réplica negativa y los contratos de comparación. El dominio de `acciones_nativas_apd04.balance(left,right)` es **0..20 por carga pública** y su códec es `[left,20-right,0,...]`; el límite0..32 corresponde a los componentes materiales de FI128 y NO cambia aquel sesgo20. No se reutiliza el sesgo32 de la resta aritmética.','',
      'El primer desacuerdo funcional que los registros antiguos ya muestran es C en817933:14 en vez de31. No hay fotografías globales de817878..817932 en esas fuentes; por ello el primer encuentro responsable anterior a C todavía no está localizado. La admisión de176 eventos no cubre su transporte.','',
      '## Calendario exacto y convención temporal','',
      '`Runtime::advance` aplica primero los eventos cuyo tick solicitado esT, ejecuta un paso v27 y después incrementa el tick. Por tanto el fotograma de fronteraT es **antes** de la admisión programada enT; el siguienteT+1 incorpora admisión y un paso. `effective_tick=T` acredita la admisión, no una observación independiente después de inyectar y antes de evolucionar. La API pública no expone aquí esa frontera intermedia.','',
      '| Frontera | Hecho documentado o función contractual |','|---:|---|','|817876|Corte completo físico previo; empieza la operación.|','|817878|128 muestras RAW solicitadas/aplicadas;14 y17 son los dos payloads no nulos.|','|817879|Primeros nodos nominales de las ramas; debe observarse, no inferirse su contenido.|','|817880|32 retornos/cambios de dirección genéricos de payload0.|','|817885|Nodos intermedios nominales de ambas ramas.|','|817886|8 recursos genéricos de payload0.|','|817897|Convergencias raíz nominales de ambas ramas.|','|817898|2 girosY genéricos0.|','|817915|2 girosX genéricos0.|','|817932|Salida común genérica0 y consultaMU5 con dos soportes0; q.|','|817933|C=(12,17,18), dato registrado14; positivo histórico31.|','|817935|S=(14,15,16), registrado14; E tiene la consulta5 antes de su interacción.|','|817936|E=(15,15,15), dirección(-1,+1,-1), carga5: signo material-1 en q+4.|','|817938|Lector fijado q+6 también-1.|','|818074|Fin del horizonte, incluidos2N=134 ticks posteriores al último grupo de lecturas.|','',
      'Las dos entradas materiales diferenciadas son:14 en(47,55,53), dirección(+1,-1,+1), cabeza nominal(48,54,54);20-b en(14,46,20), dirección(+1,+1,+1), cabeza nominal(15,47,21). Ambas se programan817878; sus cabezas corresponden817879 en la geometría.','',
      '| Rama | Nodos nominales de la geometría, no linaje medido |','|---|---|','|Izquierda|817879:(48,54,54) →817885:(52,48,58) →817897:(62,36,1)|','|Derecha|817879:(15,47,21) →817885:(19,53,25) →817897:(29,65,35)|','',
      'Los giros a seguir en ambas ramas, incluidos sus ceros, aparecen con sus coordenadas exactas en el anexo176. Un cero material puede crear un encuentro; no es ausencia de entrada.','',
      '## Lectura global y representación sin pérdida','',
      '`runtime.raw_copy()` y `runtime.clock_copy()` son métodosconst que devuelven copias en `runtime.hpp:154–155`. Cada vector tiene300763uint64, shape(67,67,67),2406104bytes; índice `(x*67+y)*67+z`. Dos vectores suman4812208bytes, no9624416(el contador operativo incluye buffers internos adicionales). `observe(Coordinate)` esconst en `runtime.cpp:446`; `receipt(id)` recupera el recibo. Las lecturas se hacen bajo el mismo propietario, con tick antes/después idéntico y sin avance concurrente.','',
      'Captura propuesta acotada a **817876..818074 inclusive**,199fronteras de un único usoFI. Ancla binariauint64LE de RAW+clocks en817876; deltas sin pérdida cada paso, guardando índices y nuevosuint64(incluidoRAW0 y state0/SEM4 no nulo). Anclas completas adicionales en817878/879,880/881,885/886/887,897/898/899,915/916,932..940 y818074; pueden reconstruirse de los deltas y no requieren otro ensayo. Si los clocks evolucionan exactamente+1, se permite codificar esa transformación externa verificada más excepciones; de otro modo conservar los valores completos. Nunca modificar clocksNative.','',
      'Cada frontera conserva tick, hashes de ambos buffers, dimensión, tamaño, max_s_reg global, soporteRAW(no sólostate>0), contador de overflow/genesis/backend y recibos nuevos. Guardar telemetría en archivos externos comprimidos, no en metadatosNative. Reconstruir todos los buffers y verificar cada hash. El flujo bruto199×4812208=957629392bytes no se materializa como duplicados; se comprimen las diferencias y se conserva un par anterior/actual en memoria. Medir coste y memoria bajo el límite512MB sin deshabilitarlo.','',
      'La inspección contempla TODO N67: fases, configuraciones inmóviles, direcciones, semántica y RAW no nulo con state0. F1Y60/Y38/Y16 es sólo un antecedente; no se restringe la búsqueda a esa fila ni se retira la guardaOP3 del principal.','',
      '## Dependencia causal derivada del kernel','',
      'Las reglas ordinarias, XNOR, firma tetraédrica y búsqueda de fuentes leen la vecindadMoore1 y el reloj local. La rama `prov_total>=UMBRAL_FUSION=19665` cuenta vecinos de vecinos, y su DEMUX se aplica en un vecino mediante el segundo pase. Por ello una cota conservadora de dependencia RAW del paso completo es radioChebyshev3 toroidal, no una supuesta velocidad universal1. Si el máximo global de s_reg antes de un paso es≤19663, el incremento de provisión(como máximo1) no alcanza aquella rama y la actualización de ese paso se acota a Moore1. Registrar los máximos y contadores permite precisar la cota observada; no asumir esa exclusión a partir de dos extremos.','',
      'Para el primer desacuerdo de tránsito encontrado, inspeccionarT−1/T/T+1 y la vecindad causal derivada, incluidos aportes de otras regiones. Si el camino nominal no contiene la influencia, continuar con diferencias globales, sin rellenar trayectorias a partir de una carga coincidente.','',
      '## Contrastes mínimos prospectivos','',
      '1. Obtener un prefijo operativo completo y coherente817876. Existe su snapshot físico, pero no debe tratarse como par completo por sí solo. Si no se preservó el par, alcanzarlo en una copia desde816019 con los dos trabajos y los cinco usos originales, y exportar0ticks mediante contrato; no ensamblar snapshot con una SQLite posterior. La candidata de recuperación puede continuar el futuro ya fallido; este prefijo diagnóstico no sustituye su historia.','',
      '2. Ejecutar el mismo FI14/3 con captura, conservando las176 entradas y los lectoresq+4/q+6. Comparar su final con el brazo sin captura ya reproducido desde el mismo prefijo: buffers completos, interfaces, agenda, recibos y estado operativo pertinente, excluyendo sólo identidad/diarios declarados. Si la captura divide `run_until` en pasos, conservar los eventos/calendario exactos y cotejar además el avance sin captura. Una variante compact con la misma granularidad y sin copias globales separa lectura de división temporal si aparece una discrepancia. No retirar la consulta funcional y llamarlo ausencia de observador.','',
      '3. En clones completos del MISMO prefijo,14/2,14/3,14/4 modifican sólo el payload18/17/16 de `MU.raw.L128.right.root.0.0.raw.0` en(14,46,20)817878. Todos los otros175 eventos/calendario permanecen iguales. El dominio es legal y el signo útil es positivo en los tres; la discriminación principal es el conjuntoglobalD(T) de diferenciasRAW/clocks, el primer contacto y su transformación, no únicamente el signo. Mantener todos los rechazos si la evolución cambia la admisión posterior.','',
      '4. Si hace falta, comparar omitir aquella entrada(175eventos) con payload0 material(176eventos; b=20 legal). Ambos difieren de17; no son equivalentes entre sí ni un sham automáticamente equiparable. Consultar ausente o cortar un portador son intervenciones materiales adicionales que requieren motivo y controles propios; no se añaden de rutina.','',
      '5. Antes del contraste de rescate, fijar encuentro/condición sospechosa, predicción, intervención legal y sham, lectores, horizonte y conservación. Ningún atlas/delta o resultado esperado se entrega al ente. Una huella externamente distinguible sólo es capacidad del observador hasta demostrar usoNative.','',
      '## Prefijos REAL/NONE/YOKED T816019: lectura pasiva exacta','',
      'REAL yYOKED tienen RAW/clocks byteidénticos, interfaces y agenda iguales; sus recibos/prefijos causales y ambientes difieren. NONE difiere de REAL en un soloRAW: B=(20,53,5), s_reg153 frente152; clocks e interfaces/agenda coinciden. No se concluye igualdad de mundos completos.','',
      'El contrato YOKED deC2C está agotado tras20slots: `validate` rechaza una continuaciónordinal20 que invente señales futuras. Para repetir los dos trabajos en ese brazo hace falta una extensiónPI05 explícita que preserve el plan/historia20 y declare sus retornos nuevos(por ejemplo los dos retornos reales ya registrados, ambosFalse). No editar calladamente el pasado, ni contar una modificación administrativa de plan como aprendizaje. No se ejecutó tal extensión en esta lectura.','',
      'Datos recalculados de los snapshots(los hashes completos de las fuentes quedan abajo):','```json',json.dumps({'prefixes':prefixes,'REAL_vs_others':comparisons},ensure_ascii=False,indent=2),'```','',
      '## API real disponible para Root','',
      'La petición utilizada y preservada es `Owner.material(ID_NUEVO,{"modo":"eci01-balance","izquierda":14,"derecha":3},feedback="omit")` sobre un propietario aislado ya abierto. El propietario dePI05 elegirá sólo prefijos completos y nuevosID. Para captura, un wrapper que delegueworld/tick y haga los mismos avances con eventos previamente fijados puede leer `a.world.runtime.raw_copy()`, `clock_copy()`, `current_tick`, `last_tick_info` y `receipt(id)`; debe contrastarse con la continuación sin captura. No usar `diagnostic_fork`, ediciones, `--nueva` ni save deCognitiveSession como supuesta lectura pasiva: ese save actualiza metadatos operativos.','',
      '## Fuentes leídas/cotejadas en este bloque','',
      'Lectura completa del promptPI05; lectura dirigida del código geométrico, comparación, calendario/lector, Runtime y reglas v27; recálculo pasivo de176recibos y de tres snapshotsT816019. No se declaran releídos íntegramente los manuales ni todos los expedientes. No se ejecutó Native, no se escribió el producto ni se incorporó una solución.','',
      '| Fuente | Bytes | SHA-256 actual |','|---|---:|---|']
    for f in files:
        if f.exists():lines.append('|'+str(f.resolve())+'|'+str(f.stat().st_size)+'|'+sha(f)+'|')
        else:lines.append('|'+str(f.resolve())+'|NO ACCESIBLE EN ESTA RUTA|—|')
    lines.extend(['','## Anexo:176 eventos exactos solicitados y aplicados','',
      'Coordenadas/dirección de la interfaz congelada anterior; tick y payload del primario. Las cabezas/nodos descritos arriba son derivados de la geometría, no de seguir una identidad por s_reg.','',
      '| ID Native | Tick solicitado/aplicado | Canal | Sitio | Dirección | Payload |','|---:|---:|---|---|---|---:|'])
    for q in sorted(trial['requests'],key=lambda x:(x['tick'],x['id'])):
        ch=channels[q['port']];lines.append('|'+str(q['id'])+'|'+str(q['tick'])+'|'+q['port']+'|'+str(ch['site'])+'|'+str(ch['direction'])+'|'+str(q['payload'])+'|')
    out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'note':str(out.resolve()),'bytes':out.stat().st_size,'sha256':sha(out),'events':len(trial['requests']),'Native_ticks':0,'product_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
