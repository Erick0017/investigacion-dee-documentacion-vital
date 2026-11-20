"""Prospective N0 source revision: ACT_R03 plus dormant optional P0 view.

The imported children, material curriculum, circular default and wall guards
are unchanged. No apd04-vista command is present in these first two histories.
Earlier executor R02 is preserved and was not executed Native.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE/'EJECUTOR_WAIT_R03_SAFE_R02'
TARGET = HERE/'EJECUTOR_WAIT_R03_SAFE_R03'
PROPOSAL = HERE/'PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01'
PROPOSAL_SHA = 'd746f0612f1ede4dea72e00a8ac4941d56540833670b52cab3cbc0d86b3ea53c'
EXPECTED = {
    'sistema/app/protocolo_apd04.py':'f66989c3d9fb6779029d6ba626f4c366633d4f9d97006ae5e42f910dac3f0fe5',
    'sistema/capacidades/ecosistema_apd04.py':'6e829bc1ec7c5920613878718068b5b158d99993cec56fafa7c79e3ba5a31013',
    'sistema/app/usar_dee.py':'a63e4a9fba9b675c9beac7a4fabfc11c852b36aa508d00ba257052f87451e594'}
EV = ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def check_proposal():
    assert sha(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json')==PROPOSAL_SHA
    assert {r['file']:r['proposed_sha256']for r in read(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json')['members']}==EXPECTED
    assert all(sha(PROPOSAL/p)==h for p,h in EXPECTED.items())


def close_n0():
    check_proposal()
    if TARGET.exists():raise FileExistsError('Preserve the existing revision; never overwrite.')
    TARGET.mkdir()
    for path in BASE.iterdir():
        if path.is_file()and path.name not in('MANIFIESTO_N0.json',)and not path.name.endswith('_CERRADO_R02.json'):
            shutil.copy2(path,TARGET/path.name)
    driver=load('wait_r03_sourceonly_driver',TARGET/'ejecutar_plan_apd04_r04.py')
    ui=load('wait_r03_sourceonly_proposed_ui',PROPOSAL/'sistema/app/usar_dee.py')
    checks=[]
    for branch in('REAL','OMIT'):
        source=BASE/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R02.json'
        plan=read(source)
        assert plan['local_closing_start_seconds']==600 and plan['supervision_wall_limit_seconds']==900
        assert plan['duration_seconds']==240
        assert not any(e.get('situations',[{}])[0].get('modo')=='apd04-vista'for e in plan['events'])
        assert not any(e.get('argv',[None])[0]=='configurar-vista-ecosistema'for e in plan['events'])
        plan.update(required_exact_installed_source_hashes=EXPECTED,
            code_revision='ACT_R03 plus optional persistent view present but NOT configured',
            view_policy_for_this_original='circular_R01 by missing metadata, unchanged from earlier histories',
            earlier_executor_R02_status='N0 preserved, not Native executed',native_GO_still_required=True)
        driver.validate_plan(plan)
        for event in plan['events']:
            if event['kind']=='command':ui.literal_rows(ui.command_parser().parse_args(event['argv']))
        target=TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R03.json'
        emit(target,plan)
        checks.append({'branch':branch,'source_sha256':sha(source),'closed_sha256':sha(target),
            'events_exactly_unchanged':plan['events']==read(source)['events'],
            'initial_snapshot_exactly_unchanged':plan['initial_snapshot_sha256']==read(source)['initial_snapshot_sha256']})
    # Reuse the post10-only importer; only explicit source/output revision changes.
    helper=HERE/'importar_derivados_post10_wait_r03_n0_r01.py'
    text=helper.read_text(encoding='utf8').replace('HERE = Path(__file__).resolve().parent\n','HERE = Path(__file__).resolve().parent.parent\n')
    text=text.replace("HERE/'EJECUTOR_WAIT_R03_SAFE_R02'","HERE/'EJECUTOR_WAIT_R03_SAFE_R03'")
    text=text.replace("f'WAIT_R03_{branch}_ORIGINAL_R02'","f'WAIT_R03_{branch}_ORIGINAL_R03'")
    text=text.replace("HERE/'PROPUESTA_ACTUADOR_R03_R02/MANIFIESTO_PROPUESTA_N0.json'","HERE/'PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01/MANIFIESTO_PROPUESTA_N0.json'")
    ast.parse(text)
    with(TARGET/'importar_derivados_post10_wait_r03_n0_r02.py').open('x',encoding='utf8',newline='\n')as stream:stream.write(text)
    shutil.copy2(helper,TARGET/'BASE_importar_derivados_post10_wait_r03_n0_r01.py')
    shutil.copy2(__file__,TARGET/Path(__file__).name)
    for relative in EXPECTED:
        target=TARGET/'FUENTES_PROPUESTAS'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(PROPOSAL/relative,target)
    emit(TARGET/'REVISION_PROSPECTIVA_N0_R03.json',{'new_native_ticks':0,'owners_started':0,
        'shared_sistema_modified':False,'required_exact_source_hashes':EXPECTED,
        'source_proposal_manifest_sha256':PROPOSAL_SHA,'checks':checks,
        'scope':'New executed source revision only when Root later authorizes Native. Optional P0 view is inactive; no earlier physical result is attributed to these bytes.',
        'no_view_configuration_in_first_two_histories':True,'Native_GO_still_required':True,
        'default_circular_R01_for_all_old_metadata_preserved':True,
        'no_runtime_geometry_cache_cursor_clock_or_memory_edit':True})
    emit(TARGET/'PROPUESTA_DOS_BRAZOS_VISTA_POST10_NO_EJECUTADA.json',{
        'status':'DRAFT_NOT_AUTHORIZED_FOR_NATIVE','parent_complete_pair':None,
        'required_parent':'The SAME actual stopped/sealed post10 REAL original, only if operationally usable. No such cut is asserted to exist yet.',
        'parent_snapshot_sha256':None,'parent_tick':None,
        'branches':[{'prospective_life':'APD04_VISTA_PERSISTENTE_REAL_R01','feedback':'real'},
                    {'prospective_life':'APD04_VISTA_PERSISTENTE_OMIT_R01','feedback':'omit'}],
        'common_prepared_factors':{'view_policy':'inspeccion_persistente','action_codec':'R03',
            'sensor':'independent_balanced','actuator':'closed','lexico':True,
            'no_cache_reset':True,'no_cursor_reset':True,'no_automatic_USE':True},
        'fixed_common_schedule':[{'at_seconds':0,'literal':{'modo':'apd04-vista','politica':'inspeccion_persistente'},'feedback':'omit'},
            {'at_seconds':1,'literal':{'modo':'apd04-cambio','etiqueta_objetivo':0,
                'mutaciones':[{'fuente':0,'valor':17},{'fuente':1,'valor':26}]},'feedback':'omit'},
            *[{'at_seconds':t,'literal':{'modo':'apd04-vivir','oportunidades':1,
                'sensor':'independent_balanced','lexico':True,'desacoplado':False},
                'feedback':'branch_fixed_real_or_omit'}for t in(15,35,55,75)]],
        'prospective_timing_only':{'minimum_window_seconds':120,'local_stop_start_seconds':600,
            'outer_hard_seconds':900,'cleanup_budget_seconds':300,'absolute_campaign_deadline_unchanged':'2026-10-27T03:30:51+00:00'},
        'comparison':'Only generic postaction consequence return differs; first Native choice must precede it. Different later environmental observations may legitimately follow different Native actions.',
        'measure':['Native sign and unique formation','INSPECT/WAIT/USE/NULL denominators',
            'source retention/advance without relevance-dependent retargeting','new and stale observed versions',
            'work_gain versus new_quality separately','INSPECT followed by USE only if both actually emitted',
            'admission/rejection and physical/capacity losses'],
        'not_learning_evidence':['Installing the view','cursor retention designed by host',
            'external cache exposure','correcting a stage or triggering USE automatically'],
        'negative_protected':['Repeated INSPECT can dwell indefinitely; no hidden escape.',
            'NULL advances by environmental default, never an intelligent WAIT.',
            'Incorrect USE or absent response remains a failure.'],
        'old22_new2_panel_only_on_diagnostic_descendants':True,
        'Root_new_GO_required_for_import_and_execution':True,'new_native_ticks':0,'owners_started':0,
        'scope':'A proposed later independent variant, not a modification or result of the already closed circular R03 histories.'})
    emit(TARGET/'MANIFIESTO_N0.json',{'members':[{'file':p.relative_to(TARGET).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
        for p in sorted(TARGET.rglob('*'))if p.is_file()]})
    print(json.dumps({'bundle':str(TARGET),'manifest_sha256':sha(TARGET/'MANIFIESTO_N0.json'),'new_native_ticks':0},ensure_ascii=False))


def execute(branch):
    check_proposal()
    if not all(sha(ROOT/p)==h for p,h in EXPECTED.items()):raise ValueError('Root exact joint source patch is not installed; no Native.')
    out=EV/f'WAIT_R03_{branch}_ORIGINAL_R03'
    command=[sys.executable,'-I','-B','-X','utf8',str(TARGET/'supervisar_plan_apd04_r04.py'),
        '--root',str(ROOT),'--plan',str(TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R03.json'),
        '--out',str(out),'--root-go','APD04_LITERAL_PLAN_CLOSED']
    code=subprocess.run(command,cwd=Path(sys.executable).parent).returncode
    if code:return code
    final=read(out/'TRAYECTORIA/RESULTADO.json')
    if(final['error']or not final['owner_stop_confirmed']or final['final_protocol'].get('pending_material')
        or final['final_protocol'].get('uncertain_preserved')or not final['frozen_sources_unchanged']):
        raise ValueError('Actual stopped continuation is not established; preserve without replay.')
    plan=read(TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R03.json')
    work_ids={e['request_id']for e in plan['events']if e.get('situations',[{}])[0].get('modo')=='apd04-vivir'}
    events=[json.loads(line)for line in(out/'TRAYECTORIA/EVENTOS.jsonl').read_text(encoding='utf8').splitlines()]
    rows=[e for e in events if e['kind']=='scheduled_material_result'and e.get('requested_id')in work_ids]
    if len(rows)!=10 or any(e['result'].get('request',e['result']).get('status')!='completed'for e in rows):
        raise ValueError('Not all ten work requests completed; no full-completion assertion.')
    card=final['final_record'];target=f"{card['life_id']}_T{card['physical']['tick']}_POST10_PRE_PANEL_R01"
    sealer=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/sellar_corte_poststop_apd04_n0_r01.py'
    command=[sys.executable,'-I','-B','-X','utf8',str(sealer),'--root',str(ROOT),'--life',card['life_id'],
        '--tick',str(card['physical']['tick']),'--snapshot-sha256',card['snapshot_sha256'],
        '--target-name',target,'--out',str(out/'SELLO_POST10_N0'),
        '--scope','Actual ACT_R03 circular original post10 before material panel. Optional persistent view not configured.',
        '--root-go','APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
    subprocess.run(command,cwd=Path(sys.executable).parent,check=True)
    print(json.dumps({'branch':branch,'life':card['life_id'],'tick':card['physical']['tick'],
        'snapshot_sha256':card['snapshot_sha256'],'post10_seal':str(out/'SELLO_POST10_N0'),
        'persistent_view_configured':False,'material_panel_in_original':False},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--close-n0',action='store_true')
    mode.add_argument('--execute-after-go',choices=('ROOT_GO_WAIT_R03_NATIVE_R03',))
    parser.add_argument('--branch',choices=('REAL','OMIT'))
    args=parser.parse_args()
    if args.close_n0:close_n0()
    else:
        if args.branch is None:parser.error('One explicit branch is required, never selected by score.')
        raise SystemExit(execute(args.branch))
