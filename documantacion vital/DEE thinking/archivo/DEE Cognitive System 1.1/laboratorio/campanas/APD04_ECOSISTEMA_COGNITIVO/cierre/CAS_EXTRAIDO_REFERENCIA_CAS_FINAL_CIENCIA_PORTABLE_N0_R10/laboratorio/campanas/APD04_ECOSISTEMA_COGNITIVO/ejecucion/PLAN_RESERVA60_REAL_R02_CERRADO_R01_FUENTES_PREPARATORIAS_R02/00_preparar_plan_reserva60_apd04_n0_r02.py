"""N0 R02 assembler: explicit once-only sensor and genealogical candidate.

R01 source/DRAFT are immutable antecedents. Reuses its EXACT agenda and changes
only the43fixed work sensor fields plus the explicitly selected life identity.
No Native, S edit, driver run, response lookup, policy search or host action.
Root chooses a compatible complete candidate BEFORE closing/launching a plan.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,re,shutil,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
R01_SHA='ba1505a97065c46868f18d9911892d89af0b3fed8455899c7df3e44923970aa1'
R01_DRAFT_SHA='3c5a1eae637e34f94983112ac1d1f75b0a74436a352c558942926c1fee58c490'
SENSORS=('independent_balanced','independent_two_pairs')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def base():
    path=HERE/'preparar_plan_reserva60_apd04_n0_r01.py';draft=HERE/'PLAN_RESERVA60_DRAFT_R01.json'
    if sha(path)!=R01_SHA or sha(draft)!=R01_DRAFT_SHA:raise ValueError('Preserved R01 source/DRAFT changed; never reconstruct them silently')
    return load('preserved_R01_literal_agenda_only',path)
def identifier(v):
    if not isinstance(v,str)or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',v)or v.endswith('.'):raise ValueError('Explicit portable life/world identity required')
    return v
def make(b,life,world,sensor,snapshot=None,tick=None,pending=None,closed=False,provenance=None):
    if sensor not in SENSORS:raise ValueError('Sensor must be explicitly selected, never guessed from results')
    identifier(life);identifier(world)
    # R01's hardcoded life check remains intact; only this new declared
    # assembly layer substitutes the Root-selected candidate identity.
    p=b.build(b.LIFE,snapshot,tick,pending,closed);original_events=copy.deepcopy(p['events']);changed=0
    for e in p['events']:
        if e['kind']=='material':
            for r in e['situations']:
                if r['modo']=='apd04-vivir':r['sensor']=sensor;changed+=1
    if changed!=43:raise AssertionError('The frozen agenda must retain exactly43one-opportunities')
    normalized=copy.deepcopy(p['events'])
    for e in normalized:
        if e['kind']=='material':
            for r in e['situations']:
                if r['modo']=='apd04-vivir':r['sensor']='independent_two_pairs'
    if normalized!=original_events:raise AssertionError('R02 changed tools, timing, metrics or another literal field')
    p['life']=life;p['world_id']=world
    p['assembly_revision']='APD04.reserve60.N0.R02.explicit_sensor_and_genealogy'
    p['explicit_sensor_selection']={'sensor':sensor,'work_rows':changed,'selected_by':'Root before sealing and reserve, not a Native autonomous decision or response-conditioned runtime switch',
        'no_automatic_selection_or_sensor_retry':True,'same_sensor_for_all43_work_rows':True}
    p['candidate_genealogy']=provenance
    p['candidate_scope']='One selected actual complete candidate with its own genealogy; never a fusion of comparison-fork memories. Selecting an externally prepared profile/actuator codec is P0 engineering, not acquisition credited to the candidate.'
    return p
def freeze_sources(folder,paths):
    folder.mkdir(exist_ok=False);members=[]
    for i,p in enumerate(paths):
        p=p.resolve(strict=True);q=folder/(str(i).zfill(2)+'_'+p.name);shutil.copy2(p,q)
        if sha(p)!=sha(q):raise ValueError('Preparation source changed during byte capture')
        members.append({'original':str(p),'copy':q.name,'sha256':sha(q),'bytes':q.stat().st_size})
    dump(folder/'HASHES.json',{'members':members,'self_hash_excluded':True});return members
def self_check(b,out):
    if out.exists():raise FileExistsError('Preserve previous N0 proof')
    protocol=load('literal_protocol_N0_only',ROOT/'sistema/app/protocolo_apd04.py')
    ui=load('UI_literal_parser_N0_only',ROOT/'sistema/app/usar_dee.py')
    driver=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py'
    cases=[]
    for sensor in SENSORS:
        p=make(b,'APD04_CANDIDATO_VALIDACION_N0','APD04_CANDIDATO_VALIDACION_N0',sensor)
        proof=b.validate_n0(p,driver);rows=[r for e in p['events']if e['kind']=='material'for r in e['situations']]
        for r in rows:protocol.validate_literal(r)
        commands=[ui.literal_rows(ui.command_parser().parse_args(e['argv']))for e in p['events']if e['kind']=='command']
        for r in p['after_window_pending']['situations']:protocol.validate_literal(r)
        cases.append({'sensor':sensor,'checks':proof,'literal_rows_validated':len(rows),'commands_parsed':len(commands),
            'pending_rows_validated':len(p['after_window_pending']['situations']),'same_agenda_except43sensor_fields':True,
            'synthetic_validation_identity_not_a_created_or_selected_life':True})
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('N0 proof must not import Native')
    paths=[Path(__file__),HERE/'preparar_plan_reserva60_apd04_n0_r01.py',HERE/'PLAN_RESERVA60_DRAFT_R01.json',driver,
        ROOT/'sistema/app/protocolo_apd04.py',ROOT/'sistema/app/usar_dee.py']
    members=freeze_sources(out.parent/(out.stem+'_FUENTES'),paths)
    dump(out,{'schema':'APD04.reserve60.generator_R02.N0_proof','cases':cases,'sources':members,'Native_imports':0,'Native_ticks':0,
        'no_S_edits':True,'R01_and_DRAFT_preserved':True,'does_not_test_world_admission_or_future_outcomes':True,
        'both_options_validated_in_memory_not_a_sensor_selection':True})
    print(json.dumps({'proof':str(out),'sensor_options':len(cases),'Native_ticks':0,'R01_unchanged':True},ensure_ascii=False))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--self-check-n0',action='store_true')
    ap.add_argument('--life');ap.add_argument('--world-id');ap.add_argument('--sensor',choices=SENSORS)
    ap.add_argument('--snapshot-sha256');ap.add_argument('--tick',type=int);ap.add_argument('--resume-pending-id')
    ap.add_argument('--genealogy-file',type=Path);ap.add_argument('--paired-manifest',type=Path)
    ap.add_argument('--root-go',choices=['APD04_RESERVA60_PLAN_CLOSED']);a=ap.parse_args();b=base()
    if a.self_check_n0:
        if a.root_go or a.life or a.sensor:raise ValueError('N0 proof does not select a life/sensor or authorize execution')
        return self_check(b,a.out)
    if a.out.exists():raise FileExistsError('Never replace a prior candidate plan')
    if not a.life or not a.sensor:raise ValueError('Root must explicitly supply --life and --sensor; no defaults or result-based choice')
    closed=bool(a.root_go);genealogy=None;genealogy_bytes=None
    if closed:
        if a.tick is None or a.tick<0 or not a.snapshot_sha256 or not re.fullmatch('[0-9a-f]{64}',a.snapshot_sha256):raise ValueError('Actual current physical tick and SHA256 required')
        if not a.genealogy_file:raise ValueError('Existing actual VIDA.json genealogy required; no invented parent record')
        if datetime.now(timezone.utc)>=datetime.fromisoformat(b.LATEST_START):raise TimeoutError('Original00:50UTC start limit passed; budget is not restarted')
        genealogy_bytes=a.genealogy_file.read_bytes();record=json.loads(genealogy_bytes)
        if record['life_id']!=a.life or record['snapshot_sha256']!=a.snapshot_sha256 or record['physical']['tick']!=a.tick:raise ValueError('CLI identity differs from actual genealogy record')
        world=a.world_id or record['world_id']
        if world!=record['world_id']or not record.get('parent'):raise ValueError('Actual world identity and physical parent are indispensable')
        genealogy={'VIDA_source':str(a.genealogy_file.resolve()),'VIDA_sha256':hashlib.sha256(genealogy_bytes).hexdigest(),
            'life_id':record['life_id'],'world_id':record['world_id'],'parent':record['parent'],'branch':record.get('branch'),'physical_tick':a.tick,
            'snapshot_sha256':a.snapshot_sha256,'scope':'Read-only identity/provenance check. Existing owner must still load the complete snapshot plus operational queues/sidecars; this assembler does not certify state completeness or cognition.'}
        if a.paired_manifest:
            pb=a.paired_manifest.read_bytes();pm=json.loads(pb)
            if pm.get('life_id')!=a.life or pm.get('snapshot_sha256')!=a.snapshot_sha256:raise ValueError('Declared complete paired export differs from current candidate')
            genealogy['existing_paired_manifest']={'source':str(a.paired_manifest.resolve()),'sha256':hashlib.sha256(pb).hexdigest()}
    else:
        if a.snapshot_sha256 is not None or a.tick is not None or a.genealogy_file or a.paired_manifest:raise ValueError('DRAFT has no future actual identity or invented proof')
        world=a.world_id or a.life
    plan=make(b,a.life,world,a.sensor,a.snapshot_sha256,a.tick,a.resume_pending_id,closed,genealogy)
    driver=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py';proof=b.validate_n0(plan,driver)
    copies=a.out.parent/(a.out.stem+'_FUENTES_PREPARATORIAS_R02');paths=[Path(__file__),HERE/'preparar_plan_reserva60_apd04_n0_r01.py',driver]
    members=freeze_sources(copies,paths)
    if genealogy_bytes is not None:
        with(copies/'VIDA_PROCEDENCIA_ORIGINAL.json').open('xb')as f:f.write(genealogy_bytes)
        if a.genealogy_file.read_bytes()!=genealogy_bytes:raise ValueError('Selected life changed while assembling; do not launch this plan')
    dump(a.out,plan);dump(a.out.parent/(a.out.stem+'_PREPARACION_N0_R02.json'),{'checks':proof,'sources':members,
        'R01_source_sha256':R01_SHA,'R01_DRAFT_sha256':R01_DRAFT_SHA,'explicit_sensor':a.sensor,'new_Native_ticks':0,
        'no_S_write_no_actor_action_selection':True,'selection_must_remain_frozen_before_reserve':True})
    print(json.dumps({'plan':str(a.out),'status':plan['status'],'life':a.life,'sensor':a.sensor,**proof},ensure_ascii=False))
if __name__=='__main__':main()
