"""One P0 view affordance proposal; no Native, shared edits or current-life edits.

The environment may retain the same source after a formed native INSPECT.
It never examines relevance, value, cache, quality or goal to move the cursor.
Earlier ACT_R03 proposal and all circular historical protocols remain intact.
"""
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
BASE = HERE/'PROPUESTA_ACTUADOR_R03_R02'
OUT = HERE/'PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if OUT.exists():
        raise FileExistsError('Preserve the proposed revision, never overwrite.')
    manifest = json.loads((BASE/'MANIFIESTO_PROPUESTA_N0.json').read_bytes())
    assert sha(BASE/'MANIFIESTO_PROPUESTA_N0.json') == 'cc097318ed0684274bc6487768cfe65791e2ac7b157c49e8e13ffbc138e09fa4'
    OUT.mkdir()
    transformed = {}
    protocol = (BASE/'sistema/app/protocolo_apd04.py').read_text(encoding='utf8')
    protocol = replace_once(protocol,
        "      'apd04-actuador':({'modo','version'},{'modo','version'}),",
        "      'apd04-actuador':({'modo','version'},{'modo','version'}),\n      'apd04-vista':({'modo','politica'},{'modo','politica'}),")
    protocol = replace_once(protocol,
        "    if 'texto'in row:",
        "    if mode=='apd04-vista' and(type(row['politica'])is not str or row['politica']not in('circular_R01','inspeccion_persistente')):raise ValueError('Vista P0 fija; no direccion de fuente, objetivo o respuesta por caso')\n    if 'texto'in row:")
    transformed['sistema/app/protocolo_apd04.py'] = protocol
    ui = (BASE/'sistema/app/usar_dee.py').read_text(encoding='utf8')
    ui = replace_once(ui, '    eco_actuator = sub.add_parser("configurar-actuador-ecosistema",',
        '    eco_view = sub.add_parser("configurar-vista-ecosistema", help="Oportunidad P0 fija de retener tras INSPECT; no elige la fuente por utilidad")\n    eco_view.add_argument("politica", choices=("circular_R01", "inspeccion_persistente"))\n    eco_actuator = sub.add_parser("configurar-actuador-ecosistema",')
    ui = replace_once(ui, 'eco_r04, eco_sensor, eco_actuator):', 'eco_r04, eco_sensor, eco_actuator, eco_view):')
    ui = replace_once(ui, '    if a == "configurar-actuador-ecosistema":',
        '    if a == "configurar-vista-ecosistema": return [{"modo": "apd04-vista", "politica": options.politica}]\n    if a == "configurar-actuador-ecosistema":')
    transformed['sistema/app/usar_dee.py'] = ui
    eco = (BASE/'sistema/capacidades/ecosistema_apd04.py').read_text(encoding='utf8')
    eco = replace_once(eco, "SELECT_CODEC=ACTION_CODECS['R01']", "VIEW_POLICIES=('circular_R01','inspeccion_persistente')\nSELECT_CODEC=ACTION_CODECS['R01']")
    eco = replace_once(eco, "    return m\n\ndef validate(a,row):", "    if m.get('view_policy','circular_R01')not in VIEW_POLICIES:raise ValueError('Vista desconocida; no reparar cursor o cache')\n    return m\n\ndef validate(a,row):")
    eco = replace_once(eco, "allowed={'apd04-actuador',", "allowed={'apd04-vista','apd04-actuador',")
    eco = replace_once(eco, "    if m.get('action_codec','R01')=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed')\n    return result",
        "    if m.get('action_codec','R01')=='R03':result.update(quality_contract=QUALITY_R03,quality_domain_actuator='closed')\n    if 'view_policy'in m:result['view_policy']=m['view_policy']\n    return result")
    pure = '''def next_cursor_prepared_view(policy,cursor,source_count,action,formed_unique,actuator):
    """P0 environment transition only; no object, cache, value, goal or score input."""
    if policy not in VIEW_POLICIES:raise ValueError('Unknown fixed view')
    if type(cursor)is not int or type(source_count)is not int or source_count<1 or not 0<=cursor<source_count:raise ValueError('Invalid current cursor; never reset it')
    retain=policy=='inspeccion_persistente'and action=='INSPECT'and formed_unique is True and actuator=='closed'
    return cursor if retain else(cursor+1)%source_count


def configure_view(a,row):
    """External P0 affordance selection, not learned source addressing."""
    m=get(a);policy=row['politica'];before=m.get('view_policy','circular_R01')
    if policy not in VIEW_POLICIES:raise ValueError('Fixed view enum only')
    m['view_policy']=policy;save(a,m)
    return {'kind':'explicit_prepared_environment_view','before':before,'after':policy,
        'new_native_ticks_in_operation':0,'cursor_preserved':m['cursor'],
        'scope':'P0 affordance only. No RAW/clock, cache, object, loads or cursor reset. Only later formed INSPECT may retain the current source; Native selects the emission.'}


'''
    eco = replace_once(eco, 'def task_env_signature(m):', pure+'def task_env_signature(m):')
    eco = replace_once(eco,
        "        m['cursor']=(m['cursor']+1)%len(m['objects']);m['in_progress']=None;save(a,m)",
        "        cursor_before=m['cursor'];view_policy=m.get('view_policy','circular_R01')\n        m['cursor']=next_cursor_prepared_view(view_policy,cursor_before,len(m['objects']),action,formed_native_choice(sign,selected['reader']),actuator);m['in_progress']=None;save(a,m)")
    eco = replace_once(eco, '        rows.append(result_row)',
        "        if view_policy=='inspeccion_persistente':\n            result_row.update(view_policy=view_policy,cursor_before=cursor_before,cursor_after=m['cursor'],\n                cursor_rule='P0 persistent view retains only formed native INSPECT with closed actuator; USE/WAIT advance. NULL, ambiguity or nulled output advance by declared environmental default, not intelligent Native choice.')\n        rows.append(result_row)")
    eco = replace_once(eco, "    if mode=='apd04-actuador':return configure_actuator(a,row)",
        "    if mode=='apd04-vista':return configure_view(a,row)\n    if mode=='apd04-actuador':return configure_actuator(a,row)")
    transformed['sistema/capacidades/ecosistema_apd04.py'] = eco
    members = []
    for row in manifest['members']:
        relative = row['file'];base = BASE/relative;target = OUT/relative
        assert sha(base) == row['proposed_sha256']
        target.parent.mkdir(parents=True, exist_ok=True)
        before = base.read_text(encoding='utf8');after = transformed[relative]
        ast.parse(after)
        with target.open('x', encoding='utf8', newline='\n') as stream:stream.write(after)
        original = OUT/'BASE_ACT_R03_R02'/relative
        original.parent.mkdir(parents=True, exist_ok=True);shutil.copy2(base, original)
        patch = OUT/'diff'/((relative.replace('/','__'))+'.patch')
        patch.parent.mkdir(parents=True, exist_ok=True)
        with patch.open('x', encoding='utf8', newline='\n') as stream:
            stream.write(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),fromfile='accepted_ACT_R03/'+relative,tofile='proposed_persistent_view/'+relative)))
        members.append({'file':relative,'base_sha256':sha(base),'proposed_sha256':sha(target)})
    # Extract pure transition only; importing the ecosystem would load Native.
    module = ast.parse(eco)
    fn = next(n for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='next_cursor_prepared_view')
    namespace={'VIEW_POLICIES':('circular_R01','inspeccion_persistente')}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pure-N0-view-transition>','exec'),namespace)
    transition=namespace['next_cursor_prepared_view'];cases=[]
    for cursor in range(3):
        for action in ('INSPECT','USE','WAIT',None):
            for formed in (False,True):
                for actuator in ('closed','nulled'):
                    old=transition('circular_R01',cursor,3,action,formed,actuator)
                    assert old==(cursor+1)%3
                    actual=transition('inspeccion_persistente',cursor,3,action,formed,actuator)
                    expected=cursor if action=='INSPECT'and formed and actuator=='closed'else(cursor+1)%3
                    assert actual==expected
                    cases.append({'cursor':cursor,'action':action,'formed_unique':formed,'actuator':actuator,'circular':old,'persistent':actual})
    assert [a.arg for a in fn.args.args]==['policy','cursor','source_count','action','formed_unique','actuator']
    forbidden={'tag','goal','value','observed','cache','quality','useful','correct'}
    assert not ({n.id for n in ast.walk(fn)if isinstance(n,ast.Name)} & forbidden)
    proto=load('persistent_view_literal_only',OUT/'sistema/app/protocolo_apd04.py')
    for policy in namespace['VIEW_POLICIES']:assert proto.validate_literal({'modo':'apd04-vista','politica':policy})
    invalid=[{'modo':'apd04-vista','politica':'auto'}, {'modo':'apd04-vista','politica':'inspeccion_persistente','fuente':0},
        {'modo':'apd04-vista','politica':'inspeccion_persistente','etiqueta_objetivo':1}]
    for row in invalid:
        try:proto.validate_literal(row)
        except ValueError:pass
        else:raise AssertionError('Target-aware or free cursor directive accepted')
    old_ui=load('view_legacy_ui_only',BASE/'sistema/app/usar_dee.py');new_ui=load('view_candidate_ui_only',OUT/'sistema/app/usar_dee.py')
    legacy=[['configurar-actuador-ecosistema',v]for v in ('R01','R02','R03')]+[
        ['ecosistema-vivir','1'],['ecosistema-vivir','2','--sensor','independent_balanced'],
        ['ecosistema-cambio','--goal','0'],['panel','--nuevas','--memorias'],['palabra-ecosistema','clasifica']]
    for argv in legacy:assert old_ui.literal_rows(old_ui.command_parser().parse_args(argv))==new_ui.literal_rows(new_ui.command_parser().parse_args(argv))
    for policy in namespace['VIEW_POLICIES']:
        assert new_ui.literal_rows(new_ui.command_parser().parse_args(['configurar-vista-ecosistema',policy]))==[{'modo':'apd04-vista','politica':policy}]
    emit(OUT/'PRUEBAS_SOFTWARE_N0.json',{'AST_valid':True,'pure_transition_cases':cases,'legacy_cli_identical':len(legacy),
        'strict_invalid_cases_rejected':len(invalid),'new_native_ticks':0,'Runtime_created':False,
        'functions_tested_without_importing_Native':True,'shared_sistema_modified':False,'earlier_proposals_unchanged':True})
    emit(OUT/'CONTROLES_PROSPECTIVOS_NO_EJECUTADOS.json',{
        'status':'PROPOSAL_ONLY_NOT_NATIVE_GO','parent':'Actual complete reached R03 post10 REAL FULL, subject to Root compatibility decision; never replace a diverged future.',
        'minimum_affordance_contrast':{'forks':2,'conditions':['circular_R01','inspeccion_persistente'],
            'common':'Same parent, codecR03, sensorR03, fixed material schedule/goal/values, real feedback; only fixed view policy differs.',
            'dose':'4 single opportunities each, predeclared timing; no source reset, retargeting or per-response stage selection.',
            'measure':['formed Native sign/action','source before/after','INSPECT then USE on same source if actually emitted','work_gain separate from quality','Native receipts admitted/rejected','old-capacity panel in diagnostic copies only']},
        'consequence_learning_contrast_if_justified_later':{'forks':2,'conditions':['persistent+real','persistent+omit'],
            'scope':'Same prepared affordance, sole difference generic consequence return; not proof of learned policy from installation.'},
        'negative_cases':['Repeated formed INSPECT may dwell indefinitely; no hidden escape timer or correct-stage fallback.',
            'NULL/ambiguous output advances by fixed environmental default, not an intelligent WAIT.',
            'USE without a valid learned/useful response remains failure; no cache injection.',
            'Different source exposure after actions is a real environmental consequence, not matched future stimuli.'],
        'no_Native_executed':True,'no_plan_or_checkpoint_of_current_R03_modified':True})
    emit(OUT/'MANIFIESTO_PROPUESTA_N0.json',{'schema':'APD04.P0.persistent_inspection_view.N0.r01',
        'members':members,'new_native_ticks':0,'Runtime_created':False,'shared_sistema_modified':False,
        'cursor_default_for_all_missing_metadata':'circular_R01','no_existing_cursor_or_cache_reset':True,
        'scope':'External environmental affordance, not learning, free source addressing or Native attention acquired.'})
    shutil.copy2(__file__,OUT/Path(__file__).name)
    print(json.dumps({'proposal':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO_PROPUESTA_N0.json'),
        'pure_transition_cases':len(cases),'legacy_cli_identical':len(legacy),'new_native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
