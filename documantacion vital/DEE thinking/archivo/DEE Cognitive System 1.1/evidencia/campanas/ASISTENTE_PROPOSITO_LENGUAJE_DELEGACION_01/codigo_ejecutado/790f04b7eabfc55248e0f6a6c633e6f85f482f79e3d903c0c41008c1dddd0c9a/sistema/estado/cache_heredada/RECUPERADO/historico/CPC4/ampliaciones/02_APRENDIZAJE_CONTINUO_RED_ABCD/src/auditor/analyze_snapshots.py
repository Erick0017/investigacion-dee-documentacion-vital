"""Passive local reconstruction and nontrivial deep-fork isolation, no ticks."""
from pathlib import Path
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.auditor.passive import capture,digest,record,operation_state,neighborhood

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,x):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

def main():
    import dee_thinking as d
    out=ROOT/'resultados/auditor';base=ROOT/'resultados/red/discovery01/CENTRAL'
    frames=[]
    cases=[('SOCIAL93','BEFORE_D_SOCIAL.deetsnap',(26,43,23),58),
           ('READ160','BEFORE_D_READ.deetsnap',(27,43,23),74)]
    for label,name,site,expected_load in cases:
        source=base/name;world=d.OrganizationalWorld.load_snapshot(str(source));q=d.Coordinate(*site)
        before=operation_state(world);pre=record(world.runtime.observe(q))
        assert pre['active'] and pre['s_reg']==expected_load
        edit=d.ResearchStateEdit();edit.coordinate=q;edit.raw=0;edit.label='AUDITOR_NONTRIVIAL_LIVE_PORTADOR_REMOVAL'
        child=world.diagnostic_fork([edit],True);post=record(child.runtime.observe(q))
        raw_parent=world.runtime.raw_copy();raw_child=child.runtime.raw_copy()
        clocks_parent=world.runtime.clock_copy();clocks_child=child.runtime.clock_copy()
        nraw=sum(a!=b for a,b in zip(raw_parent,raw_child));nclock=sum(a!=b for a,b in zip(clocks_parent,clocks_child))
        assert nraw==1 and nclock==0 and operation_state(world)==before
        parent_path=out/'NONTRIVIAL_FORKS'/(label+'_PARENT_RUNTIME.deetsnap');parent_path.parent.mkdir(parents=True,exist_ok=True)
        world.runtime.save_snapshot(str(parent_path));child_path=parent_path.with_name(label+'_CHILD.deetsnap');child.save_snapshot(str(child_path))
        frames.append({'id':label,'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),
            'mode':'DIAGNOSTIC_FORK_NO_ADVANCE_NEVER_MERGED','pre':pre,'post':post,'RAW_sites_changed':nraw,
            'clock_sites_changed':nclock,'full_parent_operational_unchanged':operation_state(world)==before,
            'parent':str(parent_path.relative_to(ROOT)),'child':str(child_path.relative_to(ROOT)),
            'source_tick_preserved':child.runtime.current_tick==world.runtime.current_tick,
            'scope':'Proves nontrivial copy isolation for these two states, not functional necessity; no child evolved.'})
    put(out/'NONTRIVIAL_FORK_ISOLATION.json',{'native_ticks_advanced':0,'checks':frames})
    preworld=d.OrganizationalWorld.load_snapshot(str(base/'BEFORE_D_SOCIAL.deetsnap'))
    postworld=d.OrganizationalWorld.load_snapshot(str(base/'AFTER_D_SOCIAL.deetsnap'))
    context=neighborhood(preworld,(26,44,24));post=record(postworld.runtime.observe(d.Coordinate(26,44,24)))
    proposals=context['directional_proposals_without_activity_prefilter']
    direction_sum=[sum(r['direction'][i] for r in proposals) for i in range(3)]
    expected_direction=[(x>0)-(x<0) for x in direction_sum]
    source_load_sum=sum(r['s_reg'] for r in proposals)
    reconstruction={'classification':'PASSIVE_FIELD_RULE_RECONSTRUCTION_NO_ABLATION',
       'transition':[93,94],'target':[26,44,24],'pre_context':context,'post_target':post,
       'observed_proposal_count':len(proposals),'observed_source_load_sum':source_load_sum,
       'observed_source_direction_sum':direction_sum,'sign_direction':expected_direction,
       'post_matches_two_source_context':len(proposals)==2 and source_load_sum==post['s_reg'] and expected_direction==post['direction'],
       'empty_target_before':context['center']['raw']==0,
       'scope':'Target is empty in saved93 and receives the measured local sources58(0,+1,+1) and16(-1,0,0). This is field/branch participation. Functional necessity requires the separate new native cut controls; it is not inferred from source-load equality alone.',
       'source_snapshots':[{'path':str((base/name).relative_to(ROOT)),'sha256':sha(base/name)} for name in ('BEFORE_D_SOCIAL.deetsnap','AFTER_D_SOCIAL.deetsnap')]}
    put(out/'D_SOCIAL_CONTEXT93_94.json',reconstruction)
    attempted=out/'ABCD_WINDOW160_161';a=(attempted/'lazy_FINAL_RUNTIME.deetsnap').read_bytes();diff=[]
    for name in ('dense_FINAL_RUNTIME.deetsnap','parallel_one_thread_FINAL_RUNTIME.deetsnap','DIRECT_FINAL_RUNTIME.deetsnap'):
        b=(attempted/name).read_bytes();offsets=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
        diff.append({'artifact':str((attempted/name).relative_to(ROOT)),'sha256':sha(attempted/name),
            'same_length':len(a)==len(b),'different_byte_count':len(offsets),'different_offsets':offsets,
            'values_at_difference':[{'offset':i,'lazy':a[i],'other':b[i]} for i in offsets]})
    note={'technical_attempt':'auditor_ABCD_window01','original_lazy_sha256':sha(attempted/'lazy_FINAL_RUNTIME.deetsnap'),
       'comparison':diff,'cause':'Runtime.cpp656 saves execution_options_.backend; snapshot checksum also changes. This is an intentionally different scheduling descriptor, not a difference in observed RAW/clocks/operative future.',
       'resolution':'Keep original artifacts distinct. V2 also compares opaque full Runtime bytes after setting only the final technical-copy execution descriptor back to the same value, without advance or physical edits.',
       'noop_fork_notice':'The original broad window checks attempted RAW0 removal at an empty fixed port. That parent remained unchanged, but the no-op is not used to claim nontrivial isolation. NONTRIVIAL_FORK_ISOLATION explicitly removes actual58/74 records and verifies one RAW site and zero clocks.'}
    put(out/'TECHNICAL_HOTFIX_AND_BYTE_DIFF.json',note)
    print(json.dumps({'forks':2,'native_ticks':0,'social_proposals':len(proposals),'post74':post['s_reg'],
                      'context_matches':reconstruction['post_matches_two_source_context']}))

if __name__=='__main__':main()
