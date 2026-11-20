"""Pre/post local reducer reconstruction, not charge-based carrier genealogy."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha


def sign(x):return(x>0)-(x<0)


def pack(state,load,vector,semantic):
    return state | (load<<32) | ((vector[0]&15)<<48) | ((vector[1]&15)<<52) | ((vector[2]&15)<<56) | ((semantic&15)<<60)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from presence_count import PresenceCountSession
    from relaciones.contact_cardinality import move
    s=PresenceCountSession.load(a.parent/'T10.deetsnap.gz')
    data={'schema':'CPC9.native.local_reducer_reconstruction.v1','preparations':0,'forks':0,'continuations':1,'technical_reproduction':1,
          'parent':{'snapshot':'T10.deetsnap.gz','sha256':sha(a.parent/'T10.deetsnap.gz'),'case':a.parent.name},'new_inputs':[],
          'branches':[],'source_sha256':sha(__file__),'scope':'Exact localbranch only. No global unique genealogy inferred from charge or proximity.'}
    for post_tick in(13,45):
        s.run_until(post_tick-1);target=move(s.geometry['collector'],(1,0,1),post_tick-10);pre=s.observe(target)
        neighbors=[]
        for x in(-1,0,1):
            for y in(-1,0,1):
                for z in(-1,0,1):
                    if(x,y,z)==(0,0,0):continue
                    obs=s.observe(move(target,(x,y,z)));neighbors.append({'offset':[x,y,z],'physical':obs})
        sources=[]
        for row in neighbors:
            obs=row['physical'];v=obs['direction']
            if v!=[0,0,0] and move(obs['site'],v)==target:sources.append(obs)
        nactive=sum(o['physical']['state']>0 and o['physical']['semantic']!=5 for o in neighbors)
        gradient=[-sum(row['offset'][i]*row['physical']['s_reg']for row in neighbors if row['physical']['state']>0)for i in range(3)]
        branch={'post_tick':post_tick,'target':target,'pre':pre,'Moore26_pre':neighbors,'sources_pointing_to_target':sources,
                'n_active_neighbors':nactive,'gradient_pre':gradient,'empty_branch_low_mass_guard':pre['state']==0 and nactive<8 and sum(abs(x)for x in gradient)//19665<966,
                'prediction_origin':'AUDITOR_PRIOR_NATIVE_RULE_RECONSTRUCTION_NOT_ENTE_EXPECTATION'}
        if branch['empty_branch_low_mass_guard'] and sources:
            if len(sources)==1:expected=int(sources[0]['raw'])
            else:expected=pack(1,min(19664,sum(o['s_reg']for o in sources)),[sign(sum(o['direction'][i]for o in sources))for i in range(3)],1)
            branch['predicted_raw_before_step']=str(expected)
        data['branches'].append(branch);data['last_complete_tick']=s.tick;put(a.out/'MEASUREMENTS.json',data)
        s.run_until(post_tick);post=s.observe(target);branch['post']=post
        branch['predicted_raw_equal_post']=branch.get('predicted_raw_before_step')==post['raw']
        branch['clock_rule_equal']=int(post['clock'])==int(pre['clock'])+1
        data['last_complete_tick']=s.tick;put(a.out/'MEASUREMENTS.json',data)
    data.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts());put(a.out/'MEASUREMENTS.json',data)
    print(json.dumps({'branches':[{'tick':r['post_tick'],'sources':len(r['sources_pointing_to_target']),'source_loads':[o['s_reg']for o in r['sources_pointing_to_target']],
        'raw_match':r['predicted_raw_equal_post'],'clock_match':r['clock_rule_equal'],'post':r['post']}for r in data['branches']]}),flush=True)
