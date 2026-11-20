"""Prospective N0 only: three six-op body/feedback conditions, one REAL past.

No source installation, Native import, life creation, plan closure or ticks.
Post10 REAL does not yet exist: all real future hashes/ticks stay explicitNULL.
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
OUT=HERE/'PROPUESTA_TRES_BRAZOS_VISTA_REAL_POST10_N0_R01'
PATCH=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01'
PATCH_SHA='d746f0612f1ede4dea72e00a8ac4941d56540833670b52cab3cbc0d86b3ea53c'
EXEC=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/native_candidates/EJECUTOR_WAIT_R03_SAFE_R03'
PARENT_LIFE='APD04_WAIT_R03_REAL_AUX_R05'
QUALITY='APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def make(label,policy,feedback):
    base=read(EXEC/'PLAN_WAIT_R03_REAL_ORIGINAL_CERRADO_R03.json')
    life=PARENT_LIFE if label=='CIRCULAR_REAL'else'APD04_VISTA_'+label+'_POST10_REAL_R01'
    p=copy.deepcopy(base);prefix='apd04_vista_'+label.lower()+'_post10_r01_'
    p.update(status='DRAFT_NOT_AUTHORIZED_FOR_NATIVE',life=life,world_id=life,
        initial_snapshot_sha256=None,initial_tick=None,duration_seconds=240,
        local_closing_start_seconds=600,supervision_wall_limit_seconds=900,closing_reserve_seconds=300)
    # Remove obsolete pre-short initial-past claims. No prior source record/hash
    # can stand in for the NOT YET REACHED post10 REAL causal past.
    for k in('required_parent_complete_pair','required_parent_snapshot_sha256','required_parent_tick',
             'proposed_identity_not_yet_imported','candidate_genealogy','initial_record','initial_protocol'):
        p.pop(k,None)
    p['required_actual_parent']={'life':PARENT_LIFE,'milestone':'actual REAL R03 post-ten-work BEFORE material old22/new2 standalone panels',
        'snapshot_sha256':None,'complete_pair_manifest_sha256':None,'tick':None,'pair_local_path':None,
        'not_yet_exists_as_post10':True,'NOT_OMIT_parent':True,
        'no_alternative_favorable_checkpoint_or_reconstructed_recipe':True}
    p['branch_mode']='CONTINUE_REAL_ORIGINAL_FROM_THIS_EXACT_CUT'if label=='CIRCULAR_REAL'else'NEW_FULL_FORK_FROM_SAME_REAL_POST10'
    p['required_P0_action_codec']='R03';p['required_posteffect_quality_contract']=QUALITY
    p['required_prepared_view_policy']=policy;p['root_execution_authorization']=None
    def event(t,name,row,fb='omit'):
        return{'at_seconds':t,'kind':'material','request_id':prefix+name,'situations':[row],'feedback':fb,'actuator':'closed'}
    p['events']=[{'at_seconds':0,'kind':'command','request_id':prefix+'configure_generic_P0_view',
        'argv':['configurar-vista-ecosistema',policy,'--retorno','omit']},
        event(1,'exogenous_new_values_goal0',{'modo':'apd04-cambio','etiqueta_objetivo':0,
            'palabra':'clasifica','criterio':20,'cargas':[7,3],
            'mutaciones':[{'fuente':0,'valor':11},{'fuente':1,'valor':34}]})]
    for i in range(6):
        p['events'].append(event(15+30*i,'opportunity_'+str(i+1).zfill(2),
            {'modo':'apd04-vivir','oportunidades':1,'sensor':'independent_balanced','lexico':True,'desacoplado':False},feedback))
    p['events'].append({'at_seconds':210,'kind':'checkpoint','tag':'post6_actual_original_before_material_panels'})
    p.pop('after_window_pending',None)
    p['scope']='Prospective six opportunities only. All three begin from the EXACT SAME actual post10 REAL FULL cut, never post10 OMIT. Two factors: P0 body opportunity (fixed circular versus retain-after-formed-INSPECT), then consequences under the same persistent body (REAL versus OMIT). No source-address, cache/goal-aware view policy, automaticUSE, world reset, NativeN change, memory transplant or favorable checkpoint. Material old22/new2 panels only on later diagnostic descendants.'
    p['prospective_new_trial_not_a_rewrite_of_R03_short_or_reserve']=True
    p['freeze_source_paths']=list(dict.fromkeys(p['freeze_source_paths']+['sistema/app/usar_dee.py']))
    return p


def main():
    if OUT.exists():raise FileExistsError('Preserve old drafts/results')
    if sha(PATCH/'MANIFIESTO_PROPUESTA_N0.json')!=PATCH_SHA:raise ValueError('Proposed body source differs')
    for x in read(PATCH/'MANIFIESTO_PROPUESTA_N0.json')['members']:
        if sha(PATCH/x['file'])!=x['proposed_sha256']:raise ValueError('Proposed component byte mismatch')
    protocol=load('prospective_body_protocol_N0',PATCH/'sistema/app/protocolo_apd04.py')
    ui=load('prospective_body_UI_parser_N0',PATCH/'sistema/app/usar_dee.py')
    driver=load('existing_R04_static_plan_validator_N0',EXEC/'ejecutar_plan_apd04_r04.py')
    specs=[('CIRCULAR_REAL','circular_R01','real'),('PERSISTENTE_REAL','inspeccion_persistente','real'),
           ('PERSISTENTE_OMIT','inspeccion_persistente','omit')]
    plans=[make(*x)for x in specs];checks=[]
    for p in plans:
        t=copy.deepcopy(p);t.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=0)
        driver.validate_plan(t)
        for e in p['events']:
            if e['kind']=='command':ui.literal_rows(ui.command_parser().parse_args(e['argv']))
            elif e['kind']=='material':
                for row in e['situations']:protocol.validate_literal(row)
        checks.append({'life_not_created':p['life'],'fixed_work_opportunities':6,'events':len(p['events']),
            'static_driver_and_proposed_literal_validation':True,'native_ticks':0,
            'actual_post10_parent_hash_tick':None})
    # Pair equality refers to literal curricula/protocol opportunities, not to
    # imposed identical interactive futures after different Native decisions.
    a,b=copy.deepcopy(plans[1]),copy.deepcopy(plans[2])
    for p in(a,b):
        p['life']=p['world_id']='SAME_FOR_COMPARISON_ONLY'
        for e in p['events']:
            if'request_id'in e:e['request_id']='SAME_'+str(e['at_seconds'])
            if e['kind']=='material'and e['situations'][0]['modo']=='apd04-vivir':e['feedback']='SAME_FOR_COMPARISON_ONLY'
    if a!=b:raise ValueError('Persistent pair differs beyond declared work feedback/identity')
    OUT.mkdir()
    for spec,p in zip(specs,plans):write(OUT/('PLAN_'+spec[0]+'_DRAFT_R01.json'),p)
    c={'schema':'APD04.body_opportunity_and_consequences.prospective.N0.R01','status':'DRAFT_NO_NATIVE_GO',
       'Native_ticks':0,'shared_S_edited':False,'Native_instances_or_lives_created':False,
       'parent_rule':plans[0]['required_actual_parent'],
       'before_GO_requirements':[
           'REAL R03 completed all ten work IDs and has confirmed ownerSTOP, complete exact snapshot, Native interfaces/agenda and required transport artifacts; no pending/uncertain short-work operation is hidden.',
           'Actual post10 REAL is utilizable under its inherited domains; if adverse/unusable preserve it and do not rescue with OMIT, an earlier favorable cut, re-teaching or edited fields.',
           'Before any arm advances, fix and retain that SAME post10 REAL complete cut as the parent of both persistent forks. Circular may continue that original. Never fork persistent arms from a later circular future.',
           'Fill real parent/child SHA,tick,pair paths and proof of RAW/clocks/interfaces/pending/environment equality on full import. Documentary identity changes are declared, not biological acquisitions.',
           'Install only the reviewed P0 enum proposal after current global sourcefreeze ends and RootGO. Keep NativeN67, inherited actual caches/cursor/episode and relative reference; no RAW/clocks writes or Native content transplant.',
           'At most two Native owners at once, each512MiB/OMP1; same source revision freezes while either runs. Preserve code revision and ALL port/channel Native receipt IDs with finalFULL terminal status.'
       ],
       'fixed_preparation':{'actuator_codec':'R03','quality_contract':QUALITY,'sensor':'R03 independent_balanced',
           'sources':2,'Native_N':67,'view_options':['circular_R01','inspeccion_persistente'],
           'opportunities_per_arm':6,'minimum_window_seconds':240,'local_closing_seconds':600,'hard_guard_seconds':900,
           'closing_reserve_seconds':300,'deadline_UTC':'2026-10-27T03:30:51+00:00',
           'exogenous_values':{'source0':11,'source1':34},'goal_tag':0,'word':'clasifica','criterion':20,'loads':[7,3],
           'no_cache_or_cursor_reset':True,'no_old22_material_panel_originals':True},
       'P0_body_rule':'Pure enum/cursor/source_count/action/formed/actuator rule. circular always advances. Persistent retains ONLY unique formed native INSPECT with closedactuator; USE, WAIT, NULL/ambiguous advance. No value, target, cache, usefulness, goal or source-specific address enters this rule. It never choosesUSE automatically.',
       'old_metric':'Keep old_work_gain unchanged and report its full denominator, requested/applied/responded/correct/incorrect/NULL/rejected/out-of-domain separately. INSPECT new_fact is an environmental cache change, not automatic Native acquisition of that number.',
       'new_metric':'Keep R03quality separate: correct WAIT requires unique formed0, irrelevant tag and exact unchanged task objects/loads. INSPECT/USE quality equals oldgain. NULL is not WAIT. Domain closedactuator only; do not execute a nulled arm or call it a valid quality test.',
       'contrasts':[
           {'pair':['CIRCULAR_REAL','PERSISTENTE_REAL'],'question':'Does the prepared opportunity to retain a source after Native INSPECT enable subsequent NativeUSE/classification or alter interfering/repeated accesses?',
            'scope':'Engineering/body-affordance comparison, NOT learning. Different source sequences after Native actions are legitimate interactive consequences. Do not force a matched future by retargeting cursor or inputs.'},
           {'pair':['PERSISTENTE_REAL','PERSISTENTE_OMIT'],'question':'Under the SAME body opportunity and common real past, does generic actual consequence change a later Native selection/use?',
            'scope':'Work feedback is the only planned literal difference, not equal material dose. Preserve actual consequence contacts, querytimes and all admissions. Causal evidence is local; a changed selector alone is not generalP2.'}
       ],
       'frozen_analysis':[
           'Report every first and later response; distinguish physical sign, transduced action, cache mutation, correct current-version classification, useful NEW bin/gap gain and WAITquality.',
           'Recalculate selector/lexicon/numeric commands from exact uint64RAW state low32/semantic high4 and signed48/52/56 directions at fixed unchanged gates. Never use expected answer to select a reader.',
           'Trace actual cursor before/after and observed versions. Count INSPECT→laterUSE on the SAME source with unchanged current value/version between them; also record repeatedINSPECT withoutUSE and USEofstalecache.',
           'Compare actual source visits and traffic, not sixopportunities as sixindependent samples. No source-policy winner based only on new_fact count; joint correctUSE and sustained gain remain distinct.',
           'First opportunity precedes the new six-op feedback and acts as baseline. Compare persistent arms at later common physical observation only if it really occurs; if routes diverge, report the divergence, do not select favorable matching cases.',
           'Retention testing in copies is alternative future evidence, not consecutive use in these originals. A short positive body effect remains P0; any consequence-dependent selection requires paired evidence and later reserve before generalization.'
       ],
       'recording_and_stop':'Passive existing observer; no audit probes between six opportunities. Same fixed events15,45,75,105,135,165 and checkpoint210. Late operations stay ordered and lateness/pending/guard cuts remain visible. Save/STOP reached originals; full bridge/Native/queue state retained. No extra replay or refilling missed opportunities.',
       'diagnostic_after_only':{'parent':'Each ACTUAL post6 original complete cut, separately identified and still preserved.',
           'allowed_template':'Existing R05 diagnostic old16+MA6 command followed by clasifica/equilibra queries on a FULL descendant only, if separately authorized within global budget.',
           'not_executed_or_authorized_here':True,'no_original_queries_before_later_reserve':True},
       'hypotheses_not_results':['Persistent view may expose another opportunity to use data, or may trap repeatedINSPECT. No success is presumed.',
           'REAL/OMIT may differ by acquired route state; opportunity/preparation, dose, history and useful selection must not be conflated.'],
       'proposal_sources':{'body_manifest':str(PATCH/'MANIFIESTO_PROPUESTA_N0.json'),'body_manifest_SHA256':PATCH_SHA,
           'driver':str(EXEC/'ejecutar_plan_apd04_r04.py'),'driver_SHA256':sha(EXEC/'ejecutar_plan_apd04_r04.py'),
           'wrapper':str(EXEC/'supervisar_plan_apd04_r04.py'),'wrapper_SHA256':sha(EXEC/'supervisar_plan_apd04_r04.py')},
       'validation':checks,'persistent_pair_identical_except_identity_workfeedback':True}
    write(OUT/'CRITERIOS_Y_ASISTENCIA_PROSPECTIVOS_R01.json',c)
    write(OUT/'IDENTIDADES_PENDIENTES_R01.json',{'actual_REAL_post10_parent':None,
        'fixed_original_life':PARENT_LIFE,'three_proposed_arms':[p['life']for p in plans],
        'no_hash_tick_or_parent_completion_invented':True,'no_execution_authorization':True})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':q.name,'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.iterdir())if q.is_file()]})
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('Unexpected Native import')
    print(json.dumps({'out':str(OUT),'plans':3,'Native_ticks':0,'manifest_sha256':sha(OUT/'MANIFIESTO.json')}))


if __name__=='__main__':main()
