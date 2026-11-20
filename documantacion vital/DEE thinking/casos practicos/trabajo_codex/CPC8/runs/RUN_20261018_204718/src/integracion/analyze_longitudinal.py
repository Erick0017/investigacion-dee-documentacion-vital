"""Read-only reconciliation of four controlled continuations and one replay."""
import hashlib
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'resultados/integracion'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def main():
    cases={};index=[];data=[]
    for path in sorted(BASE.glob('LIF_*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'))
        if m.get('schema')!='CPC8.integration.longitudinal690.measurements.v1' or m.get('status')!='MEASURED':continue
        cid=m['case']['id'];cases[cid]=m;frames={f['tick']:f['observation']for f in m['frames']}
        def active(rows):return{k:v for k,v in rows.items()if v['active']}
        def valid_action(p):return p['active']and p['semantic']==1 and p['direction'][0]in(-1,1)and p['direction'][1]in(-1,1)and p['direction'][2]==1
        source_checks=[{'path':name,'declared':digest,'matches':(path.parent/'executed_source'/name).exists()and sha(path.parent/'executed_source'/name)==digest}for name,digest in m['executed_source'].items()]
        index.append({'case_id':cid,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'preparations':0,'continuations':1,'diagnostic_forks':0,
            'individual':m['parent']['individual'],'parent':m['parent'],'source_checks':source_checks,
            'snapshots':[{'path':(path.parent/x['path']).relative_to(ROOT).as_posix(),'sha256':x['sha256'],'exists':(path.parent/x['path']).exists()}for x in m['snapshots']]})
        data.append({'case_id':cid,'identity':m['parent']['individual'],'new_exposures':m['new_inputs'],
            'new_exposure_receipts':[q for q in m['new_requests']if q['receipt']['requested_tick']<1048],
            'emission791':frames[791]['body']['emission'],'questions805_all_active':active(frames[805]['questions']),
            'right920':frames[920]['own_information']['right'],'actions922_all_active':active(frames[922]['actions']),
            'action922_three_component_products':[v for v in frames[922]['actions'].values()if valid_action(v)],
            'B926_all_active':active(frames[926]['social']['hubs']),'B943_all_active':active(frames[943]['social']['query_targets']),
            'B947_all_active':active(frames[947]['social']['effect_targets']),
            'delivery952_all_active':active(frames[952]['social']['delivery_targets']),
            'retention1051':m['calculations'],'resource_actual':m['resources_actual'],'resource_metadata_inherited':m['geometry']['resources'],
            'scope':'Data at frozen targets. Activity is not automatically a new emission or a genealogically identified response.'})
    pilot=cases['LIF_P11_NEW_AB'];comparisons=[]
    for cid,m in cases.items():
        if cid=='LIF_P11_NEW_AB':continue
        a={x['tick']:x['physical']for x in pilot['snapshots']};b={x['tick']:x['physical']for x in m['snapshots']}
        af=next(x['observation']['social']['delivery_targets']for x in pilot['frames']if x['tick']==952)
        bf=next(x['observation']['social']['delivery_targets']for x in m['frames']if x['tick']==952)
        comparisons.append({'pilot':'LIF_P11_NEW_AB','control':cid,'full_physical_at_common_frontiers':[{'tick':t,'RAW_clocks_tick_equal':a[t]==b[t]}for t in sorted(set(a)&set(b))],
            'all_delivery952_records_equal':af==bf})
    replay_path=BASE/'LIF_ENTRY_REPLAY/MEASUREMENTS.json';replay=json.loads(replay_path.read_text(encoding='utf8'))
    result={'schema':'CPC8.integration.longitudinal690.analysis.v1','data':data,'calculations':{'preparations':0,'controlled_continuations':len(cases),
        'distinct_parent_frontiers':len({m['parent']['sha256']for m in cases.values()}),'technical_replays':1,
        'source_copies_checked':sum(len(x['source_checks'])for x in index),'source_copy_mismatches':sum(not s['matches']for x in index for s in x['source_checks']),
        'comparisons':comparisons,'technical_replay':{'path':replay_path.relative_to(ROOT).as_posix(),'sha256':sha(replay_path),'comparisons':replay['comparisons']}},
        'provisional_reading':[
            'All four branches continue the same physical parent690 without a new recipe, interface or reset; they are controlled continuations, not four independent initial preparations.',
            'The prior63accessible directional relations remain usable1051 and match all63previous covered values658, after additional experiences and no re-teaching.',
            'The fixed new RIGHT cue/event is admitted and leaves a normalized mobileYcarrier920. The no-cue control has an empty declaredRIGHT hub920, but a distinct load18(+1,-1,+1)product at the action site922 and B hub926. These are different trajectories; covered windows do not establish its entire ancestry. Neither makes the proposed new RIGHT query/use/delivery chain.',
            'New A/B events and common order reader are rejectedOccupied. The prospective second order-learning episode was not admitted; continuing body activity cannot be credited to that new experience.',
            'In the pilot, opposite-order and no-new-order branches no frozen three-component new action appears922. The no-cue branch produces the distinct load18three-component product noted above, without a normalized B memory or new RIGHT delivery. The old LEFT.plus delivery952 is identical in all four branches, including no new order and no newRIGHT cue; it is not evidence of the proposed newRIGHT communication chain.',
            'RAW occupancy of interface targets and passive kernel write-gate flags belong to different contracts. A non-protected kernel site may still reject a host interface because RAW is not empty.',
            'The period6N prediction is one bounded tested apparatus. No phase sweep or port clearing rescues the continuation; failure of admission is a local access boundary, not a universal limit of v27.'],
        'inherited_metadata_caveat':'The original SOC_I21 snapshot records219base interfaces before40social additions. Runtime has259interfaces and15original material sites. Both are retained here; load did not silently repair or reprepare the world.'}
    put(BASE/'LONGITUDINAL_INDEX.json',{'schema':'CPC8.integration.longitudinal690.index.v1','cases':index,'technical_replay':result['calculations']['technical_replay']})
    put(BASE/'LONGITUDINAL_ANALYSIS.json',result);print(json.dumps(result['calculations']))


if __name__=='__main__':main()
