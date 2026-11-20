"""N0 proposal only: one REAL post-ten-work original, no material old22 panel.

Reuses the exact previous43-op exogenous calendar, not its results/state. Never
selects OMIT/favorable checkpoints, installs sources, runs or closes a plan.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/PLAN_RESERVA60_REAL_R02_CERRADO_R01.json'
BSHA='a4fdc4d2ef23d383f5accae548fc3ab25baaa3b25e4d44109bf3319197dc23fc'
OUT=HERE/'PROPUESTA_RESERVA60_WAIT_R03_REAL_N0_R01'
QUALITY='APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    if OUT.exists():raise FileExistsError('Preserve previous proposal')
    if sha(BASE)!=BSHA:raise ValueError('Exact previous frozen calendar changed')
    old=read(BASE);p=copy.deepcopy(old)
    p.update(status='DRAFT_NOT_AUTHORIZED_FOR_NATIVE',life='APD04_WAIT_R03_REAL_AUX_R05',world_id='APD04_WAIT_R03_REAL_AUX_R05',
        initial_snapshot_sha256=None,initial_tick=None,candidate_genealogy=None,
        required_prepared_action_codec='R03',required_posteffect_quality_contract=QUALITY,
        assembly_revision='APD04.reserve60.N0.R03.explicit_WAIT_quality_REAL_post10_before_panel')
    for e in p['events']:
        if 'request_id'in e:e['request_id']=e['request_id'].replace('apd04_reserve_','apd04_wait_r03_reserve_')
    p['after_window_pending']['request_id']='apd04_wait_r03_reserve_exact_pending_r01'
    p['freeze_source_paths']=list(dict.fromkeys(p['freeze_source_paths']+['sistema/app/usar_dee.py']))
    p['scope']='Continues the actual same REAL R03 original after its ten fixed opportunities, saved/STOPped and sealed FULL before material old22/new2 diagnostic panels. This proposal does not know its future state; no Native execution/installation/import/favorable prefix selection. Same43-op exogenous agenda, no cache/cursor reset, no NativeN change or source retargeting. R03 fixed three-action affordance and fixed NEW posteffect quality are inherited from that actually reached REAL original.'
    p['candidate_scope']='Pre-designated REAL arm only, not the arm with the best new score. Root must fill the real complete identity/hash/tick and explicitly authorize; adverse/incomplete REAL is preserved, not rescued from OMIT or an earlier favorable checkpoint.'
    p['coverage_and_criteria']['quality']='Two separate measures: old NEW environmental work_gain (unchanged; WAIT0), and fixed R03 quality_contract '+QUALITY+'. A WAIT is a unique formedNative0, not NULL, and is good only for irrelevant tag with unchanged task objects/loads. INSPECT/USE keep oldgain; actuatorclosed only. Generic posteffect feedback uses fixed R03quality after actual action, never the desired response.'
    p['coverage_and_criteria']['source_counts']='2→5→10→20 external objects append-only within the SAME NativeN67. Sequential two-bit source/goal view. Twenty opportunities at20-source level are sequential cursor slots, never twenty simultaneous observations or twenty Native semantic acquisitions.'
    p['coverage_and_criteria']['initial_environment_mutation']='The initial literal mutations16/25 are preserved from the prior frozen calendar. REAL short protocol also prepared16/25, so these may advance environmental versions without changing values, intentionally making caches stale under the existing change contract. They do NOT write Native memory. No claim that this is a matched R02/R03 causal comparison.'
    p['coverage_and_criteria']['first_five_core_at_each_level']='Same supplied clasifica/goal0/criterion20 and expected inherited relative reference20, but actual physical reference/history must be measured, not forced. One continuing history, not a head-to-head source-count or old/new-codec experiment.'
    p['coverage_and_criteria']['current_first_response']='Compare first formed action before feedback and subsequent actions separately. Do not redefine uniqueNative0 as unformed equalityNULL, or relabel fixedWAIT affordance as a learned strategy.'
    p['required_actual_preGO_proofs']=[
        'Actual pre-designated REAL short trajectory completed all ten work IDs; no unfinished/uncertain material request is silently skipped.',
        'Confirmed owner STOP/no live world lock and complete current snapshot+interfaces+Nativeagenda+transport/operational artifacts, with actual hashes/tick/genealogy filled before closure.',
        'No old22 or new2 standalone material diagnostic panel was run on this original before reserve. Those belong only to separately identified descendants.',
        'The actual original includes prepared actuatorR03 and exact fixedquality contract, unchanged frozen sensorR03 independent_balanced and inherited20reference inspected offline when available.',
        'If REAL is materially adverse or no longer permits these functions, preserve it. No automatic OMIT substitution, favorable snapshot import, memorystore fusion, clearing or re-teaching.',
        'All43 work IDs and final queued calibrationID are NEW to this life; current caches/cursor/episode remain its real state. A final transport-queued calibration is preserved and not counted as executed.']
    p['timing_is_prospective_no_new_budget']=True
    if len(p['events'])!=64:raise ValueError('Exactly prior64 fixed events')
    work=[e for e in p['events']if e['kind']=='material'and e['situations'][0]['modo']=='apd04-vivir']
    if len(work)!=43 or any(e['situations'][0].get('sensor')!='independent_balanced'for e in work):raise ValueError('Wrong workshop coverage')
    # Every event retains exact timing/payload/feedback; only transport IDs change.
    for x,y in zip(old['events'],p['events']):
        if{k:v for k,v in x.items()if k!='request_id'}!={k:v for k,v in y.items()if k!='request_id'}:
            raise ValueError('Changed the prior literal exposure calendar')
    spec=importlib.util.spec_from_file_location('existing_driver_no_Native',BASE.with_name('ejecutar_plan_apd04_r03.py'))
    driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    test=copy.deepcopy(p);test.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=639374)
    driver.validate_plan(test)
    OUT.mkdir();write(OUT/'PLAN_RESERVA60_WAIT_R03_REAL_DRAFT_R01.json',p)
    write(OUT/'VALIDACION_N0_Y_ALCANCE.json',{'status':'PROPOSAL_ONLY_NO_NATIVE_GO','new_native_ticks':0,
        'previous_closed_calendar_source':str(BASE),'previous_SHA256':BSHA,'unchanged_literal_events_except_transport_ids':64,
        'work':43,'duration_seconds':3600,'outer_guard_seconds':5400,'absolute_deadline_unchanged':p['deadline_utc'],
        'reserve_start_latest_UTC_unchanged':p['reserve_start_latest_utc'],'no_source_edit_no_life_created':True,
        'no_claim_of_future_REAL_completion_or_success':True})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':q.name,'sha256':sha(q),'bytes':q.stat().st_size}for q in sorted(OUT.iterdir())if q.is_file()]})
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('Unexpected Native import')
    print(json.dumps({'out':str(OUT),'Native_ticks':0,'manifest_sha256':sha(OUT/'MANIFIESTO.json')}))


if __name__=='__main__':main()
