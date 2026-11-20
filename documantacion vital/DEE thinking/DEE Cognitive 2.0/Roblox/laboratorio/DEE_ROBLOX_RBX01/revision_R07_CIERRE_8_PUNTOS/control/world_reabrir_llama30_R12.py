"""Prepared reference-only restore correction. Import performs no connection.

The original full comparator remains authoritative. Four saved collision flags
may be restored after rig preparation; nothing is ignored to obtain equality.
No Native, model, policy, sensor, motor-parameter or World API source change.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='2fda6fa8b8226a76aa6ea5a40093c8d1942cebe11f71449204cd8a0282d9b526'
SID='R07_CONVENTIONAL_AI_R09_01'
LIFE='R07_CONVENTIONAL_AI'
HOOK_SHA='d4168ecaaafe686e443b57d2e678600e2a030bae73f432c968bfebac10e069da'
LIMBS={'DEE_Body/Left Arm','DEE_Body/Left Leg','DEE_Body/Right Arm','DEE_Body/Right Leg'}
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
BASE=load(ROOT/'control/world_comprimido_v3_R08_REFERENCIAS.py','_R12_original_reference_world')
def need(x,m):
    if not x:raise ValueError(m)
def save(p,value):
    with Path(p).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def source_guard(state,identity,source_sha):
    need(source_sha==SOURCE_SHA,'EXACT_CLOSED_R11_WORLD_SHA')
    need(state['world_id']=='RBX01_CIERRE8_R07'and state['native_life_id']==LIFE and state['native_tick']==0,'REFERENCE_WORLD_ONLY_NO_NATIVE')
    need(identity=={'life':LIFE,'session':SID,'participant':'CONVENTIONAL_AI','diagnostic':False},'SAME_REFERENCE_IDENTITY')
    b=state['boundary'];s=state['S']
    need(b['phase']=='BOUNDARY'and b['native_phase']=='IDLE'and b['uncertain']is False and b['next_opportunity']==31 and b['completed_opportunities']==30,'ONLY_30_CLOSED_REOPEN_AT31')
    need(s['sessionId']==SID and s['lifeId']==LIFE and s['completedCycles']==30 and s['seq']==60 and s['nativeTick']==0,'SAME_HISTORY_WORLD_COUNTERS')
def saved_mask(state):
    rows=[];indices={}
    for i,row in enumerate(state['physical']['parts']):
        if row.get('path')in LIMBS:
            need(row['path']not in indices and type(row.get('canCollide'))is bool,'ONE_SAVED_BOOLEAN_PER_LIMB')
            need(isinstance(row.get('attributes'),dict)and row['attributes'].get('R07PreparedBody')is True,'SAVED_PREPARED_RIG')
            rows.append({'path':row['path'],'canCollide':row['canCollide'],'attributes':{'R07PreparedBody':True}});indices[row['path']]=i
    need(set(indices)==LIMBS and len(rows)==4,'EXACT_FOUR_SAVED_LIMBS')
    return sorted(rows,key=lambda x:x['path']),indices
def full_compare(source,restored,identity):
    # Identical normalizations to BASE.initialize for a SAME_PAIR re-open.
    need(source['native_life_id']==identity['life']and source['world_id']==restored['world_id'],'NO_PARENT_CONTENTS_ONLY_FALLBACK')
    kinds=BASE.verify_restore_events(source,restored,identity)
    before=copy.deepcopy(source);after=copy.deepcopy(restored)
    before['events']=[];after['events']=[];after['checkpoint_id']=before['checkpoint_id']
    comparison=BASE.compare_values(before,after)
    comparison.update(comparison_mode='SAME_PAIR_FULL_STATE_REOPEN',appended_preparation_events=kinds,
      normalization='Original BASE comparison: exact declared appended preparation events and checkpoint document identity only; original technical UI exclusions/tolerance unchanged.')
    return comparison
def require_only_collision_diffs(comparison,state):
    rows,indices=saved_mask(state)
    allowed={'physical.parts['+str(indices[r['path']])+'].canCollide':r['canCollide']for r in rows}
    for d in comparison['differences']:
        need(d.get('path')in allowed and type(d.get('before'))is bool and type(d.get('after'))is bool and d['before']is allowed[d['path']],
             'OTHER_RESTORE_DIFFERENCE_PRESERVED_NO_PATCH:'+str(d.get('path')))
    return rows
def repair_code(state):
    rows,_=saved_mask(state);hook=ROOT/'mundo/ReponerColisionesTrasRig_R07_R02.luau'
    raw=hook.read_bytes();need(hashlib.sha256(raw).hexdigest()==HOOK_SHA,'PREPARED_RESTORE_HOOK_SOURCE_CHANGED')
    packet=json.dumps(json.dumps(rows,ensure_ascii=True,separators=(',',':')))
    return ('local H=game:GetService("HttpService");local API=require(game:GetService("ServerScriptService").RBX01Server.WorldAPI_R07);'
      'local current=API.status();assert(current.phase=="BOUNDARY"and current.S.sessionId=='+json.dumps(SID)+
      ' and current.S.lifeId=='+json.dumps(LIFE)+' and current.S.completedCycles==30 and current.S.seq==60 and current.S.nativeTick==0,"R12_EXACT_RESTORED_REFERENCE_BOUNDARY");'
      'local worldRoot=assert(workspace:FindFirstChild("RBX01"));local body=assert(worldRoot:FindFirstChild("DEE_Body"));'
      'local hook=(function()\n'+raw.decode('utf8')+'\nend)();local rows=H:JSONDecode('+packet+');'
      'return hook.applySavedMask(worldRoot,body,rows,"DEE_Body")')
class ReopenedReferenceWorld(BASE.CompressedWorld):
    def initialize(self,state,identity,source_sha):
        source_guard(state,identity,source_sha);saved_mask(state)
        self._R12_source=copy.deepcopy(state);self._R12_identity=copy.deepcopy(identity);self._R12_restore_pending=True
        try:return super().initialize(state,identity,source_sha)
        finally:self._R12_restore_pending=False
    def checkpoint(self,checkpoint_id,path):
        if not getattr(self,'_R12_restore_pending',False):return super().checkpoint(checkpoint_id,path)
        need(Path(path).name=='WORLD_RESTORED_BEFORE_NATIVE.json','EXACT_ORIGINAL_RESTORE_CAPTURE_CALL')
        source=self._R12_source;identity=self._R12_identity
        before=super().checkpoint(checkpoint_id+'_BEFORE_MASK',self.output/'WORLD_RESTORED_BEFORE_COLLISION_MASK_R12.json')
        pre=full_compare(source,before,identity);save(self.output/'WORLD_RESTORE_PRE_MASK_COMPARISON_R12.json',pre)
        mask=require_only_collision_diffs(pre,source)
        applied=None
        if pre['differences']:
            applied=self.mcp(repair_code(source),'restore_exact_saved_four_CanCollide_once_R12')
            need(isinstance(applied,dict)and len(applied.get('changes',[]))==4,'EXACT_RESTORE_ACK_REQUIRED')
        restored=super().checkpoint(checkpoint_id,path)
        post=full_compare(source,restored,identity)
        save(self.output/'WORLD_RESTORE_POST_MASK_COMPARISON_R12.json',post)
        need(post['equal_with_declared_geometry_tolerance'],'ORIGINAL_FULL_COMPARE_FAILED_AFTER_MASK')
        time.sleep(1.0) # World stability only, no backend/model/Native invocation.
        stable=super().checkpoint(checkpoint_id+'_STABLE',self.output/'WORLD_RESTORED_STABLE_AFTER_COLLISION_MASK_R12.json')
        stability=full_compare(source,stable,identity)
        save(self.output/'WORLD_RESTORE_STABILITY_COMPARISON_R12.json',stability)
        need(stability['equal_with_declared_geometry_tolerance'],'ORIGINAL_FULL_COMPARE_FAILED_AFTER_ONE_SECOND')
        proof={'schema':'DEE.R07.reference_same_pair_collision_restore.R12','source_world_sha256':SOURCE_SHA,
          'session':SID,'source_completed':30,'next_opportunity':31,'saved_mask':mask,'pre_patch_differences':pre['differences'],
          'mask_required':bool(pre['differences']),'mask_ack':applied,'post_original_full_equal':True,'one_second_original_full_equal':True,
          'geometry_tolerance':1e-5,'comparator_unchanged':True,'no_ignored_collision_fields':True,
          'backend_or_model_opened_by_hook':False,'Native_calls':0,'policy_changes':0,'actions':0,'rewards':0,'source_event_history_unchanged':True}
        save(self.output/'WORLD_SAME_PAIR_REOPEN_PROOF_R12.json',proof);self.record('WORLD_SAME_PAIR_COLLISIONS_RESTORED_VERIFIED_R12',proof=proof)
        self._R12_restore_pending=False
        return restored
