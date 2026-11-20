"""Lanzador de distribución; delega las operaciones al gestor Cognitive existente."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ROOT / 'sistema'
PYTHON = ROOT / 'motor/python313/python.exe'
WHEEL = ROOT / 'motor/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def prepare():
    """Instala sólo el WHL incluido, sin pip, red ni entorno del autor."""
    if sha(WHEEL) != WHEEL_SHA:
        raise RuntimeError('El WHL no corresponde al producto oficial congelado.')
    target = ROOT / 'motor/python313/site-packages'
    marker = target / 'INSTALACION_DEE.json'
    if not marker.exists():
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(WHEEL) as z:
            for item in z.infolist():
                p = Path(item.filename)
                if p.is_absolute() or '..' in p.parts or ':' in item.filename:
                    raise ValueError('Miembro inseguro del WHL')
                z.extract(item, target)
        marker.write_text(json.dumps({'wheel_sha256': WHEEL_SHA, 'method': 'Unmodified official wheel, local extraction; no pip or network'}, indent=2), encoding='utf8')
    for relative in ('estado/checkpoints', 'estado/vidas', 'resultados', 'experiencias', 'temporal'):
        (ROOT / 'trabajo_personal' / relative).mkdir(parents=True, exist_ok=True)
    # El kernel utiliza archivos temporales nativos. No se altera el TEMP global.
    temporary = ROOT / 'trabajo_personal/temporal'
    if str(temporary).isascii():
        os.environ['TEMP'] = os.environ['TMP'] = str(temporary)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'


def call(args, capture=False):
    command = [str(PYTHON), '-I', '-B', '-X', 'utf8', str(SYSTEM / 'gestionar.py'), *map(str, args)]
    if capture:
        p = subprocess.run(command, cwd=PYTHON.parent, text=True, encoding='utf8', capture_output=True)
        if p.returncode:
            message = p.stderr or p.stdout
            if 'DLL load failed' in message or 'MSVCP140' in message:
                message += '\nDependencia nativa: instale manualmente motor/VC_redist.x64.exe (Microsoft firmado) y vuelva a iniciar. No se sustituye el motor ni se crea otra vida.'
            raise RuntimeError(message)
        return json.loads(p.stdout)
    return subprocess.call(command, cwd=PYTHON.parent)


def catalog():
    return json.loads((ROOT / 'entes/CATALOGO.json').read_text(encoding='utf8'))['cuts']


def show_catalog():
    for row in catalog():
        print(f"{row['alias']}: {row['source_life']} T{row['tick']} / {row['profile']}\n  {row['scope']}\n  Límite: {row['limits']}")


def open_copy(alias, life, activate=True):
    row = next((x for x in catalog() if x['alias'] == alias), None)
    if row is None:
        raise ValueError('Alias no incluido. Use INICIAR.bat catalogo.')
    if life in {x['source_life'] for x in catalog()}:
        raise ValueError('Use una identidad nueva, por ejemplo COLAB_E1_01; no el nombre del original.')
    path = ROOT / row['snapshot']
    if sha(path) != row['snapshot_sha256']:
        raise ValueError('Snapshot distribuido alterado')
    print(f"INSTRUMENTO: copia explícita de {row['source_life']} T{row['tick']} -> {life}; no es creación desde T0.")
    # import_state usa el propietario original del perfil, restaura todo el estado
    # y asigna la identidad de la copia mediante metadatos; no edita RAW ni clocks.
    if row.get('persistent_service'):
        bundle_path=(ROOT/row['persistent_service']['bundle']).resolve(strict=True)
        if not bundle_path.is_relative_to(ROOT/'entes/protocolos'):raise ValueError('Paired service bundle outside distributed state')
        bundle=json.loads(bundle_path.read_text(encoding='utf8'))
        if bundle.get('schema')!='DEE.collaboration.deduplicated_service_bundle.v1'or bundle['snapshot_package_member']!=row['snapshot']:raise ValueError('Invalid paired service bundle')
        paired=bundle['paired_export_manifest'];temporary_root=ROOT/'actualizaciones/temporales';temporary_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='paired-import-',dir=temporary_root)as name:
            temporary=Path(name)
            for member in paired['members']:
                relative=Path(member['file'])
                if relative.is_absolute()or'..'in relative.parts or':'in member['file']or'\\'in member['file']:raise ValueError('Unsafe paired member')
                source=path if member['file']=='VIDA.deetsnap.gz'else(ROOT/bundle['assets_prefix']/relative).resolve(strict=True)
                if not source.is_relative_to(ROOT):raise ValueError('Undistributed service dependency')
                if source.stat().st_size!=member['bytes']or sha(source)!=member['sha256']:raise ValueError('Paired operational member hash mismatch')
                target=temporary/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
            (temporary/'EXPORTACION_SERVICIO.json').write_text(json.dumps(paired,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            result=call(['mente-unificada-importar','--paquete',str(temporary),'--vida',life],True)
    else:
        result = call(['importar-estado', str(path), life, '--perfil', row['profile'], '--sha256', row['snapshot_sha256']], True)
    if activate:
        call(['activar', life], True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def current_life():
    p = ROOT / 'trabajo_personal/estado/ACTIVO.json'
    if not p.exists():
        raise ValueError('No hay vida personal activa. Abra primero una copia con INICIAR.bat abrir ALIAS IDENTIDAD_NUEVA.')
    return json.loads(p.read_text(encoding='utf8'))['life_id']


def service_cf01(args):
    """Una entrada de uso; la elección material sigue en el gestor existente."""
    parser = argparse.ArgumentParser(description='Servicio CF01 sobre una copia personal de un corte completo.')
    parser.add_argument('life', help='Identidad nueva; nunca el nombre de un original distribuido.')
    parser.add_argument('--mediciones', required=True, help='Pares RAW izquierdo:derecho, separados por comas.')
    parser.add_argument('--referencia-entorno', type=int, help='Opcional: calibración externa explícita. Sin ella se conserva la almacenada; no se enseña a A.')
    parser.add_argument('--reiniciar-entorno', action='store_true', help='Reiniciar explícitamente sólo el entorno externo; nunca la vida DEE.')
    parser.add_argument('--retorno', choices=('intact', 'omit_return'), default='intact', help='Control declarado del retorno ambiental, no reparación del contenido.')
    parser.add_argument('--continuar', action='store_true', help='Usar explícitamente la vida personal ya existente, sin importarla otra vez.')
    options = parser.parse_args(args)
    # La validación de identidad y las mediciones pertenecen al mismo gestor;
    # este lanzador no calcula signo, utilidad, lector ni acción deseada.
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}', options.life):
        raise ValueError('Identidad ASCII de 1..91 caracteres requerida.')
    record = ROOT / 'trabajo_personal/estado/vidas' / options.life / 'VIDA.json'
    if options.continuar:
        if not record.is_file(): raise ValueError('No existe esa vida personal. No se sustituye por otra ni se reconstruye desde T0.')
    else:
        if record.exists(): raise ValueError('La vida personal ya existe y se conserva. Use --continuar u otra identidad nueva.')
        open_copy('CF01_OPERATIVO', options.life)
    command = ['cf01-servicio', '--vida', options.life, '--mediciones=' + options.mediciones]
    if options.referencia_entorno is not None: command.extend(['--referencia-entorno', str(options.referencia_entorno)])
    if options.reiniciar_entorno: command.append('--reiniciar-entorno')
    if options.retorno != 'intact': command.extend(['--retorno', options.retorno])
    return call(command)


def service_ente(args):
    """Uso EO01 sobre una vida completa; no decide ni actualiza el contenido."""
    parser = argparse.ArgumentParser(description='Ente EO01: consecuencia externa posterior a su acción material.')
    parser.add_argument('life', help='Identidad personal nueva o existente con --continuar.')
    parser.add_argument('--mediciones', required=True, help='Pares RAW izquierdo:derecho, separados por comas; dominio del contrato vigente.')
    parser.add_argument('--continuar', action='store_true', help='Continuar la vida personal ya guardada, sin importar otra copia.')
    parser.add_argument('--referencia-entorno', type=int, help='Calibración externa explícita; omitida conserva la almacenada.')
    parser.add_argument('--reiniciar-entorno', action='store_true', help='Reinicio explícito sólo del entorno externo, nunca del estado DEE.')
    parser.add_argument('--retorno', choices=('real', 'omit', 'decoupled'), default='real', help='Retorno real por defecto; los otros son controles declarados.')
    parser.add_argument('--actuador', choices=('closed', 'nulled'), default='closed', help='Actuación real por defecto; nulled es control posterior a la emisión.')
    parser.add_argument('--fase', type=int, help='Cambio sensorial explícito dentro del dominio admitido, no búsqueda automática de una fase favorable.')
    parser.add_argument('--privada-B', type=int, help='Dato privado RAW para B; se reenvía sin calcular su contenido ni el efecto conveniente.')
    parser.add_argument('--valvula-social', action='store_true', help='Habilitar explícitamente la válvula externa P0; su estado queda en el entorno.')
    parser.add_argument('--actuador-B', choices=('closed', 'nulled'), default='closed', help='Actuación de B; nulled es un control externo explícito.')
    parser.add_argument('--corte-mensaje', choices=('none', 'minus_bus', 'plus_bus'), default='none', help='Corte diagnóstico declarado del mensaje; no selección de respuesta.')
    parser.add_argument('--detalle', action='store_true', help='Registrar contexto microscópico; no selecciona la respuesta.')
    options = parser.parse_args(args)
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}', options.life):
        raise ValueError('Identidad ASCII de 1..91 caracteres requerida.')
    record = ROOT / 'trabajo_personal/estado/vidas' / options.life / 'VIDA.json'
    if options.continuar:
        if not record.is_file(): raise ValueError('No existe esa vida personal. No se reconstruye ni se sustituye por otra.')
    else:
        if record.exists(): raise ValueError('La vida personal ya existe y se conserva. Use --continuar u otra identidad nueva.')
        open_copy('ENTE_OPERATIVO', options.life)
    command = ['ente-servicio', '--vida', options.life, '--mediciones=' + options.mediciones]
    if options.referencia_entorno is not None: command.extend(['--referencia-entorno', str(options.referencia_entorno)])
    if options.reiniciar_entorno: command.append('--reiniciar-entorno')
    if options.retorno != 'real': command.extend(['--retorno', options.retorno])
    if options.actuador != 'closed': command.extend(['--actuador', options.actuador])
    if options.fase is not None: command.extend(['--fase', str(options.fase)])
    if options.privada_B is not None: command.extend(['--privada-B', str(options.privada_B)])
    if options.valvula_social: command.append('--valvula-social')
    if options.actuador_B != 'closed': command.extend(['--actuador-B', options.actuador_B])
    if options.corte_mensaje != 'none': command.extend(['--corte-mensaje', options.corte_mensaje])
    if options.detalle: command.append('--detalle')
    return call(command)


def service_evolucion(args):
    """Transporte literal al servicio EO02 existente; sin agregación ni política."""
    parser = argparse.ArgumentParser(description='EO02: observaciones individuales, tarea explícita y continuidad completa.')
    parser.add_argument('life', help='Identidad personal nueva o existente con --continuar.')
    parser.add_argument('--observaciones', required=True, help='JSON de listas RAW, por ejemplo [[2,14,1,3],[8,21,0,2]]; se envía sin sumar ni elegir respuestas.')
    parser.add_argument('--dominio', choices=('puertas', 'trabajadores', 'transaccion'), default='puertas', help='Selección explícita de tarea por operador; no decisión autónoma del ente.')
    parser.add_argument('--sensorial', action='store_true', help='Elegir explícitamente la otra vida T0 SENSORIAL_R10 y su contrato de8entradas; no se elige por la respuesta esperada.')
    parser.add_argument('--continuar', action='store_true', help='Cargar la misma vida personal guardada, sin crear otra.')
    parser.add_argument('--referencia-entorno', type=int, help='Capacidad de la ley externa; no es una referencia correcta inyectada a DEE.')
    parser.add_argument('--reiniciar-entorno', action='store_true', help='Reset explícito sólo del dominio externo, nunca de DEE.')
    parser.add_argument('--retorno', choices=('real', 'omit', 'decoupled'), default='real')
    parser.add_argument('--actuador', choices=('closed', 'nulled'), default='closed')
    parser.add_argument('--fase-visible', action='store_true', help='Sensor preparado del estado transaccional actual; no entrega el trabajador correcto.')
    parser.add_argument('--fase-cero', action='store_true', help='Control sensorial declarado; requiere --fase-visible según el mismo contrato.')
    parser.add_argument('--detalle', action='store_true')
    options = parser.parse_args(args)
    if options.sensorial and (options.dominio == 'transaccion' or options.fase_visible or options.fase_cero):
        raise ValueError('SENSORIAL_R10 admite puertas/trabajadores, no el contrato C/fase de R9. No se cambia de perfil silenciosamente.')
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}', options.life):
        raise ValueError('Identidad ASCII de 1..91 caracteres requerida.')
    record = ROOT / 'trabajo_personal/estado/vidas' / options.life / 'VIDA.json'
    if options.continuar:
        if not record.is_file(): raise ValueError('No existe esa vida. No se reconstruye ni se elige otra rama para responder.')
    else:
        if record.exists(): raise ValueError('La vida personal ya existe y se conserva. Use --continuar u otra identidad nueva.')
        open_copy('SENSORIAL_R10' if options.sensorial else 'EVOLUCION_OPERATIVA', options.life)
    command = ['evolucion-sensorial' if options.sensorial else 'evolucion-servicio', '--vida', options.life, '--observaciones', options.observaciones, '--dominio', options.dominio]
    if options.referencia_entorno is not None: command.extend(['--referencia-entorno', str(options.referencia_entorno)])
    if options.reiniciar_entorno: command.append('--reiniciar-entorno')
    if options.retorno != 'real': command.extend(['--retorno', options.retorno])
    if options.actuador != 'closed': command.extend(['--actuador', options.actuador])
    if options.fase_visible: command.append('--fase-visible')
    if options.fase_cero: command.append('--fase-cero')
    if options.detalle: command.append('--detalle')
    return call(command)


def service_mente(args):
    """Una misma copia completa; las situaciones pasan literalmente al gestor."""
    parser = argparse.ArgumentParser(description='Sesión continua MENTE_ACUMULATIVA; vocabulario y dominio finitos del contrato.')
    parser.add_argument('life', nargs='?', help='Identidad personal nueva, o guardada con --continuar. Omitida: activo personal; primer uso importa explícitamente el corte seleccionado.')
    parser.add_argument('--situaciones', help='JSON de situaciones del contrato vigente; se transporta sin resolver ni elegir memorias. Omitido: estado pasivo, cero ticks.')
    parser.add_argument('--continuar', action='store_true', help='Continuar esa misma vida guardada; no volver a importar ni crear otra.')
    parser.add_argument('--retorno', choices=('real', 'omit', 'decoupled'), default='real', help='Los dos últimos son controles materiales declarados.')
    parser.add_argument('--actuador', choices=('closed', 'nulled'), default='closed', help='Control posterior a la emisión; no una política externa.')
    options = parser.parse_args(args)
    if options.life is None:
        active = ROOT / 'trabajo_personal/estado/ACTIVO.json'
        if active.exists():
            options.life = current_life()
            options.continuar = True
        else:
            if options.continuar:
                raise ValueError('No hay activo personal que continuar. Inicie explícitamente con mente, sin --continuar, para importar el corte completo seleccionado.')
            options.life = 'COLAB_MENTE_' + __import__('uuid').uuid4().hex[:12]
            print('INSTRUMENTO: primer inicio explícito MENTE; se importa continuidad completa del corte seleccionado, no un universo T0. No se reemplaza una vida personal existente.')
            open_copy('MENTE_ACUMULATIVA', options.life)
            options.continuar = True
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}', options.life):
        raise ValueError('Identidad ASCII de 1..91 caracteres requerida.')
    record = ROOT / 'trabajo_personal/estado/vidas' / options.life / 'VIDA.json'
    if options.continuar:
        if not record.is_file(): raise ValueError('No existe esa vida personal. No se sustituye por otro perfil ni por una preparación T0.')
        # Sólo identificación del contrato, nunca selección de una memoria ni
        # lectura de un target. Un activo ajeno no se cambia para dar respuesta.
        selected = next((q for q in catalog() if q['alias'] == 'MENTE_ACUMULATIVA'), None)
        current = json.loads(record.read_text(encoding='utf8'))
        parent = current.get('parent') or {}
        admitted = False
        while isinstance(parent, dict):
            if selected and (parent.get('encoded_sha256') == selected['snapshot_sha256']
                or parent.get('life_id') == selected['source_life']
                or str(parent.get('source_name', '')).startswith(selected['source_life'] + '.')):
                admitted = True
            parent = parent.get('historical_parent')
        if not selected or current.get('profile') != selected['profile'] or not admitted:
            raise ValueError('Fuera del contrato MENTE_ACUMULATIVA: el activo personal se conserva intacto. Abra explícitamente otra copia del alias admitido; no se sustituye por una rama favorable.')
    else:
        if record.exists(): raise ValueError('La vida personal existe. Use --continuar; no se rebobina ni se sobrescribe.')
        open_copy('MENTE_ACUMULATIVA', options.life)
    if options.situaciones is None:
        return call(['mente-estado', '--vida', options.life])
    command = ['mente-sesion', '--vida', options.life, '--situaciones', options.situaciones]
    if options.retorno != 'real': command.extend(['--retorno', options.retorno])
    if options.actuador != 'closed': command.extend(['--actuador', options.actuador])
    return call(command)


def service_mente2(args):
    """Transport only: new MA02 contract; legacy mente/R9 remains unchanged."""
    parser=argparse.ArgumentParser(description='MA02: asociaciones físicas y composición preparada; no lenguaje libre ni política P2.')
    parser.add_argument('life',nargs='?')
    parser.add_argument('--situaciones',help='JSON literal del contrato; omitido consulta estado pasivo.')
    parser.add_argument('--continuar',action='store_true')
    parser.add_argument('--retorno',choices=('real','omit'),default='real')
    parser.add_argument('--actuador',choices=('closed','nulled'),default='closed')
    parser.add_argument('--detalle',action='store_true')
    options=parser.parse_args(args)
    alias='MENTE_ACUMULATIVA_R02'
    if options.life is None:
        active=ROOT/'trabajo_personal/estado/ACTIVO.json'
        if active.exists():
            options.life=current_life();options.continuar=True
        else:
            if options.continuar:raise ValueError('No hay activo personal. Inicie mente2 para importar explícitamente el corte completo seleccionado, no T0.')
            options.life='COLAB_MENTE2_'+__import__('uuid').uuid4().hex[:12]
            print('INSTRUMENTO: primer inicio explícito MENTE2; importación de continuidad completa del corte MA02 seleccionado. No se crea un universo T0 ni se reemplaza una vida existente.')
            open_copy(alias,options.life);options.continuar=True
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',options.life):raise ValueError('Identidad ASCII de1..91caracteres requerida.')
    record=ROOT/'trabajo_personal/estado/vidas'/options.life/'VIDA.json'
    if options.continuar:
        if not record.is_file():raise ValueError('No existe la vida; no hay reconstrucción ni sustitución silenciosa.')
        allowed=[q for q in catalog()if q.get('source_life')in('MA02_MAIN_5','MA02_MAIN','MA02_MEMORIA_SEPARADA','MA02_COMPOSICION_PLUS_LISTA','MA02_COMPOSICION_PLUS_USO','MA02_PENDIENTE_CONTROL')]
        current=json.loads(record.read_text(encoding='utf8'));parent=current.get('parent')or{};admitted=False
        while isinstance(parent,dict):
            if any(current.get('profile')==q['profile']and(parent.get('encoded_sha256')==q['snapshot_sha256']or parent.get('life_id')==q['source_life']or str(parent.get('source_name','')).startswith(q['source_life']+'.'))for q in allowed):admitted=True
            parent=parent.get('historical_parent')
        if not admitted:raise ValueError('Fuera del contrato MA02: se conserva el activo personal. Abra explícitamente una copia MA02; mente continúa disponible para R9.')
    else:
        if record.exists():raise ValueError('La vida existe; use --continuar o una identidad nueva, sin rebobinarla.')
        open_copy(alias,options.life)
    if options.situaciones is None:return call(['mente2-estado','--vida',options.life])
    command=['mente2-sesion','--vida',options.life,'--situaciones',options.situaciones]
    if options.retorno!='real':command.extend(['--retorno',options.retorno])
    if options.actuador!='closed':command.extend(['--actuador',options.actuador])
    if options.detalle:command.append('--detalle')
    return call(command)


def service_asistente(args):
    """Literal APD transport through the existing single-owner manager.

    No word-to-operation dictionary, calculator, route choice, implicit import,
    favorable branch switch or automatic owner start is implemented here.
    """
    parser=argparse.ArgumentParser(description='APD: formas literales, propietario explícito y continuidad emparejada.')
    parser.add_argument('life',help='Copia personal ya importada explícitamente con abrir ASISTENTE_PROPOSITO ID.')
    actions=parser.add_subparsers(dest='action',required=True)
    start=actions.add_parser('iniciar');start.add_argument('--pausado',action='store_true');start.add_argument('--intervalo',type=float,default=.1);start.add_argument('--max-segundos',type=float)
    actions.add_parser('estado')
    for name in('pausar','reanudar','guardar','detener','exportar','resultado'):
        sub=actions.add_parser(name);sub.add_argument('--id',required=True)
        if name!='resultado':sub.add_argument('--esperar',type=float,default=180 if name=='exportar'else 40)
    use=actions.add_parser('usar');use.add_argument('--texto',required=True);use.add_argument('--operandos',type=int,nargs=2,required=True)
    teach=actions.add_parser('ensenar');teach.add_argument('--texto',required=True);teach.add_argument('--senal',type=int,choices=(-1,1),required=True);teach.add_argument('--revision',action='store_true')
    route_teacher=actions.add_parser('ensenar-ruta');route_teacher.add_argument('--lado',choices=('A','B'),required=True)
    count=actions.add_parser('contar');count.add_argument('--presencias',type=int,nargs='+',required=True)
    composition=actions.add_parser('componer');composition.add_argument('--formas',nargs='+',required=True);composition.add_argument('--datos',type=int,nargs='+',required=True)
    environment=actions.add_parser('ambiente');environment.add_argument('--configuracion',required=True,help='JSON literal: precios[2]0..28, demora[2]ticksDEE0..4096, disponibilidad[2], presupuesto fijo2.')
    for sub in(use,teach,route_teacher,count,composition,environment):
        sub.add_argument('--id',required=True);sub.add_argument('--esperar',type=float,default=40)
        sub.add_argument('--retorno',choices=('real','omit'),default='real');sub.add_argument('--actuador',choices=('closed','nulled'),default='closed')
    options=parser.parse_args(args)
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',options.life):raise ValueError('Identidad personal portable requerida.')
    record=ROOT/'trabajo_personal/estado/vidas'/options.life/'VIDA.json'
    if not record.is_file():raise ValueError('No existe esa copia. Importe explícitamente: INICIAR.bat abrir ASISTENTE_PROPOSITO IDENTIDAD_NUEVA. No se creóT0 ni otra vida.')
    if options.action=='iniciar':
        import math
        if not math.isfinite(options.intervalo)or options.intervalo<=0 or options.max_segundos is not None and(not math.isfinite(options.max_segundos)or options.max_segundos<=0):raise ValueError('Cadencia y horizonte explícitos positivos y finitos.')
        command=['mente-unificada-iniciar','--vida',options.life,'--backend','mente_unificada','--intervalo',str(options.intervalo)]
        if options.pausado:command.append('--pausado')
        if options.max_segundos is not None:command+=['--max-segundos',str(options.max_segundos)]
        return call(command)
    if options.action=='estado':return call(['mente-unificada-estado','--vida',options.life])
    if options.action in('pausar','reanudar','guardar','detener','exportar','resultado'):
        command=['mente-unificada-'+options.action,'--vida',options.life,'--id',options.id]
        if options.action!='resultado':command+=['--esperar',str(options.esperar)]
        return call(command)
    if options.action=='usar':row={'modo':'apd','texto':options.texto,'operandos':options.operandos}
    elif options.action=='ensenar':row={'modo':'apd-docencia','texto':options.texto,'senal':options.senal,'revision':options.revision}
    elif options.action=='ensenar-ruta':row={'modo':'apd-ruta-docencia','lado':options.lado}
    elif options.action=='contar':row={'modo':'apd-conteo','presencias':options.presencias}
    elif options.action=='componer':row={'modo':'apd-componer','formas':options.formas,'datos':options.datos}
    else:row={'modo':'apd-ambiente','configuracion':json.loads(options.configuracion)}
    return call(['mente-unificada-pedir','--vida',options.life,'--id',options.id,'--situaciones',json.dumps([row],ensure_ascii=False,separators=(',',':')),'--actuador',options.actuador,'--retorno',options.retorno,'--esperar',str(options.esperar)])


APD02_ALIAS='ASISTENTE_CALIDAD'


def _apd02_lineage(record,selected):
    if record.get('profile')!=selected['profile']:return False
    parent=record.get('parent')or{}
    while isinstance(parent,dict):
        if (parent.get('encoded_sha256')==selected['snapshot_sha256']or
            parent.get('life_id')==selected['source_life']or
            str(parent.get('source_name','')).startswith(selected['source_life']+'.')):return True
        parent=parent.get('historical_parent')
    return False


def research_apd02(args):
    """Explicitly import/identify the new research copy, never old ACTIVO/T0.

    This separate personal pointer never replaces a collaborator's ACTIVO,
    experiments or previous APD01 copy. Identification advances no DEE ticks;
    starting the owner remains a separate explicit command.
    """
    parser=argparse.ArgumentParser(description='Corte nuevo APD02 como copia personal emparejada; no inicia el propietario.')
    parser.add_argument('life',nargs='?',help='Identidad nueva opcional. Sin ella identifica la copia APD02 personal o importa una nueva por primera vez.')
    options=parser.parse_args(args)
    selected=next((r for r in catalog()if r['alias']==APD02_ALIAS),None)
    if not selected or not selected.get('persistent_service'):raise ValueError('No está incorporado un corte APD02 emparejado cerrado. No se sustituye por MA_R9, APD01 ni T0.')
    pointer=ROOT/'trabajo_personal/INVESTIGACION_APD02.json'
    if options.life is None and pointer.exists():
        old=json.loads(pointer.read_bytes());life=old['life_id'];record_path=ROOT/'trabajo_personal/estado/vidas'/life/'VIDA.json'
        if old.get('source_snapshot_sha256')!=selected['snapshot_sha256']:raise ValueError('La copia personal pertenece a un corte anterior y se conserva. Para el nuevo corte use investigacion IDENTIDAD_NUEVA; no se rebobina la copia guardada.')
        if not record_path.is_file()or not _apd02_lineage(json.loads(record_path.read_bytes()),selected):raise ValueError('Puntero personal APD02 inconsistente; no se repara importando otra vida silenciosamente.')
        print('INSTRUMENTO: misma copia personal APD02 '+life+'; identificación pasiva, sin iniciar dueño ni consultar contenido.')
        return call(['mente-unificada-estado','--vida',life])
    life=options.life or('COLAB_APD02_'+__import__('uuid').uuid4().hex[:12])
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',life):raise ValueError('Identidad personal portable requerida.')
    record=ROOT/'trabajo_personal/estado/vidas'/life/'VIDA.json'
    if record.exists():raise ValueError('Esa identidad personal ya existe; no se sobrescribe ni se usa otra rama favorable.')
    print('INSTRUMENTO: importación explícita del NUEVO corte '+selected['source_life']+' T'+str(selected['tick'])+' mediante paquete emparejado completo; no T0 ni inicio automático. ACTIVO personal anterior intacto.')
    result=open_copy(APD02_ALIAS,life,activate=False)
    # A new explicit name may coexist without replacing an older research pointer.
    if not pointer.exists():
        pointer.parent.mkdir(parents=True,exist_ok=True)
        with pointer.open('x',encoding='utf8')as f:json.dump({'life_id':life,'source_alias':APD02_ALIAS,'source_life':selected['source_life'],'source_snapshot_sha256':selected['snapshot_sha256'],'source_tick':selected['tick'],'owner_started':False},f,ensure_ascii=False,indent=2);f.write('\n')
    print('Continúe explícitamente en otra terminal: INICIAR.bat asistente2 '+life+' iniciar --pausado')
    return 0


def service_asistente2(args):
    """Typed literal APD02 requests; no answer, operator or route is inferred."""
    parser=argparse.ArgumentParser(description='APD02: calidad postacción, dos nuevas señales y acumulación preparada en una copia personal completa.')
    parser.add_argument('life',help='Copia emparejada personal del alias ASISTENTE_CALIDAD; nunca el original distribuido.')
    actions=parser.add_subparsers(dest='action',required=True)
    start=actions.add_parser('iniciar');start.add_argument('--pausado',action='store_true');start.add_argument('--intervalo',type=float,default=.1);start.add_argument('--max-segundos',type=float)
    actions.add_parser('estado')
    for name in('pausar','reanudar','guardar','detener','exportar','resultado'):
        sub=actions.add_parser(name);sub.add_argument('--id',required=True)
        if name!='resultado':sub.add_argument('--esperar',type=float,default=180 if name=='exportar'else 120)
    use=actions.add_parser('usar');use.add_argument('--texto',required=True);use.add_argument('--operandos',type=int,nargs=2,required=True)
    teach=actions.add_parser('ensenar');teach.add_argument('--texto',required=True);teach.add_argument('--senal',type=int,choices=(-1,1),required=True);teach.add_argument('--revision',action='store_true')
    language=actions.add_parser('lenguaje');language.add_argument('--texto',required=True);language.add_argument('--valor',type=int,required=True);language.add_argument('--contexto',choices=('alfa','beta','gamma','delta','epsilon','zeta'),required=True)
    accumulate=actions.add_parser('acumular');accumulate.add_argument('--valor',type=int,required=True);accumulate.add_argument('--demora-periodos',type=int,default=0)
    route_admit=actions.add_parser('preparar-ruta04',help='Preparación anatómica explícita; no reinicia una ruta ya admitida ni enseña una respuesta.')
    composition=actions.add_parser('componer');composition.add_argument('--formas',nargs='+',required=True);composition.add_argument('--datos',type=int,nargs='+',required=True)
    goals=[]
    for name in('meta','meta-iniciar'):
        goal=actions.add_parser(name);goal.add_argument('--texto',required=True);goal.add_argument('--operandos',type=int,nargs=2,required=True)
        visibility=goal.add_mutually_exclusive_group(required=True);visibility.add_argument('--segundo-visible',dest='segundo_visible',action='store_true');visibility.add_argument('--segundo-oculto',dest='segundo_visible',action='store_false');goals.append(goal)
    goal_step=actions.add_parser('meta-paso');goal_step.add_argument('--oportunidades',type=int,choices=(1,2,3,4),required=True,help='Oportunidades genéricas, nunca una lista de acciones ni un plan resuelto.')
    environment=actions.add_parser('ambiente');environment.add_argument('--configuracion',required=True,help='JSON literal: precios[2], demora[2], disponibilidad[2], fallos[2], presupuesto2 y demora_maxima.')
    for sub in(use,teach,language,accumulate,route_admit,composition,*goals,goal_step,environment):
        sub.add_argument('--id',required=True);sub.add_argument('--esperar',type=float,default=240)
        sub.add_argument('--retorno',choices=('real','omit'),default='real');sub.add_argument('--actuador',choices=('closed','nulled'),default='closed')
    options=parser.parse_args(args)
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',options.life):raise ValueError('Identidad personal portable requerida.')
    selected=next((r for r in catalog()if r['alias']==APD02_ALIAS),None)
    record=ROOT/'trabajo_personal/estado/vidas'/options.life/'VIDA.json'
    if not selected or not record.is_file()or not _apd02_lineage(json.loads(record.read_bytes()),selected):raise ValueError('No es una copia personal del corte APD02 admitido. Use investigacion IDENTIDAD_NUEVA; no se crea otra vida ni se cambia de perfil automáticamente.')
    if options.action=='iniciar':
        import math
        if not math.isfinite(options.intervalo)or options.intervalo<=0 or options.max_segundos is not None and(not math.isfinite(options.max_segundos)or options.max_segundos<=0):raise ValueError('Cadencia y horizonte positivos finitos requeridos.')
        command=['mente-unificada-iniciar','--vida',options.life,'--backend','mente_unificada','--intervalo',str(options.intervalo)]
        if options.pausado:command.append('--pausado')
        if options.max_segundos is not None:command+=['--max-segundos',str(options.max_segundos)]
        return call(command)
    if options.action=='estado':return call(['mente-unificada-estado','--vida',options.life])
    if options.action in('pausar','reanudar','guardar','detener','exportar','resultado'):
        command=['mente-unificada-'+options.action,'--vida',options.life,'--id',options.id]
        if options.action!='resultado':command+=['--esperar',str(options.esperar)]
        return call(command)
    if options.action=='usar':row={'modo':'apd02','texto':options.texto,'operandos':options.operandos}
    elif options.action=='ensenar':row={'modo':'apd02-docencia','texto':options.texto,'senal':options.senal,'revision':options.revision}
    elif options.action=='lenguaje':row={'modo':'apd02-lenguaje','texto':options.texto,'valor':options.valor,'contexto':options.contexto}
    elif options.action=='acumular':row={'modo':'apd02-acumular','valor':options.valor,'demora_periodos':options.demora_periodos}
    elif options.action=='preparar-ruta04':row={'modo':'apd02-ruta04-admitir'}
    elif options.action=='componer':row={'modo':'apd02-componer','formas':options.formas,'datos':options.datos}
    elif options.action in('meta','meta-iniciar'):row={'modo':'apd02-'+options.action,'texto':options.texto,'operandos':options.operandos,'segundo_visible':options.segundo_visible}
    elif options.action=='meta-paso':row={'modo':'apd02-meta-paso','oportunidades':options.oportunidades}
    else:row={'modo':'apd02-ambiente','configuracion':json.loads(options.configuracion)}
    return call(['mente-unificada-pedir','--vida',options.life,'--id',options.id,'--situaciones',json.dumps([row],ensure_ascii=False,separators=(',',':')),'--actuador',options.actuador,'--retorno',options.retorno,'--esperar',str(options.esperar)])


def example(number, life=None, value=None):
    """Cinco recorridos cortos; no repite ninguna campaña científica."""
    life = life or 'COLAB_' + __import__('uuid').uuid4().hex[:10]
    if number == 5:
        source = current_life()
        source_record = json.loads((ROOT/'trabajo_personal/estado/vidas'/source/'VIDA.json').read_bytes())
        if source_record.get('persistent_service'):
            raise ValueError('Esta vida contiene un protocolo persistente: una bifurcación ordinaria no copia su SQLite/colas/artefactos. No se creó otra vida ni se avanzó la actual. Use explícitamente INICIAR.bat gestor mente-unificada-exportar --vida '+source+' --id IDENTIFICADOR_NUEVO --esperar 120 con su propietario disponible; luego INICIAR.bat gestor mente-unificada-importar --paquete DIRECTORIO_EXPORTADO --vida '+life+'. No descarte el diario ni restaure solamente el snapshot. Para una copia del corte distribuido, use INICIAR.bat abrir ALIAS IDENTIDAD_NUEVA.')
    out = ROOT / 'trabajo_personal/resultados' / life
    out.mkdir(parents=True, exist_ok=True)
    if number == 1:
        result = call(['version'], True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif number == 2:
        open_copy('E1_PROTEGIDO', life)
        result = call(['observar', '--vida', life, '0', '0', '0'], True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif number == 3:
        open_copy('LECTOR_AUXILIAR', life)
        result = call(['mi02-comparar-efimero', '--vida', life, '--objetos', '22,24,26,None'], True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif number == 4:
        open_copy('SOCIAL_REUTILIZABLE', life)
        conditions = value or '1,-1,1'
        result = call(['mi02-vivir', '--vida', life, '--condiciones=' + conditions], True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif number == 5:
        source = current_life()
        call(['bifurcar', source, life], True)
        before = call(['estado', '--vida', life], True)
        call(['guardar', '--vida', life], True)
        # Dos procesos distintos, mismo estado guardado; sólo tres ticks nuevos.
        target = int(before['INSTRUMENTO']['tick']) + 3
        call(['continuar', '--vida', life, '--hasta', str(target)], True)
        result = call(['estado', '--vida', life], True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        raise ValueError('Ejemplos 1..5')
    (out / f'EJEMPLO_{number}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')


def service_usar(args):
    """Una sola ruta UI para CLI/menú; identidad y modo siempre explícitos."""
    parser=argparse.ArgumentParser(description='Corte completo seleccionado: una terminal, una copia personal y un propietario.')
    identity=parser.add_mutually_exclusive_group(required=True)
    identity.add_argument('--nueva',metavar='IDENTIDAD_NUEVA')
    identity.add_argument('--vida',metavar='IDENTIDAD_EXISTENTE')
    parser.add_argument('--sin-iniciar',action='store_true')
    parser.add_argument('--guion',type=Path)
    options=parser.parse_args(args)
    life=options.nueva or options.vida
    if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',life):
        raise ValueError('Identidad personal explícita ASCII de1..91caracteres requerida; no se crea otra automáticamente.')
    command=[str(PYTHON),'-I','-B','-X','utf8',str(SYSTEM/'app/usar_dee.py'),'--raiz',str(ROOT),
        '--nueva'if options.nueva is not None else'--vida',life]
    if options.sin_iniciar:command.append('--sin-iniciar')
    if options.guion is not None:
        path=options.guion if options.guion.is_absolute()else ROOT/options.guion
        command+=['--guion',str(path.resolve())]
    return subprocess.call(command,cwd=PYTHON.parent)


def menu():
    print('DEE Cognitive System 1.1 — copia para colaboración. No es un chatbot.')
    print('Entrada recomendada: corte completo seleccionado en el contrato vigente. Las vidas anteriores siguen disponibles; no se mezclan sus recuerdos.')
    print('1 Usar corte seleccionado (nueva/continuar, una terminal) / 2 Catálogo / 3 Abrir otro alias / 4 Estado activo histórico / 5 Ejemplos / 6 Gestor / 7 Versión / 0 Salir')
    while True:
        option = input('Opción: ').strip()
        try:
            if option == '0': return 0
            if option == '1':
                mode=input('Modalidad [nueva/continuar/cancelar]: ').strip().lower()
                if mode=='cancelar':continue
                if mode not in('nueva','continuar'):raise ValueError('Elija explícitamente nueva o continuar; no se importa ni elige una vida automáticamente.')
                life=input('Identidad personal explícita: ').strip()
                code=service_usar(['--nueva'if mode=='nueva'else'--vida',life])
                if code:print('La UI terminó con código '+str(code)+'. Se conservan sus recibos y estado; no se reinicia ni reenvía automáticamente.')
            elif option == '2': show_catalog()
            elif option == '3':
                show_catalog()
                open_copy(input('Alias: ').strip(), input('Identidad nueva (COLAB_...): ').strip())
            elif option == '4': call(['estado', '--vida', current_life()])
            elif option == '5':
                print('1 motor; 2 abrir/observar; 3 función adquirida; 4 cambiar experiencia; 5 bifurcar/guardar/continuar')
                example(int(input('Ejemplo: ')))
            elif option == '6': call(['interactivo'])
            elif option == '7': call(['version'])
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))


def main():
    sys.stdout.reconfigure(encoding='utf8')
    prepare()
    args = sys.argv[1:]
    if not args: return menu()
    if args[0] == 'catalogo': show_catalog(); return 0
    if args[0] == 'usar': return service_usar(args[1:])
    if args[0] == 'abrir' and len(args) == 3: open_copy(args[1], args[2]); return 0
    if args[0] == 'ejemplo':
        p = argparse.ArgumentParser(); p.add_argument('number', type=int); p.add_argument('--vida'); p.add_argument('--condiciones')
        a = p.parse_args(args[1:]); example(a.number, a.vida, a.condiciones); return 0
    if args[0] == 'gestor': return call(args[1:])
    if args[0] == 'servicio-cf01': return service_cf01(args[1:])
    if args[0] == 'ente': return service_ente(args[1:])
    if args[0] == 'evolucion': return service_evolucion(args[1:])
    if args[0] == 'mente': return service_mente(args[1:])
    if args[0] == 'mente2': return service_mente2(args[1:])
    if args[0] == 'asistente': return service_asistente(args[1:])
    if args[0] == 'asistente2': return service_asistente2(args[1:])
    if args[0] == 'investigacion': return research_apd02(args[1:])
    if args[0] == 'preparar': print('Dependencias locales y espacio personal preparados; no se creó ningún universo.'); return 0
    raise ValueError('Use usar --nueva IDENTIDAD_NUEVA o usar --vida IDENTIDAD_EXISTENTE (APD03, una terminal); investigacion [IDENTIDAD_NUEVA] y asistente2 ID ACCION conservan APD02 histórico; catalogo, abrir ALIAS ID, asistente ID ACCION (APD01 histórico), mente2 [ID] --situaciones JSON, mente [ID] --situaciones JSON (R9), evolucion ID --observaciones JSON, ente ID --mediciones=..., servicio-cf01 ID --mediciones=..., ejemplo 1..5, gestor COMANDO o preparar.')


if __name__ == '__main__':
    try: raise SystemExit(main())
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        raise SystemExit(2)
