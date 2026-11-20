"""Install only the external F1 auditor tool and stdlib RP entry point."""
from pathlib import Path
import ast,datetime,hashlib,json,os
P4=Path(__file__).resolve().parents[1];C=P4.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
SOURCE=P4/'fuentes/observador_F1_portable';BACK=P4/'codigo/revisiones/F1_RP_ANTES';TARGET=RP/'observadores/F1_PI04'
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def atomic(p,b,expected):
 if sha(p.read_bytes())!=expected:raise ValueError('Concurrent change '+str(p))
 tmp=p.with_name(p.name+'.PI04_F1.tmp')
 with tmp.open('xb')as f:f.write(b)
 if sha(p.read_bytes())!=expected:raise ValueError('Concurrent change before publish')
 os.replace(tmp,p)
def main():
 script=RP/'reproducir.py';registry=RP/'RECURSOS.json';old=script.read_bytes();oldreg=registry.read_bytes()
 reg=json.loads(oldreg.decode('utf-8-sig'));manifest=json.loads((SOURCE/'MANIFIESTO_SHA256.json').read_text(encoding='utf-8'))
 if 'PI04_F1'in reg.get('instrument_deltas',{})or TARGET.exists():raise ValueError('Existing incorporation protected')
 if BACK.exists()and((BACK/'reproducir.py').read_bytes()!=old or (BACK/'RECURSOS.json').read_bytes()!=oldreg):raise ValueError('Existing original backup differs; reconcile')
 names=('DATOS_F1.json','LEER_PRIMERO.txt','MANIFIESTO_SHA256.json','RECALCULAR_F1.py','RESULTADO_CONTRASTADO.json')
 for name,expected in manifest['members'].items():
  actual=info(SOURCE/name)
  if actual['bytes']!=expected['bytes']or actual['sha256']!=expected['sha256']:raise ValueError('Portable source mismatch')
 if not BACK.exists():
  BACK.mkdir(parents=True);(BACK/'reproducir.py').write_bytes(old);(BACK/'RECURSOS.json').write_bytes(oldreg)
 function='''
def external_f1_info():
    entry = config().get('instrument_deltas', {}).get('PI04_F1')
    if not entry: return []
    return [{'id': 'PI04_F1_OBSERVADOR_COLA_AUDITOR', 'kind': 'instrumento_externo',
             'modality': 'A_recalculo_registros', 'entrypoint': 'recalcular-f1 --destino <DIRECTORIO_NUEVO>',
             'product_relative': entry['product_relative'], 'manifest_sha256': entry['manifest_sha256'],
             'new_native_ticks': 0, 'DEE_imports': 0, 'acquisition_attributed_to_MAIN': False,
             'scope': entry['scope'], 'operation_coverage': entry.get('operation_coverage', {})}]

def recalculate_f1(args):
    dest = fresh_destination(args.destino)
    if dest.exists(): raise ValueError('F1 exige un destino NUEVO, incluso si el directorio existente está vacío')
    c = config(); entry = c.get('instrument_deltas', {}).get('PI04_F1')
    if not entry: raise ValueError('Herramienta externa F1 no incorporada')
    root = resource(entry); manifest = inside(root, 'MANIFIESTO_SHA256.json')
    if sha(manifest) != entry['manifest_sha256']: raise ValueError('Manifiesto F1 distinto del fijado')
    expected_names = {'DATOS_F1.json', 'RECALCULAR_F1.py', 'LEER_PRIMERO.txt', 'RESULTADO_CONTRASTADO.json'}
    members = read(manifest)['members']
    if set(members) != expected_names: raise ValueError('Miembros F1 no reconocidos')
    for name, witness in members.items():
        path = inside(root, name)
        if path.stat().st_size != witness['bytes'] or sha(path) != witness['sha256']:
            raise ValueError('Identidad de F1 alterada: ' + name)
    dest.mkdir(parents=False, exist_ok=False)
    save(dest / 'CONTEXTO_HERRAMIENTA_F1.json', {
        'kind': 'instrumento_externo', 'modality': 'A_recalculo_registros', 'created_utc': now(),
        'source': str(root), 'manifest_sha256': entry['manifest_sha256'],
        'RP_code_sha256': sha(HERE / 'reproducir.py'), 'no_MAIN_capacity_or_acquisition': True,
        'scope': 'Exact frozen physical features only; no Native owner, world import or new ticks.'})
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(inside(root, 'RECALCULAR_F1.py'))]
    process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8',
                             timeout=120, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if process.returncode:
        save(dest / 'FALLO_PRESERVADO.json', {'returncode': process.returncode, 'stdout': process.stdout,
             'stderr': process.stderr, 'automatic_retry': False, 'new_native_ticks': 0})
        raise RuntimeError('F1 falló; destino preservado sin reintento')
    result = json.loads(process.stdout)
    if result != read(root / 'RESULTADO_CONTRASTADO.json'):
        raise ValueError('F1 difiere del resultado contrastado; preservar destino')
    if result.get('new_Native_ticks') != 0 or result.get('DEE_imports') != 0:
        raise ValueError('Modalidad F1 no es recálculo puro')
    save(dest / 'RESULTADO_F1.json', result)
    proof = {'kind': 'instrumento_externo', 'mode': 'recalcular-f1', 'result': str(dest / 'RESULTADO_F1.json'),
             'result_sha256': sha(dest / 'RESULTADO_F1.json'), 'checks': result['checks'],
             'result_equal_preserved_reference': True, 'stderr_bytes': len(process.stderr.encode('utf-8')),
             'new_native_ticks': 0, 'DEE_imports': 0, 'MAIN_modified': False,
             'not_Native_reproduction': True, 'not_a_MAIN_capacity': True}
    save(dest / 'VERIFICACION_HERRAMIENTA_F1.json', proof)
    emit(proof)
    return 0

'''
 text=old.decode('utf-8').replace('\r\n','\n');anchor='def main():\n'
 if text.count(anchor)!=1:raise ValueError('RP main anchor ambiguous')
 text=text.replace(anchor,function+anchor)
 anchor="    sub.add_parser('listar')\n";assert text.count(anchor)==1
 text=text.replace(anchor,anchor+"    f1 = sub.add_parser('recalcular-f1'); f1.add_argument('--destino', required=True)\n")
 anchor="'recipes': [{**{key: value.get(key)";assert text.count(anchor)==1
 text=text.replace(anchor,"'external_tools': external_f1_info(),\n              "+anchor)
 anchor="    if args.modo == 'recalcular': return recalculate(args)\n";assert text.count(anchor)==1
 text=text.replace(anchor,anchor+"    if args.modo == 'recalcular-f1': return recalculate_f1(args)\n")
 before_functions={x.name:ast.dump(x)for x in ast.parse(old.decode('utf-8')).body if isinstance(x,ast.FunctionDef)}
 after_functions={x.name:ast.dump(x)for x in ast.parse(text).body if isinstance(x,ast.FunctionDef)}
 unchanged=[name for name,value in before_functions.items()if name!='main'and after_functions.get(name)==value]
 if len(unchanged)!=len(before_functions)-1:raise ValueError('An existing RP function changed')
 TARGET.mkdir(parents=True)
 for name in names:
  b=(SOURCE/name).read_bytes();(TARGET/name).write_bytes(b)
  if (TARGET/name).read_bytes()!=b:raise ValueError('Copy mismatch')
 atomic(script,text.encode('utf-8'),sha(old))
 reg.setdefault('instrument_deltas',{})['PI04_F1']={
  'product_relative':'reproducibilidad/observadores/F1_PI04','manifest':'MANIFIESTO_SHA256.json',
  'manifest_sha256':sha((TARGET/'MANIFIESTO_SHA256.json').read_bytes()),'kind':'instrumento_externo',
  'modality':'A_recalculo_registros','scope':'Detecta una huella histórica en registros PI03; no capacidad, adquisición ni recuperación de MAIN. RAW/clocks exactos47cortes;28diffglobales; no Native.',
  'RP_before_sha256':sha(old),'RP_after_sha256':sha(script.read_bytes()),
  'operation_coverage':{'listar':'IMPLEMENTED_TEST_PENDING','recalcular-f1':'IMPLEMENTED_TEST_PENDING'},
  'source_evidence':str(P4/'control/F1_PORTABLE_VERIFICADO.json'),
  'original_before':str(BACK),'new_native_ticks':0,'no_MAIN_or_selector_change':True}
 atomic(registry,(json.dumps(reg,ensure_ascii=False,indent=2)+'\n').encode('utf-8'),sha(oldreg))
 proof={'schema':'PI04.F1.external_tool_installed.v1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'portable_target':str(TARGET),'portable_files':{n:info(TARGET/n)for n in names},
  'RP_before':info(BACK/'reproducir.py'),'RP_after':info(script),'registry_before':info(BACK/'RECURSOS.json'),'registry_after':info(registry),
  'all_existing_RP_functions_except_dispatch_exact_AST':unchanged,'previous_resource_entries_preserved':all(reg[k]==json.loads(oldreg.decode('utf-8-sig'))[k]for k in reg if k!='instrument_deltas'),
  'previous_instrument_deltas_preserved':all(reg['instrument_deltas'][k]==v for k,v in json.loads(oldreg.decode('utf-8-sig')).get('instrument_deltas',{}).items()),
  'new_native_ticks':0,'DEE_imports':0,'MAIN_changed':False,'S_gestionar_changed':False,'operational_test':'PENDING'}
 path=P4/'control/F1_INCORPORACION_RP_EJECUTADA.json'
 with path.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':info(path),'RP_after':info(script),'target':str(TARGET),'existing_functions_preserved':len(unchanged),'new_Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
