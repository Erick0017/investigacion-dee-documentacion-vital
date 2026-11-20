"""Root-only finite PI07 execution through the existing Cognitive owner.

No action policy: executes a frozen list of opportunities, preserves all
numeric/NULL/admission outcomes and stops on transport/safety uncertainty.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,sys

P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
S=P/'estados/candidato/sistema';RP=C/'reproducibilidad'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
    for q in (p,*p.parents):
        if q.exists() and (q.is_symlink() or getattr(q.lstat(),'st_file_attributes',0)&1024):
            raise ValueError('No linked experiment path: '+str(q))

def ledger():
    stores={S.resolve()};registry=RP/'EJECUCIONES'
    if registry.exists():
        for f in registry.glob('*PI07_*.json'):
            d=Path(read(f)['destination']).resolve(strict=True)
            if not (d.is_relative_to((P/'estados').resolve()) or d.is_relative_to((RP/'diagnosticos').resolve())):
                raise ValueError('A registered PI07 world is outside its scoped stores')
            stores.add(d/'sistema')
    lives=[];seen=set();ticks=0
    for system in stores:
        folder=system/'estado/vidas'
        for f in sorted(folder.glob('*/VIDA.json')):
            regular(f);d=read(f);life=d['life_id']
            if life in seen:raise ValueError('A diagnostic identity is duplicated')
            seen.add(life);start=d.get('parent',{}).get('source_tick')
            if type(start)is not int or d['physical']['tick']<start:raise ValueError('A coherent full imported prefix is required')
            delta=d['physical']['tick']-start;ticks+=delta
            lives.append({'life_id':life,'system':str(system),'import_tick':start,'saved_tick':d['physical']['tick'],'Native_delta':delta})
    return ticks,lives

def main(args):
    if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}',args.vida):raise ValueError('Explicit fresh PI07 diagnostic life only')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,55}',args.tag):raise ValueError('Fresh bounded request tag required')
    path=args.plan.resolve(strict=True);regular(path)
    if not path.is_relative_to(P.resolve()):raise ValueError('A frozen in-campaign plan is required')
    literal_bytes=path.read_bytes();plan=json.loads(literal_bytes)
    if plan.get('schema')!='DEE.PI07.fixed_phase_plan.v1' or plan.get('status')!='SEALED':raise ValueError('Prospective sealed PI07 plan only')
    allowed={'schema','status','initial_tick','max_native_ticks','steps','description','registration_utc','source_proof'}
    if set(plan)-allowed:raise ValueError('No hidden runtime policy in the plan')
    steps=plan['steps'];labels=set();bound=0
    if not isinstance(steps,list) or not 1<=len(steps)<=100:raise ValueError('Finite list of 1–100 operations required')
    for step in steps:
        if set(step)-{'label','literal','max_native_ticks','expected_new_ticks','feedback','actuator'}:raise ValueError('Only frozen operations and bounds')
        if not re.fullmatch(r'[A-Za-z0-9_]{1,36}',step['label']) or step['label']in labels:raise ValueError('Unique bounded step label required')
        labels.add(step['label']);n=step['max_native_ticks']
        if type(n)is not int or not 0<=n<=10000:raise ValueError('Prospective finite Native tick bound required')
        bound+=n
        if not str(step['literal'].get('modo','')).startswith(('eci01-pi07-','eci01-pi04-c2c-','eci01-pi05-')):raise ValueError('Only reviewed PI07 or inherited test commands')
        if step.get('feedback','omit')not in ('real','omit') or step.get('actuator','closed')not in('closed','nulled'):raise ValueError('Existing outer contracts required')
    if bound>plan['max_native_ticks']:raise ValueError('Plan bound does not cover all operation bounds')
    campaign=read(P/'REGISTRO_CAMPANA.json');ticks,lives=ledger()
    if ticks+bound>campaign['budget']['Native_ticks_all_branches'] or len(lives)>campaign['budget']['diagnostic_worlds']:raise ValueError('Fixed PI07 budget would be exceeded')
    if datetime.now(timezone.utc)>=datetime.fromisoformat(campaign['science_cutoff_local']).astimezone(timezone.utc):raise ValueError('Scientific cutoff reached')
    if (S/'estado/ACTIVO.json').exists() or (RP/'EJECUCION_MATERIAL.lock').exists():raise ValueError('Never select a main or overlap a material RP owner')
    locks=S/'estado/locks'
    if locks.exists() and any(locks.iterdir()):raise ValueError('A scoped writer remains; inspect instead of replacing it')
    cardfile=S/'estado/vidas'/args.vida/'VIDA.json';card=read(cardfile)
    if card['physical']['N']!=67 or card['physical']['tick']!=plan['initial_tick']:raise ValueError('Current life/cut differs from the preregistered prefix')
    if (cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('An interrupted future must not be retried silently')
    proof_path=P/'control'/(args.tag+'.json');writer=P/'PI07_ROOT_NATIVE_WRITER.lock'
    if proof_path.exists() or writer.exists():raise FileExistsError('No reused transport tag or second campaign writer')
    current=read(C/'sistema/estado/vidas'/MAIN/'VIDA.json')
    critical=[C/'sistema/estado/ACTIVO.json',C/'sistema/estado/vidas'/MAIN/'VIDA.json',C/'sistema'/current['snapshot']]
    before={str(f):sha(f) for f in critical}
    with writer.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life':args.vida,'plan':str(path),'plan_sha256':hashlib.sha256(literal_bytes).hexdigest()},f)
    outcomes=[];owner=None;error=None;safety=None
    try:
        sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI07 import Owner
        owner=Owner(args.vida,args.tag)
        with owner:
            for step in steps:
                if datetime.now(timezone.utc)>=datetime.fromisoformat(campaign['science_cutoff_local']).astimezone(timezone.utc):raise ValueError('Scientific cutoff between operations')
                request=args.tag+'_'+step['label']
                value=owner.material(request,step['literal'],feedback=step.get('feedback','omit'),actuator=step.get('actuator','closed'),allow_failure=True)
                primary=P/'ensayos'/(request+'.json')
                outcomes.append({'label':step['label'],'id':request,'before_tick':value.get('before_tick'),'after_tick':value.get('after_tick'),'primary':str(primary),'primary_sha256':sha(primary)})
                if 'before_tick'not in value or 'after_tick'not in value:raise RuntimeError('The request did not complete; preserve this future and original ID')
                delta=value['after_tick']-value['before_tick']
                if not 0<=delta<=step['max_native_ticks']:raise RuntimeError('Actual step exceeded its prospectively declared Native bound')
                if 'expected_new_ticks'in step and delta!=step['expected_new_ticks']:raise RuntimeError('Unexpected physical age; do not retime after observing the outcome')
                rows=value.get('result',{}).get('rows',[])
                for row in rows:
                    if row.get('host_safety_stop')is True:safety={'source':'HOST_SAFETY','step':step['label'],'not_learned_regulation':True}
                    if row.get('uncertain')is True or row.get('transport_uncertain')is True:raise RuntimeError('Uncertain actual operation; preserve without resend')
                if path.read_bytes()!=literal_bytes:raise RuntimeError('The sealed plan changed during execution')
                if safety:break
            owner.control('guardar')
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
    after=read(cardfile)
    closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    protected_after={str(f):sha(f) for f in critical}
    if protected_after!=before:error={'type':'PRINCIPAL_CHANGED_CONCURRENTLY','message':'No old candidate may replace the advanced principal','automatic_retry':False}
    status='FAILED_PRESERVED'if error or not closed else ('HOST_SAFETY_STOP_CLOSED'if safety else'CLOSED')
    proof={'schema':'DEE.PI07.finite_owned_execution.R01','at_utc':datetime.now(timezone.utc).isoformat(),
        'life_id':args.vida,'status':status,'closed':closed,'plan':str(path),'plan_sha256':hashlib.sha256(literal_bytes).hexdigest(),
        'initial_tick':card['physical']['tick'],'final_tick':after['physical']['tick'],'new_ticks':after['physical']['tick']-card['physical']['tick'],
        'final_snapshot_sha256':after['snapshot_sha256'],'outcomes':outcomes,'error':error,'host_safety':safety,
        'budget_before':{'Native_ticks_all_branches':ticks,'lives':lives},
        'protected_main_before':before,'protected_main_after':protected_after,'protected_main_unchanged':before==protected_after,
        'full_plan_completed':error is None and closed and safety is None and len(outcomes)==len(steps),
        'all_material_calls_recorded':len(outcomes)==len(steps),
        'runner_status_is_not_functional_success':True,'selection_modified':False,
        'terminal_numeric_NULL_and_admission_outcomes_are_not_automatically_technical_failures':True}
    with proof_path.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    if closed:
        if read(writer)['pid']!=os.getpid():raise RuntimeError('Writer marker identity changed; preserve it')
        writer.unlink()
    print(json.dumps({'proof':str(proof_path),'sha256':sha(proof_path),'status':status,'closed':closed,'new_ticks':proof['new_ticks'],'error':error},ensure_ascii=False))
    return 0 if status in('CLOSED','HOST_SAFETY_STOP_CLOSED') else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--vida',required=True);parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--tag',required=True)
    raise SystemExit(main(parser.parse_args()))
