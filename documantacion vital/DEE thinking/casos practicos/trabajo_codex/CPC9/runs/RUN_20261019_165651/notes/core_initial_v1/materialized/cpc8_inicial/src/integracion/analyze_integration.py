"""Post-trajectory reconciliation only; never imports or advances the engine."""
from pathlib import Path
import hashlib
import json
import os

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'resultados/integracion'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path,v):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def shape(p,kind):
    if not p['active'] or p['semantic']!=1:return False
    x,y,z=p['direction']
    return (x in(-1,1) and y==z==0) if kind=='question' else (x in(-1,1) and y in(-1,1) and z==(1 if kind=='action' else 0))


def main():
    index=[];data=[];loaded={};replays=[]
    for path in sorted(BASE.glob('*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'));schema=m.get('schema','')
        if schema=='CPC8.integration.passive_local_replay.v1':
            replays.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'technical_status':m['technical_status'],'independent_preparations':0,'scientific_replicates_added':0});continue
        if m.get('status')!='MEASURED' or schema not in('CPC8.integration.shared.measurements.v1','CPC8.integration.alias_L17.measurements.v1','CPC8.integration.revision_L01.measurements.v1'):continue
        cid=m['case']['id'];loaded[cid]=m
        family='RELOCATED_L17_WITH_FINITE_L01_REVISION' if m['geometry'].get('revision_profile') else 'RELOCATED_L17' if m.get('factory_adapter') else 'DIRECT_ALIAS_L17' if 'alias' in m['geometry'] else 'COEXISTENCE_K65_PLUS_TWO'
        snap=[{'path':(path.parent/q['path']).relative_to(ROOT).as_posix(),'sha256':q['sha256'],'exists':(path.parent/q['path']).exists()} for q in m['snapshots']]
        expected_sources={**m.get('executed_source',{}),**m.get('factory_adapter',{}).get('sources',{})}
        source_checks=[{'name':name,'declared_sha256':digest,'copied_sha256':sha(path.parent/'executed_source'/name) if(path.parent/'executed_source'/name).exists()else None,
            'matches':(path.parent/'executed_source'/name).exists()and sha(path.parent/'executed_source'/name)==digest} for name,digest in expected_sources.items()]
        index.append({'case_id':cid,'family':family,'schema':schema,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'preparations':m['preparations'],'diagnostic_forks':m['diagnostic_forks'],'individual':m['individual'],'snapshots':snap,
            'source_cuts':{q.name:sha(q) for q in (path.parent/'executed_source').glob('*.py')},'declared_source_checks':source_checks})
        frames={r['tick']:r for r in m['local_frames']};t=m['geometry']['ticks']
        def items(tick,field,kind):return [{'port':k,'physical':p} for k,p in frames.get(tick,{}).get(field,{}).items() if shape(p,kind)]
        signs=[{'tick':r['tick'],'readings':[{'bank':x['name'],'value':x['value'],'status':x['status'],'physical':x['physical'],'receipt':x['receipt']} for x in r['responses'] if x['coverage']],
            'all_original_readings':r['responses']} for r in m['reads'] if r['kind']=='name']
        data.append({'case_id':cid,'family':family,'resources':m['geometry']['resources'],'question':items(19,'questions','question'),
            'own_information':items(t['information'],'own_information','information'),'action':items(t['action'],'actions','action'),
            'opaque_sign_queries':signs,'lower_panels':m['calculations'].get('lower_panels',m['calculations'].get('panels',[])),'receipt_statuses':m['calculations']['receipt_statuses'],
            'final_physical':m['final_physical'],'initial_alias':m['geometry'].get('alias'),
            'revision_profile':m['geometry'].get('revision_profile'),'baseline_before_revision':m.get('baseline_before_revision'),
            'scope':'Vectors/receipts and labelled output classes only; the resource count is not an NSM meaning count.'})
    comparisons=[]
    for mainid,shamid in(('E1_P11_AB','E1_D12_SHAM'),('AL_P11_BA','AL_D12_SHAM'),('RL_P11_BA','RL_D12_SHAM')):
        if mainid in loaded and shamid in loaded:
            a,b=loaded[mainid],loaded[shamid]
            at={p['tick']:p['physical'] for p in a['frontiers']};bt={p['tick']:p['physical'] for p in b['frontiers']}
            common=sorted(set(at)&set(bt));matched_tick=max(common)
            def past(m):return[q for q in m['requests'] if q['receipt']['requested_tick']<=matched_tick]
            comparisons.append({'main':mainid,'sham':shamid,'matched_tick':matched_tick,
                'common_frontiers':[{'tick':tick,'full_RAW_clocks_tick_equal':at[tick]==bt[tick]} for tick in common],
                'full_matched_RAW_clocks_tick_equal':at[matched_tick]==bt[matched_tick],
                'past_request_payload_tick_receipt_fields_equal':past(a)==past(b),
                'final_ages_equal':a['final_physical']['tick']==b['final_physical']['tick'],
                'scope':'Compare equal-age physical frontiers and requested inputs through that age. Long parent trajectories may queue additional future panels that shorter shams do not request. Case/identity/diagnostic metadata intentionally differ; not snapshot-envelope equality.'})
    summary={'schema':'CPC8.integration.reconciliation.v1','data':data,'calculations':{
        'independent_preparations':sum(x['preparations'] for x in index),'diagnostic_forks':sum(x['diagnostic_forks'] for x in index),
        'scientific_primary_records':len(index),'technical_replays':len(replays),'sham_comparisons':comparisons,
        'declared_source_copies_checked':sum(len(x['declared_source_checks']) for x in index),'source_copy_mismatches':sum(not c['matches'] for x in index for c in x['declared_source_checks'])},
        'provisional_interpretation':[
            'E1 tests same-Runtime compatibility of65lower banks and a finiteU0 chain using2extra own banks; it is not native selection among65.',
            'E1RIGHT shifted-cue control can preserve output through a ballistic event return: compare48with53 and direction, not only final sign.',
            'LEFT alias experiments make actualL17 supply the native query. Its original-port access and later sign use are measured separately.',
            'Direct column near the body may lose additional lower accesses; selective relocation is a new equal-inventory research geometry, not a repair of the frozen kernel.',
            'Finite L01 revision, when present, adds only inert interfaces beforeT0 and later explicit experiences; it is not autonomous selection of an update policy or a fourth physical architecture family.',
            'All65lower correspondences draw from2physical direction classes; no65generalNSM meanings are credited by these trajectories.'],
        'technical_reproduction_records':replays,'primary_index':'resultados/integracion/INDEX_INCREMENTAL.json'}
    put(BASE/'INDEX_INCREMENTAL.json',{'schema':'CPC8.integration.index.v1','cases':index,'technical_replays':replays})
    put(BASE/'ANALYSIS_INCREMENTAL.json',summary)
    print(json.dumps(summary['calculations']))


if __name__=='__main__':main()
