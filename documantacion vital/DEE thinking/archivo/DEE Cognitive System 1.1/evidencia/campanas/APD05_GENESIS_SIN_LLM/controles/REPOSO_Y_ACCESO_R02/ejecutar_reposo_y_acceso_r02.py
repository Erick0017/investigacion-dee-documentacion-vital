"""Finite matched APD05 controls using the installed full-pair and owner APIs.

The controller schedules declared experiences; it does not compute actor answers.
Worker loads ONE world, imports ONE complete paired state and preserves every
request ID. REST advances v27; no RAW/clock/learned-state edits are permitted.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import copy
import hashlib
import json
import os
import shutil
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SYSTEM = ROOT / 'sistema'
EVIDENCE = ROOT / 'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles'
PROTOCOL = HERE / 'PROTOCOLO_REPOSO_Y_ACCESO_R02.json'
PROTOCOL_SHA = '3b4097091dd556913995ba8336aa16f3175e0875f2dbf2b285adc7076a871719'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def now(): return datetime.now(timezone.utc).isoformat()


def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')


def append(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', encoding='utf8', newline='\n') as f:
        f.write(json.dumps(value, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':'), allow_nan=False) + '\n')


def walk(obj, path='$'):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('result', 'result_json') and isinstance(v, str) and v.lstrip().startswith(('{', '[')):
                try: v = json.loads(v)
                except json.JSONDecodeError: pass
            yield from walk(v, path + '.' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from walk(v, path + '[' + str(i) + ']')


def fields(obs):
    raw = int(obs['raw'])
    if not 0 <= raw < 2**64: raise ValueError('RAW uint64 domain')
    return {'state': raw & 0xffffffff, 's_reg': (raw >> 32) & 65535,
            'semantic': (raw >> 60) & 15,
            'direction': [((raw >> k) & 15) - (16 if ((raw >> k) & 15) >= 8 else 0)
                          for k in (48, 52, 56)]}


def summarize(value):
    words=[]; numbers=[]; receipts={}; seen=set(); work=[]
    for path, node in walk(value):
        if not isinstance(node, dict): continue
        if isinstance(node.get('reader'), dict) and 'panel' in node['reader'] and 'form' in node:
            stamp=(node['form'], node.get('read_tick'))
            if stamp not in seen:
                seen.add(stamp); signs=[]
                for obs in node['reader']['panel']:
                    f=fields(obs)
                    if f['state'] and f['semantic']==1 and f['direction'] in ([0,0,-1],[0,0,1]):
                        signs.append(f['direction'][2])
                words.append({'form': node['form'], 'read_tick': node.get('read_tick'),
                              'RAW_sign': signs[0] if len(signs)==1 else None,
                              'candidate_count': len(signs), 'reported': node['reader'].get('formed_native_command'),
                              'locator': path})
        if node.get('kind') in ('APD04_candidate_scalar_classification','APD04_candidate_native_balance'):
            trial=node['native_trial']; signs=[]
            for obs in trial['reader']['observations']:
                f=fields(obs)
                for x in (-1,0,1):
                    for z in (0,-1):
                        if obs['site']==[15+2*x,17,15+2*z] and f['state'] and f['semantic']==1 and f['direction']==[x,1,z]: signs.append(x)
            numbers.append({'kind': node['kind'], 'RAW_sign': signs[0] if len(signs)==1 else None,
                            'candidate_count': len(signs), 'read_tick':trial['read_tick'],
                            'reported':node['physical_choice'],'locator':path})
        if 'physical_action' in node and 'committed_effect' in node and 'episode' in node:
            work.append({'episode':node['episode'],'action':node['physical_action'],
                         'effect':node['committed_effect'],'public_before':node.get('public_before'),
                         'query_tick':(node.get('selection') or {}).get('query_tick'),'locator':path})
        if isinstance(node.get('receipt'),dict) and 'id' in node['receipt']:
            receipt=node['receipt']; key=str(receipt['id']); old=receipts.get(key)
            if old is None or old.get('status') in ('scheduled','pending','admitted'): receipts[key]=receipt
    return {'words':words,'numbers':numbers,'work':work,
            'native_receipts_unique':len(receipts),'native_receipt_statuses':dict(Counter(r.get('status') for r in receipts.values())),
            'native_receipts':list(receipts.values()),
            'scope':'Exact new Native IDs found in this request only, never the inherited journal or nested duplicate count.'}


def protocol():
    if sha(PROTOCOL) != PROTOCOL_SHA: raise ValueError('Frozen protocol changed')
    return read(PROTOCOL)


def worker(args):
    p=protocol(); branch=next(x for x in p['prevention_arms']+p['recovery_arms'] if x['life']==args.life)
    parent=p['parents']['adverse' if '_REC_' in args.life else 'functional']
    out=Path(args.out)
    if not out.resolve().is_relative_to((SYSTEM/'estado/observatorios/APD05_CONTROLES_R02').resolve()):
        raise ValueError('Worker recorder output must remain in its declared state instrument directory')
    out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(SYSTEM)); sys.path.insert(0,str(SYSTEM/'app'))
    from app import process_control as pc
    pc.protect_current(output=out/'RECURSOS_NATIVE.json',memory_limit=512*1024**2)
    from app.lives import Store
    from app.importacion_emparejada import import_pair
    from app.native_tools import atomic_json, physical, observe
    from app.servicio_persistente import NativeWorld, PersistentService
    from app.cola_local import QueueDB
    from app.native_tools import identity
    write(out/'IDENTIDAD_Y_FUENTES.json',{'time':now(),'identity':identity(SYSTEM),
          'protocol_sha256':PROTOCOL_SHA,'entry_sha256':sha(__file__),
          'source_hashes':{str(q.relative_to(SYSTEM)):sha(q) for q in [SYSTEM/'app/servicio_persistente.py',SYSTEM/'app/cola_local.py',SYSTEM/'app/importacion_emparejada.py',SYSTEM/'app/protocolo_apd04.py',SYSTEM/'capacidades/ecosistema_apd04.py',SYSTEM/'capacidades/acciones_nativas_apd04.py']}})
    pair=SYSTEM/parent['pair_relative_to_system']
    if sha(pair/'EXPORTACION_SERVICIO.json')!=parent['manifest_sha256']: raise ValueError('Parent manifest changed')
    store=Store(SYSTEM); imported=import_pair(store,pair,args.life)
    if imported['snapshot_sha256']!=parent['snapshot_sha256'] or imported['physical']['tick']!=parent['tick']:
        raise ValueError('Parent snapshot mismatch')
    write(out/'IMPORTACION_N0.json',imported)
    world=NativeWorld(SYSTEM,args.life,backend='mente_unificada').open()
    queue=QueueDB(world.folder/'cola.sqlite3')
    service=PersistentService(world,queue,start_paused=True,idle_ticks=1,idle_seconds=.1,save_seconds=3600)
    service.restore_transport(); service.publish()
    if queue.outstanding(): raise ValueError('Imported outstanding transport was not silently ignored')
    started_tick=world.tick; all_results=[]; stage='interval'; counter=0
    def capture(label):
        row={'utc':now(),'label':label,'physical':physical(world.a.world,occupation=True),
             'queue_outstanding':[{'id':x['id'],'status':x['status'],'payload_sha':x['payload_sha']} for x in queue.outstanding()],
             'operational_dependencies':world.operational_dependencies(),
             'ROI': [observe(world.a.world,site) for site in ((24,12,53),(26,12,53),(23,15,53),(25,15,53),(27,15,53))],
             'scope':'Passive fixed-coordinate witness; not a new Native input and not total lineage coverage.'}
        append(out/'OBSERVACION_PASIVA.jsonl',row); return row
    def perform(payload,label):
        nonlocal counter
        counter+=1; identifier=args.life.lower()+'_%03d'%counter
        atomic_json(out/'PROGRESO_ACTUAL.json',{'stage':stage,'label':label,'request_id':identifier,'started_wall_monotonic':time.monotonic(),'started_tick':world.tick,'wall_utc':now()})
        admission=queue.put(identifier,payload)
        if admission.get('admission')!='queued': raise ValueError('New ID was not admitted once: '+str(admission))
        row=queue.next(paused=False)
        if row is None or row['id']!=identifier: raise ValueError('Unexpected operational queue order; nothing repeated')
        service.perform(row); finished=queue.get(identifier)
        if finished['status']!='completed':
            append(out/'SESIONES.jsonl',{'label':label,'id':identifier,'payload':payload,'admission':admission,'transport':finished})
            raise RuntimeError('Preserved incomplete operation: '+finished['status'])
        result=json.loads(finished['result']); all_results.append({'label':label,'id':identifier,'payload':payload,'result':result})
        append(out/'SESIONES.jsonl',all_results[-1]); append(out/'RESUMENES_POR_PEDIDO.jsonl',{'label':label,'id':identifier,'summary':summarize(result)})
        atomic_json(out/'PROGRESO_ACTUAL.json',{'stage':stage,'label':label,'request_id':identifier,'completed':True,'tick':world.tick,'wall_utc':now()})
        return result
    def fill(target):
        while world.tick<target:
            # Fine passive sampling, but no complete dense snapshot per tick.
            count=min(256,target-world.tick)
            perform({'operacion':'avanzar','ticks':count},'age_fill_%d'%target); capture('after_age_fill')
    try:
        capture('initial_before_any_new_tick')
        for i,offset in enumerate(branch['task_offsets']):
            target=started_tick+offset
            if world.tick>target:
                raise ValueError('Fixed task boundary overrun; not backdated or retargeted')
            fill(target); payload=copy.deepcopy(p['ordinary_literal_opportunity'])
            if branch['condition']=='ORD_OMIT': payload['retorno']='omit'
            perform(payload,'ordinary_work_%d'%(i+1)); capture('after_ordinary_work_%d'%(i+1))
        target=started_tick+branch['duration_native_ticks']
        if world.tick>target: raise ValueError('Fixed common-age target overrun')
        fill(target); interval_end=capture('interval_end_before_material_panel')
        stage='common_panel'
        for i,payload in enumerate(p['common_post_interval_panel']):
            perform(copy.deepcopy(payload),'common_panel_%02d'%(i+1)); capture('after_common_panel_%02d'%(i+1))
        stage='save_stop_export'
        perform({'operacion':'guardar'},'explicit_save')
        perform({'operacion':'detener'},'explicit_stop')
        service.checkpoint({'kind':'PERSISTENT_GRACEFUL_CLOSE','idle_ticks':service.idle_total})
        service.publish()
        full=world.export_pair('APD05_CONTROL_COMPLETO_R01',queue)
        panel=[x for x in all_results if x['label'].startswith('common_panel_')]
        summary=summarize(panel); expected=p['frozen_evaluation']['lexical_expected_RAW_signs']
        for x in summary['words']: x['expected']=expected[x['form']]; x['correct']=x['RAW_sign']==x['expected']
        for i,x in enumerate(summary['numbers']):
            x['expected']=p['frozen_evaluation']['numeric_expected_RAW_signs'][i]; x['correct']=x['RAW_sign']==x['expected']
        final=capture('final_after_stop')
        write(out/'RESULTADO.json',{'schema':'APD05.rest_access.executed.R01','life':args.life,'branch':branch,'parent':parent,
              'started_tick':started_tick,'interval_end':interval_end,'final':final,'panel_summary':summary,
              'all_new_receipts':summarize(all_results),'stop_confirmed':service.stop,'owner_closed_in_finally':True,
              'complete_pair':full,'status':'CLOSED_PHYSICAL_TRAJECTORY_NOT_GLOBAL_SCIENTIFIC_VERDICT','utc':now(),
              'energy':'NO_MEDIDA','no_raw_clock_or_target_edit':True})
    except BaseException as e:
        # Preserve a final state if the actual owner can still safely checkpoint.
        failure={'type':type(e).__name__,'detail':str(e),'stage':stage,'tick':world.tick,'traceback':traceback.format_exc(),
                 'no_restore_or_automatic_retry':True,'all_completed_requests':len(all_results)}
        try:
            service.stop=True
            failure['checkpoint']=service.checkpoint({'kind':'FAILED_APD05_CONTROL_PRESERVED','error':{'type':type(e).__name__,'detail':str(e)}})
            service.publish()
            failure['complete_pair']=world.export_pair('APD05_CONTROL_FALLO_COMPLETO_R01',queue)
        except BaseException as save: failure['preservation_error']=repr(save)
        write(out/'FALLO_PRESERVADO.json',failure); raise
    finally: world.close()


def supervise(args):
    p=protocol(); out=EVIDENCE/'REPOSO_Y_ACCESO_R02'
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,out/Path(__file__).name); shutil.copy2(PROTOCOL,out/PROTOCOL.name)
    sys.path.insert(0,str(SYSTEM)); from app import process_control as pc
    began=time.monotonic(); runs=[]
    wanted=[x for x in p['prevention_arms']+p['recovery_arms'] if not args.only or x['life'] in args.only]
    for branch in wanted:
        folder=out/branch['life']; folder.mkdir()
        native=SYSTEM/'estado/observatorios/APD05_CONTROLES_R02'/branch['life']
        started=time.monotonic(); timed_out=None
        argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker','--life',branch['life'],'--out',str(native),'--root-go',args.root_go]
        with (folder/'STDOUT.txt').open('w',encoding='utf8') as stdout,(folder/'STDERR.txt').open('w',encoding='utf8') as stderr:
            process,job,name=pc.spawn_owned(argv,cwd=ROOT,stdout=stdout,stderr=stderr,memory_limit=1024**3)
            try:
                while process.poll() is None:
                    elapsed=time.monotonic()-started
                    progress=native/'PROGRESO_ACTUAL.json'; current=read(progress) if progress.is_file() else {}
                    if elapsed>p['timing']['per_arm_wall_limit_seconds']: timed_out='per_arm_wall_limit'
                    if not current.get('completed',True) and time.monotonic()-current.get('started_wall_monotonic',time.monotonic())>p['timing']['material_request_wall_limit_seconds']:
                        timed_out='per_material_request_wall_limit'
                    if time.monotonic()-began>p['timing']['outer_all_arms_limit_seconds']: timed_out='all_arms_wall_limit'
                    if timed_out:
                        pc.terminate_job(job,124); process.wait(30); break
                    append(folder/'RECURSOS_ARBOLES.jsonl',{'utc':now(),'wall_seconds':elapsed,**pc.job_resources(job)})
                    time.sleep(2)
                resources=pc.job_resources(job)
                run={'life':branch['life'],'argv':argv,'exit_code':process.returncode,'timeout':timed_out,
                     'wall_seconds':time.monotonic()-started,'owned_job':name,'resources':resources,
                     'energy':'NO_MEDIDA','scope':'One whole owned process tree; nested native resource report is not added to it.'}
                write(folder/'SUPERVISION.json',run); runs.append(run)
                if native.is_dir(): shutil.copytree(native,folder/'NATIVE')
            finally: pc.close_job(job)
        print(json.dumps(run,ensure_ascii=False),flush=True)
        if timed_out=='all_arms_wall_limit': break
    write(out/'SUPERVISION_TOTAL.json',{'runs':runs,'wall_seconds':time.monotonic()-began,'Native_replicates':'Five forks with shared historical prefixes, not five independent ancestries.','utc':now()})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker',action='store_true'); parser.add_argument('--life')
    parser.add_argument('--out',type=Path); parser.add_argument('--only',nargs='*')
    parser.add_argument('--root-go',required=True)
    args=parser.parse_args()
    if args.root_go!='APD05_CONTROLES_REPOSO_PROTOCOLO_R02_APPROVED': raise ValueError('Root GO required; no Native launch')
    if args.worker: worker(args)
    else: supervise(args)


if __name__=='__main__': main()
