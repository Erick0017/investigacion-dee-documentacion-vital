"""N0 calendar-only R05: no Native, no shared source edit or plan closure."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE / 'PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R04'
OUT = HERE / 'PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R05'


def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')


def main():
    if OUT.exists(): raise FileExistsError('Preserve all prior proposals')
    for x in read(OLD/'MANIFIESTO.json')['members']:
        if sha(OLD/x['file']) != x['sha256']: raise ValueError('R04 source changed')
    s = importlib.util.spec_from_file_location('R05_existing_driver_schema_only', ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py')
    driver = importlib.util.module_from_spec(s); s.loader.exec_module(driver)
    OUT.mkdir(); checks=[]
    offsets=[15,35,55,75,95,115,135,155,175,195]
    for arm in ('REAL','OMIT'):
        old=read(OLD/('PLAN_WAIT_R03_'+arm+'_ORIGINAL_DRAFT_R04.json'))
        p=copy.deepcopy(old)
        p['life']=p['world_id']='APD04_WAIT_R03_'+arm+'_AUX_R05'
        k=0
        for e in p['events']:
            if e['kind']=='material' and e['situations'][0]['modo']=='apd04-vivir':
                e['at_seconds']=offsets[k]; k+=1
            elif e['kind']=='material' and e['situations'][0].get('etiqueta_objetivo')==0:
                e['at_seconds']=30
            elif e['kind']=='material' and e['at_seconds']==375:
                e['at_seconds']=110
            elif e['kind']=='checkpoint': e['at_seconds']=230
        if k!=10: raise ValueError('Exactly ten fixed opportunities')
        p['events'].sort(key=lambda e:e['at_seconds'])
        p.update(duration_seconds=240,supervision_wall_limit_seconds=900,closing_reserve_seconds=180)
        p['scope']+=' R05 prospective timing-only reduction: fixed offsets15..195, minimal window240s, outer900. Late events remain in original order and their lateness is reported. No answer-conditioned rescue, deletion or rescheduling. No extension beyond the original absolute campaign deadline.'
        original_no_times=[{k:v for k,v in e.items() if k!='at_seconds'}for e in old['events']]
        new_by_id={e.get('request_id',e.get('tag')):{k:v for k,v in e.items()if k!='at_seconds'}for e in p['events']}
        if any(new_by_id[e.get('request_id',e.get('tag'))] != n for e,n in zip(old['events'],original_no_times)):
            raise ValueError('R05 changed more than timing/life')
        t=copy.deepcopy(p);t.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=639374)
        driver.validate_plan(t)
        write(OUT/('PLAN_WAIT_R03_'+arm+'_ORIGINAL_DRAFT_R05.json'),p)
        diag=read(OLD/('PLAN_WAIT_R03_'+arm+'_PANEL_DIAGNOSTICO_DRAFT_R04.json'))
        diag['life']=diag['world_id']=p['life']+'_PANEL_DIAGNOSTICO'
        diag['required_parent_life_after_actual_post10_STOP']=p['life']
        write(OUT/('PLAN_WAIT_R03_'+arm+'_PANEL_DIAGNOSTICO_DRAFT_R05.json'),diag)
        checks.append({'arm':arm,'work_offsets':offsets,'goal_changes':[1,30,110],
            'only_timing_and_proposed_identity_changed':True,'material_panel_original':False,
            'Native_ticks':0,'actual_life_created':False})
    c=read(OLD/'CONTRATO_Y_CRITERIOS_WAIT_R03_R04.json')
    c['schema']='APD04.WAIT_affordance_and_posteffect_contract.N0.R05'
    c['timing_proposal_not_yet_approved_by_Root']={'original':{'duration_seconds':240,'outer_guard_seconds':900,'closing_reserve_seconds':180},
        'diagnostic':{'duration_seconds':300,'outer_guard_seconds':900},
        'absolute_campaign_deadline_unchanged':'2026-10-27T03:30:51+00:00',
        'scope':'Calendar-only prospective reduction before Native GO. Duration is a minimum window; fixed events may run late in order, preserving actual lateness and guard outcomes.'}
    c['plan_validation']=checks;c['previous_R04_manifest_sha256']=sha(OLD/'MANIFIESTO.json')
    write(OUT/'CONTRATO_Y_CRITERIOS_WAIT_R03_R05.json',c)
    write(OUT/'VALIDACION_N0.json',{'Native_ticks':0,'status':'DRAFT_NOT_AUTHORIZED_FOR_NATIVE','checks':checks,
        'no_shared_system_edit':True,'previous_R04':str(OLD),'previous_manifest_sha256':sha(OLD/'MANIFIESTO.json')})
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.iterdir())if p.is_file()]})
    print(json.dumps({'out':str(OUT),'manifest_sha256':sha(OUT/'MANIFIESTO.json'),'Native_ticks':0}))


if __name__=='__main__':main()
