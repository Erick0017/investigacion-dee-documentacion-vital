"""Two truthful product catalogue entries + one contract; no life adoption.

Default prepares a literal plan for Root review. --aplicar uses that exact plan
with CAS and backups. No operational Python, kernel, WHL, selector, world, life,
queue, capsule or recipe is changed. No Native import or material invocation.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import json

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
RP = C / 'reproducibilidad'
CAT = S / 'capacidades/CATALOGO_CAPACIDADES.json'
CONTRACT_REL = 'contratos/PI04_OBSERVACION_Y_REPRODUCCION_01.json'
CONTRACT = S / CONTRACT_REL
PLAN = P / 'codigo/INCORPORACION_MECANISMOS_PI04_JSON_R01'
RID = 'pi04_c2c_adquisicion_20_R01'
IDS = ['PI04_F1_OBSERVACION_EXTERNA_RECALCULABLE', 'PI04_C2C_ADQUISICION_EXPERIMENTAL_REPRODUCIBLE']


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(v): return (json.dumps(v, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def desc(p): return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}
def at(v, path):
    for key in path: v = v[key]
    return v
def save_new(p, data):
    with p.open('xb') as f: f.write(data)


def protected():
    active = read(S / 'estado/ACTIVO.json'); cardfile = S / 'estado/vidas' / active['life_id'] / 'VIDA.json'
    card = read(cardfile)
    if active['life_id'] != 'ECI02_PI03_MAIN' or card['physical']['N'] != 67 or card['physical']['tick'] != 775355:
        raise ValueError('Protected actual principal changed; reconcile, never replace a later main')
    files = [S / 'estado/ACTIVO.json', cardfile, S / card['snapshot'], C / 'PROYECTO.json', S / 'estado/genesis/SELECCION_PERSONAL.json']
    return {'life_id': active['life_id'], 'N':67, 'T':775355, 'snapshot_sha256': card['snapshot_sha256'],
        'critical_files': {str(p): sha(p) for p in files}}


def regression():
    recipefile = RP / 'recetas/panel_12.json'; recipe = read(recipefile); rows = []
    for batch in recipe['variants']['principal']['batches']:
        for spec in batch:
            f = P / 'ensayos' / ('PI04_MAIN_PANEL12_OP2_' + spec['label'] + '.json')
            if not f.exists(): return {'source_recipe': desc(recipefile), 'rows': rows, 'panel_not_completed': True}
            q = read(f); n = json.loads(q['result']) if isinstance(q['result'],str) else q['result']
            if 'expected' not in spec: continue
            actual = at(n, spec['read_path'])
            row = {'label':spec['label'], 'literal':spec['literal'], 'before_tick':n['before_tick'], 'after_tick':n['after_tick'],
                'observed':actual,'expected_evaluator_only':spec['expected'],'criterion_met':type(actual)is type(spec['expected'])and actual==spec['expected'],'primary':desc(f)}
            rows.append(row)
            if not row['criterion_met']:
                return {'source_recipe': desc(recipefile), 'rows': rows,
                    'tested':len(rows),'correct':sum(r['criterion_met']for r in rows),
                    'first_material_regression':row,'panel_not_completed':True,
                    'scope':'One failed fixed FI comparison/access witness at this future. Not proof that all arithmetic/content is lost. No remedial teaching or principal adoption.'}
    raise ValueError('The expected actual regression record is absent; do not invent a negative or an adoption gate')


def prepare():
    if PLAN.exists():
        print(json.dumps({'mode':'EXISTING_PLAN_NO_OVERWRITE','plan':str(PLAN),'review':desc(PLAN/'PLAN.json')},ensure_ascii=False));return
    before = CAT.read_bytes(); cat = json.loads(before.decode('utf-8-sig'))
    if cat.get('schema') != 'DCS1.1.capabilities.registry.v1' or any(e['id']in IDS for e in cat['entries']):
        raise ValueError('Unexpected catalogue schema or prior PI04 incorporation')
    if CONTRACT.exists(): raise ValueError('An existing contract must not be overwritten')
    main = protected()
    if cat['current_principal']['life_id'] != main['life_id'] or cat['current_principal']['tick'] != main['T']:
        raise ValueError('Catalogue and protected actual selection disagree')
    resources = read(RP/'RECURSOS.json'); f1 = resources['instrument_deltas']['PI04_F1']
    f1proof = Path(f1['operational_verification']['path'])
    if sha(f1proof) != f1['operational_verification']['sha256']: raise ValueError('Actual F1 proof differs')
    f1actual = read(f1proof)
    tests = {v['name']:v for v in f1actual['tests']}
    if tests['listar_actual']['returncode'] != 0 or tests['recalcular_actual']['returncode'] != 0:
        raise ValueError('F1 actual manager operations are not demonstrated')
    coldfile = P/'control/C2C_COLD20_NATIVE_VERIFICADA_R01.json'; cold = read(coldfile)
    if cold['status'] != 'NATIVE_REPLAY_VERIFIED' or not cold['closed'] or (cold['opportunities'],cold['products'],cold['reserved_products'],cold['Native_inputs_applied']) != (20,19,8,3720):
        raise ValueError('Actual C2C cold replay is required')
    publicfile = P/'control/RP_C2C_LISTAR_VERIFICAR_POSTREPLAY_R01/COMPROBACION.json'; public = read(publicfile)
    if public['actual_verified_runs'] != 1 or not public['requirements_available'] or not public['watched_hashes_unchanged']:
        raise ValueError('Actual public list/verify is required')
    registered = RP/'verificaciones'/RID/'ECI02_PI03_REPRO_PI04_RP_COLD20_OP2.json'; registered_actual = read(registered)
    if not registered_actual['actual_native_execution_completed'] or not registered_actual['fixed_local_criteria_met']:
        raise ValueError('Existing actual RP registration required')
    recipefile = RP/'recetas'/(RID+'.json'); recipe = read(recipefile)
    if sha(recipefile) != registered_actual['recipe_sha256_at_run'] or not recipe['reproduction_enabled'] or not recipe['requires_explicit_material']:
        raise ValueError('The exact preserved Native-tested material recipe is required')
    alias = 'PI03_PI04_C2C_POST_RES_T816019'; pair = resources['pairs'][alias]
    pairmanifest = C/pair['product_relative']/'EXPORTACION_SERVICIO.json'; pairdata = read(pairmanifest)
    if sha(pairmanifest) != pair['manifest_sha256'] or pairdata['physical']['tick'] != 816019 or pairdata['life_id'] != 'ECI02_PI03_REPRO_PI04_MAIN_02':
        raise ValueError('Exact learned experimental source pair required')
    reg = regression()
    if reg.get('first_material_regression',{}).get('label') != 'FIplus': raise ValueError('Actual FIplus regression must be preserved')
    when = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run = 'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py reproducibilidad '
    f1entry = {'id':IDS[0],'name':'Observación documental F1 de huellas y diferencias físicas conservadas',
        'kind':'instrumento_externo','availability':'OPERATIVO_DESDE_EL_MISMO_GESTOR_RECALCULO_VERIFICADO',
        'scope':'Recalcula registros congelados y verifica47cortes RAW/clocks y28diferencias globales dentro de su corpus. No consulta materialmente una vida ni demuestra memoria funcional por una diferencia de hash.',
        'implementation':['../reproducibilidad/reproducir.py','../'+f1['product_relative']+'/RECALCULAR_F1.py'],
        'validated_lives':[], 'attributed_to_main':False, 'contract':CONTRACT_REL,
        'commands_from_product_root':{'listar':run+'listar','recalcular':run+'recalcular-f1 --destino <DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>'},
        'actual_verification':desc(f1proof),'assistance':['Lectura, reconstrucción y clasificación por un instrumento externo; no decisión de DEE.'],
        'limits':['Es observación/recálculo sobre evidencia, no nueva simulación, recuperación cognitiva ni habilidad adquirida por PI03_MAIN.'],
        'incorporated_utc':when}
    c2centry = {'id':IDS[1],'name':'Adquisición contextual C2C y uso de resultado Native en una segunda selección',
        'kind':'mecanismo_experimental_reproducible','availability':'NATIVE_REPLAY_VERIFIED_EXPERIMENTAL_NO_ADOPTADO_AL_PRINCIPAL',
        'scope':'Desde el prefijo completo real800379, la receta permite repetir20experiencias C2C en una copia:19productos,8/8reservados y3720/3720entradas. La salida Native elige una función aritmética y su resultado real alimenta una segunda selección Native de conducto; secuencia y condiciones son preparadas.',
        'implementation':['../reproducibilidad/reproducir.py','../reproducibilidad/recetas/'+recipefile.name,
            '../reproducibilidad/codigo_preservado/'+recipe['code_capsule_key']+'/capacidades/pi04_coordinacion_central_C2C.py'],
        'validated_lives':[{'life_id':pairdata['life_id'],'role':'original_experimental_acquisition_not_main','physical':pairdata['physical'],
            'complete_pair':pair['product_relative'],'complete_pair_manifest_sha256':pair['manifest_sha256']},
            {'life_id':cold['life_id'],'role':'technical_cold_replay_shared_prefix_not_independent_organism','physical':cold['final_physical']}],
        'attributed_to_main':False,'current_principal_possesses_this_acquisition':False,'principal_adoption':False,
        'recipe':RID,'contract':CONTRACT_REL,'complete_source_prefix_alias':recipe['prefix'],'complete_learned_pair_alias':alias,
        'commands_from_product_root':{'listar':run+'listar','verificar':run+'verificar '+RID,
            'recalcular':run+'recalcular --receta '+RID+' --destino <DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>',
            'reproducir':run+'reproducir '+RID+' --variante real --vida ECI02_PI03_REPRO_PI04_<ID_NUEVO> --destino <DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE> --material'},
        'actual_verification':desc(coldfile),'actual_public_list_and_verify':desc(publicfile),'actual_registration':desc(registered),
        'assistance':['Inicio y orden consulta→aritmética→comparación→dispositivo, calendario, sensor y lector q+4 retenido a q+6 preparados.',
            'Codecs fijos de salida a función/conducto; el host transporta el entero Native real y evalúa la consecuencia, sin elegir respuestas por el objetivo.'],
        'limits':['No planificación o iniciativa general. Los controles con prefijo compartido no son organismos independientes.',
            'La continuación posterior T818074 no fue adoptada: el panel conservó5testigos y falló FIplus14/3 con−1 esperado+1. Resto del panel no ejecutado.',
            'La receta y cápsula permanecen históricas e inmutables; la verificación Native posterior consta en el registro externo.',
            '26recursos ambientales preparados,20consumidos al corte816019; no se garantiza repetición indefinida, autorreparación ni conservación de todos los usos anteriores.'],
        'incorporated_utc':when}
    contract = {'schema':'DCS1.1.PI04.observation_and_reproducibility.v1','status':'OPERATIVE_MECHANISMS_WITHOUT_MAIN_ADOPTION',
        'created_utc':when,'capability_ids':IDS,'principal_preserved':main,
        'code_scope':'Catalogue and this contract only; no19-file PI04 operational-code deployment, selector change or candidate promotion.',
        'F1':{'resource_entry':f1,'actual_proof':desc(f1proof),'attribution':'external_read_only_instrument'},
        'C2C':{'recipe':{'product_relative':recipefile.relative_to(C).as_posix(),'sha256':sha(recipefile)},
            'source_capsule_key':recipe['code_capsule_key'],'complete_pre_acquisition_prefix':resources['pairs'][recipe['prefix']],
            'complete_acquired_cut':pair,'original_acquisition_life':pairdata['life_id'],'original_cut':pairdata['physical'],
            'cold_verification':desc(coldfile),'actual_registration':desc(registered),'public_read_only_verification':desc(publicfile),
            'mechanism_scope':'Native capability choice and actual-result-dependent Native route within a prepared experimental sequence; no transfer of its learned state to PI03_MAIN.',
            'regression_and_nonadoption':reg,'principal_adoption':False},
        'safety':{'one_existing_principal':True,'no_snapshot_or_memory_transfer':True,
            'material_reproduction_requires_fresh_diagnostic_ID_and_explicit_new_absolute_destination':True,
            'read_only_modes_do_not_advance_world':True,'catalogue_not_consulted_to_answer':True},
        'commands':{'F1':f1entry['commands_from_product_root'],'C2C':c2centry['commands_from_product_root']}}
    proposed = copy.deepcopy(cat); proposed['entries'].extend([f1entry,c2centry])
    assert proposed['entries'][:-2] == cat['entries'] and all(proposed[k] == cat[k] for k in cat if k!='entries')
    PLAN.mkdir()
    save_new(PLAN/'CATALOGO_ANTES_LITERAL.json', before)
    save_new(PLAN/'CATALOGO_PROPUESTO.json', encoded(proposed))
    save_new(PLAN/'CONTRATO_PROPUESTO.json', encoded(contract))
    plan = {'schema':'DEE.PI04.product_mechanism_JSON.plan.v1','status':'PREPARED_ROOT_REVIEW_REQUIRED',
        'catalogue':str(CAT),'catalogue_before_sha256':hashlib.sha256(before).hexdigest(),
        'catalogue_after_sha256':sha(PLAN/'CATALOGO_PROPUESTO.json'),'old_entries':len(cat['entries']),'new_entries':len(proposed['entries']),
        'new_ids':IDS,'contract':str(CONTRACT),'contract_sha256':sha(PLAN/'CONTRATO_PROPUESTO.json'),
        'principal_preserved':main,'old_entry_values_and_all_other_top_fields_preserved':True,
        'Native_ticks':0,'operational_code_or_selectors_changed':False,
        'Root_apply':'Review these literal proposed JSONs, then invoke this same script --aplicar; CAS rejects changed catalogue/principal or a prior contract.'}
    save_new(PLAN/'PLAN.json', encoded(plan))
    print(json.dumps({'plan':str(PLAN/'PLAN.json'),'sha256':sha(PLAN/'PLAN.json'),**plan},ensure_ascii=False,indent=2))


def apply():
    plan = read(PLAN/'PLAN.json'); current = protected()
    if sha(CAT) != plan['catalogue_before_sha256'] or current != plan['principal_preserved']:
        raise ValueError('Catalogue or protected principal CAS changed; no overwrite')
    if CONTRACT.exists(): raise ValueError('Prior contract preserved; no repeat')
    if sha(PLAN/'CATALOGO_PROPUESTO.json') != plan['catalogue_after_sha256'] or sha(PLAN/'CONTRATO_PROPUESTO.json') != plan['contract_sha256']:
        raise ValueError('Reviewed proposed JSON changed')
    proof = P/'control/INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R01.json'
    if proof.exists(): raise ValueError('Prior incorporation proof preserved')
    backup = P/'codigo/revisiones/CATALOGO_ANTES_MECANISMOS_PI04_JSON_R01'
    backup.mkdir()
    save_new(backup/'CATALOGO_CAPACIDADES.json',CAT.read_bytes())
    if sha(backup/'CATALOGO_CAPACIDADES.json') != plan['catalogue_before_sha256']: raise ValueError('Literal preservation failed')
    save_new(CONTRACT,(PLAN/'CONTRATO_PROPUESTO.json').read_bytes())
    temporary = CAT.with_name(CAT.name+'.PI04_JSON_writing')
    save_new(temporary,(PLAN/'CATALOGO_PROPUESTO.json').read_bytes());temporary.replace(CAT)
    if sha(CAT) != plan['catalogue_after_sha256'] or sha(CONTRACT) != plan['contract_sha256'] or protected()!=current:
        raise ValueError('Postwrite verification differs; preserve files and diagnose')
    result = {**plan,'status':'INCORPORATED_PRODUCT_TOOLS_AND_REPRODUCTION_NOT_MAIN',
        'applied_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'catalogue_before_literal_backup':desc(backup/'CATALOGO_CAPACIDADES.json'),
        'actual_catalogue':desc(CAT),'actual_contract':desc(CONTRACT),'protected_critical_hashes_unchanged':True,
        'principal_adoption':False,'Native_ticks':0,'no_operational_Python_or_recipe_or_capsule_changes':True}
    save_new(proof,encoded(result));print(json.dumps({'proof':str(proof),'sha256':sha(proof),'new_ids':IDS,'Native_ticks':0,'principal_unchanged':True},ensure_ascii=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');args=ap.parse_args()
    apply() if args.aplicar else prepare()
