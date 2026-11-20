"""N0 prospective revision: literal values31/14, no actor/Native execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OLD=HERE/'PROPUESTA_TRES_BRAZOS_VISTA_REAL_POST10_N0_R01'
OUT=HERE/'PROPUESTA_TRES_BRAZOS_VISTA_REAL_POST10_N0_R02'
PATCH=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01'
EXEC=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/EJECUTOR_WAIT_R03_SAFE_R03'


def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def main():
    if OUT.exists():raise FileExistsError('Never overwrite prior designs')
    for x in read(OLD/'MANIFIESTO.json')['members']:
        if sha(OLD/x['file'])!=x['sha256']:raise ValueError('Prior11/34 proposal changed')
    protocol=load('strict_proposed_body_protocol_R02_N0',PATCH/'sistema/app/protocolo_apd04.py')
    ui=load('strict_proposed_body_UI_R02_N0',PATCH/'sistema/app/usar_dee.py')
    driver=load('existing_driver_R04_R02_validation_only',EXEC/'ejecutar_plan_apd04_r04.py')
    OUT.mkdir();checks=[];removed={}
    for label in('CIRCULAR_REAL','PERSISTENTE_REAL','PERSISTENTE_OMIT'):
        old=read(OLD/('PLAN_'+label+'_DRAFT_R01.json'));p=copy.deepcopy(old)
        change=[e for e in p['events']if e['kind']=='material'and e['situations'][0]['modo']=='apd04-cambio']
        if len(change)!=1:raise ValueError('Exactly one preset environmental event')
        change[0]['situations'][0]['mutaciones']=[{'fuente':0,'valor':31},{'fuente':1,'valor':14}]
        removed[label]={}
        for key in('n0_import_proof','prior_720_guard_revision','earlier_executor_R02_status'):
            if key in p:removed[label][key]=p.pop(key)
        p['code_revision']='Prospective body-opportunity trial R02: R03action/quality plus generic fixed view enum; actual post10 REAL parent still pending.'
        p['view_policy_for_this_original']=p['required_prepared_view_policy']
        p['proposal_design_status']='FROZEN_PROSPECTIVE_LITERAL_DESIGN_R02_PENDING_ACTUAL_REAL_PARENT_AND_ROOT_GO'
        p['values_revision_reason']='Root fixed31/14 BEFORE anyNativeR03/view trial: reverses value categories relative to prior curriculum16/25 while criterion20 stays fixed. Does not clear bins/caches, force USE or deliver correct action to Native.'
        p['scope']+=' R02 is prospective values31/14 (superseding unexecuted11/34), not a retrospective metric change. Correctness/freshness and NEWgain stay separate; maintenance is not relabeled as gain.'
        t=copy.deepcopy(p);t.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=0)
        driver.validate_plan(t)
        for e in p['events']:
            if e['kind']=='command':ui.literal_rows(ui.command_parser().parse_args(e['argv']))
            elif e['kind']=='material':
                for r in e['situations']:protocol.validate_literal(r)
        if [e['at_seconds']for e in p['events']]!=[e['at_seconds']for e in old['events']]:raise ValueError('Calendar changed')
        if p['initial_snapshot_sha256']is not None or p['initial_tick']is not None:raise ValueError('Invented future')
        write(OUT/('PLAN_'+label+'_DRAFT_R02.json'),p)
        checks.append({'arm':label,'six_work_unchanged':True,'calendar_unchanged':True,
            'mutations_fixed_before_any_Native_trial':[31,14],'criterion_unchanged':20,
            'future_parent_SHA_tick_NULL':True,'Native_ticks':0})
    c=read(OLD/'CRITERIOS_Y_ASISTENCIA_PROSPECTIVOS_R01.json')
    c['schema']='APD04.body_opportunity_and_consequences.prospective.N0.R02'
    c['fixed_preparation']['exogenous_values']={'source0':31,'source1':14}
    c['prospective_values_revision']={'old_unexecuted':[11,34],'new_fixed':[31,14],
        'criterion':20,'reason':'Invert categories relative to the declared preceding16/25 curriculum, so prior correct same-bin maintenance does not mechanically prevent every new-bin gain. Root fixed this before Native trials, not from their outcomes.',
        'no_cache_bin_cursor_or_Native_memory_edit':True,
        'observation_limit':'Actual prior bins/caches and Native reference remain the real FULL parent state. New values enter a Native comparison only after Native selects USE and the fixed apparatus supplies its acquired environmental cache; stale cache may yield an incorrect action and is retained as failure.'}
    c['frozen_analysis'].append('Keep fresh/current-version correctness, correct maintenance, old_NEWgain and WAITquality distinct. A correct already-binned result is maintenance and remains old_gain0; neither error nor improvement is hidden by renaming.')
    c['validation']=checks
    write(OUT/'CRITERIOS_Y_ASISTENCIA_PROSPECTIVOS_R02.json',c)
    write(OUT/'REVISION_N0_R02.json',{'status':'FROZEN_DESIGN_NOT_EXECUTION_GO','Native_ticks':0,'shared_S_edits':False,
        'prior11_34_folder':str(OLD),'prior_manifest_sha256':sha(OLD/'MANIFIESTO.json'),
        'three_arms_only_six_work_each_same_calendar':True,'literal_mutations_before_evaluation':[31,14],
        'obsolete_short_import_metadata_removed':removed,
        'reason_for_cleanup':'A T639374 pre-short import proof is NOT a proof of the still-unknown actual post10REAL parent. Source hashes remain valid proposed dependencies, not future-state witnesses.'})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':q.name,'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.iterdir())if q.is_file()]})
    print(json.dumps({'out':str(OUT),'plans':3,'Native_ticks':0,'manifest_sha256':sha(OUT/'MANIFIESTO.json')}))


if __name__=='__main__':main()
