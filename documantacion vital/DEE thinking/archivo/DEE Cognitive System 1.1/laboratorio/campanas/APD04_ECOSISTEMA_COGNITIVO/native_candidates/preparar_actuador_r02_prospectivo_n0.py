"""Build one prospective actuator-codec patch in LAB. No DEE imports/ticks."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / 'PROPUESTA_ACTUADOR_R02_R01'


def write(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def digest(path):
    content = path.read_bytes()
    return {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def load_cli(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if OUT.exists():
        raise FileExistsError('Frozen proposal exists; no overwrite or silent revision')
    OUT.mkdir()
    members, patches = [], []

    def propose(relative, replacements):
        source = ROOT / 'sistema' / relative
        base = OUT / 'FUENTES_BASE' / relative
        base.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, base)
        before = source.read_text(encoding='utf8')
        after = before
        for old, new in replacements:
            if after.count(old) != 1:
                raise ValueError('Non-exact patch base: ' + relative + ': ' + old[:80])
            after = after.replace(old, new)
        ast.parse(after)
        target = OUT / 'sistema' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf8', newline='\n') as stream:
            stream.write(after)
        patches.append(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                       fromfile='sistema/' + relative, tofile='sistema/' + relative)))
        members.append({'file': 'sistema/' + relative, 'base': digest(base), 'proposed': digest(target)})

    propose('app/protocolo_apd04.py', [
        ("      'apd04-estado':({'modo'},{'modo'}),", "      'apd04-estado':({'modo'},{'modo'}),\n      'apd04-actuador':({'modo','version'},{'modo','version'}),"),
        ("    if 'texto'in row:", "    if mode=='apd04-actuador' and(type(row['version'])is not str or row['version']not in('R01','R02')):raise ValueError('Codec P0 fijo R01/R02; no decision por caso')\n    if 'texto'in row:"),
    ])
    configure = '''def configure_actuator(a,row):
    """Explicit external P0 transducer preparation; no learned association."""
    m=get(a);before=m.get('action_codec','R01');version=row['version']
    if version not in ACTION_CODECS:raise ValueError('Codec fijo R01/R02')
    m['action_codec']=version;save(a,m)
    return {'kind':'explicit_prepared_actuator_codec','before':before,'after':version,
       'fixed_signed_map':dict(ACTION_CODECS[version]),'new_native_ticks_in_operation':0,
       'scope':'External transduction preparation only. No RAW, clock, source cache, world reset, target or learned-policy edit.'}


'''
    propose('capacidades/ecosistema_apd04.py', [
        ("SELECT_CODEC={-1:'USE',0:'INSPECT',1:'INSPECT'}", "ACTION_CODECS={'R01':{-1:'USE',0:'INSPECT',1:'INSPECT'},\n               'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'}}\nSELECT_CODEC=ACTION_CODECS['R01']  # Historical public constant; retained for existing callers."),
        ("    if m['version']!=VERSION:raise ValueError('Otro contrato de taller; no migracion silenciosa')\n    return m", "    if m['version']!=VERSION:raise ValueError('Otro contrato de taller; no migracion silenciosa')\n    if m.get('action_codec','R01')not in ACTION_CODECS:raise ValueError('Codec de actuacion desconocido; no reparar silenciosamente')\n    return m"),
        ("allowed={'apd04-r04-admitir'", "allowed={'apd04-actuador','apd04-r04-admitir'"),
        ("       'native_answers_in_metadata':False", "       'action_codec':'R01','native_answers_in_metadata':False"),
        ("       'world_serial':m['world_serial'],'episode':m['episode'],'counters':m['counters'],'in_progress':m['in_progress'],", "       'world_serial':m['world_serial'],'episode':m['episode'],'counters':m['counters'],'in_progress':m['in_progress'],\n       'action_codec':m.get('action_codec','R01'),'fixed_signed_action_map':dict(ACTION_CODECS[m.get('action_codec','R01')]),"),
        ("def change(a,row):", configure + "def change(a,row):"),
        ("    m=get(a);before=physical(a.world);rows=[];folder=Path(directory)/'synthetic_workshop';folder.mkdir(parents=True,exist_ok=True)", "    m=get(a);codec_version=m.get('action_codec','R01');action_codec=ACTION_CODECS[codec_version]\n    before=physical(a.world);rows=[];folder=Path(directory)/'synthetic_workshop';folder.mkdir(parents=True,exist_ok=True)"),
        ("action=SELECT_CODEC.get(sign)", "action=action_codec.get(sign)"),
        ("effect={'action':action,'actuator':actuator,'new_fact':False", "effect={'action':action,'actuator':actuator,'prepared_action_codec':codec_version,'new_fact':False"),
        ("    if mode=='apd04-iniciar':return start(a,row)", "    if mode=='apd04-iniciar':return start(a,row)\n    if mode=='apd04-actuador':return configure_actuator(a,row)"),
    ])
    propose('app/usar_dee.py', [
        ('    eco_r04 = sub.add_parser("admitir-sensor-r04",', '    eco_actuator = sub.add_parser("configurar-actuador-ecosistema", help="Preparacion P0 fija; no aprende ni elige por respuesta")\n    eco_actuator.add_argument("version", choices=("R01", "R02"))\n    eco_r04 = sub.add_parser("admitir-sensor-r04",'),
        ('eco_start, eco_live, eco_change, eco_teach, eco_word, eco_r04, eco_sensor):', 'eco_start, eco_live, eco_change, eco_teach, eco_word, eco_r04, eco_sensor, eco_actuator):'),
        ('    if a == "admitir-sensor-r04":', '    if a == "configurar-actuador-ecosistema": return [{"modo": "apd04-actuador", "version": options.version}]\n    if a == "admitir-sensor-r04":'),
    ])
    with (OUT / 'PARCHE_PROPUESTO.diff').open('x', encoding='utf8', newline='\n') as stream:
        stream.write(''.join(patches))

    before_cli = load_cli(OUT / 'FUENTES_BASE/app/usar_dee.py', 'actuator_before_cli_n0')
    after_cli = load_cli(OUT / 'sistema/app/usar_dee.py', 'actuator_after_cli_n0')
    protocol = {}
    exec(compile((OUT / 'sistema/app/protocolo_apd04.py').read_text(encoding='utf8'), '<literal-only>', 'exec'), protocol)
    legacy_commands = [
        ['usar','suma','7','3'], ['ensenar','suma','1'], ['lenguaje','suma','21','alfa'],
        ['acumular','8','--demora','2'], ['componer','suma','resta','--datos','1','2','3'],
        ['meta','suma','4','6'], ['meta-paso','1'], ['admitir-apd03'],
        ['ensenar-nueva','luma','1'], ['lenguaje-nuevo','luma','19','beta'],
        ['objetivo','luma','7','3','--contexto-ambiente','1'], ['paso','2'],
        ['panel','--nuevas','--memorias'], ['ecosistema-iniciar','--semilla','42','--fuentes','2'],
        ['ecosistema-vivir','1','--sensor','independent_balanced'],
        ['ecosistema-cambio','--goal','1','--palabra','clasifica','--cargas','7','3'],
        ['calibrar-sensor-ecosistema','--familia','R03','00','01','10','11'],
    ]
    legacy = []
    for tokens in legacy_commands:
        old_options = before_cli.command_parser().parse_args(tokens)
        new_options = after_cli.command_parser().parse_args(tokens)
        old_rows, new_rows = before_cli.literal_rows(old_options), after_cli.literal_rows(new_options)
        assert vars(old_options) == vars(new_options) and old_rows == new_rows
        legacy.append({'argv': tokens, 'literal_rows_identical': new_rows})
    literal_tests = []
    for version in ('R01','R02'):
        options = after_cli.command_parser().parse_args(['configurar-actuador-ecosistema',version])
        rows = after_cli.literal_rows(options)
        for row in rows:protocol['validate_literal'](row)
        literal_tests.append({'argv':['configurar-actuador-ecosistema',version], 'rows':rows})
    negatives = [
        {'modo':'apd04-actuador','version':'R03'},
        {'modo':'apd04-actuador','version':2},
        {'modo':'apd04-actuador','version':'R02','goal':0},
        {'modo':'apd04-actuador','version':'R02','target':1},
        {'modo':'apd04-actuador','version':'R02','sign':1},
        {'modo':'apd04-actuador','version':'R02','quality':'SUCCESS'},
        {'modo':'apd04-vivir','oportunidades':1,'action_codec':'R02'},
        {'modo':'apd04-actuador','version':{'-1':'INSPECT','1':'USE'}},
    ]
    for row in negatives:
        try:protocol['validate_literal'](row)
        except ValueError:continue
        raise AssertionError('Forbidden literal accepted: '+repr(row))

    # Execute only the isolated pure P0 function against dictionaries; no DEE import.
    tree = ast.parse((OUT/'sistema/capacidades/ecosistema_apd04.py').read_text(encoding='utf8'))
    configure_node = next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='configure_actuator')
    isolated = ast.Module(body=[configure_node], type_ignores=[])
    saved = []
    example = {'objects':[{'observed':{'value':33,'version':0},'bin':-1}], 'cursor':1,'episode':27,
               'goal_tag':0, 'loads':[7,3], 'in_progress':None}
    namespace = {'ACTION_CODECS':{'R01':{-1:'USE',0:'INSPECT',1:'INSPECT'},'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'}},
                 'get':lambda a:copy.deepcopy(example), 'save':lambda a,m:saved.append(copy.deepcopy(m))}
    exec(compile(isolated,'<P0-dictionary-test-only>','exec'), namespace)
    result = namespace['configure_actuator'](None,{'modo':'apd04-actuador','version':'R02'})
    expected = copy.deepcopy(example);expected['action_codec']='R02'
    assert saved == [expected] and result['before']=='R01' and result['after']=='R02'
    signed_map = namespace['ACTION_CODECS']
    assert signed_map['R01']=={-1:'USE',0:'INSPECT',1:'INSPECT'}
    assert signed_map['R02']=={-1:'INSPECT',0:'INSPECT',1:'USE'}
    assert all(mapping.get(None) is None for mapping in signed_map.values())
    write(OUT/'PRUEBAS_N0.json',{'schema':'APD04.actuator_proposal.software_only.N0.v1',
        'AST_files':3,'legacy17':legacy,'new_literal':literal_tests,'forbidden_cases_rejected':negatives,
        'P0_dictionary_only_test':{'saved_keys_difference':['action_codec'],'cache_cursor_loads_episode_unchanged':True,
                                 'zero_is_valid_signed_emission_not_NULL':True,'NULL_maps_to_no_action_both':True},
        'native_ticks':0,'Runtime_created':False,'no_Native_equivalence_or_learning_claim':True})
    common_change = {'modo':'apd04-cambio','etiqueta_objetivo':0,'palabra':'clasifica','cargas':[7,3],
                     'mutaciones':[{'fuente':0,'valor':18},{'fuente':1,'valor':24}]}
    branches = []
    for life, feedback in [('APD04_ACTUADOR_REAL_R02','real'),('APD04_ACTUADOR_OMIT_R02','omit')]:
        steps = [{'literal':{'modo':'apd04-actuador','version':'R02'},'feedback':'omit','P0_only':True},
                 {'literal':common_change,'feedback':'omit','keep_existing_stale_cache':True}]
        for episode in range(1,11):
            if episode==6:steps.append({'literal':{'modo':'apd04-cambio','etiqueta_objetivo':1},'feedback':'omit'})
            steps.append({'literal':{'modo':'apd04-vivir','oportunidades':1,'sensor':'independent_balanced','lexico':True},
                          'feedback':feedback,'actuator':'closed','declared_opportunity':episode})
        branches.append({'life':life,'feedback':feedback,'steps':steps})
    write(OUT/'PLAN_DOS_AUX_CONGELADO_N0.json',{
        'schema':'APD04.actuator_R02.two_forks.predefined.N0.v1',
        'common_parent':'APD04_MAIN_T639374_EXPLORACION_R01',
        'parent_snapshot_sha256':'771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8',
        'parent_manifest_sha256':'5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db',
        'one_shared_prefix_not_independent_learners':True,
        'sensor':'R03 / independent_balanced; NOT new right-pair R04',
        'fixed_action_codec':'R02: -1 INSPECT;0 INSPECT;+1 USE;NULL no action',
        'freeze_before_reserve':True,'do_not_restart_workshop_or_clear_cached_versions':True,
        'branches':branches,
        'analysis_before_feedback':['first raw reader observations and Native choice','signed output','fixed transduced action'],
        'analysis_after_effect':['actual cache update or material artifact','useful consequence by predeclared evaluator',
                                  'admitted/rejected/pending receipts','references and retention','Native choice and utility over10opportunities'],
        'old_panel':'Only after10; identified diagnostic descendant perbranch; inherited old-panel protocol, not a new phase/reader search. No claim that diagnostic forks are consecutive uses in the same life.',
        'stop_rules':'Preserve every adverse future. No automatic NULL restoration, no per-response codec switch. Native owner resource supervision must not be called a cognitive criterion.',
        'full_fork_selection':'A final complete branch may be retained with own identity and documented gains/losses; never sum histories or transplant memories.',
        'new_native_ticks_by_this_plan':0,
    })
    justification = '''# ACTUADOR_R02: propuesta P0, no aprendizaje demostrado

La ruta nativa histórica declara que una consecuencia FAILURE inhibe A tanto para
la emisión −1 como para la emisión neutra0; +1 sigue la inhibición B. El codec
R01 traduce −1 a USE y0/+1 a INSPECT. Un cambio físico0↔+1 puede, por tanto,
no cambiar la acción externa. La alternativa única R02 fija −1/0→INSPECT,
+1→USE para hacer visible esa distinción. No calcula utilidad, igualdad, signo
correcto, acción objetivo ni reparación usando el target del auditor.

La elección de este codec es ingeniería externa P0 basada en el contrato
route.Failure, no conocimiento ni política aprendida por E1. Sólo un contraste
posterior de historias con consecuencias reales/omitidas podría acreditar un
cambio nativo condicionado, su utilidad, su conservación o sus pérdidas.

`apd04-actuador` sólo admite el enum R01/R02 y se ejecuta explícitamente antes de
evaluar. Persiste `action_codec` dentro del estado ambiental existente. No toca
RAW, clocks, cachés, recuerdos, geometría ni crea un mundo. Los snapshots antiguos
sin ese campo conservan exactamente la interpretación R01; un enum desconocido
se rechaza y no se repara. La vida y el entorno completos siguen siendo necesarios.

CLI propuesta: `configurar-actuador-ecosistema R02`. R01 permanece seleccionable.
El enum queda fijo durante cada bloque; no existe un override por oportunidad.
La ausencia de emisión sigue sin acción;0 es una emisión neutra válida, no silencio.

Dos ramas completas del mismo T639374, sensor R03 en ambas, conservarán el pasado
ambiental/cachés y recibirán diez oportunidades1+1 con cambio de goal después de5.
La única diferencia prospectiva del contraste es retorno real/omitido, con su
diferencia material declarada. No se importa R04 nuevo ni se limpia ningún futuro.

Esta carpeta es una propuesta N0. No se instaló en sistema ni se ejecutó DEE.
'''
    with (OUT/'JUSTIFICACION_Y_LIMITES.md').open('x',encoding='utf8') as stream:stream.write(justification)
    # Preserve the actual native route used to justify the P0 proposal, unchanged.
    route = ROOT/'sistema/capacidades/ruta_adaptativa_apd02_04.py'
    route_copy = OUT/'FUENTES_BASE/capacidades/ruta_adaptativa_apd02_04.py'
    shutil.copy2(route,route_copy)
    write(OUT/'MANIFIESTO_PROPUESTA_N0.json',{'schema':'APD04.actuator_R02.proposal.N0.v1',
        'source_and_proposed':members,'route_justification_original':digest(route_copy),
        'native_ticks':0,'Runtime_created':False,'shared_sistema_modified':False,
        'source_code_only':True,'legacy17_identical':True})
    print(json.dumps({'folder':str(OUT),'members':members,'Native_ticks':0},indent=2))


if __name__=='__main__':main()
