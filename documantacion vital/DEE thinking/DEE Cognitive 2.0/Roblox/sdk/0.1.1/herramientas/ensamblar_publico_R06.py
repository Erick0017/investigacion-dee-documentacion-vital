"""Reproducible PUBLIC candidate assembler. Stdlib only; never imports Native."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,re,stat,sys,zipfile,xml.etree.ElementTree as E
SCHEMA='DEE.SDK.PublicCandidate.R06.01'
MANIFEST='MANIFIESTO.json'
MAX_ZIP=15000000
MAX_RAW=30000000
CORE_MODULES={'Main':'conector/Main_R06.luau','BackendBinding':'conector/BackendBinding.luau',
 'SDKConfig':'configuracion/SDKConfig.luau','MapaEjemplo':'ejemplos/MapaEjemplo.luau',
 'SDKBootstrap':'conector/SDKBootstrap.luau','HttpTransport':'conector/HttpTransport.luau',
 'HttpLoop':'conector/HttpLoop.luau','LiveAdapters_R06':'conector/LiveAdapters_R06.luau',
 'MotorPathfinding_R06':'conector/MotorPathfinding_R06.luau','StateCodec_R06':'conector/StateCodec_R06.luau',
 'PersistenceChecks_R06':'conector/PersistenceChecks_R06.luau','Evidence_R06':'conector/Evidence_R06.luau',
 'SDK_Arranque':'ejemplos/SDK_Arranque.server.luau'}
EXT_MODULES={'Config_EXT_R06':'configuracion/Config_EXT_R06.luau',
 'CapabilitiesClient_EXT_R06':'conector/CapabilitiesClient_EXT_R06.luau',
 'VistaES_EXT_R06':'conector/VistaES_EXT_R06.luau','API_EXT_R06':'conector/API_EXT_R06.luau',
 'Arranque_EXT_R06':'ejemplos/Arranque_EXT_R06.server.luau'}
CORE_EXTRA=['conector/DEEConnector_SDK_0_1_1.rbxmx','ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx','guias/CONTRATO_K4_R06.json']
EXT_EXTRA=['configuracion/CONFIG_EXT_R06.json','conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx',
 'ejemplos/DEE_SDK_CAPACIDADES_EXT_R06.rbxlx','guias/CONTRATO_EXT_R06_02.json',
 'guias/LEER_EXT_R06.md','guias/API_DESARROLLADOR_ES.md','guias/RUTAS_WINDOWS_PREFLIGHT.md',
 'pruebas/preflight_rutas_EXT_R06.py']
DENIED_SEGMENTS={'runtime_privado_local','configuracion_privada','estado_demo','estados','snapshots','.git','__pycache__'}
DENIED_LEAVES={'sdk_pair.json','vida.json','conexion_privada.json'}
DENIED_EXT={'.pyd','.dll','.exe','.whl','.sqlite3','.db','.png','.mp4','.mkv','.zip'}
STATUSES={'VERIFIED','PARTIAL','PENDING','BLOCKED','FAILED','NOT_RUN'}
PRIOR_DOCS={'guias/CRITERIOS_PILOTO.md':'fd542680d11ee194c1b68f07846b4a7ccd20c53adbe5a4b50677ff532112e72b','guias/FICHA_VALIDACION_EXTERNA.md':'6296e772382250c6294624403255b3a322d92ed5d3478766351673f9d401e3f6'}
GENERATED={'ESTADO_VERIFICACION.json','VERSION.txt','LEER_PRIMERO.md','GUIAS/INICIO_Y_REQUISITOS.md','GUIAS/EXCLUSIONES_Y_REPRODUCCION.md','herramientas/ensamblar_publico_R06.py','FUENTES_PUBLICAS.json','METADATOS/PINES_CORE_ORIGINALES.json','METADATOS/PINES_EXT_ORIGINALES.json','KIT_DESARROLLADOR/configuracion/CONFIGURACION_PUBLICA.json'}
PUBLIC_MEMBERS={*('KIT_DESARROLLADOR/'+x for x in list(CORE_MODULES.values())+CORE_EXTRA+list(PRIOR_DOCS)),*('KIT_EXTENSION/'+x for x in list(EXT_MODULES.values())+EXT_EXTRA),*GENERATED}

def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(data):return hashlib.sha256(data).hexdigest()
def read_json(path):return json.loads(Path(path).read_text('utf-8-sig'))
def safe_name(name):
    if not isinstance(name,str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('UNSAFE_MEMBER_NAME')
    if any(x in ('','..','.') or x.endswith((' ','.')) or re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',x) for x in name.split('/')):
        raise ValueError('UNSAFE_RAW_MEMBER_SEGMENT')
    p=PurePosixPath(name)
    if p.is_absolute() or any(x in ('..','.') for x in p.parts):raise ValueError('UNSAFE_MEMBER_PATH')
    if any(x.casefold() in DENIED_SEGMENTS for x in p.parts) or p.name.casefold() in DENIED_LEAVES:
        raise ValueError('PRIVATE_MEMBER_EXCLUDED')
    if p.suffix.lower() in DENIED_EXT or p.name.upper().startswith('INYECCION_'):
        raise ValueError('NONPUBLIC_FILE_EXCLUDED')
    return p

def no_links(path):
    for p in (path,*path.parents):
        if p.exists() and (p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&1024):
            raise ValueError('SYMLINK_OR_REPARSE_PATH_REJECTED')

def privacy(data,name):
    s=data.decode('utf-8')
    if re.search(r'(?i)[a-z]:[\\/]+(?:users|genesis\b)|/(?:Users|home)/[^/\s]+',s):
        raise ValueError('PERSONAL_PATH_IN_PUBLIC_FILE:'+name)
    if re.search(r'(?i)Bearer\s+[A-Za-z0-9_.-]{24,}|(?:token|api_key|password|secret)\s*=\s*["\x27][A-Za-z0-9_.-]{24,}',s):
        raise ValueError('LITERAL_CREDENTIAL_IN_PUBLIC_FILE:'+name)
    if name.endswith('.json'):
        obj=json.loads(s)
        def walk(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if str(k).casefold() in {'token','cookie','authorization','secret','password','api_key','apikey'} and isinstance(x,str) and x:
                        raise ValueError('PRIVATE_JSON_FIELD:'+name)
                    walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(obj)
    if name.endswith(('.rbxlx','.rbxmx')):
        root=E.fromstring(data)
        for item in root.iter('Item'):
            if item.get('class')=='StringValue':
                props=item.find('Properties')
                if props is not None:
                    n=props.find("string[@name='Name']");value=props.find("string[@name='Value']")
                    if n is not None and n.text in ('Token','BaseUrl','InstanceId') and value is not None and value.text:
                        raise ValueError('PRIVATE_CONNECTION_XML_EXCLUDED:'+name)

def public_record(value):
    keys={'schema','sdkVersion','status','rootApproved','verifiedUtc','checks','limits','externalEvaluation',
          'distributionMode','nativeRuntimeIncluded','remoteEndpointOffered'}
    if set(value)!=keys or value['schema']!='DEE.SDK.PublicVerification.R06.01' or value['sdkVersion']!='0.1.1':
        raise ValueError('EXACT_PUBLIC_VERIFICATION_SCHEMA_REQUIRED')
    if value['status'] not in ('CANDIDATE_PENDING_ROOT','ROOT_RECORDED') or type(value['rootApproved']) is not bool:
        raise ValueError('EXPLICIT_ROOT_RECORD_STATUS')
    if value['verifiedUtc'] is not None and not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z',value['verifiedUtc']):
        raise ValueError('UTC_OR_NULL_REQUIRED')
    if (value['externalEvaluation']!='PENDING' or value['distributionMode']!='LOCAL_ACCOMPANIED_AUTHORIZED_BACKEND'
            or value['nativeRuntimeIncluded'] is not False or value['remoteEndpointOffered'] is not False):
        raise ValueError('LOCAL_ACCOMPANIED_NO_PRIVATE_RUNTIME_OR_REMOTE_ENDPOINT')
    if set(value['checks'])!={'K1','K2','K3','K4','K5','EXT'}:raise ValueError('ALL_SIX_PUBLIC_RESULTS_REQUIRED')
    for key,row in value['checks'].items():
        if (set(row)!={'status','summary','evidenceSha256'} or row['status'] not in STATUSES
                or not isinstance(row['summary'],str) or not 1<=len(row['summary'])<=1500
                or not isinstance(row['evidenceSha256'],list) or len(row['evidenceSha256'])>32
                or any(not isinstance(x,str) or re.fullmatch(r'[0-9a-f]{64}',x) is None for x in row['evidenceSha256'])):
            raise ValueError('EXACT_PUBLIC_CHECK:'+key)
    if (not isinstance(value['limits'],list) or len(value['limits'])>24
            or any(not isinstance(x,str) or not 1<=len(x)<=1500 for x in value['limits'])):
        raise ValueError('BOUNDED_PUBLIC_LIMITS')
    privacy((canonical(value)+'\n').encode(),'ESTADO_VERIFICACION.json')
    return value

def scripts(data):
    found={}
    root=E.fromstring(data)
    for item in root.iter('Item'):
        props=item.find('Properties')
        if props is None:continue
        name=props.find("string[@name='Name']");source=props.find("ProtectedString[@name='Source']")
        if name is not None and source is not None:
            if name.text in found:raise ValueError('DUPLICATE_SCRIPT_NAME')
            found[name.text]=(item.get('class'),source.text or '')
    return found

def config(source):
    m=re.search(r'\[=\[(.*?)\]=\]',source,re.S)
    if not m:raise ValueError('CONFIG_JSON_ENVELOPE')
    return json.loads(m.group(1))

def defaults(files):
    core=json.loads(files['KIT_DESARROLLADOR/configuracion/CONFIGURACION_PUBLICA.json'])
    if (core['Version']!='0.1.1' or core['Mode']!='PREVIEW' or core['AutoEndStudioTest'] is not False
            or (core['MaxOpportunities'],core['MaxActions'],core['RunCycles'])!=(3,6,1)):
        raise ValueError('SAFE_CORE_MAX3_PREVIEW_REQUIRED')
    if config(files['KIT_DESARROLLADOR/configuracion/SDKConfig.luau'].decode())!=core:
        raise ValueError('PUBLIC_CORE_CONFIG_MUST_MATCH_FROZEN_LUA')
    ext=json.loads(files['KIT_EXTENSION/configuracion/CONFIG_EXT_R06.json'])
    if ext['Enabled'] is not False or ext['NoAutomaticMaterial'] is not True:
        raise ValueError('EXT_DISABLED_NO_AUTOMATIC_MATERIAL_REQUIRED')
    if config(files['KIT_EXTENSION/configuracion/Config_EXT_R06.luau'].decode())!=ext:
        raise ValueError('PUBLIC_EXT_CONFIG_MISMATCH')
    for prefix,mapping,pkg,scene in [
        ('KIT_DESARROLLADOR',CORE_MODULES,'conector/DEEConnector_SDK_0_1_1.rbxmx','ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx'),
        ('KIT_EXTENSION',EXT_MODULES,'conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx','ejemplos/DEE_SDK_CAPACIDADES_EXT_R06.rbxlx')]:
        a=scripts(files[prefix+'/'+pkg]);b=scripts(files[prefix+'/'+scene])
        if a!=b or set(a)!=set(mapping):raise ValueError('SCENE_PACKAGE_MODULE_NAMES_OR_SOURCES_CHANGED')
        for name,relative in mapping.items():
            if a[name][1]!=files[prefix+'/'+relative].decode():raise ValueError('FROZEN_EMBEDDED_SOURCE_CHANGED:'+name)
        for rel in (pkg,scene):
            root=E.fromstring(files[prefix+'/'+rel])
            for item in root.iter('Item'):
                if item.get('class')=='HttpService':
                    p=item.find('Properties')
                    if p is not None and any(x.get('name')=='HttpEnabled' and x.text=='true' for x in p):
                        raise ValueError('PUBLIC_HTTP_NOT_ENABLED_BY_DEFAULT')

def collect(kit,pinfile,paths,prefix):
    kit=Path(kit).resolve(strict=True);no_links(kit);no_links(Path(pinfile).resolve(strict=True))
    pins=read_json(pinfile)['files'];out={}
    for relative in paths:
        safe_name(relative);p=kit.joinpath(*PurePosixPath(relative).parts);no_links(p)
        if not p.is_file() or not p.resolve().is_relative_to(kit):raise ValueError('PINNED_REGULAR_FILE_REQUIRED')
        data=p.read_bytes();pin=pins[relative]
        if len(data)!=pin['bytes'] or digest(data)!=pin['sha256']:raise ValueError('FROZEN_SOURCE_PIN_MISMATCH:'+relative)
        out[prefix+'/'+relative]=data
    return out

def guides(record):
    rows='\n'.join('| '+k+' | '+record['checks'][k]['status']+' | '+record['checks'][k]['summary'].replace('|','/').replace('\n',' ')+' |' for k in ('K1','K2','K3','K4','K5','EXT'))
    readme='# DEE Roblox SDK 0.1.1 · candidato público\n\nDos componentes separados: KIT_DESARROLLADOR (CoreMax3) y KIT_EXTENSION (capacidades asistidas). No incluye el cerebro/runtime privado, credenciales ni estados Native.\n\nEl paquete se entrega como candidato. El registro final aportado por Root está en ESTADO_VERIFICACION.json; el ensamblador no deduce éxito material desde hashes o fixtures. Aprobación pública declarada por Root: '+('sí' if record['rootApproved'] else 'pendiente')+'.\n\n| Criterio | Estado declarado | Alcance |\n|---|---|---|\n'+rows+'\n\nLos criterios originales previos se conservan en KIT_DESARROLLADOR/guias/CRITERIOS_PILOTO.md (su encabezado histórico no es el estado actual). La ficha externa sigue pendiente. Lea GUIAS/INICIO_Y_REQUISITOS.md. Modalidad inicial: piloto local acompañado en este PC, con backend privado autorizado por su propietario. No hay runtime entregado ni endpoint remoto ofrecido. La evaluación externa sigue PENDIENTE; nadie fue contactado por este ensamblador.\n\nVerificación portable sin Native:\n\n    python herramientas/ensamblar_publico_R06.py verify --root .\n\nEste comando comprueba integridad, fuentes y defaults; no reproduce Native, Roblox, aprendizaje ni K1–K5. No ejecute experiencias antiguas para verificar el ZIP.\n'
    start='# Inicio y requisitos\n\n## Core\n\nAbra KIT_DESARROLLADOR/ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx, o importe KIT_DESARROLLADOR/conector/DEEConnector_SDK_0_1_1.rbxmx en ServerScriptService. Use una entrada, no ambas. Los nombres y Sources son los congelados. Mode=PREVIEW construye el aparato/NPC y no abre Native; no satisface K2/K3.\n\nPara Native, el propietario debe proporcionar una vida diagnóstica completa, lease vigente, servicio privado local y autorización real. El propietario configura HTTP del Place local y la conexión en ServerStorage; Token nunca en Source, chat, guía o archivo público. No se tocan ajustes globales ni se eluden denegaciones. Si falta el backend, se informa el bloqueo: no hay FakeNative fallback.\n\nCore conserva MaxOpportunities3/MaxActions6/RunCycles1; un cierre y una continuación son explícitos, nunca una renovación infinita. El contratoK4 previo está en KIT_DESARROLLADOR/guias/CONTRATO_K4_R06.json. Su texto fija criterios, no sustituye el resultado Root actual. Tras un cambio de geometría/sensores/bindings se necesita validación propia; no cambie lector/bancos para adaptar el mapa.\n\n## EXT\n\nImporte KIT_EXTENSION/conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx en una escena aparte o abra su ejemplo. Enabled=false y NoAutomaticMaterial=true. La consola es ilustración hasta que el propietario autorice/configure el servicio separado y habilite su copia privada. Primero GetCapabilitiesRO; SubmitCapability es MATERIAL, explícito, iniciado por el desarrollador. Native devuelve el valor literal; 0 es válido y NULL no se rellena. El cliente registra ID antes de unPOST y sólo consulta el mismoID.\n\nEXT no dirige ni coordina el avatar. Sus capacidades asistidas no prueban elección autónoma de herramienta. Después de avance Native, la pareja SDK anterior es PRE_CAP y no representa un World actual: una escena de archivo debe rotularse como preparación. No reactive el loopCore sobre esa pareja sin un protocolo autorizado nuevo.\n\n## Backend y Windows\n\nEl acceso inicial es local acompañado; ni el runtime privado ni un endpoint remoto se distribuyen aquí. El propietario decide futuras modalidades/accesos. No se inventa licencia ni promesa de instalación en3min o respuesta inmediata. Use un runtime autorizado en raíz corta, por ejemplo C:\\DEE_SDK: localizar el PYD con find_spec NO demuestra cargaDLL. El preflightFS inspecciona rutas y tampoco acredita carga material; el propietario debe verificar el cargador real antes de preparar una identidad. Nunca mueva una vida activa o recopie sólo RAW/relojes.\n\nLas esperas son finitas, aceptan PENDING_RESOURCE y preservan IDs. Ante incertidumbre, no rePOSTee ni cree otroID para obtener otra respuesta. Mantenga un solo escritor Native. No publique escenas privadas, tokens o estados. Consulte KIT_EXTENSION/guias/API_DESARROLLADOR_ES.md para las seis solicitudes y lectura íntegra por bloques.\n'
    exclude='# Contenido excluido\n\nSelección por allowlist de fuentes públicas congeladas, no copia recursiva del producto. Se excluyen RUNTIME_PRIVADO_LOCAL, configuraciones/conexiones privadas, escenas inyectadas, snapshots, SDK_PAIR, VIDA, ledgers, diarios/outboxes/colas, SQLite, DLL/PYD/WHL/EXE, imágenes y vídeo. No se incluyen el Manual global, kernel o fuentes privadas.\n\nMANIFIESTO.json lista bytes/SHA256 de todos los miembros salvo él mismo: no tiene autorreferencia. El ZIP usa miembros ordenados, timestamps/permisos fijos y Deflate; la igualdad binaria se espera con los mismos inputs/interprete/zlib. La verificación limpia no abre Native, Studio, modelo, HTTP o SQLite. Fuentes locales y hashes no son un respaldo ejecutable del estado cognitivo.\n'
    return {'LEER_PRIMERO.md':readme.encode(),'GUIAS/INICIO_Y_REQUISITOS.md':start.encode(),'GUIAS/EXCLUSIONES_Y_REPRODUCCION.md':exclude.encode()}

def assemble(core_kit,core_pins,ext_kit,ext_pins,verification,output):
    output=Path(output).absolute()
    if output.exists():raise FileExistsError('FRESH_CANDIDATE_DESTINATION_REQUIRED')
    no_links(output.parent)
    for source in (Path(core_kit).resolve(strict=True),Path(ext_kit).resolve(strict=True)):
        if output.is_relative_to(source) or source.is_relative_to(output):raise ValueError('OUTPUT_CANNOT_OVERLAP_SOURCES')
    record=public_record(read_json(verification))
    files=collect(core_kit,core_pins,list(CORE_MODULES.values())+CORE_EXTRA,'KIT_DESARROLLADOR')
    files.update(collect(ext_kit,ext_pins,list(EXT_MODULES.values())+EXT_EXTRA,'KIT_EXTENSION'))
    for name,pin in PRIOR_DOCS.items():
        p=Path(core_kit).joinpath(*PurePosixPath(name).parts);no_links(p);data=p.read_bytes()
        if digest(data)!=pin:raise ValueError('PREVIOUSLY_FIXED_CRITERIA_OR_EXTERNAL_FORM_CHANGED')
        files['KIT_DESARROLLADOR/'+name]=data
    files['METADATOS/PINES_CORE_ORIGINALES.json']=Path(core_pins).read_bytes()
    files['METADATOS/PINES_EXT_ORIGINALES.json']=Path(ext_pins).read_bytes()
    cfg=config(files['KIT_DESARROLLADOR/configuracion/SDKConfig.luau'].decode())
    files['KIT_DESARROLLADOR/configuracion/CONFIGURACION_PUBLICA.json']=(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n').encode()
    files['ESTADO_VERIFICACION.json']=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode()
    files['VERSION.txt']=b'0.1.1\nCANDIDATO_PUBLICO_R06\n'
    files.update(guides(record))
    files['herramientas/ensamblar_publico_R06.py']=Path(__file__).read_bytes()
    provenance={'schema':SCHEMA,'corePinsSha256':digest(Path(core_pins).read_bytes()),
        'extensionPinsSha256':digest(Path(ext_pins).read_bytes()),'frozenModuleSourcesPreserved':True,
        'distributionMode':'LOCAL_ACCOMPANIED_AUTHORIZED_BACKEND','privateRuntimeIncluded':False,
        'materialClaimByAssembler':False}
    files['FUENTES_PUBLICAS.json']=(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n').encode()
    defaults(files)
    if set(files)!=PUBLIC_MEMBERS:raise ValueError('EXPLICIT_PUBLIC_SELECTION_ONLY')
    for name,data in files.items():safe_name(name);privacy(data,name)
    if sum(map(len,files.values()))>MAX_RAW:raise ValueError('PUBLIC_RAW_LIMIT')
    manifest={'schema':SCHEMA,'members':[{'path':n,'bytes':len(d),'sha256':digest(d)} for n,d in sorted(files.items())],
        'selfExcluded':MANIFEST,'NativeExecutedByAssembler':False,'privateRuntimeIncluded':False,
        'verificationRecordSha256':digest(files['ESTADO_VERIFICACION.json'])}
    output.mkdir(parents=False)
    try:
        for name,data in sorted(files.items()):
            target=output.joinpath(*PurePosixPath(name).parts);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:f.write(data)
        with (output/MANIFEST).open('x',encoding='utf8',newline='\n') as f:json.dump(manifest,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    except BaseException:
        marker=output/'ASSEMBLY_INCOMPLETE.json'
        if not marker.exists():marker.write_text('{"status":"INCOMPLETE_NOT_PUBLIC","NativeExecuted":false}\n',encoding='utf8')
        raise
    return verify(output)

def verify(root):
    root=Path(root).resolve(strict=True);no_links(root)
    manifest=read_json(root/MANIFEST)
    if manifest.get('schema')!=SCHEMA or manifest.get('selfExcluded')!=MANIFEST:raise ValueError('EXACT_MANIFEST_SCHEMA')
    expected={};files={}
    for row in manifest['members']:
        name=row['path'];safe_name(name)
        if name==MANIFEST or name.casefold() in {x.casefold() for x in expected}:raise ValueError('SELF_REFERENCE_OR_DUPLICATE')
        expected[name]=row
    if set(expected)!=PUBLIC_MEMBERS:raise ValueError('EXPLICIT_PUBLIC_MEMBER_ALLOWLIST_REQUIRED')
    actual=set()
    for p in root.rglob('*'):
        no_links(p)
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    if actual!=set(expected)|{MANIFEST}:raise ValueError('EXACT_MEMBER_SET_REQUIRED')
    for name,row in expected.items():
        data=root.joinpath(*PurePosixPath(name).parts).read_bytes()
        if len(data)!=row['bytes'] or digest(data)!=row['sha256']:raise ValueError('MEMBER_HASH_OR_SIZE_MISMATCH:'+name)
        privacy(data,name);files[name]=data
    if digest(files['ESTADO_VERIFICACION.json'])!=manifest['verificationRecordSha256']:raise ValueError('VERIFICATION_RECORD_CHANGED')
    public_record(json.loads(files['ESTADO_VERIFICACION.json']));defaults(files)
    return {'schema':SCHEMA,'integrity':'VERIFIED','members':len(expected)+1,
        'manifestSha256':digest((root/MANIFEST).read_bytes()),'NativeExecutedByVerifier':False,
        'materialVerification':'Only the Root-supplied public record; this check never reproduces Native'}

def archive(root,target):
    root=Path(root).resolve(strict=True);target=Path(target).absolute();verify(root);no_links(target.parent)
    if target.exists() or target.is_relative_to(root):raise FileExistsError('NEW_ZIP_OUTSIDE_CANDIDATE_REQUIRED')
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,strict_timestamps=True) as z:
        for p in sorted(x for x in root.rglob('*') if x.is_file()):
            n=p.relative_to(root).as_posix();safe_name(n)
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    if target.stat().st_size>MAX_ZIP:raise ValueError('ZIP_EXCEEDS15M_PRESERVED_NOT_RELEASED')
    return {'bytes':target.stat().st_size,'sha256':digest(target.read_bytes()),'NativeExecuted':False}

def extract_verify(source,target):
    target=Path(target).absolute()
    if target.exists():raise FileExistsError('FRESH_CLEAN_EXTRACTION_REQUIRED')
    no_links(target.parent)
    with zipfile.ZipFile(source) as z:
        infos=z.infolist();seen=set();total=0
        for info in infos:
            safe_name(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr>>16) or info.filename.casefold() in seen:
                raise ValueError('UNSAFE_ZIP_MEMBER_OR_DUPLICATE')
            seen.add(info.filename.casefold());total+=info.file_size
            if total>MAX_RAW:raise ValueError('ZIP_RAW_LIMIT')
        if MANIFEST.casefold() not in seen:raise ValueError('ZIP_MANIFEST_REQUIRED')
        target.mkdir()
        for info in infos:
            p=target.joinpath(*PurePosixPath(info.filename).parts);p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(z.read(info))
    return verify(target)

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('assemble')
    for name in ('core-kit','core-pins','ext-kit','ext-pins','verification','output'):a.add_argument('--'+name,required=True,type=Path)
    v=s.add_parser('verify');v.add_argument('--root',required=True,type=Path)
    a=s.add_parser('archive');a.add_argument('--root',required=True,type=Path);a.add_argument('--zip',required=True,type=Path)
    e=s.add_parser('extract-verify');e.add_argument('--zip',required=True,type=Path);e.add_argument('--output',required=True,type=Path)
    x=p.parse_args()
    if x.command=='assemble':result=assemble(x.core_kit,x.core_pins,x.ext_kit,x.ext_pins,x.verification,x.output)
    elif x.command=='verify':result=verify(x.root)
    elif x.command=='archive':result=archive(x.root,x.zip)
    else:result=extract_verify(x.zip,x.output)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
