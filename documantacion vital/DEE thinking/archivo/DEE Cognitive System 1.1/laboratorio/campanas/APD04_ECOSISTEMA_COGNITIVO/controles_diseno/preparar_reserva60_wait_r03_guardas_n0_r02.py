"""Root-requested N0 guard revision only, absolute campaign deadline unchanged."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OLD=HERE/'PROPUESTA_RESERVA60_WAIT_R03_REAL_N0_R01'
OUT=HERE/'PROPUESTA_RESERVA60_WAIT_R03_REAL_N0_R02'
DRIVER=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/EJECUTOR_WAIT_R03_SAFE_R02/ejecutar_plan_apd04_r04.py'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    if OUT.exists():raise FileExistsError('Preserve older proposal bytes')
    for m in read(OLD/'MANIFIESTO.json')['members']:
        if sha(OLD/m['file'])!=m['sha256']:raise ValueError('Previous proposal changed')
    old=read(OLD/'PLAN_RESERVA60_WAIT_R03_REAL_DRAFT_R01.json');p=copy.deepcopy(old)
    p.update(local_closing_start_seconds=4500,supervision_wall_limit_seconds=4800,closing_reserve_seconds=300,
        assembly_revision='APD04.reserve60.N0.R03.REAL.post10.guard4500_4800_close300.R02')
    p['proposed_existing_LAB_R04_driver']={'source':str(DRIVER),'sha256':sha(DRIVER),
        'scope':'Existing LAB driver revision with local_closing_start_seconds, not shared S or Native physics. Root must preserve exact executed revision when authorizing.'}
    p['coverage_and_criteria']['deadline']='No reset of campaign time. Minimum3600s window, local closing begins4500s, hard outer4800s and closing300s; absolute deadline2026-10-27T03:30:51+00:00 and latest prospective start00:50UTC remain fixed. Pending/late/unfinished work is reported, never silently completed in a substitute life.'
    p['scope']+=' R02 changes timing guards only under Root instruction: LABR04 local4500/hard4800/closing300. Still a DRAFT, with no real post10 hash/tick invented and no automatic launch.'
    if p['events']!=old['events']or p['after_window_pending']!=old['after_window_pending']:
        raise ValueError('Guard revision changed the exposure calendar')
    s=importlib.util.spec_from_file_location('LAB_R04_static_validator_only',DRIVER)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    test=copy.deepcopy(p);test.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=639374)
    m.validate_plan(test)
    text=DRIVER.read_text(encoding='utf8')
    if "plan['local_closing_start_seconds']"not in text:raise ValueError('Proposed LABR04 local guard absent')
    OUT.mkdir();write(OUT/'PLAN_RESERVA60_WAIT_R03_REAL_DRAFT_R02.json',p)
    write(OUT/'VALIDACION_N0_Y_ALCANCE.json',{'status':'DRAFT_NO_NATIVE_GO','Native_ticks':0,'no_shared_S_edit':True,
        'REAL_original_only':'APD04_WAIT_R03_REAL_AUX_R05','post10_actual_FULL_not_yet_known':True,
        'no_automatic_OMIT_or_favorable_checkpoint_substitution':True,'events_identical_prior_R01':64,
        'work_opportunities':43,'minimum_window_seconds':3600,'local_closing_start_seconds':4500,
        'outer_guard_seconds':4800,'closing_reserve_seconds':300,'deadline_unchanged':p['deadline_utc'],
        'previous_manifest_sha256':sha(OLD/'MANIFIESTO.json'),'LAB_R04_driver_sha256':sha(DRIVER)})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':q.name,'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.iterdir())if q.is_file()]})
    print(json.dumps({'out':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO.json'),'Native_ticks':0}))


if __name__=='__main__':main()
