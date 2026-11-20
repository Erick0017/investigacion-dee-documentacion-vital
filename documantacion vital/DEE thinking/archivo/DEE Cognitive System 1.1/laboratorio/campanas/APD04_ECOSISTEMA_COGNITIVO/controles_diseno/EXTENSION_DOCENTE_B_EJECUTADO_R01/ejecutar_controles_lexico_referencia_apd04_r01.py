"""Six prospective AUX histories through existing complete-pair/UI contracts.

No Runtime is constructed here. All physical experience is submitted literally
to the owned service. No policy, expected sign or auditor source is delivered
except the explicitly identified lexical teacher. Never replaces MAIN/ACTIVO.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
S=ROOT/'sistema'
LAB=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTROLES_LEXICO_REFERENCIA_AUX_R01'
FROZEN=LAB/'controles_diseno/FUENTES_CONTROLES_EJECUTADO_R01'
PAIR=S/'estado/fuentes_emparejadas/APD04_LEX_P0_R02_T605516_R01'
PAIR_SHA='32c08b09eb274be3d9ba63a546c60bf45841537089cc7096d5bd24ddbd3e50d7'
SNAPSHOT_SHA='f8081af0e79d9091009b4a0f14e16d51dd00eeca561666735f6727265a1c30d0'
PREFIX_TICK=605516
BRANCHES=[('LEX_PLUS','APD04_LEX_PLUS_AUX_R01','lex',1),
          ('LEX_MINUS','APD04_LEX_MINUS_AUX_R01','lex',-1),
          ('LEX_OMIT','APD04_LEX_OMIT_AUX_R01','lex',None),
          ('REF_A','APD04_REF_A_AUX_R01','ref','A'),
          ('REF_B','APD04_REF_B_AUX_R01','ref','B'),
          ('REF_OMIT','APD04_REF_OMIT_AUX_R01','ref',None)]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')


def walk(obj,path='$'):
    yield path,obj
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in('result','result_json')and isinstance(v,str)and v.lstrip().startswith(('{','[')):
                try:v=json.loads(v)
                except json.JSONDecodeError:pass
            yield from walk(v,path+'.'+str(k))
    elif isinstance(obj,list):
        for k,v in enumerate(obj):yield from walk(v,path+'['+str(k)+']')


def decoded(obs):
    n=int(obs['raw'])
    if not 0<=n<2**64:raise ValueError('RAW outside uint64')
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
            'direction':[((n>>k)&15)-(16 if ((n>>k)&15)>=8 else 0)for k in(48,52,56)]}


def summary(result):
    lexical=[];primitives=[];requests={};seen=set()
    for path,node in walk(result):
        if not isinstance(node,dict):continue
        if isinstance(node.get('reader'),dict)and'panel'in node['reader']and'form'in node:
            stamp=(node['form'],node.get('read_tick'))
            if stamp not in seen:
                seen.add(stamp);candidates=[];panel=node['reader']['panel']
                for o in panel:
                    fields=decoded(o)
                    if fields['state']and fields['semantic']==1 and fields['direction']in([0,0,-1],[0,0,1]):candidates.append(fields['direction'][2])
                lexical.append({'form':node['form'],'read_tick':node.get('read_tick'),'reader_sites':len(panel),
                                'reported':node['reader'].get('formed_native_command'),
                                'RAW_sign':candidates[0]if len(candidates)==1 else None,'candidate_count':len(candidates),'locator':path})
        if node.get('kind')in('APD04_candidate_scalar_classification','APD04_candidate_native_balance'):
            trial=node['native_trial'];candidates=[]
            for o in trial['reader']['observations']:
                d=decoded(o)
                for x in(-1,0,1):
                    for z in(0,-1):
                        if o['site']==[15+2*x,17,15+2*z]and d['state']and d['semantic']==1 and d['direction']==[x,1,z]:candidates.append(x)
            primitives.append({'kind':node['kind'],'value':trial.get('raw_sensor_value'),
                'loads':node.get('public_independent_loads'),'read_tick':trial['read_tick'],
                'reported':node['physical_choice'],'RAW_choice':candidates[0]if len(candidates)==1 else None,
                'candidate_count':len(candidates),'locator':path})
        if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
            r=node['receipt'];key=str(r['id']);old=requests.get(key)
            if old is None or old.get('status')in('scheduled','pending','admitted'):requests[key]=r
    status={}
    for r in requests.values():status[r.get('status')]=status.get(r.get('status'),0)+1
    return {'lexical':lexical,'primitives':primitives,'unique_native_receipts':len(requests),'receipt_statuses':status,
            'receipt_scope':'Exported physical IDs only; terminal dominates cached scheduled copy; not the entire historical queue.'}


def plans(kind,condition):
    if kind=='lex':
        plan=[]
        for word in('suma','resta','compara','recuerda'):plan.append(('old4_before_'+word,{'modo':'apd04-palabra','texto':word}))
        plan.extend([
            ('A_lesson_'+('omitted'if condition is None else str(condition)),{'modo':'apd04-docencia','texto':'clasifica','senal':1 if condition is None else condition,'docente':'omitted'if condition is None else'paired'}),
            ('A_source_first_use',{'modo':'apd04-palabra','texto':'clasifica'}),
            ('B_FIRST_BEFORE_ANY_B_LESSON',{'modo':'apd04-palabra','texto':'equilibra'}),
            ('B_single_lesson_minus',{'modo':'apd04-docencia','texto':'equilibra','senal':-1,'docente':'paired'}),
            ('B_first_after_one_lesson',{'modo':'apd04-palabra','texto':'equilibra'}),
            ('B_second_after_one_lesson',{'modo':'apd04-palabra','texto':'equilibra'}),
            ('A_source_retention_after_B',{'modo':'apd04-palabra','texto':'clasifica'})])
        for word in('suma','resta','compara','recuerda'):plan.append(('old4_after_'+word,{'modo':'apd04-palabra','texto':word}))
        return plan
    plan=[]
    if condition is not None:plan.append(('source_reference_experience_'+condition,{'modo':'apd04-leccion-referencia','lado':condition}))
    # The omission arm advances to the same fixed clock-domain opportunity by
    # a queued read-only state request only; it receives NO invented sham.
    else:plan.append(('source_reference_OMITTED_no_material_sham',{'modo':'apd04-estado'}))
    plan.extend([
        ('common_FIRST_value20',{'modo':'apd04-calibrar','casos':[{'tipo':'clasifica','valor':20}]}),
        ('common_NEXT_balance6_4_bias20',{'modo':'apd04-calibrar','casos':[{'tipo':'equilibra','cargas':[6,4]}]}),
        ('common_NEXT_balance6_6_no_HOLD_substitution',{'modo':'apd04-calibrar','casos':[{'tipo':'equilibra','cargas':[6,6]}]})])
    return plan


def main():
    if sys.version_info[:2]!=(3,13):raise ValueError('Use the installed exact compatible CPython3.13, not a replacement environment')
    if OUT.exists()or FROZEN.exists():raise FileExistsError('Declared controls already exist; do not repeat or replace futures')
    for _,life,_,_ in BRANCHES:
        if(S/'estado/vidas'/life).exists():raise FileExistsError('An AUX life already exists')
    if sha(PAIR/'EXPORTACION_SERVICIO.json')!=PAIR_SHA:raise ValueError('Exact P0 paired manifest differs')
    verifier=load('controls_existing_complete_pair_verifier',S/'app/importacion_emparejada.py')
    _,manifest,proof=verifier.verify_export(PAIR)
    if manifest['snapshot_sha256']!=SNAPSHOT_SHA or manifest['physical']['tick']!=PREFIX_TICK:raise ValueError('Different P0 physical prefix; no fallback')
    OUT.mkdir(parents=True);FROZEN.mkdir(parents=True)
    pc=load('controls_existing_owned_processes',S/'app/process_control.py')
    pc.protect_current(output=OUT/'RECURSOS_DRIVER.json',memory_limit=536870912)
    ui=load('controls_existing_single_entry',S/'app/usar_dee.py')
    sealer=load('controls_existing_stopped_pair_export',ROOT/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    config=ui.read(S/'contratos/ENTRADA_SENCILLA_APD03.json')
    config.update(source_alias='APD04_P0_LEX_R02_T605516',source_life=manifest['life_id'],source_tick=PREFIX_TICK,
        source_snapshot_sha256=SNAPSHOT_SHA,paired_export_manifest_sha256=PAIR_SHA,
        source_paired_export_manifest=(PAIR/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix(),
        memory_limit_bytes=536870912,owner_max_seconds=1200,material_wait_seconds=240)
    frozen=[]
    source_paths=sorted(set([p for p in S.rglob('*.py')if'__pycache__'not in p.parts]+list((S/'contratos').glob('*.json'))))
    for source in source_paths:
        rel=source.relative_to(S);destination=FROZEN/'sistema'/rel;destination.parent.mkdir(parents=True,exist_ok=True)
        digest=sha(source);shutil.copy2(source,destination)
        if sha(source)!=digest or sha(destination)!=digest:raise ValueError('Shared source changed before Native execution')
        frozen.append({'file':rel.as_posix(),'sha256':digest,'bytes':source.stat().st_size})
    shutil.copy2(Path(__file__),FROZEN/Path(__file__).name)
    write(FROZEN/'MANIFEST_FUENTES.json',{'revision':FROZEN.name,'members':frozen,'driver_sha256':sha(Path(__file__)),'captured_before_native':True})
    write(OUT/'PLAN_CERRADO_ANTES_NATIVE.json',{'schema':'APD04.six_shared_prefix_controls.R01','status':'CLOSED_FOR_EXECUTION',
        'parent_proof':proof,'parent_snapshot_sha256':SNAPSHOT_SHA,'parent_tick':PREFIX_TICK,'config_local_not_installed':config,
        'branches':[{'label':label,'life':life,'kind':kind,'condition':condition,'events':plans(kind,condition)}for label,life,kind,condition in BRANCHES],
        'assistance':'Explicit lessons/operator probes; no Native choices made by host. No sham exists in reference omission arm.',
        'denominator':'Six dependent branches share P0, not six independently trained learners; lexical queries are material.',
        'reference_timing_limit':'A/B experience advances to an odd391writingwindow; omission has no such material. Exact ticks/age recorded; no clock edit or false dose matching.'})
    began=time.perf_counter();closed=[]
    for label,life,kind,condition in BRANCHES:
        if time.perf_counter()-began>1200:raise TimeoutError('20minute control guard reached before next branch; preserve completed branches')
        folder=OUT/label;folder.mkdir();backend=ui.OriginalBackend(ROOT,dict(config));session=ui.Supervisor(ROOT,life,backend,dict(config))
        start=time.perf_counter();error=None;events=[];card=None
        with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
            try:
                card=session.open(new=True);write(folder/'IMPORTACION_COMPLETA.json',card)
                if card['parent']['encoded_sha256']!=SNAPSHOT_SHA:raise ValueError('Imported parent identity differs')
                write(folder/'START.json',session.start());write(folder/'REANUDAR.json',session.control('reanudar'))
                for serial,(event,row)in enumerate(plans(kind,condition),1):
                    request_id='apd04_ctrl_'+label.lower()+'_'+str(serial)+'_'+event.lower().replace('-','m')
                    request_id=request_id[:90]
                    result=session.material([row],feedback='omit',actuator='closed',request_id=request_id)
                    write(folder/(str(serial).zfill(2)+'_'+event+'.json'),result)
                    status=ui.row_of(result).get('status');metrics=summary(result)
                    entry={'serial':serial,'event':event,'request_id':request_id,'status':status,'metrics':metrics}
                    events.append(entry);print(json.dumps({'branch':label,**entry},ensure_ascii=False),flush=True)
                    if status!='completed':raise RuntimeError('Material request not completed; preserve same ID/future, never requeue')
                write(folder/'GUARDAR.json',session.control('guardar'))
                write(folder/'STOP.json',session.control('detener'))
            except BaseException as exc:
                error={'type':type(exc).__name__,'message':str(exc),'no_rewind_or_automatic_retry':True}
                write(folder/'ERROR_PRESERVADO.json',error)
            finally:
                session.close()
        record=backend.record(life)
        pair_target=S/'estado/fuentes_emparejadas'/(life+'_T'+str(record['physical']['tick'])+'_R01')
        paired=None
        try:
            paired=sealer.stopped_pair(ROOT,ui,life,pair_target,allow_queued=False,
                scope='Reached APD04 AUX control future after actual declared history. Not MAIN; no future rewind or learned-state merging.')
            write(folder/'PAR_POSTSTOP.json',paired)
        except BaseException as exc:
            write(folder/'ERROR_SELLO_POSTSTOP.json',{'type':type(exc).__name__,'message':str(exc),'future_and_operational_files_preserved':True})
        changed=[r['file']for r in frozen if sha(S/r['file'])!=r['sha256']]
        closure={'label':label,'life':life,'kind':kind,'condition':condition,'prefix_snapshot_sha256':SNAPSHOT_SHA,
                 'initial_tick':PREFIX_TICK,'final_tick':record['physical']['tick'],'snapshot_sha256':record['snapshot_sha256'],
                 'elapsed_seconds':time.perf_counter()-start,'events':events,'error':error,'paired':paired,
                 'source_changed':changed,'shared_prefix_not_independent_learner':True}
        write(folder/'CIERRE.json',closure);closed.append(closure)
        print(json.dumps({'BRANCH_CLOSED':label,'life':life,'final_tick':record['physical']['tick'],'events':len(events),'error':error,'source_changed':changed},ensure_ascii=False),flush=True)
        if changed:raise ValueError('Shared source changed during controls; preserve completed runs and stop next import')
    write(OUT/'CIERRE_CONTROLES.json',{'schema':'APD04.six_shared_prefix_controls.closed.R01','branches':closed,
        'total_wall_seconds':time.perf_counter()-began,'no_MAIN_or_ACTIVO_changed':True,
        'references_omitted_is_not_sham':True,'new_NSM65_promotions':0,'sources_frozen':str(FROZEN)})
    print(json.dumps({'CONTROLS_CLOSED':len(closed),'elapsed_seconds':time.perf_counter()-began},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
