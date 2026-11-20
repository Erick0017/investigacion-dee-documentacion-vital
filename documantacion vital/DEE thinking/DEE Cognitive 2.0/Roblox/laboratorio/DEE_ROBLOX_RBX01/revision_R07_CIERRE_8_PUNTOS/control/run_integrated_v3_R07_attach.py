"""Same frozen R06 Native loop, adopting a verified already-restored World.
Import/help is stdlib-only. Never replays World.initialize or opportunity34.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='3c8420a1fcbebce4514030fb937d76d87e1686f8349a3dcf04922850a8a1a2a7'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN';SID='R07_MAIN_adc933c82cc74fb0bb19'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_text('utf-8-sig'))
def guard_identity(state,identity,source_sha):
    need(source_sha==SOURCE_SHA and state['native_life_id']==LIFE and state['native_tick']==1000571,'EXACT_SOURCE_NO_FUTURE_TRANSPLANT')
    need(identity==dict(life=LIFE,session=SID,participant='LIVE_NATIVE'),'SAME_MAIN_AND_SESSION')
    need(state['boundary']['next_opportunity']==35 and state['S']['seq']==68 and state['S']['sessionId']==SID,'NO_BEGIN_OR_Q1_REPLAY34')
def execute(args):
    need(args.execute_root_only and args.destination.resolve()==ROOT/'native/MAIN'and args.stop_cycle==46 and args.session==SID,'ONLY_THE_AUTHORIZED_MAIN_BLOCK')
    need(sha(ROOT/'control/run_integrated_v3_R06.py')=='eafe42bd08135345249bb8739edab419d2eec047d08f3cc55903e2de16554de8','FROZEN_R06_LOOP_UNCHANGED')
    need(sha(ROOT/'control/world_comprimido_v3_R06.py')=='cdc3f45f7d2816eb07eab71774576df4d05206d1888af1a8cdefcbe44b8cd088','FROZEN_R06_TRANSPORT_UNCHANGED')
    proof_path=args.repair_proof.resolve(strict=True);proof=read(proof_path)
    need(proof_path==ROOT/'evidencia/MAIN_RESTORE_FIX_R07/RESULTADO.json'and
      proof['status']=='EXACT_SAVED_COLLISIONS_RESTORED_FULL_WORLD_STABLE'and proof['Native_calls']==0 and not proof['initialization_replayed'],'ROOT_REVIEWED_ZERO_NATIVE_REPAIR')
    before=ROOT/'evidencia/MAIN_REAPERTURA_35_46_R06/EVENTS.jsonl'
    old=[json.loads(x)for x in before.read_text('utf8').splitlines()if x.strip()]
    need(not any(x['kind']in('NATIVE_INTENT','NATIVE_COMPLETED','PROTOCOL_STARTED')for x in old),'FAILED_FIRST_RESTORE_NEVER_OPENED_OWNER')
    card=ROOT/'native/MAIN/sistema/estado/vidas'/LIFE/'VIDA.json'
    need(sha(card)==proof['unchanged_native_card_and_ledger'][str(card)],'NATIVE_CARD_CHANGED_AFTER_ZERO_TICK_REPAIR')
    ledger=ROOT/'control/LEDGER_V3.json';need(sha(ledger)==proof['unchanged_native_card_and_ledger'][str(ledger)],'LEDGER_CHANGED_AFTER_REPAIR')
    budget=read(ledger);need(not budget['intents']and budget['consumed']==32844,'QUIESCENT_NATIVE_BOUNDARY')
    loop=load(ROOT/'control/run_integrated_v3_R06.py','_same_native_loop_R06')
    transport=load(ROOT/'control/world_comprimido_v3_R06.py','_same_transport_R06')
    repair=load(ROOT/'control/reparar_colisiones_restore_R07.py','_pure_restore_comparison_R07')
    class AttachedWorld(transport.CompressedWorld):
        def initialize(self,state,identity,source_sha):
            guard_identity(state,identity,source_sha)
            actual=self.checkpoint('R07_ADOPT_VERIFIED_SAME_WORLD',self.output/'WORLD_ADOPTED_BEFORE_NATIVE_R07.json')
            need(actual['native_life_id']==LIFE and actual['native_tick']==1000571 and actual['S']['sessionId']==SID and
                 actual['S']['seq']==68 and actual['boundary']['next_opportunity']==35 and
                 actual['boundary']['phase']=='BOUNDARY'and actual['boundary']['native_phase']=='IDLE'and actual['boundary']['uncertain']is False,'CURRENT_WORLD_SAME_IDS_READY')
            comparison=repair.compare(transport,state,actual)
            with(self.output/'WORLD_ADOPTION_COMPARISON_R07.json').open('x',encoding='utf8')as f:json.dump(comparison,f,ensure_ascii=False,indent=2)
            need(comparison['equal_with_declared_geometry_tolerance'],'ORIGINAL_FULL_COMPARATOR_MUST_STILL_PASS')
            self.record('WORLD_RESTORE_SEMANTICS_VERIFIED',comparison=comparison,initialization_replayed=False,
              adoption_only=True,repair_proof=str(proof_path),repair_proof_sha256=sha(proof_path),Native_memory_edited=False)
            return dict(restored={'checkpoint_id':actual['checkpoint_id']},S=actual['S'],phase='BOUNDARY',new_Native_ticks=0,adoption_only=True)
    loop._world_class=lambda:AttachedWorld
    return loop.execute(args)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
    for flag in('destination','world','output','ledger','repair-proof'):p.add_argument('--'+flag,type=Path,required=True)
    p.add_argument('--studio-id',required=True);p.add_argument('--session',required=True);p.add_argument('--stop-cycle',type=int,required=True)
    p.add_argument('--expected-place',default='DEE_RBX01_R07_NATIVE.rbxlx');execute(p.parse_args())
