"""One authorized panel24 on a full diagnostic descendant, never on the seed.

N0 preparation uses the installed importer/UI. Native execution separately
requires the Root token AND an externally coordinated free owner slot.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3];S=ROOT/'sistema'
LAB=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
LIFE='APD04_SEMILLA_PANEL24_DIAG_R01'
OUT=EV/'SEMILLA_PANEL24_DIAGNOSTICO_R01'
BUNDLE=HERE/'EJECUTOR_WAIT_R03_SAFE_R03'


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def requests(path):
    con=sqlite3.connect(Path(path).as_uri()+'?mode=ro&immutable=1',uri=True)
    try:return con.execute('SELECT id,payload,payload_sha,status,result FROM requests ORDER BY id').fetchall()
    finally:con.close()


def prepare():
    if OUT.exists()or(S/'estado/vidas'/LIFE).exists():raise FileExistsError('Preserve the attempted diagnostic; no repeat or replacement.')
    seed_record=S/'estado/vidas/APD04_SEMILLA_COLABORADOR_R01/VIDA.json'
    seal=read(EV/'SEMILLA_REGISTRO_LOCALIZADOR_N0_R01/SELLO_COMPLETO_N0/CORTE_COMPLETO_POSTSTOP.json')
    pair=Path(seal['pair']['directory']).resolve(strict=True)
    verifier=load('seed_diag_existing_pair_verifier',S/'app/importacion_emparejada.py')
    _,manifest,verification=verifier.verify_export(pair)
    if manifest['life_id']!='APD04_SEMILLA_COLABORADOR_R01'or manifest['snapshot_sha256']!='52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc':
        raise ValueError('Only the prospectively selected exact unprobed seed is accepted.')
    ui=load('seed_diag_existing_UI',S/'app/usar_dee.py')
    observer=load('seed_diag_pure_observer',S/'capacidades/observador_causal_retrospectivo_01.py')
    config=dict(ui.read(ui.selected_config_path(ROOT)))
    config.update(source_alias='APD04_SEMILLA_PANEL_DIAGNOSTIC_ONLY',source_life=manifest['life_id'],
        source_tick=manifest['physical']['tick'],source_snapshot_sha256=manifest['snapshot_sha256'],
        paired_export_manifest_sha256=sha(pair/'EXPORTACION_SERVICIO.json'),
        source_paired_export_manifest=(pair/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    immutable={str(seed_record):sha(seed_record),str(S/read(seed_record)['snapshot']):sha(S/read(seed_record)['snapshot']),
        str(S/'estado/ACTIVO.json'):sha(S/'estado/ACTIVO.json'),str(pair/'EXPORTACION_SERVICIO.json'):sha(pair/'EXPORTACION_SERVICIO.json')}
    OUT.mkdir();shutil.copy2(__file__,OUT/Path(__file__).name)
    emit(OUT/'ANTES_IMPORTACION_N0.json',{'verification':verification,'source_manifest':str(pair/'EXPORTACION_SERVICIO.json'),
        'source_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'local_config':config,'protected_seed':immutable,
        'new_native_ticks':0,'owner_started':False,'material_queries':0})
    backend=ui.OriginalBackend(ROOT,config);session=ui.Supervisor(ROOT,LIFE,backend,config)
    with ui.SessionLock(backend.protocol_home/LIFE/'SUPERVISOR.lock'):card=session.open(new=True)
    parent=observer.Snapshot(pair/'VIDA.deetsnap.gz',verify_checksum=False)
    child=observer.Snapshot(S/card['snapshot'],verify_checksum=False)
    assert parent.raw==child.raw and parent.clocks==child.clocks
    assert parent.channels==child.channels and parent.pending==child.pending and parent.receipts==child.receipts
    assert requests(pair/'cola.sqlite3')==requests(S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3')
    assert backend.process is None and not session.owned and not session.state.get('pending_material')
    assert all(sha(p)==h for p,h in immutable.items())
    emit(OUT/'IMPORTACION_COMPLETA_N0.json',{'record':card,'protocol':session.state,'parent_full':str(pair),
        'parent_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'physical_and_operational_equal':True,
        'new_native_ticks':0,'owner_started':False,'protected_seed_unchanged':True,
        'scope':'Independent diagnostic trajectory from complete seed, not material queries or extra knowledge attributed to the seed.'})
    template=LAB/'controles_diseno/PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R05/PLAN_WAIT_R03_REAL_PANEL_DIAGNOSTICO_DRAFT_R05.json'
    plan=read(template)
    plan.update(status='CLOSED_FOR_EXECUTION',life=LIFE,world_id=card['world_id'],
        initial_tick=card['physical']['tick'],initial_snapshot_sha256=card['snapshot_sha256'],
        proposed_identity_not_yet_imported=False,local_closing_start_seconds=600,
        owner_cleanup_budget_seconds=300,required_parent_complete_pair=pair.relative_to(ROOT).as_posix(),
        required_parent_snapshot_sha256=manifest['snapshot_sha256'],required_parent_tick=manifest['physical']['tick'],
        scope='Root-authorized one diagnostic fork of full unprobed collaborator seed: old16+MA6 then two APD04 words. No development/seed material intervention. No retries or reader adjustment.')
    for event in plan['events']:
        if event['kind']in('command','material'):event['request_id']=event['request_id'].replace('apd04_wait_real_r02','apd04_seed_diag24_r01')
    driver=load('seed_diag_literal_validator_only',BUNDLE/'ejecutar_plan_apd04_r04.py');driver.validate_plan(plan)
    ast.parse(Path(__file__).read_text(encoding='utf8'))
    emit(OUT/'PLAN_PANEL24_CERRADO_R01.json',plan)
    print(json.dumps({'diagnostic_life':LIFE,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],
        'new_native_ticks':0,'material_queries':0,'plan':str(OUT/'PLAN_PANEL24_CERRADO_R01.json')},ensure_ascii=False),flush=True)


def execute():
    if not(OUT/'PLAN_PANEL24_CERRADO_R01.json').is_file():raise ValueError('The complete diagnostic import is not prepared.')
    for item in read(HERE/'PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01/MANIFIESTO_PROPUESTA_N0.json')['members']:
        if sha(ROOT/item['file'])!=item['proposed_sha256']:raise ValueError('Frozen source bytes differ; no Native.')
    seed_paths=[S/'estado/vidas/APD04_SEMILLA_COLABORADOR_R01/VIDA.json',S/read(S/'estado/vidas/APD04_SEMILLA_COLABORADOR_R01/VIDA.json')['snapshot']]
    protected={str(p):sha(p)for p in seed_paths}
    command=[sys.executable,'-I','-B','-X','utf8',str(BUNDLE/'supervisar_plan_apd04_r04.py'),
        '--root',str(ROOT),'--plan',str(OUT/'PLAN_PANEL24_CERRADO_R01.json'),
        '--out',str(OUT/'EJECUCION_NATIVE'),'--root-go','APD04_LITERAL_PLAN_CLOSED']
    result=subprocess.run(command,cwd=Path(sys.executable).parent)
    emit(OUT/'SEMILLA_PROTEGIDA_TRAS_DIAGNOSTICO.json',{'protected_before':protected,
        'protected_after':{str(p):sha(p)for p in seed_paths},'seed_unchanged':all(sha(p)==h for p,h in protected.items()),
        'native_wrapper_exit_code':result.returncode,'no_sameID_reput_or_restore':True})
    if not all(sha(p)==h for p,h in protected.items()):raise ValueError('Protected seed changed; preserve the actual evidence.')
    return result.returncode


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare-n0',choices=('ROOT_GO_SEED_PANEL24_FORK_N0',))
    mode.add_argument('--execute-after-slot',choices=('ROOT_GO_SEED_PANEL24_NATIVE_AND_SLOT_FREE',))
    args=parser.parse_args()
    if args.prepare_n0:prepare()
    else:raise SystemExit(execute())
