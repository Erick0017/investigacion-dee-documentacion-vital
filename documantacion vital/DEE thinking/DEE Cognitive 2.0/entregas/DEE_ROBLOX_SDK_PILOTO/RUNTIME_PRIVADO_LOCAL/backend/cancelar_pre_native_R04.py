"""Root-only cancellation of ONE proven pre-submit HTTP rename failure.

No Native imports, queue writes, ledger mutation, replay or flag clearing.
The original PENDING/RUNNING bytes are archived literally before replacement.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import sqlite3
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, IDENTIFIER, atomic, canonical, closed_native, digest, instance_home, read, sha

def cancel(instance_id, operation_id, *, execute=False):
    if IDENTIFIER.fullmatch(operation_id) is None:raise ValueError('EXACT_FINITE_OPERATION_IDENTIFIER')
    home,cfg=instance_home(instance_id);store=home/'http_operations'
    final=store/(operation_id+'.json');writing=Path(str(final)+'.WRITING')
    a=read(final);b=read(writing)
    if a['operationId']!=operation_id or b['operationId']!=operation_id or a['kind']!='decision':raise ValueError('EXACT_FAILED_FIRST_Q1_ID')
    if a['status']!='PENDING' or b['status']!='RUNNING' or set(b)-set(a)!={'startedUtcEpoch'}:raise ValueError('ONLY_PENDING_TO_RUNNING_PRE_SUBMIT')
    expected={**a,'status':'RUNNING','startedUtcEpoch':b['startedUtcEpoch']}
    if b!=expected or a['requestSha256']!=digest({'kind':a['kind'],'body':a['body']}):raise ValueError('EXACT_SAME_DURABLE_REQUEST_BYTES')
    if cfg['nativeTick']!=991187 or cfg['localSequence']!=0 or cfg['completedCycles']!=0:raise ValueError('ORIGINAL_UNUSED_DEMO_ONLY')
    proof=closed_native(home,cfg)
    if proof['nativeTick']!=991187:raise ValueError('NATIVE_ADVANCED_PRESERVE_NO_CANCEL')
    ledger=read(RUNTIME/'estado_demo/LEDGER_SDK.json')
    if ledger['intents'] or ledger['consumed']!=0:raise ValueError('NO_PENDING_OR_CONSUMED_NATIVE_DOSE')
    service=home/'sistema/estado/servicios_persistentes'/cfg['lifeId']
    con=sqlite3.connect((service/'cola.sqlite3').resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if con.execute('SELECT COUNT(*) FROM requests WHERE id=?',(operation_id,)).fetchone()[0]!=0:raise ValueError('NATIVE_QUEUE_ID_EXISTS_DO_NOT_CANCEL')
    finally:con.close()
    if (home/'ensayos'/(operation_id+'.json')).exists():raise ValueError('MATERIAL_RECEIPT_EXISTS_PRESERVE')
    card=read(home/'sistema/estado/vidas'/cfg['lifeId']/'VIDA.json')
    if card['physical']['RAW_sha256']!='9ad61a393fecc935f1c873cd09b14524cb3be9a4b0058b044ce853363aaa6c57' or card['physical']['clocks_sha256']!='8211dc23dcea257aa42e80a22d08cc93902961528470f99d18648b2815a05655':
        raise ValueError('EXACT_UNADVANCED_RAW_CLOCKS_REQUIRED')
    c=read(home/'CONTEXTO_EJECUCION.json');observer=next(x for x in c['tool_sources'] if Path(x['file']).name=='observador_pasivo.py')
    path=RUNTIME/observer['file']
    if sha(path)!=observer['sha256']:raise ValueError('OFFICIAL_PASSIVE_OBSERVER_PIN')
    spec=importlib.util.spec_from_file_location('_cancel_passive_observer',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    view=m.snapshot_view(home/'sistema'/card['snapshot'])
    if 'DEE.Cognitive.Roblox.SDK.native.0.1.0' in view['metadata']:raise ValueError('ACTOR_ALREADY_ADMITTED_NO_CANCEL')
    journal=[json.loads(x) for x in (home/'ENSAYOS.jsonl').read_text('utf8').splitlines() if x.strip()]
    closed=[x for x in journal if x.get('kind')=='OWNER_CLOSED']
    if not closed or closed[-1]['exit_code']!=0 or closed[-1]['final_status']['running'] is not False:raise ValueError('EXACT_OWNER_CLOSED_PROOF_REQUIRED')
    value={'schema':'DEE.Roblox.SDK.pre_native_cancel.R04','instanceId':instance_id,'operationId':operation_id,
           'finalSha256':sha(final),'writingSha256':sha(writing),'native':proof,'nativeQueueExactIdCount':0,
           'actorKeyAbsent':True,'newNativeTicks':0,'ledgerSha256':sha(RUNTIME/'estado_demo/LEDGER_SDK.json'),
           'cause':'WinError5 publishing RUNNING before adapter.execute; no Native admission',
           'ownerClosed':{k:closed[-1][k] for k in ('run','pid','exit_code')},'executed':execute}
    if not execute:return value
    target=home/'technical_cancellations'/operation_id;target.mkdir(parents=True,exist_ok=False)
    (target/'PENDING_ORIGINAL.json').write_bytes(final.read_bytes());(target/'RUNNING_UNPUBLISHED.json').write_bytes(writing.read_bytes())
    if sha(final)!=value['finalSha256'] or sha(writing)!=value['writingSha256']:raise RuntimeError('FAILED_REQUEST_CHANGED_BEFORE_CANCELLATION')
    os.replace(writing,target/'RUNNING_ORIGINAL.json.WRITING')
    cancelled={**a,'status':'CANCELLED_PRE_NATIVE','error':{'code':'WINDOWS_ATOMIC_RENAME_PRE_SUBMIT','message':'Known not submitted; preserve original ID, no automatic replay'},
               'cancellationEvidence':str((target/'RESULTADO.json').relative_to(home)),'cancelledUtcEpoch':time.time()}
    atomic(final,cancelled);value['cancelledSha256']=sha(final);atomic(target/'RESULTADO.json',value,new=True)
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--instance',required=True);p.add_argument('--operation-id',required=True);p.add_argument('--execute-root-only',action='store_true')
    a=p.parse_args();print(canonical(cancel(a.instance,a.operation_id,execute=a.execute_root_only)))
