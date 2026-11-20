"""Root-approved zero-Native restoration of four saved rig collision flags.
No initialize, movement, action, reward, owner, or Native engine import.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
SID='R07_MAIN_adc933c82cc74fb0bb19';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
SOURCE=ROOT/'evidencia/MAIN_BLOQUE_01_CONTINUACION34_R01/WORLD_CHECKPOINT.json'
SOURCE_SHA='3c8420a1fcbebce4514030fb937d76d87e1686f8349a3dcf04922850a8a1a2a7'
PATHS=['DEE_Body/Left Arm','DEE_Body/Left Leg','DEE_Body/Right Arm','DEE_Body/Right Leg']
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def load(p,n):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m);return m
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def compare(module,source,actual):
    identity={'life':LIFE,'session':SID,'participant':'LIVE_NATIVE'}
    prep=module.verify_restore_events(source,actual,identity)
    before=json.loads(json.dumps(source));after=json.loads(json.dumps(actual))
    before['events']=[];after['events']=[];after['checkpoint_id']=before['checkpoint_id']
    result=module.compare_values(before,after);result['appended_preparation_events']=prep
    return result
def run():
    out=ROOT/'evidencia/MAIN_RESTORE_FIX_R07';need(not out.exists(),'NEW_ROOT_APPROVED_REPAIR_ONLY')
    need(sha(SOURCE)==SOURCE_SHA,'IMMUTABLE_MAIN34_SOURCE')
    source=read(SOURCE);need(source['native_life_id']==LIFE and source['native_tick']==1000571,'EXACT_NATIVE_CUT')
    desired={r['path']:r['canCollide']for r in source['physical']['parts']if r['path']in PATHS}
    need(set(desired)==set(PATHS)and all(v is False for v in desired.values()),'FOUR_EXACT_SAVED_BOOLEANS')
    card=ROOT/'native/MAIN/sistema/estado/vidas'/LIFE/'VIDA.json';ledger=ROOT/'control/LEDGER_V3.json'
    unchanged={str(p):sha(p)for p in(card,ledger)}
    need(read(card)['physical']['tick']==1000571 and not read(ledger)['intents'],'CLOSED_NATIVE_WITH_NO_INTENT')
    out.mkdir();events=out/'EVENTS.jsonl'
    def record(kind,**fields):
        with events.open('a',encoding='utf8')as f:f.write(json.dumps(dict(kind=kind,**fields),ensure_ascii=False)+'\n')
    module=load(ROOT/'control/world_comprimido_v3_R06.py','_restore_collision_transport_only')
    world=module.CompressedWorld('522e9816-883b-4c8b-88cd-04de5607b901',out,record,expected_place='DEE_RBX01_R07_NATIVE.rbxlx')
    try:
        before=world.checkpoint('R07_BEFORE_COLLISION_FIX',out/'WORLD_BEFORE_FIX.json');initial=compare(module,source,before)
        write(out/'COMPARACION_ANTES.json',initial)
        expected_paths={'physical.parts['+str(i)+'].canCollide'for i,r in enumerate(source['physical']['parts'])if r['path']in PATHS}
        need(all(x['path']in expected_paths and x.get('before')is False and x.get('after')is True for x in initial['differences']),'NO_OTHER_DIFFERENCE_MAY_BE_REPAIRED')
        code='''local h=game:GetService("HttpService");local s=require(game:GetService("ServerScriptService").RBX01Server.WorldAPI_R07).status();assert(s.phase=="BOUNDARY" and s.S.nativeTick==1000571 and s.S.seq==68 and s.S.sessionId==SESSION and s.S.lifeId==LIFE);local b=workspace.RBX01.DEE_Body;local changes={};local saved=h:JSONDecode(SAVED);for path,wanted in pairs(saved)do local name=path:match("^DEE_Body/(.+)$");local p=b:FindFirstChild(name);assert(p and p:IsA("Part") and p:GetAttribute("R07PreparedBody")==true and type(wanted)=="boolean");changes[#changes+1]={path=path,before=p.CanCollide,after=wanted};p.CanCollide=wanted end;return {changed_fields=changes,Native_calls=0,actions=0,rewards=0,source_sha256=SOURCE}'''
        code=code.replace('SESSION',json.dumps(SID)).replace('LIFE',json.dumps(LIFE)).replace('SAVED',module.BASE.literal(json.dumps(desired))).replace('SOURCE',json.dumps(SOURCE_SHA))
        repaired=world.mcp(code,'restore_exact_four_collision_flags_once');write(out/'INTERVENCION_TECNICA.json',repaired)
        first=world.checkpoint('R07_AFTER_COLLISION_FIX',out/'WORLD_AFTER_FIX.json');one=compare(module,source,first);write(out/'COMPARACION_DESPUES.json',one)
        need(one['equal_with_declared_geometry_tolerance'],'FULL_ORIGINAL_COMPARISON_REQUIRED')
        time.sleep(1)
        stable=world.checkpoint('R07_COLLISION_FIX_STABILITY',out/'WORLD_STABLE_AFTER_1S.json');two=compare(module,source,stable);write(out/'COMPARACION_ESTABILIDAD_1S.json',two)
        need(two['equal_with_declared_geometry_tolerance'],'COLLISIONS_OR_OTHER_FIELDS_CHANGED_AFTER_ONE_SECOND')
        need(unchanged=={str(p):sha(p)for p in(card,ledger)},'NATIVE_CARD_OR_LEDGER_CHANGED')
        result=dict(status='EXACT_SAVED_COLLISIONS_RESTORED_FULL_WORLD_STABLE',source_world_sha256=SOURCE_SHA,
          stable_world=str(out/'WORLD_STABLE_AFTER_1S.json'),stable_world_sha256=sha(out/'WORLD_STABLE_AFTER_1S.json'),
          original_comparator_tolerance=one['geometry_absolute_tolerance'],differences_after=two['differences'],
          unchanged_native_card_and_ledger=unchanged,Native_calls=0,actions=0,rewards=0,initialization_replayed=False,
          next_opportunity=35,sequence=68,session=SID)
        write(out/'RESULTADO.json',result);return result
    finally:world.close()
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
